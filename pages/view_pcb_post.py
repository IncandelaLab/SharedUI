from PyQt5 import QtCore
import time
import datetime

from filemanager import fm

NO_DATE = [2020,1,1]

PAGE_NAME = "view_pcb_step"
OBJECTTYPE = "PCB_step"
DEBUG = False

INDEX_INSTITUTION = {
    'CERN':0,
    'FNAL':1,
    'UCSB':2,
    'UMN':3,
	'HEPHY':4,
	'HPK':5,
}

STATUS_NO_ISSUES = "valid (no issues)"
STATUS_ISSUES    = "invalid (issues present)"

# tooling and supplies
I_BATCH_ARALDITE_DNE     = "araldite batch does not exist or is not selected"
I_BATCH_ARALDITE_EXPIRED = "araldite batch has expired"

# rows / positions
I_NO_PARTS_SELECTED     = "no parts have been selected"
I_ROWS_INCOMPLETE       = "positions {} are partially filled"

# compatibility
I_SIZE_MISMATCH   = "size mismatch between some selected objects"
I_SIZE_MISMATCH_8 = "* list of 8-inch objects selected: {}"

# institution
I_INSTITUTION = "some selected objects are not at this institution: {}"

# Missing user
I_USER_DNE = "no kapton step user selected"

# supply batch empty
I_BATCH_ARALDITE_EMPTY = "araldite batch is empty"

# NEW
I_INSTITUTION_NOT_SELECTED = "no institution selected"


class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		#New stuff
		self.modules      = [fm.module()      for _ in range(6)]
		self.batch_araldite        = fm.batch_araldite()

		self.step_pcb = fm.step_pcb()
		self.step_pcb_exists = False

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

		for i in range(6):
			self.pb_go_modules[i].clicked.connect(     self.goModule     )

			self.le_modules[i].textChanged.connect(     self.loadModule     )

		self.page.cbInstitution.currentIndexChanged.connect( self.loadAllTools )

		self.page.sbBatchAraldite.editingFinished.connect( self.loadBatchAraldite       )

		self.page.sbID.valueChanged.connect(self.loadStep)

		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoBatchAraldite.clicked.connect(self.goBatchAraldite)

		self.page.pbRunStartNow     .clicked.connect(self.setRunStartNow)
		self.page.pbRunStopNow      .clicked.connect(self.setRunStopNow)
		self.page.pbCureStartNow    .clicked.connect(self.setCureStartNow)
		self.page.pbCureStopNow     .clocked.connect(self.setCureStopNow)

		auth_users = fm.userManager.getAuthorizedUsers(PAGE_NAME)
		self.index_users = {auth_users[i]:i for i in range(len(auth_users))}
		for user in self.index_users.keys():
			self.page.cbUserPerformed.addItem(user)


	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbID.value()
		else:
			self.page.sbID.setValue(ID)

		#self.step_pcb_exists = (ID == self.step_pcb.ID)  #self.step_pcb.load(ID)
		self.step_pcb_exists = False
		if getattr(self.step_pcb, 'ID', None) != None:
			self.step_pcb_exists = (ID == self.step_pcb.ID)

		self.page.listIssues.clear()
		self.page.leStatus.clear()

		if self.step_pcb_exists:
			self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.step_pcb.institution, -1))

			if not self.step_pcb.user_performed in self.index_users.keys() and not self.step_pcb.user_performed is None:
				# Insertion user was deleted from user page...just add user to the dropdown
				self.index_users[self.step_pcb.user_performed] = max(self.index_users.values()) + 1
				self.page.cbUserPerformed.addItem(self.step_pcb.user_performed)
			self.page.cbUserPerformed.setCurrentIndex(self.index_users.get(self.step_pcb.user_performed, -1))
			self.page.leLocation.setText(self.step_pcb.location)

			# New
			times_to_set = [(self.step_sensor.run_start,  self.page.dtRunStart),
			                (self.step_sensor.run_stop,   self.page.dtRunStop),
			                (self.step_sensor.cure_start, self.page.dtCureStart),
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
			run_start = self.step_pcb.run_start
			run_stop  = self.step_pcb.run_stop
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
			self.page.dsbCureTemperature.setValue(self.step_pcb.cure_temperature if self.step_pcb.cure_temperature else 70)
			self.page.sbCureHumidity    .setValue(self.step_pcb.cure_humidity    if self.step_pcb.cure_humidity    else 10)

			self.page.sbBatchAraldite.setValue(self.step_pcb.batch_araldite if not (self.step_pcb.batch_araldite is None) else -1)
			self.page.sbTrayAssembly.setValue( self.step_pcb.tray_assembly  if not (self.step_pcb.tray_assembly  is None) else -1)
			self.page.sbTrayComponent.setValue(self.step_pcb.tray_component_pcb if not (self.step_pcb.tray_component_pcb is None) else -1)

			if not (self.step_pcb.modules is None):
				for i in range(6):
					#self.sb_modules[i].setValue(self.step_pcb.modules[i] if not (self.step_pcb.modules[i] is None) else -1)
					self.le_modules[i].setText(str(self.step_pcb.modules[i]) if not (self.step_pcb.modules[i] is None) else "")
			else:
				for i  in range(6):
					#self.sb_modules[i].setValue(-1)
					self.le_modules[i].setText("")

		else:
			self.page.cbInstitution.setCurrentIndex(-1)
			self.page.cbUserPerformed.setCurrentIndex(-1)
			self.page.leLocation.setText("")
			self.page.dtRunStart.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtRunStart.setTime(QtCore.QTime(0,0,0))
			self.page.dtRunStop.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtRunStop.setTime(QtCore.QTime(0,0,0))
			self.page.dtCureStart.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStart.setTime(QtCore.QTime(0,0,0))
			self.page.dtCureStop.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStop.setTime(QtCore.QTime(0,0,0))
			self.page.dsbCureTemperature.setValue(-1)
			self.page.sbCureHumidity.setValue(-1)
			self.page.sbBatchAraldite.setValue(-1)
			for i in range(6):
				self.le_modules[i].setText("")

		if self.page.sbBatchAraldite.value() == -1:  self.page.sbBatchAraldite.clear()
		
		self.updateElements()

	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'
		modules_exist      = [_.text()!="" for _ in self.le_modules     ]
		step_pcb_exists    = self.step_pcb_exists

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbID.setEnabled(mode_view)

		self.page.cbInstitution.setEnabled(mode_creating or mode_editing)

		self.page.pbRunStartNow     .setEnabled(mode_creating or mode_editing)
		self.page.pbRunStopNow      .setEnabled(mode_creating or mode_editing)
		self.page.pbCureStartNow     .setEnabled(mode_creating or mode_editing)
		self.page.pbCureStopNow      .setEnabled(mode_creating or mode_editing)

		self.page.cbUserPerformed  .setEnabled( mode_creating or mode_editing)
		self.page.leLocation       .setReadOnly(mode_view)
		self.page.dtRunStart       .setReadOnly(mode_view)
		self.page.dtRunStop        .setReadOnly(mode_view)
		self.page.dtCureStart      .setReadOnly(mode_view)
		self.page.dtCureStop       .setReadOnly(mode_view)

		self.page.dsbCureTemperature.setReadOnly(mode_view)
		self.page.sbCureHumidity   .setReadOnly(mode_view)
		self.page.sbBatchAraldite  .setReadOnly(mode_view)

		self.page.pbGoBatchAraldite.setEnabled(mode_view and self.page.sbBatchAraldite.value() >= 0)

		for i in range(6):
			self.le_modules[i].setReadOnly(     mode_view)
			self.pb_go_modules[i].setEnabled(     mode_view and modules_exist[i]     )

		self.page.pbEdit.setEnabled(   mode_view and     step_pcb_exists )
		self.page.pbSave.setEnabled(   mode_creating or mode_editing     )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing     )


	#NEW:  Add all load() functions

	@enforce_mode(['editing','creating'])
	def loadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.modules[i].load(     self.le_modules[i].text()     )

		self.batch_araldite.load(       self.page.sbBatchAraldite.value())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadAllTools(self,*args,**kwargs):  # Same as above, but load only tools:
		self.step_pcb.institution = self.page.cbInstitution.currentText()
		self.batch_araldite.load(       self.page.sbBatchAraldite.value())
		self.updateIssues()


	@enforce_mode(['editing','creating'])
	def unloadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.modules[i].clear()

		self.batch_araldite.clear()


	@enforce_mode(['editing','creating'])
	def loadModule(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		#self.modules[which].load(self.sb_modules[which].value())
		self.modules[which].load(self.le_modules[which].text(), query_db=False)
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadBatchAraldite(self, *args, **kwargs):
		self.batch_araldite.load(self.page.sbBatchAraldite.value())
		self.updateIssues()



	#NEW:  Add updateIssues and modify conditions accordingly
	@enforce_mode(['editing', 'creating'])
	def updateIssues(self,*args,**kwargs):
		issues = []
		objects = []

		if self.step_pcb.institution is None:
			issues.append(I_INSTITUTION_NOT_SELECTED)

		#if self.step_pcb.user_performed is None:
		#	issues.append(I_USER_DNE)

		if self.batch_araldite.ID is None:
			issues.append(I_BATCH_ARALDITE_DNE)
		else:
			objects.append(self.batch_araldite)
			if not (self.batch_araldite.date_expires is None):
				ydm = self.batch_araldite.date_expires.split('-')
				expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))  #datetime.date(*self.batch_araldite.date_expires)
				if QtCore.QDate.currentDate() > expires:
					issues.append(I_BATCH_ARALDITE_EXPIRED)
			if self.batch_araldite.is_empty:
				issues.append(I_BATCH_ARALDITE_EMPTY)

		#New
		modules_selected      = [_.text() for _ in self.le_modules      ]

		rows_empty           = []
		rows_full            = []
		rows_incomplete      = []


		for i in range(6):

			# TO DO:  Add code to check for empty rows/fields here

			num_parts = 0
			#if num_parts == 0:
			#	rows_empty.append(i)
			#elif num_parts == 4: #2:
			#	rows_full.append(i)
			#else:
			#	rows_incomplete.append(i)

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
			if not (institution in [None, self.page.cbInstitution.currentText()]):  #self.MAC]):
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
		tmp_step = fm.step_pcb()
		tmp_ID = self.page.sbID.value()
		tmp_exists = tmp_step.load(tmp_ID)
		if not tmp_exists:
			self.update_info()
		else:
			self.step_pcb = tmp_step
			self.update_info()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_step = fm.step_pcb()
		tmp_ID = self.page.sbID.value()
		tmp_exists = tmp_step.load(tmp_ID)
		if tmp_exists:
			self.step_pcb = tmp_step
			self.mode = 'editing'
			self.loadAllObjects()
			self.update_info()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):
		self.step_pcb.institution = self.page.cbInstitution.currentText()

		self.step_pcb.user_performed = str(self.page.cbUserPerformed.currentText()) if str(self.page.cbUserPerformed.currentText()) else None
		self.step_pcb.location = str( self.page.leLocation.text() )

		self.step_pcb.run_start  = self.page.dtRunStart.dateTime().toTime_t()
		self.step_pcb.run_stop   = self.page.dtRunStop.dateTime().toTime_t()
		self.step_pcb.cure_start = self.page.dtCureStart.dateTime().toTime_t()
		self.step_pcb.cure_stop  = self.page.dtCureStop.dateTime().toTime_t()


		self.step_pcb.cure_humidity = self.page.sbCureHumidity.value()
		self.step_pcb.cure_temperature = self.page.dsbCureTemperature.value()

		modules      = []
		for i in range(6):
			modules.append(     self.le_modules[i].text()      if self.le_modules[i].text()      != "" else None)
	
		self.step_pcb.modules      = modules

		self.step_pcb.batch_araldite        = self.page.sbBatchAraldite.value() if self.page.sbBatchAraldite.value() >= 0 else None


		for i in range(6):
			if modules[i] is None:
				# Row is empty, continue
				continue
			temp_module = fm.module()
			module_exists = temp_module.load(protomodules[i])

			# If module exists, save changes - TODO TODO

			self.modules[i].save()

		self.step_pcb.save()
		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()


	def goModule(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		#module = self.sb_modules[which].value()
		module = self.le_modules[which].text()
		self.setUIPage('modules',ID=module)

	def goBatchAraldite(self,*args,**kwargs):
		batch_araldite = self.page.sbBatchAraldite.value()
		self.setUIPage('supplies',batch_araldite=batch_araldite)

	def setRunStartNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtRunStart.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtRunStart.setTime(QtCore.QTime(*localtime[3:6]))

	def setRunStopNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtRunStop.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtRunStop.setTime(QtCore.QTime(*localtime[3:6]))

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
