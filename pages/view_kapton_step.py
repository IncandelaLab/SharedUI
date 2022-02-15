from PyQt5 import QtCore
import time
import datetime

NO_DATE = [2000,1,1]

PAGE_NAME = "view_kapton_step"
OBJECTTYPE = "kapton_step"
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
I_TRAY_COMPONENT_DNE = "sensor component tray does not exist or is not selected"
I_TRAY_ASSEMBLY_DNE  = "assembly tray does not exist or is not selected"
I_BATCH_ARALDITE_DNE     = "araldite batch does not exist or is not selected"
I_BATCH_ARALDITE_EXPIRED = "araldite batch has expired"

# sensors
I_SENSOR_NOT_READY  = "sensor(s) in position(s) {} is not ready for kapton application. reason: {}"

# kapton inspection
I_KAPTON_INSPECTION_NOT_DONE = "kapton inspection not done for position(s) {}"
I_KAPTON_INSPECTION_ON_EMPTY = "kapton inspection checked for empty position(s) {}"

# rows / positions
I_NO_PARTS_SELECTED = "no parts have been selected"
I_ROWS_INCOMPLETE   = "positions {} are partially filled"
I_TOOL_SENSOR_DNE      = "sensor tool(s) in position(s) {} do not exist"
I_SENSOR_DNE        = "sensor(s) in position(s) {} do not exist"
I_TOOL_SENSOR_DUPLICATE = "same sensor tool is selected on multiple positions: {}"
I_SENSOR_DUPLICATE   = "same sensor is selected on multiple positions: {}"

# compatibility
I_SIZE_MISMATCH = "size mismatch between some selected objects"
I_SIZE_MISMATCH_6 = "* list of 6-inch objects selected: {}"
I_SIZE_MISMATCH_8 = "* list of 8-inch objects selected: {}"

# location
I_INSTITUTION = "some selected objects are not at this institution: {}"
I_INSTITUTION_NOT_SELECTED = "no institution selected"

# Missing user
I_USER_DNE = "no kapton step user selected"

# batch empty
I_BATCH_ARALDITE_EMPTY = "araldite batch is empty"


class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.tools_sensor = [fm.tool_sensor() for _ in range(6)]
		self.sensors   = [fm.sensor()   for _ in range(6)]
		self.tray_component_sensor = fm.tray_component_sensor()
		self.tray_assembly         = fm.tray_assembly()
		self.batch_araldite        = fm.batch_araldite()

		self.step_kapton = fm.step_kapton()
		self.step_kapton_exists = None

		#self.MAC = fm.MAC

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

	@enforce_mode('setup')
	def rig(self):
		self.sb_tools = [
			self.page.sbTool1,
			self.page.sbTool2,
			self.page.sbTool3,
			self.page.sbTool4,
			self.page.sbTool5,
			self.page.sbTool6,
		]
		self.pb_go_tools = [
			self.page.pbGoTool1,
			self.page.pbGoTool2,
			self.page.pbGoTool3,
			self.page.pbGoTool4,
			self.page.pbGoTool5,
			self.page.pbGoTool6,
		]
		self.le_sensors = [
			self.page.leSensor1,
			self.page.leSensor2,
			self.page.leSensor3,
			self.page.leSensor4,
			self.page.leSensori5,
			self.page.leSensor6,
		]
		self.pb_go_sensors = [
			self.page.pbGoSensor1,
			self.page.pbGoSensor2,
			self.page.pbGoSensor3,
			self.page.pbGoSensor4,
			self.page.pbGoSensor5,
			self.page.pbGoSensor6,
		]
		self.ck_kaptons_inspected = [
			self.page.ckKaptonInspected1,
			self.page.ckKaptonInspected2,
			self.page.ckKaptonInspected3,
			self.page.ckKaptonInspected4,
			self.page.ckKaptonInspected5,
			self.page.ckKaptonInspected6,
			]

		for i in range(6):
			self.pb_go_tools[i].clicked.connect(self.goTool)
			self.pb_go_sensors[i].clicked.connect(self.goSensor)

			self.sb_tools[i].editingFinished.connect(             self.loadToolSensor )
			self.le_sensors[i].textChanged.connect( self.loadSensor )  # Could also use editingFinshed
			self.ck_kaptons_inspected[i].clicked.connect( self.updateIssues   )

		self.page.cbInstitution.currentIndexChanged.connect( self.loadAllTools )

		self.page.sbTrayComponent.editingFinished.connect( self.loadTrayComponentSensor )
		self.page.sbTrayAssembly.editingFinished.connect(  self.loadTrayAssembly        )
		self.page.sbBatchAraldite.editingFinished.connect( self.loadBatchAraldite       )

		self.page.sbID.valueChanged.connect(self.update_info)

		self.page.pbNew.clicked.connect(    self.startCreating )
		self.page.pbEdit.clicked.connect(   self.startEditing  )
		self.page.pbSave.clicked.connect(   self.saveEditing   )
		self.page.pbCancel.clicked.connect( self.cancelEditing )

		self.page.pbGoBatchAraldite.clicked.connect( self.goBatchAraldite )
		self.page.pbGoTrayAssembly.clicked.connect(  self.goTrayAssembly  )
		self.page.pbGoTrayComponent.clicked.connect( self.goTrayComponent )

		self.page.pbRunStartNow.clicked.connect(      self.setRunStartNow      )

		auth_users = fm.userManager.getAuthorizedUsers(PAGE_NAME)
		self.index_users = {auth_users[i]:i for i in range(len(auth_users))}
		for user in self.index_users.keys():
			self.page.cbInsertUser.addItem(user)


	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbID.value()
		else:
			self.page.sbID.setValue(ID)

		self.step_kapton_exists = self.step_kapton.load(ID)

		self.page.listIssues.clear()
		self.page.leStatus.clear()

		if self.step_kapton_exists:
			self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.step_kapton.institution, -1))

			#self.page.leUserPerformed.setText(self.step_kapton.user_performed)
			if not self.step_kapton.user_performed in self.index_users.keys() and not self.step_kapton.user_performed is None:
				# Insertion user was deleted from user page...just add user to the dropdown
				self.index_users[self.step_kapton.user_performed] = max(self.index_users.values()) + 1
				self.page.cbUserPerformed.addItem(self.step_kapton.user_performed)
			self.page.cbUserPerformed.setCurrentIndex(self.index_users.get(self.step_kapton.user_performed, -1))
			self.page.leLocation.setText(self.step_kapton.location)

			run_start = self.step_kapton.run_start
			if run_start is None:
				self.page.dtRunStart.setDate(QtCore.QDate(*NO_DATE))
				self.page.dtRunStart.setTime(QtCore.QTime(0,0,0))
			else:
				localtime = list(time.localtime(run_start))
				self.page.dtRunStart.setDate(QtCore.QDate(*localtime[0:3]))
				self.page.dtRunStart.setTime(QtCore.QTime(*localtime[3:6]))

			self.page.leCureTemperature.setText(self.step_kapton.cure_temperature)
			self.page.leCureHumidity.setText(self.step_kapton.cure_humidity)

			self.page.sbBatchAraldite.setValue(self.step_kapton.batch_araldite if not (self.step_kapton.batch_araldite is None) else -1)
			self.page.sbTrayAssembly.setValue( self.step_kapton.tray_assembly  if not (self.step_kapton.tray_assembly  is None) else -1)
			self.page.sbTrayComponent.setValue(self.step_kapton.tray_component_sensor if not (self.step_kapton.tray_component_sensor is None) else -1)

			if not (self.step_kapton.tools is None):
				for i in range(6):
					self.sb_tools[i].setValue(self.step_kapton.tools[i] if not (self.step_kapton.tools[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_tools[i].setValue(-1)

			if not (self.step_kapton.sensors is None):
				for i in range(6):
					self.le_sensors[i].setText(self.step_kapton.sensors[i] if not (self.step_kapton.sensors[i] is None) else "")
			else:
				for i in range(6):
					self.le_sensors[i].setText("")

			if not (self.step_kapton.kaptons_inspected is None):
				for i in range(6):
					self.ck_kaptons_inspected[i].setChecked(False if self.step_kapton.kaptons_inspected[i] is None else self.step_kapton.kaptons_inspected[i])
			else:
				for i in range(6):
					self.ck_kaptons_inspected[i].setChecked(False)

		else:
			self.page.cbInstitution.setCurrentIndex(-1)
			self.page.leUserPerformed.setText("")
			self.page.leLocation.setText("")
			#self.page.dPerformed.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtRunStart.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtRunStart.setTime(QtCore.QTime(0,0,0))
			self.page.leCureTemperature.setText("")
			self.page.leCureHumidity.setText("")
			self.page.sbBatchAraldite.setValue(-1)
			self.page.sbTrayComponent.setValue(-1)
			self.page.sbTrayAssembly.setValue(-1)
			for i in range(6):
				self.sb_tools[i].setValue(-1)
				self.le_sensors[i].setText("")
				self.ck_kaptons_inspected[i].setChecked(False)

		for i in range(6):
			if self.sb_tools[i].value() == -1:  self.sb_tools[i].clear()

		if self.page.sbBatchAraldite.value() == -1:  self.page.sbBatchAraldite.clear()
		if self.page.sbTrayComponent.value() == -1:  self.page.sbTrayComponent.clear()
		if self.page.sbTrayAssembly.value() == -1:   self.page.sbTrayAssembly.clear()

		self.updateElements()

	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'
		tools_exist      = [_.value()>=0 for _ in self.sb_tools     ]
		sensors_exist = [_.text()!="" for _ in self.le_sensors]
		step_kapton_exists = self.step_kapton_exists

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbID.setEnabled(mode_view)

		self.page.cbInstitution.setEnabled(mode_creating or mode_editing)

		self.page.pbRunStartNow     .setEnabled(mode_creating or mode_editing)

		#self.page.leUserPerformed  .setReadOnly(mode_view)
		self.page.cbUserPerformed  .setEnabled( mode_creating or mode_editing)
		self.page.leLocation       .setReadOnly(mode_view)
		self.page.dtRunStart       .setReadOnly(mode_view)
		self.page.leCureTemperature.setReadOnly(mode_view)
		self.page.leCureHumidity   .setReadOnly(mode_view)
		self.page.sbTrayComponent  .setReadOnly(mode_view)
		self.page.sbTrayAssembly   .setReadOnly(mode_view)
		self.page.sbBatchAraldite  .setReadOnly(mode_view)

		self.page.pbGoTrayComponent.setEnabled(mode_view and self.page.sbTrayComponent.value() >= 0)
		self.page.pbGoTrayAssembly .setEnabled(mode_view and self.page.sbTrayAssembly .value() >= 0)
		self.page.pbGoBatchAraldite.setEnabled(mode_view and self.page.sbBatchAraldite.value() >= 0)

		for i in range(6):
			self.sb_tools[i].setReadOnly(mode_view)
			self.le_sensors[i].setReadOnly(mode_view)
			self.pb_go_tools[i].setEnabled(     mode_view and tools_exist[i]     )
			self.pb_go_sensors[i].setEnabled(mode_view and sensors_exist[i])
			self.ck_kaptons_inspected[i].setEnabled(mode_creating or mode_editing)

		self.page.pbNew.setEnabled(    mode_view and not step_kapton_exists )
		self.page.pbEdit.setEnabled(   mode_view and     step_kapton_exists )
		self.page.pbSave.setEnabled(   mode_creating or mode_editing        )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing        )


	@enforce_mode(['editing','creating'])
	def loadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tools_sensor[i].load(  self.sb_tools[i].value(),          self.page.cbInstitution.currentText())
			self.sensors[i].load(    self.le_sensors[i].text())
		self.tray_component_sensor.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.batch_araldite.load(       self.page.sbBatchAraldite.value())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadAllTools(self,*args,**kwargs):  # Same as above, but load only tools:
		self.step_kapton.institution = self.page.cbInstitution.currentText()
		for i in range(6):
			self.tools_sensor[i].load(  self.sb_tools[i].value(),          self.page.cbInstitution.currentText())
		self.tray_component_sensor.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def unloadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tools_sensor[i].clear()
			self.sensors[i].clear()
		self.tray_component_sensor.clear()
		self.tray_assembly.clear()
		self.batch_araldite.clear()
		
	@enforce_mode(['editing','creating'])
	def loadToolSensor(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.tools_sensor[which].load(self.sb_tools[which].value(), self.page.cbInstitution.currentText())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadSensor(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.sensors[which].load(self.le_sensors[which].text())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadTrayComponentSensor(self, *args, **kwargs):
		self.tray_component_sensor.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadTrayAssembly(self, *args, **kwargs):
		self.tray_assembly.load(self.page.sbTrayAssembly.value(), self.page.cbInstitution.currentText())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadBatchAraldite(self, *args, **kwargs):
		self.batch_araldite.load(self.page.sbBatchAraldite.value())
		self.updateIssues()


	@enforce_mode(['editing','creating'])
	def updateIssues(self,*args,**kwargs):
		issues = []
		objects = []

		if self.step_kapton.institution is None:
			issues.append(I_INSTITUTION_NOT_SELECTED)

		if self.step_kapton.user_performed is None:
			issues.append(I_USER_DNE)

		# tooling and supplies
		
		if self.tray_component_sensor.ID is None:
			issues.append(I_TRAY_COMPONENT_DNE)
		else:
			objects.append(self.tray_component_sensor)

		if self.tray_assembly.ID is None:
			issues.append(I_TRAY_ASSEMBLY_DNE)
		else:
			objects.append(self.tray_assembly)

		if self.batch_araldite.ID is None:
			issues.append(I_BATCH_ARALDITE_DNE)
		else:
			objects.append(self.batch_araldite)
			if not (self.batch_araldite.date_expires is None):
				expires = datetime.date(*self.batch_araldite.date_expires)
				today = datetime.date(*time.localtime()[:3])
				if today > expires:
					issues.append(I_BATCH_ARALDITE_EXPIRED)
			if self.batch_araldite.is_empty:
				issues.append(I_BATCH_ARALDITE_EMPTY)
		

		# rows
		sensor_tools_selected = [_.value()     for _ in self.sb_tools            ]
		sensors_selected   = [_.text()      for _ in self.le_sensors       ]
		kaptons_inspected     = [_.isChecked() for _ in self.ck_kaptons_inspected]

		sensor_tool_duplicates = [_ for _ in range(6) if sensor_tools_selected[_] >= 0 and sensor_tools_selected.count(sensor_tools_selected[_])>1]
		sensor_duplicates   = [_ for _ in range(6) if sensors_selected[_]   != "" and sensors_selected.count(  sensors_selected[_]  )>1]

		if sensor_tool_duplicates:
			issues.append(I_TOOL_SENSOR_DUPLICATE.format(', '.join([str(_+1) for _ in sensor_tool_duplicates])))
		if sensor_duplicates:
			issues.append(I_SENSOR_DUPLICATE.format(', '.join([str(_+1) for _ in sensor_duplicates])))

		rows_empty = []
		rows_full = []
		rows_incomplete = []
		rows_kapton_inspection_on_empty = []
		rows_kapton_inspection_not_done = []
		rows_sensor_dne = []
		rows_tool_sensor_dne = []

		for i in range(6):
			num_parts = 0

			if sensor_tools_selected[i] >= 0:
				num_parts += 1
				objects.append(self.tools_sensor[i])
				if self.tools_sensor[i].ID is None:
					rows_tool_sensor_dne.append(i)

			if sensors_selected[i] != "":
				num_parts += 1
				objects.append(self.sensors[i])
				if self.sensors[i].ID is None:
					rows_sensor_dne.append(i)
				else:
					#NOTE:  Max flatness is 250 um.  I think.
					max_flatness = 0.250 #mm
					max_kapton_flatness = None
					ready, reason = self.sensors[i].ready_step_kapton(self.page.sbID.value(), \
																		 max_flatness, max_kapton_flatness)
					if not ready:
						issues.append(I_SENSOR_NOT_READY.format(i,reason))

			if num_parts == 0:
				rows_empty.append(i)
				if kaptons_inspected[i]:
					rows_kapton_inspection_on_empty.append(i)

			elif num_parts == 2:
				rows_full.append(i)
				if not kaptons_inspected[i]:
					rows_kapton_inspection_not_done.append(i)
			else:
				rows_incomplete.append(i)

		if not (len(rows_full) or len(rows_incomplete)):
			issues.append(I_NO_PARTS_SELECTED)

		if rows_incomplete:
			issues.append(I_ROWS_INCOMPLETE.format(', '.join(map(str,rows_incomplete))))

		if rows_kapton_inspection_on_empty:
			issues.append(I_KAPTON_INSPECTION_ON_EMPTY.format(', '.join([str(_+1) for _ in rows_kapton_inspection_on_empty])))
		if rows_kapton_inspection_not_done:
			issues.append(I_KAPTON_INSPECTION_NOT_DONE.format(', '.join([str(_+1) for _ in rows_kapton_inspection_not_done])))

		if rows_sensor_dne:
			issues.append(I_SENSOR_DNE.format(', '.join([str(_+1) for _ in rows_sensor_dne])))
		if rows_tool_sensor_dne:
			issues.append(I_TOOL_SENSOR_DNE.format(', '.join([str(_+1) for _ in rows_tool_sensor_dne])))


		objects_8in = []
		objects_8in = []
		objects_not_here = []

		for obj in objects:

			size = getattr(obj, "size", None)
			if size in [6.0, 6, '6']:
				objects_8in.append(obj)
			if size in [8.0, 8, '8']:
				objects_8in.append(obj)

			institution = getattr(obj, "institution", None)
			if not (institution in [None, self.page.cbInstitution.currentText()]): #self.MAC]):
				objects_not_here.append(obj)

		if len(objects_8in) and len(objects_8in):
			issues.append(I_SIZE_MISMATCH)
			issues.append(I_SIZE_MISMATCH_6.format(', '.join([str(_) for _ in objects_8in])))
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
	def startCreating(self,*args,**kwargs):
		if not self.step_kapton_exists:
			ID = self.page.sbID.value()
			self.mode = 'creating'
			self.step_kapton.new(ID)
			self.updateElements()
			self.loadAllObjects()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if self.step_kapton_exists:
			self.mode = 'editing'
			self.updateElements()
			self.loadAllObjects()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		print("CANCELLING")
		self.unloadAllObjects()
		print("UPDATED OBJECTS, changing mode to view")
		self.mode = 'view'
		print("Updating info")
		self.update_info()
		print("Updated info")

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):
		self.step_kapton.institution = self.page.cbInstitution.currentText()

		#self.step_kapton.user_performed = str( self.page.leUserPerformed.text() )
		self.step_kapton.user_performed = str(self.page.cbUserPerformed.currentText()) if str(self.page.cbUserPerformed.currentText()) else None
		self.step_kapton.location       = str( self.page.leLocation.text() )

		#if self.page.dtRunStart.date().year() == NO_DATE[0]:
		#	self.step_kapton.run_start = None
		#else:
		self.step_kapton.run_start = self.page.dtRunStart.dateTime().toTime_t()

		self.step_kapton.cure_humidity    = str(self.page.leCureHumidity.text())
		self.step_kapton.cure_temperature = str(self.page.leCureTemperature.text())

		tools = []
		sensors = []
		kaptons_inspected = []
		for i in range(6):
			tools.append(self.sb_tools[i].value() if self.sb_tools[i].value() >= 0 else None)
			sensors.append(self.le_sensors[i].text() if self.le_sensors[i].text != "" else None)
			kaptons_inspected.append(self.ck_kaptons_inspected[i].isChecked() if self.le_sensors[i].text() != "" else None)
		self.step_kapton.tools = tools
		self.step_kapton.sensors = sensors
		self.step_kapton.kaptons_inspected = kaptons_inspected

		self.step_kapton.tray_component_sensor = self.page.sbTrayComponent.value() if self.page.sbTrayComponent.value() >= 0 else None
		self.step_kapton.tray_assembly         = self.page.sbTrayAssembly.value()  if self.page.sbTrayAssembly.value()  >= 0 else None
		self.step_kapton.batch_araldite        = self.page.sbBatchAraldite.value() if self.page.sbBatchAraldite.value() >= 0 else None

		# Update sensors to point to this step:
		for i in range(6):
			if not self.sensors[i].ID is None:
				self.sensors[i].step_kapton = self.step_kapton.ID
				self.sensors[i].save()


		print("Saving kapton step")
		self.step_kapton.save()
		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()

	def goTool(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1 # last character of sender name is integer 1 through 6; subtract one for zero index
		tool = self.sb_tools[which].value()
		self.setUIPage('tooling',tool_sensor=tool)

	def goSensor(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		sensor = self.le_sensors[which].text()
		self.setUIPage('sensors',ID=sensor)

	def goBatchAraldite(self,*args,**kwargs):
		batch_araldite = self.page.sbBatchAraldite.value()
		self.setUIPage('supplies',batch_araldite=batch_araldite)

	def goTrayComponent(self,*args,**kwargs):
		tray_component_sensor = self.page.sbTrayComponent.value()
		self.setUIPage('tooling',tray_component_sensor=tray_component_sensor)

	def goTrayAssembly(self,*args,**kwargs):
		tray_assembly = self.page.sbTrayAssembly.value()
		self.setUIPage('tooling',tray_assembly=tray_assembly)

	def setRunStartNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtRunStart.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtRunStart.setTime(QtCore.QTime(*localtime[3:6]))

	def filesToUpload(self):
		# Return a list of all files to upload to DB
		if self.step_kapton is None:
			return []
		else:
			return self.step_kapton.filesToUpload()


	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is int):
				raise TypeError("Expected type <int> for ID; got <{}>".format(type(ID)))
			if ID < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()


