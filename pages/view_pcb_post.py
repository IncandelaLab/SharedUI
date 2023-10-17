from PyQt5 import QtCore
import time
import datetime
# for xml loading:
import csv
from xml.etree.ElementTree import parse

from filemanager import fm, parts, assembly

from PyQt5.QtWidgets import QFileDialog, QWidget

NO_DATE = [2022,1,1]

PAGE_NAME = "view_pcb_post"
OBJECTTYPE = "PCB_step"
DEBUG = False

INDEX_INSTITUTION = {
	'CERN':0,
	'FNAL':1,
	'UCSB':2,
	'UMN':3,
	'HEPHY':4,
	'HPK':5,
	'CMU':6,
	'TTU':7,
	'IHEP':8,
	'TIFR':9,
	'NTU':10,
	'FSU':11
}

INDEX_GRADE = {
	'Green':0,
	'Yellow':1,
	'Red':2,
}

STATUS_NO_ISSUES = "valid (no issues)"
STATUS_ISSUES    = "invalid (issues present)"

# rows / positions
I_NO_PARTS_SELECTED     = "no parts have been selected"
I_ROWS_INCOMPLETE       = "positions {} are partially filled"

# compatibility
I_SIZE_MISMATCH   = "size mismatch between some selected objects"
I_SIZE_MISMATCH_8 = "* list of 8-inch objects selected: {}"

# institution
I_INSTITUTION = "some selected objects are not at this institution: {}"

class Filewindow(QWidget):
    def __init__(self):
        super(Filewindow, self).__init__()

    def getfile(self,*args,**kwargs):
        fname, fmt = QFileDialog.getOpenFileName(self, 'Open file', '~',"(*.xml)")
        return fname

    def getdir(self,*args,**kwargs):
        dname = QFileDialog.getExistingDirectory(self, "select directory")
        return dname


class func(object):
	def __init__(self,fm,userManager,page,setUIPage,setSwitchingEnabled):
		self.userManager = userManager
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.modules      = [parts.module()      for _ in range(6)]

		self.step_pcb = assembly.step_pcb()
		self.step_pcb_exists = None

		self.mode = 'setup'

	def enforce_mode(mode):
		if not (type(mode) in [str,list]):
			raise ValueError
		def wrapper(function):
			def wrapped_function(self,*args,**kwargs):
				if type(mode) is str:
					valid_mode = self.mode == mode
				elif type(mode) is list:
					valid_mode = self.mode in mode
				else:
					valid_mode = False
				if valid_mode:
					if DEBUG:
						print("page {} with mode {} req {} calling function {} with args {} kwargs {}".format(
							PAGE_NAME,
							self.mode,
							mode,
							function.__name__,
							args,
							kwargs,
							))
					function(self,*args,**kwargs)
				else:
					print("page {} mode is {}, needed {} for function {} with args {} kwargs {}".format(
						PAGE_NAME,
						self.mode,
						mode,
						function.__name__,
						args,
						kwargs,
						))
			return wrapped_function
		return wrapper

	@enforce_mode('setup')
	def setup(self):
		self.rig()
		self.mode = 'view'
		print("{} setup completed".format(PAGE_NAME))
		self.update_info()
		self.loadStep()

	@enforce_mode('setup')
	def rig(self):
		self.le_modules = [
			self.page.leModule1,
			self.page.leModule2,
			self.page.leModule3,
			self.page.leModule4,
			self.page.leModule5,
			self.page.leModule6,
		]
		self.pb_go_modules = [
			self.page.pbGoModule1,
			self.page.pbGoModule2,
			self.page.pbGoModule3,
			self.page.pbGoModule4,
			self.page.pbGoModule5,
			self.page.pbGoModule6,
		]

		self.dsb_offsets_x = [
			self.page.dsbOffX1,
			self.page.dsbOffX2,
			self.page.dsbOffX3,
			self.page.dsbOffX4,
			self.page.dsbOffX5,
			self.page.dsbOffX6,
		]

		self.dsb_offsets_y = [
			self.page.dsbOffY1,
			self.page.dsbOffY2,
			self.page.dsbOffY3,
			self.page.dsbOffY4,
			self.page.dsbOffY5,
			self.page.dsbOffY6,
		]

		self.dsb_offsets_rot = [
			self.page.dsbOffRot1,
			self.page.dsbOffRot2,
			self.page.dsbOffRot3,
			self.page.dsbOffRot4,
			self.page.dsbOffRot5,
			self.page.dsbOffRot6,
		]

		self.dsb_flatness = [
			self.page.dsbFlatness1,
			self.page.dsbFlatness2,
			self.page.dsbFlatness3,
			self.page.dsbFlatness4,
			self.page.dsbFlatness5,
			self.page.dsbFlatness6,
		]

		self.dsb_thickness = [
			self.page.dsbThickness1,
			self.page.dsbThickness2,
			self.page.dsbThickness3,
			self.page.dsbThickness4,
			self.page.dsbThickness5,
			self.page.dsbThickness6,
		]

		self.cb_grades = [
			self.page.cbGrade1,
			self.page.cbGrade2,
			self.page.cbGrade3,
			self.page.cbGrade4,
			self.page.cbGrade5,
			self.page.cbGrade6,
		]


		for i in range(6):
			self.pb_go_modules[i].clicked.connect(     self.goModule     )

		self.page.sbID.valueChanged.connect(self.loadStep)
		self.page.cbInstitution.activated.connect( self.loadStep )

		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbCureStartNow    .clicked.connect(self.setCureStartNow)
		self.page.pbCureStopNow     .clicked.connect(self.setCureStopNow)

		self.page.pbAddFile.clicked.connect(self.loadXMLFile)
		self.fwnd = Filewindow()


	@enforce_mode(['view','editing'])
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			tmp_id = self.page.sbID.value()
			tmp_inst = self.page.cbInstitution.currentText()
			ID = "{}_{}".format(tmp_inst, tmp_id)
		else:
			tmp_id, tmp_inst = ID.split("_")
			self.page.sbID.setValue(int(tmp_id))
			self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))

		self.step_pcb_exists = False
		if getattr(self.step_pcb, 'ID', None) != None:
			self.step_pcb_exists = (ID == self.step_pcb.ID)

		self.page.listIssues.clear()
		self.page.leStatus.clear()
		localtime = time.localtime()

		if self.step_pcb_exists:

			times_to_set = [(self.step_pcb.cure_begin_timestamp, self.page.dtCureStart),
			                (self.step_pcb.cure_end_timestamp,  self.page.dtCureStop)]
			for st, dt in times_to_set:
				if st is None:
					dt.setDate(QtCore.QDate(localtime.tm_year, 1, 1))
					dt.setTime(QtCore.QTime(0,0,0))
				else:
					tm = datetime.datetime.strptime(st, "%Y-%m-%d %H:%M:%S%z")
					localtime = tm.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
					dat = QtCore.QDate(localtime.year, localtime.month, localtime.day)
					tim = QtCore.QTime(localtime.hour, localtime.minute, localtime.second)
					dt.setDate(dat)
					dt.setTime(tim)


			self.page.dsbCureTemperature.setValue(self.step_pcb.temp_degc if self.step_pcb.temp_degc else 70)
			self.page.sbCureHumidity    .setValue(self.step_pcb.humidity_prcnt    if self.step_pcb.humidity_prcnt    else 10)
			self.page.leXML.setText(self.step_pcb.xml_file_name if self.step_pcb.xml_file_name else "")

			if not (self.step_pcb.modules is None):
				mods = self.step_pcb.modules
				x_off = self.step_pcb.pcb_x_offsts
				y_off = self.step_pcb.pcb_y_offsts
				ang_off = self.step_pcb.pcb_ang_offsts
				thicks = self.step_pcb.thicknesses
				flats = self.step_pcb.flatnesses
				grades = self.step_pcb.grades

				for i in range(6):
					self.le_modules[i]     .setText(mods[i] if mods[i] else "")
					self.dsb_offsets_x[i]  .setValue(x_off[i] if x_off[i] else 0)
					self.dsb_offsets_y[i]  .setValue(y_off[i] if y_off[i] else 0)
					self.dsb_offsets_rot[i].setValue(ang_off[i] if ang_off[i] else 0)
					self.dsb_thickness[i]  .setValue(thicks[i] if thicks[i] else 0)
					self.dsb_flatness[i]   .setValue(flats[i] if flats[i] else 0)
					self.cb_grades[i]      .setCurrentIndex(INDEX_GRADE.get(grades[i], -1))

			else:
				for i  in range(6):
					self.le_modules[i].setText("")
					self.dsb_offsets_x[i].setValue(0)
					self.dsb_offsets_y[i].setValue(0)
					self.dsb_offsets_rot[i].setValue(0)
					self.dsb_thickness[i].setValue(0)
					self.dsb_flatness[i].setValue(0)
					self.cb_grades[i].setCurrentIndex(-1)

		else:
			self.page.cbInstitution.setCurrentIndex(-1)
			self.page.dtCureStart.setDate(QtCore.QDate(localtime.tm_year, 1, 1))
			self.page.dtCureStart.setTime(QtCore.QTime(0,0,0))
			self.page.dtCureStop.setDate(QtCore.QDate(localtime.tm_year, 1, 1))
			self.page.dtCureStop.setTime(QtCore.QTime(0,0,0))

			self.page.dsbCureTemperature.setValue(-1)
			self.page.sbCureHumidity.setValue(-1)
			self.page.leXML.setText("")

			for i in range(6):
				self.le_modules[i].setText("")
				self.dsb_offsets_x[i].setValue(0)
				self.dsb_offsets_y[i].setValue(0)
				self.dsb_offsets_rot[i].setValue(0)
				self.dsb_thickness[i].setValue(-1)
				self.dsb_flatness[i].setValue(0)
				self.cb_grades[i].setCurrentIndex(-1)

		
		self.updateElements()

	@enforce_mode(['view','editing'])
	def updateElements(self,use_info=False):
		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		modules_exist      = [_.text()!="" for _ in self.le_modules     ]
		step_pcb_exists    = self.step_pcb_exists

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbID.setEnabled(mode_view)
		self.page.cbInstitution.setEnabled(mode_view)

		self.page.pbCureStartNow     .setEnabled(mode_editing)
		self.page.pbCureStopNow      .setEnabled(mode_editing)

		self.page.dtCureStart      .setReadOnly(mode_view)
		self.page.dtCureStop       .setReadOnly(mode_view)
		self.page.dsbCureTemperature.setReadOnly(mode_view)
		self.page.sbCureHumidity   .setReadOnly(mode_view)

		self.page.pbAddFile.setEnabled(mode_editing)

		for i in range(6):
			self.pb_go_modules[i].setEnabled(     mode_view and modules_exist[i]     )
			self.dsb_offsets_x[i]  .setReadOnly(not (mode_editing and modules_exist[i]))
			self.dsb_offsets_y[i]  .setReadOnly(not (mode_editing and modules_exist[i]))
			self.dsb_offsets_rot[i].setReadOnly(not (mode_editing and modules_exist[i]))
			self.dsb_thickness[i]  .setReadOnly(not (mode_editing and modules_exist[i]))
			self.dsb_flatness[i]   .setReadOnly(not (mode_editing and modules_exist[i]))
			self.cb_grades[i]      .setEnabled(      mode_editing and modules_exist[i])

		self.page.pbEdit.setEnabled(   mode_view and     step_pcb_exists )
		self.page.pbSave.setEnabled(mode_editing     )
		self.page.pbCancel.setEnabled(mode_editing     )


	@enforce_mode('editing')
	def loadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.modules[i].load(     self.le_modules[i].text()     )
		self.updateIssues()

	@enforce_mode('editing')
	def loadAllTools(self,*args,**kwargs):  # Same as above, but load only tools:
		self.step_pcb.institution = self.page.cbInstitution.currentText()
		self.updateIssues()


	@enforce_mode('editing')
	def unloadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.modules[i].clear()

	#NEW:  Add updateIssues and modify conditions accordingly
	@enforce_mode('editing')
	def updateIssues(self,*args,**kwargs):
		issues = []
		objects = []

		# TBD - maybe expand, check for nonzero measurements?

		self.page.listIssues.clear()
		for issue in issues:
			self.page.listIssues.addItem(issue)

		if issues:
			self.page.leStatus.setText(STATUS_ISSUES)
			self.page.pbSave.setEnabled(False)

		else:
			self.page.leStatus.setText(STATUS_NO_ISSUES)
			self.page.pbSave.setEnabled(True)


	@enforce_mode('view')
	def loadStep(self,*args,**kwargs):
		if self.page.sbID.value() == -1:  return
		if self.page.cbInstitution.currentText() == "":  return
		tmp_step = assembly.step_pcb()
		tmp_ID = self.page.sbID.value()
		tmp_inst = self.page.cbInstitution.currentText()
		tmp_exists = tmp_step.load("{}_{}".format(tmp_inst, tmp_ID))
		if not tmp_exists:
			self.update_info()
		else:
			self.step_pcb = tmp_step
			self.update_info()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_step = assembly.step_pcb()
		tmp_ID = self.page.sbID.value()
		tmp_inst = self.page.cbInstitution.currentText()
		tmp_exists = tmp_step.load("{}_{}".format(tmp_inst, tmp_ID))
		if tmp_exists:
			self.step_pcb = tmp_step
			self.mode = 'editing'
			self.loadAllObjects()
			self.update_info()

	@enforce_mode('editing')
	def cancelEditing(self,*args,**kwargs):
		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()

	@enforce_mode('editing')
	def saveEditing(self,*args,**kwargs):

		pydt = self.page.dtCureStart.dateTime().toPyDateTime().astimezone(datetime.timezone.utc)
		self.step_pcb.cure_begin_timestamp = str(pydt) # sec UTC
		pydt = self.page.dtCureStop.dateTime().toPyDateTime().astimezone(datetime.timezone.utc)
		self.step_pcb.cure_end_timestamp   = str(pydt)

		self.step_pcb.temp_degc = self.page.dsbCureTemperature.value()
		self.step_pcb.humidity_prcnt = self.page.sbCureHumidity.value()

		self.step_pcb.xml_file_name = self.page.leXML.text()

		self.step_pcb.pcb_x_offsts = [self.dsb_offsets_x[i].value() for i in range(6)]
		self.step_pcb.pcb_y_offsts = [self.dsb_offsets_y[i].value() for i in range(6)]
		self.step_pcb.pcb_ang_offsts = [self.dsb_offsets_rot[i].value() for i in range(6)]
		self.step_pcb.flatnesses = [self.dsb_flatness[i].value() for i in range(6)]
		self.step_pcb.thicknesses = [self.dsb_thickness[i].value() for i in range(6)]
		self.step_pcb.grades = [str(self.cb_grades[i].currentText()) if self.cb_grades[i].currentText() else None for i in range(6)]

		self.step_pcb.save()
		# TEMPORARY, have to do this somewhere
		self.step_pcb.generate_xml()

		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()


	def goModule(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		module = self.le_modules[which].text()
		self.setUIPage('Modules',ID=module)

	def setCureStartNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStart.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStart.setTime(QtCore.QTime(*localtime[3:6]))

	def setCureStopNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStop.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStop.setTime(QtCore.QTime(*localtime[3:6]))

	def filesToUpload(self):
		# Return a list of all files to upload to DB
		if self.step_pcb is None:
			return []
		else:
			return self.step_pcb.filesToUpload()


	def loadXMLFile(self, *args, **kwargs):
		filename = self.fwnd.getfile()
		#dirname = self.fwnd.getdir()
		# NOTE:  Only pass data to page fields.  DO NOT save to proto object
		# Only assign data during explicit save() call, so cancellation works normally!
		# (reminder: all data is stored in the PAGE ELEMENTS until save() is called.)
		# (update_info is not called during editing until after save() is called.)

		if filename == '':  return

		# FOR NOW:  Only load data into the first row.
		xml_tree = parse(filename)  # elementtree object
		
		itemdata = xml_tree.find('.//FIDUCIAL1')
		self.dsb_offsets_rot[0].setValue(float(itemdata.text))
		itemdata = xml_tree.find('.//X')
		self.dsb_offsets_x[0].setValue(float(itemdata.text))
		itemdata = xml_tree.find('.//Y')
		self.dsb_offsets_y[0].setValue(float(itemdata.text))
		itemdata = xml_tree.find('.//MEAN')
		self.dsb_thickness[0].setValue(float(itemdata.text))
		itemdata = xml_tree.find('.//GRADE')
		self.cb_grades[0].setCurrentIndex(INDEX_COLOR_GRADE[itemdata.text])

		self.page.leXML.setText(filename)



	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is int):
				raise TypeError("Expected type <int> str ID; got <{}>".format(type(ID)))
			if ID != "":
				raise ValueError("ID cannot be empty")
			tmp_inst, tmp_id = ID.split("_")
			self.page.sbID.setValue(int(tmp_id))
			self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))
			self.loadStep()

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
