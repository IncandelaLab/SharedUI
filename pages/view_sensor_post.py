from PyQt5 import QtCore
import time
import datetime

from filemanager import fm

NO_DATE = [2020,1,1]

PAGE_NAME = "view_sensor_step"
OBJECTTYPE = "sensor_step"
DEBUG = False

INDEX_INSTITUTION = {
	'CERN':0,
	'FNAL':1,
	'UCSB':2,
	'UMN':3,
	'HEPHY':4,
	'HPK':5,
}

INDEX_GRADE = {
	'A':0,
	'B':1,
	'C':2,
}

STATUS_NO_ISSUES = "valid (no issues)"
STATUS_ISSUES    = "invalid (issues present)"

# tooling and supplies
I_BATCH_ARALDITE_DNE     = "araldite batch does not exist or is not selected"
# NOTE: This is now a warning
I_BATCH_ARALDITE_EXPIRED = "araldite batch has expired"

# rows / positions
I_NO_PARTS_SELECTED = "no parts have been selected"
I_ROWS_INCOMPLETE   = "positions {} are partially filled"

# compatibility
I_SIZE_MISMATCH = "size mismatch between some selected objects"
I_SIZE_MISMATCH_8 = "* list of 8-inch objects selected: {}"

# location
I_INSTITUTION = "some selected objects are not at this institution: {}"
I_INSTITUTION_NOT_SELECTED = "no institution selected"

# Missing user
I_USER_DNE = "no sensor step user selected"

# supply batch empty
I_BATCH_ARALDITE_EMPTY = "araldite batch is empty"

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.batch_araldite        = fm.batch_araldite()

		self.step_sensor = fm.step_sensor()
		self.step_sensor_exists = None

		self.mode = 'setup'

		# NEW:
		self.xmlModList = []

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
		self.loadStep()  # sb starts at 0, so load by default

	@enforce_mode('setup')
	def rig(self):
		self.le_protomodules = [
			self.page.leProtomodule1,
			self.page.leProtomodule2,
			self.page.leProtomodule3,
			self.page.leProtomodule4,
			self.page.leProtomodule5,
			self.page.leProtomodule6,
		]
		self.pb_go_protomodules = [
			self.page.pbGoProtoModule1,
			self.page.pbGoProtoModule2,
			self.page.pbGoProtoModule3,
			self.page.pbGoProtoModule4,
			self.page.pbGoProtoModule5,
			self.page.pbGoProtoModule6,
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
			self.pb_go_protomodules[i].clicked.connect(self.goProtomodule)

		self.page.cbInstitution.currentIndexChanged.connect( self.loadAllTools )

		self.page.sbBatchAraldite.editingFinished.connect( self.loadBatchAraldite       )

		self.page.sbID.valueChanged.connect(self.loadStep)

		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoBatchAraldite.clicked.connect(self.goBatchAraldite)
		self.page.pbGoTrayAssembly.clicked.connect(self.goTrayAssembly)
		self.page.pbGoTrayComponent.clicked.connect(self.goTrayComponent)

		self.page.pbCureStartNow    .clicked.connect(self.setCureStartNow)
		self.page.pbCureStopNow     .clicked.connect(self.setCureStopNow)

		auth_users = fm.userManager.getAuthorizedUsers(PAGE_NAME)
		self.index_users = {auth_users[i]:i for i in range(len(auth_users))}
		for user in self.index_users.keys():
			self.page.cbUserPerformed.addItem(user)


	@enforce_mode(['view','editing'])
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbID.value()
		else:
			self.page.sbID.setValue(ID)

		self.step_sensor_exists = False
		if getattr(self.step_sensor, 'ID', None) != None:
			self.step_sensor_exists = (ID == self.step_sensor.ID) #self.step_sensor.load(ID)

		self.page.listIssues.clear()
		self.page.leStatus.clear()

		if self.step_sensor_exists:

			self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.step_sensor.institution, -1))

			# New
			times_to_set = [(self.step_sensor.cure_start, self.page.dtCureStart),
							(self.step_sensor.cure_stop,  self.page.dtCureStop)]
			for st, dt in times_to_set:
				if st is None:
					dt.setDate(QtCore.QDate(*NO_DATE))
					dt.setTime(QtCore.QTime(0,0,0))
				else:
					localtime = list(time.localtime(st))
					dt.setDate(QtCore.QDate(*localtime[0:3]))
					dt.setTime(QtCore.QDate(*localtiem[3:6]))
			"""
			run_start = self.step_sensor.run_start
			run_stop  = self.step_sensor.run_stop
			if run_start is None:
				self.page.dtRunStart.setDate(QtCore.QDate(*NO_DATE))
				self.page.dtRunStart.setTime(QtCore.QTime(0,0,0))
			else:
				localtime = list(time.localtime(run_start))
				self.page.dtRunStart.setDate(QtCore.QDate(*localtime[0:3]))
				self.page.dtRunStart.setTime(QtCore.QTime(*localtime[3:6]))
			if run_stop is None:
				self.page.dtRunStop.setDate(QtCore.QDate(*NO_DATE))
				self.page.dtRunStop.setTime(QtCore.QTime(0,0,0))
			else:
				localtime = list(time.localtime(run_stop))
				self.page.dtRunStop.setDate(QtCore.QDate(*localtime[0:3]))
				self.page.dtRunStop.setTime(QtCore.QTime(*localtime[3:6]))
			"""

			self.page.dsbCureTemperature.setValue(self.step_sensor.cure_temperature if self.step_sensor.cure_temperature else 70)
			self.page.sbCureHumidity    .setValue(self.step_sensor.cure_humidity    if self.step_sensor.cure_humidity    else 10)

			self.page.sbBatchAraldite.setValue(self.step_sensor.batch_araldite if not (self.step_sensor.batch_araldite is None) else -1)

			if not (self.step_sensor.protomodules is None):
				for i in range(6):
					proto = self.step_sensor.protomodules[i]
					self.le_protomodules[i].setText(str(proto) if not (proto is None) else "")
					self.dsb_offsets_x[i]  .setValue(proto.offset_translation_x if not (proto.offset_translation_x is None) else 0)
					self.dsb_offsets_y[i]  .setValue(proto.offset_translation_y if not (proto.offset_translation_y is None) else 0)
					self.dsb_offsets_rot[i].setValue(proto.offfset_rotation     if not (proto.offset_rotation      is None) else 0)
					self.dsb_thickness[i]  .setValue(proto.thickness            if not (proto.thickness            is None) else 0)
					self.dsb_flatness[i]   .setValue(proto.flatness             if not (proto.flatness             is None) else 0)
					self.cb_grades[i]      .setCurrentIndex(INDEX_GRADE.get(proto.grade, -1))

			else:
				for i in range(6):
					self.le_protomodules[i].setText("")
					self.dsb_offsets_x[i].setValue(0)
					self.dsb_offsets_y[i].setValue(0)
					self.dsb_offsets_rot[i].setValue(0)
					self.dsb_thickness[i].setValue(-1)
					self.dsb_flatness[i].setValue(0)
					self.cb_grades[i].setCurrentIndex(-1)

		else:
			self.page.cbInstitution.setCurrentIndex(-1)
			self.page.dtCureStart.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStart.setTime(QtCore.QTime(0,0,0))
			self.page.dtCureStop.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStop.setTime(QtCore.QTime(0,0,0))

			self.page.dsbCureTemperature.setValue(-1)
			self.page.sbCureHumidity.setValue(-1)
			self.page.sbBatchAraldite.setValue(-1)
			for i in range(6):
				self.le_protomodules[i].setText("")
				self.dsb_offsets_x[i].setValue(0)
				self.dsb_offsets_y[i].setValue(0)
				self.dsb_offsets_rot[i].setValue(0)
				self.dsb_thickness[i].setValue(-1)
				self.dsb_flatness[i].setValue(0)
				self.cb_grades[i].setCurrentIndex(-1)

		if self.page.sbBatchAraldite.value() == -1:  self.page.sbBatchAraldite.clear()

		self.updateElements()

	@enforce_mode(['view','editing'])
	def updateElements(self,use_info=False):
		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		protomodules_exist = [_.text()!="" for _ in self.le_protomodules]
		step_sensor_exists = self.step_sensor_exists

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbID.setEnabled(mode_view)

		self.page.cbInstitution.setEnabled(mode_editing)

		self.page.pbCureStartNow     .setEnabled(mode_editing)
		self.page.pbCureStopNow      .setEnabled(mode_editing)

		#self.page.cbUserPerformed  .setEnabled(mode_editing)
		#self.page.leLocation       .setReadOnly(mode_view)
		self.page.dtCureStart      .setReadOnly(mode_view)
		self.page.dtCureStop       .setReadOnly(mode_view)
		self.page.dsbCureTemperature.setReadOnly(mode_view)
		self.page.sbCureHumidity   .setReadOnly(mode_view)
		self.page.sbBatchAraldite  .setReadOnly(mode_view)

		self.page.pbGoBatchAraldite.setEnabled(mode_view and self.page.sbBatchAraldite.value() >= 0)

		for i in range(6):
			self.pb_go_protomodules[i].setEnabled(   mode_view and protomodules_exist[i])
			self.dsb_offsets_x[i]  .setReadOnly(not (mode_view and protomodules_exist[i]))
			self.dsb_offsets_y[i]  .setReadOnly(not (mode_view and protomodules_exist[i]))
			self.dsb_offsets_rot[i].setReadOnly(not (mode_view and protomodules_exist[i]))
			self.dsb_thickness[i]  .setReadOnly(not (mode_view and protomodules_exist[i]))
			self.dsb_flatness[i]   .setReadOnly(not (mode_view and protomodules_exist[i]))
			self.cb_grades[i]         .setEnabled(   mode_view and protomodules_exist[i])

		self.page.pbEdit.setEnabled(   mode_view and     step_sensor_exists )
		self.page.pbSave.setEnabled(   mode_editing        )
		self.page.pbCancel.setEnabled( mode_editing        )


	@enforce_mode('editing')
	def loadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.protomodules[i].load(self.le_protomodules[i].text())

		self.batch_araldite.load(       self.page.sbBatchAraldite.value())
		self.updateIssues()

	@enforce_mode('editing')
	def loadAllTools(self,*args,**kwargs):  # Same as above, but load only tools:
		self.batch_araldite.load(       self.page.sbBatchAraldite.value())
		self.updateIssues()

	@enforce_mode('editing')
	def unloadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.protomodules[i].clear()

		self.batch_araldite.clear()

	@enforce_mode('editing')
	def loadBatchAraldite(self, *args, **kwargs):
		self.batch_araldite.load(self.page.sbBatchAraldite.value())
		self.updateIssues()


	#NEW:  Add updateIssues and modify conditions accordingly
	@enforce_mode('editing')
	def updateIssues(self,*args,**kwargs):
		issues = []
		objects = []

		if self.step_sensor.institution is None:
			issues.append(I_INSTITUTION_NOT_SELECTED)

		if self.batch_araldite.ID is None:
			issues.append(I_BATCH_ARALDITE_DNE)
		else:
			objects.append(self.batch_araldite)
			if not (self.batch_araldite.date_expires is None):
				ydm =  self.batch_araldite.date_expires.split('-')
				expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))   # ymd format for constructor
				#today = datetime.date(*time.localtime()[:3])
				if QtCore.QDate.currentDate() > expires:  #today > expires:
					issues.append(I_BATCH_ARALDITE_EXPIRED)
					#print("**WARNING:** Araldite batch is expired!")
			if self.batch_araldite.is_empty:
				issues.append(I_BATCH_ARALDITE_EMPTY)


		# rows
		rows_empty           = []
		rows_full            = []
		rows_incomplete      = []
		
		for i in range(6):
			num_parts = 0

			if num_parts == 0:
				rows_empty.append(i)
			elif num_parts == 3:
				rows_full.append(i)
			else:
				rows_incomplete.append(i)
		

		if not (len(rows_full) or len(rows_incomplete)):
			issues.append(I_NO_PARTS_SELECTED)

		if rows_incomplete:
			issues.append(I_ROWS_INCOMPLETE.format(', '.join(map(str,rows_incomplete))))


		objects_8in = []
		objects_not_here = []

		for obj in objects:

			size = getattr(obj, "size", None)
			if size in [8.0, 8, '8']:
				objects_8in.append(obj)

			institution = getattr(obj, "institution", None)
			if not (institution in [None, self.page.cbInstitution.currentText()]):
				objects_not_here.append(obj)

		if len(objects_8in):
			issues.append(I_SIZE_MISMATCH)
			issues.append(I_SIZE_MISMATCH_8.format(', '.join([str(_) for _ in objects_8in])))

		if objects_not_here:
			issues.append(I_INSTITUTION.format([str(_) for _ in objects_not_here]))


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
		tmp_step = fm.step_sensor()
		tmp_ID = self.page.sbID.value()
		tmp_exists = tmp_step.load(tmp_ID)
		if not tmp_exists:
			self.update_info()
		else:
			self.step_sensor = tmp_step
			self.update_info()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_step = fm.step_sensor()
		tmp_ID = self.page.sbID.value()
		tmp_exists = tmp_step.load(tmp_ID)
		if tmp_exists:
			self.step_sensor = tmp_step
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

		self.step_sensor.cure_start = self.page.dtCureStart.dateTime().toTime_t()
		self.step_sensor.cure_stop  = self.page.dtCureStop.dateTime().toTime_t()

		self.step_sensor.cure_humidity = self.page.sbCureHumidity.value()
		self.step_sensor.cure_temperature = self.page.dsbCureTemperature.value()

		self.step_sensor.batch_araldite = self.page.sbBatchAraldite.value() if self.page.sbBatchAraldite.value() >= 0 else None

		for i in range(6):
			if self.step_sensor.protomodules[i] is None:  continue

			proto = fm.protomodule()
			if not proto.load(self.step_sensor.protomodules[i]):
				print("FATAL ERROR:  post assembly step tried to load nonexistent protomod {}".format(self.step_sensor.protomodules[i]))
				assert(False)

			# Set protomodule vars/quantities here
			proto.offset_translation_x = self.dsb_offsets_x[i].value()
			proto.offset_translation_y = self.dsb_offsets_y[i].value()
			proto.offset_rotation      = self.dsb_offsets_rot[i].value()
			proto.flatness             = self.dsb_flatness[i].value()
			proto.thickness            = self.dsb_thickness[i].value()
			proto.grade = str(self.cb_grades[i].currentText()) if self.cb_grades[i].currentText() else None

			proto.save()


		print("\n\n\nSAVING STEP SENSOR\n\n\n")
		self.step_sensor.save()
		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()

		# NEW:  (may not be necessary now)
		self.xmlModList.append(self.step_sensor.ID)

	def xmlModified(self):
		return self.xmlModList

	def xmlModifiedReset(self):
		self.xmlModList = []


	def goProtomodule(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		#protomodule = self.sb_protomodules[which].value()
		protomodule = self.le_protomodules[which].text()
		self.setUIPage('protomodules',ID=protomodule)

	def goBatchAraldite(self,*args,**kwargs):
		batch_araldite = self.page.sbBatchAraldite.value()
		self.setUIPage('supplies',batch_araldite=batch_araldite)

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
		if self.step_sensor is None:
			return []
		else:
			return self.step_sensor.filesToUpload()


	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is int):
				raise TypeError("Expected type <int> for ID; got <{}>".format(type(ID)))
			if ID < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbID.setValue(ID)
			self.loadStep()

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
