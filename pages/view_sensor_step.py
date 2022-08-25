from PyQt5 import QtCore
import time
import datetime
import os
import json

from filemanager import fm

NO_DATE = [2022,1,1]

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

STATUS_NO_ISSUES = "valid (no issues)"
STATUS_ISSUES    = "invalid (issues present)"

# tooling and supplies
I_TRAY_COMPONENT_DNE = "sensor component tray does not exist or is not selected"
I_TRAY_ASSEMBLY_DNE  = "assembly tray does not exist or is not selected"
I_BATCH_ARALDITE_DNE     = "araldite batch does not exist or is not selected"
# NOTE: This is now a warning
I_BATCH_ARALDITE_EXPIRED = "araldite batch has expired"

# baseplates
I_PART_NOT_READY  = "{}(s) in position(s) {} is not ready for sensor application. reason: {}"

# baseplate-sensor incompatibility
I_BASEPLATE_SENSOR_SHAPE = "baseplate {} has shape {} but sensor {} has shape {}"

# rows / positions
I_NO_PARTS_SELECTED     = "no parts have been selected"
I_ROWS_INCOMPLETE       = "positions {} are partially filled"
I_TOOL_SENSOR_DNE       = "sensor tool(s) in position(s) {} do not exist"
I_BASEPLATE_DNE         = "baseplate(s) in position(s) {} do not exist"
I_SENSOR_DNE            = "sensor(s) in position(s) {} do not exist"
I_TOOL_SENSOR_DUPLICATE = "same sensor tool is selected on multiple positions: {}"
I_BASEPLATE_DUPLICATE   = "same baseplate is selected on multiple positions: {}"
I_SENSOR_DUPLICATE      = "same sensor is selected on multiple positions: {}"
I_PROTOMODULE_COPY      = "protomodule has already been created: {}"

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

I_NO_TOOL_CHK = "pickup tool feet have not been checked"

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.tools_sensor = [fm.tool_sensor() for _ in range(6)]
		self.baseplates   = [fm.baseplate()   for _ in range(6)]
		self.sensors      = [fm.sensor()      for _ in range(6)]
		self.tray_component_sensor = fm.tray_component_sensor()
		self.tray_assembly         = fm.tray_assembly()
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
		self.loadStep()  # sb starts at 0, so load by default

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
			self.page.leSensor5,
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
		self.le_baseplates = [
			self.page.leBaseplate1,
			self.page.leBaseplate2,
			self.page.leBaseplate3,
			self.page.leBaseplate4,
			self.page.leBaseplate5,
			self.page.leBaseplate6,
		]
		self.pb_go_baseplates = [
			self.page.pbGoBaseplate1,
			self.page.pbGoBaseplate2,
			self.page.pbGoBaseplate3,
			self.page.pbGoBaseplate4,
			self.page.pbGoBaseplate5,
			self.page.pbGoBaseplate6,
		]
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

		# NEW:  To resolve bug where spinbox defaults to 0/prev value when left empty
		self.pb_clears = [
			self.page.pbClear1,
			self.page.pbClear2,
			self.page.pbClear3,
			self.page.pbClear4,
			self.page.pbClear5,
			self.page.pbClear6,
		]
		
		for i in range(6):
			self.pb_go_tools[i].clicked.connect(       self.goTool       )
			self.pb_go_sensors[i].clicked.connect(     self.goSensor     )
			self.pb_go_baseplates[i].clicked.connect(  self.goBaseplate  )
			self.pb_go_protomodules[i].clicked.connect(self.goProtomodule)

			self.sb_tools[i].editingFinished.connect(      self.loadToolSensor)
			self.le_baseplates[i].textChanged.connect( self.loadBaseplate)
			self.le_sensors[i].textChanged.connect( self.loadSensor)

			self.pb_clears[i].clicked.connect(self.clearRow)

		self.page.pbAddPart.clicked.connect(self.finishSearch)
		self.page.pbCancelSearch.clicked.connect(self.cancelSearch)

		self.page.ckCheckFeet.stateChanged.connect(self.updateIssues)
		self.page.cbUserPerformed.activated.connect(self.updateIssues)

		self.page.sbID.valueChanged.connect(self.loadStep)
		self.page.cbInstitution.currentIndexChanged.connect(self.loadStep)  # self.loadAllTools )

		self.page.sbTrayComponent.editingFinished.connect( self.loadTrayComponentSensor )
		self.page.sbTrayAssembly.editingFinished.connect(  self.loadTrayAssembly        )
		self.page.leBatchAraldite.textEdited.connect(self.loadBatchAraldite)

		self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoBatchAraldite.clicked.connect(self.goBatchAraldite)
		self.page.pbGoTrayAssembly.clicked.connect(self.goTrayAssembly)
		self.page.pbGoTrayComponent.clicked.connect(self.goTrayComponent)

		self.page.pbRunStartNow     .clicked.connect(self.setRunStartNow)
		self.page.pbRunStopNow      .clicked.connect(self.setRunStopNow)

		auth_users = fm.userManager.getAuthorizedUsers(PAGE_NAME)
		self.index_users = {auth_users[i]:i for i in range(len(auth_users))}
		for user in self.index_users.keys():
			self.page.cbUserPerformed.addItem(user)


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

		self.step_sensor_exists = False
		if getattr(self.step_sensor, 'ID', None) != None:
			self.step_sensor_exists = (ID == self.step_sensor.ID)

		self.page.listIssues.clear()
		self.page.leStatus.clear()

		if self.step_sensor_exists:

			if not self.step_sensor.user_performed in self.index_users.keys() and not self.step_sensor.user_performed is None:
				# Insertion user was deleted from user page...just add user to the dropdown
				self.index_users[self.step_sensor.user_performed] = max(self.index_users.values()) + 1
				self.page.cbUserPerformed.addItem(self.step_sensor.user_performed)
			self.page.cbUserPerformed.setCurrentIndex(self.index_users.get(self.step_sensor.user_performed, -1))
			self.page.leLocation.setText(self.step_sensor.location)

			# New
			
			times_to_set = [(self.step_sensor.run_start,  self.page.dtRunStart),
							(self.step_sensor.run_stop,   self.page.dtRunStop)]
			for st, dt in times_to_set:
				if st is None:
					dt.setDate(QtCore.QDate(*NO_DATE))
					dt.setTime(QtCore.QTime(0,0,0))
				else:
					localtime = list(time.localtime(st))
					dt.setDate(QtCore.QDate(*localtime[0:3]))
					dt.setTime(QtCore.QTime(*localtime[3:6]))
			


			self.page.leBatchAraldite.setText(self.step_sensor.batch_araldite if not (self.step_sensor.batch_araldite is None) else "")
			self.page.sbTrayAssembly.setValue( self.step_sensor.tray_assembly  if not (self.step_sensor.tray_assembly  is None) else -1)
			self.page.sbTrayComponent.setValue(self.step_sensor.tray_component_sensor if not (self.step_sensor.tray_component_sensor is None) else -1)

			if not (self.step_sensor.tools is None):
				for i in range(6):
					self.sb_tools[i].setValue(self.step_sensor.tools[i] if not (self.step_sensor.tools[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_tools[i].setValue(-1)

			if not (self.step_sensor.sensors is None):
				for i in range(6):
					self.le_sensors[i].setText(str(self.step_sensor.sensors[i]) if not (self.step_sensor.sensors[i] is None) else "")
			else:
				for i in range(6):
					self.le_sensors[i].setText("")

			if not (self.step_sensor.baseplates is None):
				for i in range(6):
					self.le_baseplates[i].setText(str(self.step_sensor.baseplates[i]) if not (self.step_sensor.baseplates[i] is None) else "")
			else:
				for i in range(6):
					self.le_baseplates[i].setText("")

			if not (self.step_sensor.protomodules is None):
				for i in range(6):
					self.le_protomodules[i].setText(str(self.step_sensor.protomodules[i]) if not (self.step_sensor.protomodules[i] is None) else "")
			else:
				for i in range(6):
					self.le_protomodules[i].setText("")

			self.page.ckCheckFeet.setChecked(True)
			self.page.ckCheckFeet.setChecked(self.step_sensor.check_tool_feet if not (self.step_sensor.check_tool_feet is None) else False)

		else:
			self.page.cbUserPerformed.setCurrentIndex(-1)
			self.page.leLocation.setText("")
			self.page.dtRunStart.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtRunStart.setTime(QtCore.QTime(0,0,0))
			self.page.dtRunStop.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtRunStop.setTime(QtCore.QTime(0,0,0))

			self.page.leBatchAraldite.setText("")
			self.page.sbTrayComponent.setValue(-1)
			self.page.sbTrayAssembly.setValue(-1)
			for i in range(6):
				self.sb_tools[i].setValue(-1)
				self.le_sensors[i].setText("")
				self.le_baseplates[i].setText("")
				self.le_protomodules[i].setText("")
			self.page.ckCheckFeet.setChecked(False)

		for i in range(6):
			if self.sb_tools[i].value()        == -1:  self.sb_tools[i].clear()
		

		if self.page.sbTrayComponent.value() == -1:  self.page.sbTrayComponent.clear()
		if self.page.sbTrayAssembly.value()  == -1:  self.page.sbTrayAssembly.clear()

		self.updateElements()

	@enforce_mode(['view','editing','creating','searching'])
	def updateElements(self,use_info=False):
		mode_view      = self.mode == 'view'
		mode_editing   = self.mode == 'editing'
		mode_creating  = self.mode == 'creating'
		mode_searching = self.mode == 'searching'
		tools_exist        = [_.value()>=0 for _ in self.sb_tools       ]
		sensors_exist      = [_.text()!="" for _ in self.le_sensors]
		baseplates_exist   = [_.text()!="" for _ in self.le_baseplates]
		protomodules_exist = [_.text()!="" for _ in self.le_protomodules]
		step_sensor_exists = self.step_sensor_exists

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbID.setEnabled(mode_view)
		self.page.cbInstitution.setEnabled(mode_view) #mode_creating or mode_editing)

		self.page.pbRunStartNow     .setEnabled(mode_creating or mode_editing)
		self.page.pbRunStopNow      .setEnabled(mode_creating or mode_editing)

		self.page.cbUserPerformed  .setEnabled( mode_creating or mode_editing)
		self.page.leLocation       .setReadOnly(mode_view or mode_searching)
		self.page.dtRunStart       .setReadOnly(mode_view or mode_searching)
		self.page.dtRunStop        .setReadOnly(mode_view or mode_searching)
		self.page.sbTrayComponent  .setReadOnly(mode_view or mode_searching)
		self.page.sbTrayAssembly   .setReadOnly(mode_view or mode_searching)
		self.page.leBatchAraldite  .setReadOnly(mode_view or mode_searching)

		self.page.pbGoTrayComponent.setEnabled(mode_view and self.page.sbTrayComponent.value() >= 0)
		self.page.pbGoTrayAssembly .setEnabled(mode_view and self.page.sbTrayAssembly .value() >= 0)
		self.page.pbGoBatchAraldite.setEnabled(mode_view and self.page.leBatchAraldite.text() != "")

		for i in range(6):
			self.sb_tools[i].setReadOnly(         mode_view)
			self.le_sensors[i].setReadOnly(       mode_view)
			self.le_baseplates[i].setReadOnly(    mode_view)
			self.pb_go_tools[i].setEnabled(       mode_view and tools_exist[i]       )
			# ENABLED IF:
			# - creating
			# - view, and part exists
			# DISABLED IF:
			# - editing (shouldn't want to change parts after step done)
			# - searching
			# - view, and part DNE
			self.pb_go_sensors[i].setEnabled(     mode_creating or (mode_view and self.le_sensors[i].text()    != "") )
			self.pb_go_baseplates[i].setEnabled(  mode_creating or (mode_view and self.le_baseplates[i].text() != "") )
			self.pb_go_protomodules[i].setEnabled(mode_view and protomodules_exist[i])
			self.pb_clears[i].setEnabled(         mode_creating or mode_editing)

		self.page.pbNew.setEnabled(    mode_view and not step_sensor_exists )
		self.page.pbEdit.setEnabled(   mode_view and     step_sensor_exists )
		self.page.pbSave.setEnabled(   mode_creating or mode_editing        )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing        )

		self.page.ckCheckFeet.setEnabled(not mode_view)


		self.page.pbAddPart     .setEnabled(mode_searching)
		self.page.pbCancelSearch.setEnabled(mode_searching)
		# NEW:  Update pb's based on search result
		for i in range(6):
			self.pb_go_tools[i]       .setText("" if self.sb_tools[i].value()        < 0  else "go to")
			self.pb_go_protomodules[i].setText("" if self.le_protomodules[i].text() == "" else "go to")
			for btn, ledit in [[self.pb_go_sensors[i],    self.le_sensors[i]],
			                   [self.pb_go_baseplates[i], self.le_baseplates[i]]]:
				btn.setText("select" if ledit.text() == "" else "go to")


	#NEW:  Add all load() functions

	@enforce_mode(['editing','creating'])
	def loadAllObjects(self,*args,**kwargs):
		for i in range(6):
			result = self.tools_sensor[i].load(self.sb_tools[i].value(),   self.page.cbInstitution.currentText())
			self.baseplates[i].load(self.le_baseplates[i].text())
			self.sensors[i].load(   self.le_sensors[i].text())

		self.tray_component_sensor.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.batch_araldite.load(       self.page.leBatchAraldite.text())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadAllTools(self,*args,**kwargs):  # Same as above, but load only tools:
		self.step_sensor.institution = self.page.cbInstitution.currentText()
		for i in range(6):
			self.tools_sensor[i].load(self.sb_tools[i].value(), self.page.cbInstitution.currentText())
		self.tray_component_sensor.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def unloadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tools_sensor[i].clear()
			self.baseplates[i].clear()
			self.sensors[i].clear()

		self.tray_component_sensor.clear()
		self.tray_assembly.clear()
		self.batch_araldite.clear()

	@enforce_mode(['editing','creating'])
	def loadToolSensor(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		result = self.tools_sensor[which].load(self.sb_tools[which].value(), self.page.cbInstitution.currentText())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadBaseplate(self, *args, **kwargs):
		if 'row' in kwargs.keys():
			which = kwargs['row']
		else:
			sender_name = str(self.page.sender().objectName())
			which = int(sender_name[-1]) - 1
		self.baseplates[which].load(self.le_baseplates[which].text(), query_db=False)
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadSensor(self, *args, **kwargs):
		if 'row' in kwargs.keys():
			which = kwargs['row']
		else:
			sender_name = str(self.page.sender().objectName())
			which = int(sender_name[-1]) - 1
		self.sensors[which].load(self.le_sensors[which].text(), query_db=False)
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
		self.batch_araldite.load(self.page.leBatchAraldite.text())
		self.updateIssues()


	#NEW:  Add updateIssues and modify conditions accordingly
	@enforce_mode(['editing', 'creating'])
	def updateIssues(self,*args,**kwargs):
		issues = []
		objects = []

		if self.page.cbUserPerformed.currentText() == "":
			issues.append(I_USER_DNE)

		# tooling and supplies--copied over
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
				ydm =  self.batch_araldite.date_expires.split('-')
				expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))   # ymd format for constructor
				if QtCore.QDate.currentDate() > expires:
					issues.append(I_BATCH_ARALDITE_EXPIRED)
			if self.batch_araldite.is_empty:
				issues.append(I_BATCH_ARALDITE_EMPTY)


		# rows
		sensor_tools_selected = [_.value() for _ in self.sb_tools     ]
		baseplates_selected   = [_.text() for _ in self.le_baseplates  ]
		sensors_selected      = [_.text() for _ in self.le_sensors     ]

		sensor_tool_duplicates = [_ for _ in range(6) if sensor_tools_selected[_] >= 0 and sensor_tools_selected.count(sensor_tools_selected[_])>1]
		baseplate_duplicates   = [_ for _ in range(6) if baseplates_selected[_]   != "" and baseplates_selected.count(  baseplates_selected[_]  )>1]
		sensor_duplicates      = [_ for _ in range(6) if sensors_selected[_]      != "" and sensors_selected.count(     sensors_selected[_]     )>1]

		if sensor_tool_duplicates:
			issues.append(I_TOOL_SENSOR_DUPLICATE.format(', '.join([str(_+1) for _ in sensor_tool_duplicates])))
		if baseplate_duplicates:
			issues.append(I_BASEPLATE_DUPLICATE.format(', '.join([str(_+1) for _ in baseplate_duplicates])))
		if sensor_duplicates:
			issues.append(I_SENSOR_DUPLICATE.format(', '.join([str(_+1) for _ in sensor_duplicates])))

		rows_empty           = []
		rows_full            = []
		rows_incomplete      = []

		rows_baseplate_dne   = []
		rows_tool_sensor_dne = []
		rows_sensor_dne      = []

		for i in range(6):
			num_parts = 0
			tmp_id = "{}_{}".format(self.page.cbInstitution.currentText(), self.page.sbID.value())

			if sensor_tools_selected[i] >= 0:
				num_parts += 1
				objects.append(self.tools_sensor[i])
				if self.tools_sensor[i].ID is None:
					rows_tool_sensor_dne.append(i)

			if baseplates_selected[i] != "":
				num_parts += 1
				objects.append(self.baseplates[i])
				if self.baseplates[i].ID is None:
					rows_baseplate_dne.append(i)
				else:
					ready, reason = self.baseplates[i].ready_step_sensor(tmp_id)
					if not ready:
						issues.append(I_PART_NOT_READY.format('baseplate',i,reason))

			if sensors_selected[i] != "":
				num_parts += 1
				objects.append(self.sensors[i])
				if self.sensors[i].ID is None:
					rows_sensor_dne.append(i)
				else:
					ready, reason = self.sensors[i].ready_step_sensor(tmp_id)
					if not ready:
						issues.append(I_PART_NOT_READY.format('sensor',i,reason))

			if baseplates_selected[i] != "" and sensors_selected[i] != "" \
					and not self.baseplates[i].ID is None and not self.sensors[i].ID is None:
				# Check for compatibility bw two objects:
				if self.baseplates[i].shape != self.sensors[i].shape:
					issues.append(I_BASEPLATE_SENSOR_SHAPE.format(self.baseplates[i].ID,    self.baseplates[i].shape, \
																  self.sensors[i].ID, self.sensors[i].shape))

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


		if rows_baseplate_dne:
			issues.append(I_BASEPLATE_DNE.format(', '.join([str(_+1) for _ in rows_baseplate_dne])))
		if rows_tool_sensor_dne:
			issues.append(I_TOOL_SENSOR_DNE.format(', '.join([str(_+1) for _ in rows_tool_sensor_dne])))
		if rows_sensor_dne:
			issues.append(I_SENSOR_DNE.format(', '.join([str(_+1) for _ in rows_sensor_dne])))


		objects_not_here = []

		for obj in objects:

			institution = getattr(obj, "institution", None)
			if not (institution in [None, self.page.cbInstitution.currentText()]):
				objects_not_here.append(obj)

		if objects_not_here:
			issues.append(I_INSTITUTION.format([str(_) for _ in objects_not_here]))

		if not self.page.ckCheckFeet.isChecked():
			issues.append(I_NO_TOOL_CHK)


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
		tmp_step = fm.step_sensor()
		tmp_ID = self.page.sbID.value()
		tmp_inst = self.page.cbInstitution.currentText()
		tmp_exists = tmp_step.load("{}_{}".format(tmp_inst, tmp_ID))
		if not tmp_exists:
			self.update_info()
		else:
			self.step_sensor = tmp_step
			self.update_info()

	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if self.page.sbID.value() == -1:  return
		if self.page.cbInstitution.currentText() == "":  return
		tmp_step = fm.step_sensor()
		tmp_ID = self.page.sbID.value()
		tmp_inst = self.page.cbInstitution.currentText()
		tmp_exists = tmp_step.load("{}_{}".format(tmp_inst, tmp_ID))
		if not tmp_exists:
			self.step_sensor.new("{}_{}".format(tmp_inst, tmp_ID))
			self.mode = 'creating'
			self.updateElements()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_step = fm.step_sensor()
		tmp_ID = self.page.sbID.value()
		tmp_inst = self.page.cbInstitution.currentText()
		tmp_exists = tmp_step.load("{}_{}".format(tmp_inst, tmp_ID))
		if tmp_exists:
			self.step_sensor = tmp_step
			self.mode = 'editing'
			self.loadAllObjects()
			self.update_info()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.unloadAllObjects()
		if self.mode == 'creating':  self.step_sensor.clear()
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):

		self.step_sensor.institution = self.page.cbInstitution.currentText()

		self.step_sensor.user_performed = str(self.page.cbUserPerformed.currentText()) if self.page.cbUserPerformed.currentText()!='' else None
		self.step_sensor.location = str( self.page.leLocation.text() )

		self.step_sensor.run_start  = self.page.dtRunStart.dateTime().toTime_t()
		self.step_sensor.run_stop   = self.page.dtRunStop.dateTime().toTime_t()

		tools = []
		sensors = []
		baseplates = []
		protomodules = []
		for i in range(6):
			tools.append(       self.sb_tools[i].value()        if self.sb_tools[i].value()        >= 0 else None)
			sensors.append(     self.le_sensors[i].text()      if self.le_sensors[i].text() != "" else None)
			baseplates.append(  self.le_baseplates[i].text()   if self.le_baseplates[i].text() != "" else None)
			if self.le_baseplates[i].text() != "" and self.le_sensors[i].text() != "":
				protomodules.append("PROTO_{}_{}".format(self.le_baseplates[i].text(), self.le_sensors[i].text()))
			else:
				protomodules.append(None)
		self.step_sensor.tools        = tools
		self.step_sensor.sensors      = sensors
		self.step_sensor.baseplates   = baseplates
		self.step_sensor.protomodules = protomodules

		self.step_sensor.tray_component_sensor = self.page.sbTrayComponent.value() if self.page.sbTrayComponent.value() >= 0 else None
		self.step_sensor.tray_assembly         = self.page.sbTrayAssembly.value()  if self.page.sbTrayAssembly.value()  >= 0 else None
		self.step_sensor.batch_araldite        = self.page.leBatchAraldite.text() if self.page.leBatchAraldite.text() else None


		# Add protomodule ID to baseplate, sensor lists; create protomodule if it doesn't exist:
		for i in range(6):
			if baseplates[i] is None:
				# Row is empty; ignore
				continue
			temp_protomodule = fm.protomodule()
			# Moved to active check (ensure no duplicates)
			temp_protomodule.new(protomodules[i])
			# Thickness = sum of baseplate and sensor, plus glue gaps
			temp_plt = fm.baseplate()
			temp_plt.load(baseplates[i])
			temp_sensor = fm.sensor()
			temp_sensor.load(sensors[i])

			temp_protomodule.institution    = self.step_sensor.institution
			temp_protomodule.location       = self.step_sensor.location
			temp_protomodule.insertion_user = self.step_sensor.user_performed
			temp_protomodule.thickness  = temp_plt.thickness + temp_sensor.thickness + 0.1 # 100um=1 glue layer
			if temp_plt.material == 'PCB':
				temp_protomodule.thickness += 0.5
			temp_protomodule.thickness      = temp_plt.thickness + temp_sensor.thickness + 0.1 # 100um=1 glue layer
			temp_protomodule.channels       = 192 if temp_sensor.channel_density == 'LD' else 432
			temp_protomodule.size           = temp_sensor.size
			temp_protomodule.shape          = temp_sensor.shape

			temp_protomodule.step_sensor    = self.step_sensor.ID
			temp_protomodule.baseplate      = temp_plt.ID
			temp_protomodule.sensor         = temp_sensor.ID

			# PROBLEM HERE:  Does not check for existing protomodule w/ same ID/different date before saving!!
			temp_protomodule.save()

			self.baseplates[i].step_sensor = self.step_sensor.ID
			self.baseplates[i].protomodule = temp_protomodule.ID
			self.baseplates[i].save()
			self.sensors[i].step_sensor = self.step_sensor.ID
			self.sensors[i].protomodule = temp_protomodule.ID
			self.sensors[i].save()

		self.step_sensor.check_tool_feet = self.page.ckCheckFeet.isChecked()

		self.step_sensor.save()
		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()

		# NEW:
		self.xmlModList.append(self.step_sensor.ID)

	def xmlModified(self):
		return self.xmlModList

	def xmlModifiedReset(self):
		self.xmlModList = []

	def clearRow(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.sb_tools[which].clear()
		self.le_sensors[which].clear()
		self.le_baseplates[which].clear()
		self.update_issues()

	# NEW
	def doSearch(self,*args,**kwargs):
		SEARCH_DB = False
		tmp_part = getattr(fm, self.search_part)()
		# Perform part search:
		if SEARCH_DB:
			pass  # TO IMPLEMENT LATER

		# Search local-only parts:  open part file
		part_file_name = os.sep.join([ fm.DATADIR, 'partlist', self.search_part+'s.json' ])
		with open(part_file_name, 'r') as opfl:
			part_list = json.load(opfl)

		for part_id, date in part_list.items():
			# If already added by DB query, skip:
			if len(self.page.lwPartList.findItems("{} {}".format(self.search_part, part_id), \
			                                      QtCore.Qt.MatchExactly)) > 0:
				continue
			# Search for one thing:  NOT already assigned to a protomod
			tmp_part.load(part_id, query_db=False)  # db query already done
			if tmp_part.protomodule is None:
				self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))

		self.page.leSearchStatus.setText('{}: row {}'.format(self.search_part, self.search_row))
		self.mode = 'searching'
		self.updateElements()
		print("SEARCH DONE: mode is", self.mode)

	def finishSearch(self,*args,**kwargs):
		row = self.page.lwPartList.currentRow()
		name = self.page.lwPartList.item(row).text().split()[1]
		le_to_fill = getattr(self, 'le_{}s'.format(self.search_part))[self.search_row]
		le_to_fill.setText(name)

		self.page.lwPartList.clear()
		self.page.leSearchStatus.clear()
		self.mode = 'creating'
		getattr(self, 'load'+self.search_part.capitalize())(row=row)  # load part object
		self.updateElements()
		self.updateIssues()

	def cancelSearch(self,*args,**kwargs):
		self.page.lwPartList.clear()
		self.page.leSearchStatus.clear()
		self.mode = 'creating'
		self.updateElements()
		self.updateIssues()


	def goTool(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1 # last character of sender name is integer 1 through 6; subtract one for zero index
		tool = self.sb_tools[which].value()
		self.setUIPage('Tooling',tool_sensor=tool,institution=self.page.cbInstitution.currentText())

	def goSensor(self,*args,**kwargs):
		# NEW:  If sensor DNE, change mode to search
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		sensor = self.le_sensors[which].text()
		if sensor != "":
			self.setUIPage('Sensors',ID=sensor)
		else:
			self.mode = 'searching'
			self.search_part = 'sensor'
			self.search_row = which
			self.doSearch()

	def goBaseplate(self,*args,**kwargs):
		# NEW:  If baseplate DNE, change mode to search
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		baseplate = self.le_baseplates[which].text()
		if baseplate != "":
			self.setUIPage('Baseplates',ID=baseplate)
		else:
			self.mode = 'searching'
			self.search_part = 'baseplate'
			self.search_row = which
			self.doSearch()

	def goProtomodule(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		protomodule = self.le_protomodules[which].text()
		self.setUIPage('Protomodules',ID=protomodule)

	def goBatchAraldite(self,*args,**kwargs):
		#batch_araldite = self.page.sbBatchAraldite.value()
		batch_araldite = self.page.leBatchAraldite.text()
		self.setUIPage('Supplies',batch_araldite=batch_araldite)

	def goTrayComponent(self,*args,**kwargs):
		tray_component_sensor = self.page.sbTrayComponent.value()
		self.setUIPage('Tooling',tray_component_sensor=tray_component_sensor)

	def goTrayAssembly(self,*args,**kwargs):
		tray_assembly = self.page.sbTrayAssembly.value()
		self.setUIPage('Tooling',tray_assembly=tray_assembly)

	def setRunStartNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtRunStart.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtRunStart.setTime(QtCore.QTime(*localtime[3:6]))

	def setRunStopNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtRunStop.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtRunStop.setTime(QtCore.QTime(*localtime[3:6]))


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
			if not (type(ID) is str):
				raise TypeError("Expected type <str> for ID; got <{}>".format(type(ID)))
			if ID == "":
				raise ValueError("ID cannot be empty")
			tmp_inst, tmp_id = ID.split("_")
			self.page.sbID.setValue(int(tmp_id))
			self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))
			self.loadStep()

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
