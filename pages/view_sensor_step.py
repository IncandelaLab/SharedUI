from PyQt5 import QtCore
import time
import datetime
import os
import json
import re

from filemanager import fm, parts, tools, supplies, assembly

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
	'CMU':6,
	'TTU':7,
	'IHEP':8,
	'TIFR':9,
	'NTU':10,
	'FSU':11
}

# Naming dictionary
NAME_DENSITY = {
	'LD' : 'L',
	'HD' : 'H'
}
NAME_GEOMETRY = {
	'Full'   : 'F',
	'Top'    : 'T',
	'Bottom' : 'B',
	'Left'   : 'L',
	'Right'  : 'R',
	'Five'   : '5',
	# 'Full+Three' : 'F' # not sure if necessary
}
NAME_THICKNESS = {
    '120um' : '1',
    '200um' : '2',
	'300um' : '3'
}
NAME_MATERIAL = {
	'CuW/Kapton' : 'W',
	'PCB/Kapton' : 'P',
	'CF/Kapton'  : 'C'
}
NAME_VERSION = {
	'preseries'  : 'X',
	'production' : 'X'  # TBD, currently set to X
}
NAME_INSTITUTION = {
	'CERN'  : 'CN', # TBD ?
	'FNAL'  : 'FL', # TBD ?
	'UCSB'  : 'SB',
	'UMN'   : 'MN', # TBD ?
	'HEPHY' : 'HY', # TBD ?
	'HPK'   : 'HK', # TBD ?
	'CMU'   : 'CM',
	'TTU'   : 'TT',
	'IHEP'  : 'IH',
	'TIFR'  : 'TI', # TBD ?
	'NTU'   : 'NT',
	'FSU'   : 'FS'  # TBD ?
}

def is_proper_name(name):
	# check if the protomodule name is proper
	density_list = list(NAME_DENSITY.values())
	geometry_list = list(NAME_GEOMETRY.values())
	thickness_list = list(NAME_THICKNESS.values())
	material_list = list(NAME_MATERIAL.values())
	version_list = list(NAME_VERSION.values())
	institution_list = list(NAME_INSTITUTION.values())
	flag = False
	if name[0] == 'P' \
		and name[1] in density_list \
		and name[2] in geometry_list \
		and name[3] in thickness_list \
		and name[4] in material_list \
		and name[5] in version_list \
		and name[7:9] in institution_list:
		flag = True
	return flag

STATUS_NO_ISSUES = "valid (no issues)"
STATUS_ISSUES    = "invalid (issues present)"

# tooling and supplies
I_TRAY_COMPONENT_DNE = "sensor component tray does not exist or is not selected"
I_BATCH_ARALDITE_DNE     = "araldite batch does not exist or is not selected"
I_BATCH_ARALDITE_EXPIRED = "araldite batch has expired"
I_TAPE_50_DNE = "50um tape batch does not exist or is not selected"
I_TAPE_50_EXPIRED = "50um tape batch has expired"
I_TAPE_120_DNE = "120um tape batch does not exist or is not selected"
I_TAPE_120_EXPIRED = "120um tape batch has expired"
I_TAPE_DNE = "at least one tape batch is required"
I_ADHESIVE_NOT_SELECTED = "no adhesive type is selected"

# parts
I_PART_NOT_READY  = "{}(s) in position(s) {} is not ready for sensor application. reason: {}"
I_BASEPLATE_ON_PROTO = "baseplate {} on position {} is already assembled on protomodule {}"
I_SENSOR_ON_PROTO = "sensor {} on position {} is already assembled on protomodule {}"

# baseplate-sensor incompatibility
I_BASEPLATE_SENSOR_SHAPE = "baseplate {} has shape {} but sensor {} has shape {}"
I_BASEPLATE_SENSOR_CHANNEL = "baseplate {} has channel density {} but sensor {} has channel density {}"

# rows / positions
I_NO_PARTS_SELECTED     = "no parts have been selected"
I_ROWS_INCOMPLETE       = "positions {} are partially filled"
I_TRAY_ASSEMBLY_DNE     = "assembly tray(s) in position(s) {} do not exist"
I_TOOL_SENSOR_DNE       = "sensor tool(s) in position(s) {} do not exist"
I_BASEPLATE_DNE         = "baseplate(s) in position(s) {} do not exist"
I_SENSOR_DNE            = "sensor(s) in position(s) {} do not exist"
I_TRAY_ASSEMBLY_DUPLICATE = "same assembly tray is selected on multiple positions: {}"
I_TOOL_SENSOR_DUPLICATE = "same sensor tool is selected on multiple positions: {}"
I_BASEPLATE_DUPLICATE   = "same baseplate is selected on multiple positions: {}"
I_SENSOR_DUPLICATE      = "same sensor is selected on multiple positions: {}"
I_SERIAL_DUPLICATE      = "same serial number is used on multiple positions: {}"
I_PROTOMODULE_COPY      = "protomodule has already been created: {}"
I_LONE_TRAY             = "assembly tray entered, but rows {} and {} are empty"

# compatibility
I_SIZE_MISMATCH = "size mismatch between some selected objects"
I_SIZE_MISMATCH_8 = "* list of 8-inch objects selected: {}"

# Missing user
I_USER_DNE = "no sensor step user selected"

# supply batch empty
I_BATCH_ARALDITE_EMPTY = "araldite batch is empty"
I_TAPE_50_EMPTY = "50um tape batch is empty"
I_TAPE_120_EMPTY = "120um tape batch is empty"

I_NO_TOOL_CHK = "pickup tool feet have not been checked"

# protomodule
I_PROTO_NAME_EXISTS = "protomodule name {} on position {} already exists"

class func(object):
	def __init__(self,fm,userManager,page,setUIPage,setSwitchingEnabled):
		self.userManager = userManager
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.tray_assemblys = [tools.tray_assembly() for _ in range(6)]
		self.tools_sensor = [tools.tool_sensor() for _ in range(6)]
		self.baseplates   = [parts.baseplate()   for _ in range(6)]
		self.sensors      = [parts.sensor()      for _ in range(6)]
		self.tray_component_sensor = tools.tray_component_sensor()
		self.batch_araldite        = supplies.batch_araldite()
		self.batch_tape_50         = supplies.batch_tape_50()
		self.batch_tape_120        = supplies.batch_tape_120()

		self.step_sensor = assembly.step_sensor()
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
		
		# Giving this a try...
		self.sb_tray_assemblys = [
			self.page.sbTrayAssembly1,
			self.page.sbTrayAssembly1,
			self.page.sbTrayAssembly2,
			self.page.sbTrayAssembly2,
			self.page.sbTrayAssembly3,
			self.page.sbTrayAssembly3,
		]

		self.pb_go_tray_assemblys = [
			self.page.pbGoTrayAssembly1,
			self.page.pbGoTrayAssembly1,
			self.page.pbGoTrayAssembly2,
			self.page.pbGoTrayAssembly2,
			self.page.pbGoTrayAssembly3,
			self.page.pbGoTrayAssembly3,
		]

		# NEW: protomodule version & serial number
		self.cb_versions = [
			self.page.cbVersion1,
			self.page.cbVersion2,
			self.page.cbVersion3,
			self.page.cbVersion4,
			self.page.cbVersion5,
			self.page.cbVersion6,
		]

		self.sb_serials = [
			self.page.sbSerial1,
			self.page.sbSerial2,
			self.page.sbSerial3,
			self.page.sbSerial4,
			self.page.sbSerial5,
			self.page.sbSerial6,
		]
		self.pb_set_next_serial = [
			self.page.pbSetNextSerial1,
			self.page.pbSetNextSerial2,
			self.page.pbSetNextSerial3,
			self.page.pbSetNextSerial4,
			self.page.pbSetNextSerial5,
			self.page.pbSetNextSerial6,
		]

		for i in range(6):
			# was editingFinished
			self.sb_tray_assemblys[i].valueChanged.connect(self.loadTrayAssembly)
			self.pb_go_tray_assemblys[i].clicked.connect(self.goTrayAssembly)

			self.pb_go_tools[i].clicked.connect(       self.goTool       )
			self.pb_go_sensors[i].clicked.connect(     self.goSensor     )
			self.pb_go_baseplates[i].clicked.connect(  self.goBaseplate  )
			self.pb_go_protomodules[i].clicked.connect(self.goProtomodule)
			self.pb_set_next_serial[i].clicked.connect( self.setNextSerial )

			self.sb_tools[i].editingFinished.connect(      self.loadToolSensor)
			self.le_baseplates[i].textChanged.connect( self.loadBaseplate)
			self.le_sensors[i].textChanged.connect( self.loadSensor)

			self.cb_versions[i].activated.connect( self.updateIssues )

			# update protomodule ID
			# self.le_baseplates[i].textChanged.connect( self.update_protoID)
			# self.le_sensors[i].textChanged.connect( self.update_protoID)
			# self.cb_versions[i].activated.connect( self.update_protoID )
			# self.sb_serials[i].valueChanged.connect( self.update_protoID )
			self.le_protomodules[i].textChanged.connect( self.updateIssues )

			self.pb_clears[i].clicked.connect(self.clearRow)

		self.page.pbGenerate.clicked.connect( self.update_protoID )

		self.page.pbAddPart.clicked.connect(self.finishSearch)
		self.page.pbCancelSearch.clicked.connect(self.cancelSearch)

		self.page.ckCheckFeet.stateChanged.connect(self.updateIssues)
		self.page.cbUserPerformed.activated.connect(self.updateIssues)

		self.page.sbID.valueChanged.connect(self.loadStep)
		self.page.cbInstitution.currentIndexChanged.connect(self.loadStep)  # self.loadAllTools )

		# was editingFinished
		self.page.sbTrayComponent.valueChanged.connect( self.loadTrayComponentSensor )
		#self.page.sbTrayAssembly.editingFinished.connect(  self.loadTrayAssembly        )
		self.page.leBatchAraldite.textEdited.connect(self.loadBatchAraldite)
		self.page.leTape50.textEdited.connect( self.loadTape50 )
		self.page.leTape120.textEdited.connect( self.loadTape120 )

		self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.cbAdhesive.currentIndexChanged.connect(self.switchAdhesive)
		self.page.pbGoBatchAraldite.clicked.connect(self.goBatchAraldite)
		self.page.pbGoTape50.clicked.connect(self.goTape50)
		self.page.pbGoTape120.clicked.connect(self.goTape120)
		#self.page.pbGoTrayAssembly.clicked.connect(self.goTrayAssembly)
		self.page.pbGoTrayComponent.clicked.connect(self.goTrayComponent)

		self.page.pbRunStartNow     .clicked.connect(self.setRunStartNow)
		self.page.pbRunStopNow      .clicked.connect(self.setRunStopNow)

		auth_users = self.userManager.getAuthorizedUsers(PAGE_NAME)
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
			tmp_id, tmpartsinst = ID.split("_")
			self.page.sbID.setValue(int(tmp_id))
			self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))

		self.step_sensor_exists = False
		if getattr(self.step_sensor, 'ID', None) != None:
			self.step_sensor_exists = (ID == self.step_sensor.ID)

		self.page.listIssues.clear()
		self.page.leStatus.clear()
		localtime = time.localtime()

		if self.step_sensor_exists:

			if not self.step_sensor.record_insertion_user in self.index_users.keys() and not self.step_sensor.record_insertion_user is None:
				# Insertion user was deleted from user page...just add user to the dropdown
				self.index_users[self.step_sensor.record_insertion_user] = max(self.index_users.values()) + 1
				self.page.cbUserPerformed.addItem(self.step_sensor.record_insertion_user)
			self.page.cbUserPerformed.setCurrentIndex(self.index_users.get(self.step_sensor.record_insertion_user, -1))

			# Set vars:
			times_to_set = [(self.step_sensor.run_begin_timestamp, self.page.dtRunStart),
							(self.step_sensor.run_end_timestamp,   self.page.dtRunStop)]
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

			if self.step_sensor.glue_batch_num is None and self.step_sensor.batch_tape_50 is None:
				self.page.cbAdhesive.setCurrentIndex(-1)
				self.page.leBatchAraldite.setText("")
				self.page.leTape50.setText("")
				self.page.leTape120.setText("")
			elif self.step_sensor.glue_batch_num != None and self.step_sensor.batch_tape_50 is None:
				self.page.cbAdhesive.setCurrentIndex(0)
				self.page.leBatchAraldite.setText(self.step_sensor.glue_batch_num)
				self.page.leTape50.setText("")
				self.page.leTape120.setText("")
			elif self.step_sensor.glue_batch_num is None and self.step_sensor.batch_tape_50 != None:
				self.page.cbAdhesive.setCurrentIndex(1)
				self.page.leBatchAraldite.setText("")
				self.page.leTape50.setText(self.step_sensor.batch_tape_50)
				self.page.leTape120.setText(self.step_sensor.batch_tape_120)
			else:  # Hybrid
				self.page.cbAdhesive.setCurrentIndex(2)
				self.page.leBatchAraldite.setText(self.step_sensor.glue_batch_num)
				self.page.leTape50.setText(self.step_sensor.batch_tape_50)
				self.page.leTape120.setText(self.step_sensor.batch_tape_120)
			#self.page.leBatchAraldite.setText(self.step_sensor.glue_batch_num if not (self.step_sensor.glue_batch_num is None) else "")

			#self.page.sbTrayAssembly.setValue( self.step_sensor.asmbl_tray_num  if not (self.step_sensor.asmbl_tray_num  is None) else -1)
			self.page.sbTrayComponent.setValue(self.step_sensor.comp_tray_num if not (self.step_sensor.comp_tray_num is None) else -1)

			if not (self.step_sensor.asmbl_tray_names is None):
				trays = self.step_sensor.asmbl_tray_nums
				for i in [0, 2, 4]:  # 0/1, 2/3, 4/5
					# note: if first is filled + second is empty, will erroneously set to -1 - avoid
					if trays[i] is None and trays[i+1] is None:
						self.sb_tray_assemblys[i].setValue(-1)
					elif trays[i] is None:
						self.sb_tray_assemblys[i].setValue(trays[i+1])
					else:
						self.sb_tray_assemblys[i].setValue(trays[i])
					#self.sb_tray_assemblys[i].setValue(trays[i] if trays[i] != None else -1)
			else:
				for i in range(6):
					self.sb_tray_assemblys[i].setValue(-1)
			if not (self.step_sensor.snsr_tool_names is None):
				tools = self.step_sensor.snsr_tool_nums
				for i in range(6):
					self.sb_tools[i].setValue(tools[i] if tools[i] != None else -1)
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
					if not (self.step_sensor.protomodules[i] is None) and is_proper_name(self.step_sensor.protomodules[i]):
						protomodule_name = str(self.step_sensor.protomodules[i])
						for j, (_, name) in enumerate(NAME_VERSION.items()):
							if name == protomodule_name[5]:
								self.cb_versions[i].setCurrentIndex(j)
						match = re.search(r'[1-9]', protomodule_name[7:])
						snum = protomodule_name[7:][match.start():]
						# fill the serial number if it is an integer
						if not self.has_non_integer_characters(snum):
							self.sb_serials[i].setValue(int(snum))
						else:
							self.sb_serials[i].setValue(-1)
					else:
						self.cb_versions[i].setCurrentIndex(-1)
						self.sb_serials[i].setValue(-1)
			else:
				for i in range(6):
					self.le_protomodules[i].setText("")
					self.cb_versions[i].setCurrentIndex(-1)
					self.sb_serials[i].setValue(-1)

			self.page.ckCheckFeet.setChecked(self.step_sensor.snsr_tool_feet_chk if not (self.step_sensor.snsr_tool_feet_chk is None) else False)

		else:
			self.page.cbUserPerformed.setCurrentIndex(-1)
			self.page.dtRunStart.setDate(QtCore.QDate(localtime.tm_year, 1, 1))
			self.page.dtRunStart.setTime(QtCore.QTime(0,0,0))
			self.page.dtRunStop.setDate(QtCore.QDate(localtime.tm_year, 1, 1))
			self.page.dtRunStop.setTime(QtCore.QTime(0,0,0))

			self.page.cbAdhesive.setCurrentIndex(-1)
			self.page.leBatchAraldite.setText("")
			self.page.leTape50.setText("")
			self.page.leTape120.setText("")
			self.page.sbTrayComponent.setValue(-1)
			#self.page.sbTrayAssembly.setValue(-1)
			for i in range(6):
				self.sb_tray_assemblys[i].setValue(-1)
				self.sb_tools[i].setValue(-1)
				self.le_sensors[i].setText("")
				self.le_baseplates[i].setText("")
				self.cb_versions[i].setCurrentIndex(-1)
				self.sb_serials[i].setValue(-1)
				self.le_protomodules[i].setText("")
			self.page.ckCheckFeet.setChecked(False)

		for i in range(6):
			if self.sb_tray_assemblys[i].value() == -1:  self.sb_tray_assemblys[i].clear()
			if self.sb_tools[i].value()        == -1:  self.sb_tools[i].clear()
			if self.sb_serials[i].value()        == -1:  self.sb_serials[i].clear()

		if self.page.sbTrayComponent.value() == -1:  self.page.sbTrayComponent.clear()
		#if self.page.sbTrayAssembly.value()  == -1:  self.page.sbTrayAssembly.clear()

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
		adhesive = self.page.cbAdhesive.currentText()

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbID.setEnabled(mode_view)
		self.page.cbInstitution.setEnabled(mode_view) #mode_creating or mode_editing)

		self.page.pbRunStartNow     .setEnabled(mode_creating or mode_editing)
		self.page.pbRunStopNow      .setEnabled(mode_creating or mode_editing)

		self.page.cbUserPerformed  .setEnabled( mode_creating or mode_editing)
		self.page.dtRunStart       .setReadOnly(mode_view or mode_searching)
		self.page.dtRunStop        .setReadOnly(mode_view or mode_searching)
		self.page.sbTrayComponent  .setReadOnly(mode_view or mode_searching)
		#self.page.sbTrayAssembly   .setReadOnly(mode_view or mode_searching)
		self.page.cbAdhesive   .setEnabled(not (mode_view or mode_searching))

		self.page.leBatchAraldite  .setReadOnly(mode_view or mode_searching or (adhesive!="Araldite" and adhesive!="Hybrid"))
		self.page.leTextAraldite.setEnabled(not (mode_view or mode_searching or (adhesive!="Araldite" and adhesive!="Hybrid")))
		self.page.leTape50      .setReadOnly(mode_view or mode_searching or (adhesive!="Tape" and adhesive!="Hybrid"))
		self.page.leTextTape50  .setEnabled(not (mode_view or mode_searching or (adhesive!="Tape" and adhesive!="Hybrid")))
		self.page.leTape120     .setReadOnly(mode_view or mode_searching or (adhesive!="Tape" and adhesive!="Hybrid"))
		self.page.leTextTape120 .setEnabled(not (mode_view or mode_searching or (adhesive!="Tape" and adhesive!="Hybrid")))

		self.page.pbGoTrayComponent.setEnabled(mode_view and self.page.sbTrayComponent.value() >= 0)
		#self.page.pbGoTrayAssembly .setEnabled(mode_view and self.page.sbTrayAssembly .value() >= 0)
		self.page.pbGoBatchAraldite.setEnabled((mode_creating or mode_editing or (mode_view and self.page.leBatchAraldite.text() != "")) and (adhesive == "Araldite" or adhesive == "Hybrid"))
		self.page.pbGoTape50.setEnabled((mode_creating or mode_editing or (mode_view and self.page.leTape50.text() != "")) and (adhesive == "Tape" or adhesive == "Hybrid"))
		self.page.pbGoTape120.setEnabled((mode_creating or mode_editing or (mode_view and self.page.leTape120.text() != "")) and (adhesive == "Tape" or adhesive == "Hybrid"))

		for i in range(6):
			self.sb_tray_assemblys[i].setReadOnly(mode_view)
			self.sb_tools[i].setReadOnly(         mode_view)
			self.le_sensors[i].setReadOnly(       mode_view)
			self.le_baseplates[i].setReadOnly(    mode_view)
			self.pb_go_tools[i].setEnabled(       mode_view and tools_exist[i])
			self.cb_versions[i].setEnabled( mode_creating or mode_editing)
			self.sb_serials[i].setReadOnly(    mode_view)
			self.le_protomodules[i].setReadOnly(       mode_view)  # turn on maual change protomodule name
			# ENABLED IF:
			# - creating
			# - view, and part exists
			# DISABLED IF:
			# - editing (shouldn't want to change parts after step done)
			# - searching
			# - view, and part DNE
			self.pb_go_tray_assemblys[i].setEnabled(mode_creating or (mode_view and self.sb_tray_assemblys[i].value() > -1) )
			self.pb_go_sensors[i].setEnabled(     mode_creating or (mode_view and self.le_sensors[i].text()    != "") )
			self.pb_go_baseplates[i].setEnabled(  mode_creating or (mode_view and self.le_baseplates[i].text() != "") )
			self.pb_go_protomodules[i].setEnabled(mode_view and protomodules_exist[i])
			self.pb_clears[i].setEnabled(         mode_creating or mode_editing)
			self.pb_set_next_serial[i].setEnabled(mode_creating or mode_editing)

		self.page.pbNew.setEnabled(    mode_view)# and not step_sensor_exists )
		self.page.pbEdit.setEnabled(   mode_view and     step_sensor_exists )
		self.page.pbSave.setEnabled(   mode_creating or mode_editing        )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing        )
		self.page.pbGenerate.setEnabled(mode_creating or mode_editing)

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
		aral = self.page.leBatchAraldite.text()
		self.page.pbGoBatchAraldite.setText("select" if aral == "" else "go to")
		t50 = self.page.leTape50.text()
		self.page.pbGoTape50.setText("select" if t50 == "" else "go to")
		t120 = self.page.leTape120.text()
		self.page.pbGoTape120.setText("select" if t120 == "" else "go to")


	@enforce_mode(['editing','creating'])
	def loadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tray_assemblys[i].load(self.sb_tray_assemblys[i].value(), self.page.cbInstitution.currentText())
			self.tools_sensor[i].load(self.sb_tools[i].value(),   self.page.cbInstitution.currentText())
			load_source = "remote"
			if not self.baseplates[i].load_remote(self.le_baseplates[i].text(),full=False):
				self.baseplates[i].load(self.le_baseplates[i].text())
				load_source = "local"
			if self.baseplates[i].ID:
				print("baseplate {} loaded from {}".format(self.baseplates[i].ID,load_source))
			load_source = "remote"
			if not self.sensors[i].load_remote(self.le_sensors[i].text(),full=False):
				self.sensors[i].load(self.le_sensors[i].text())
				load_source = "local"
			if self.sensors[i].ID:
				print("sensor {} loaded from {}".format(self.sensors[i].ID,load_source))
			# self.baseplates[i].load(self.le_baseplates[i].text())
			# self.sensors[i].load(   self.le_sensors[i].text())

		self.tray_component_sensor.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		#self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.batch_araldite.load(self.page.leBatchAraldite.text())
		self.batch_tape_50.load(self.page.leTape50.text())
		self.batch_tape_120.load(self.page.leTape120.text())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadAllTools(self,*args,**kwargs):  # Same as above, but load only tools:
		self.step_sensor.institution = self.page.cbInstitution.currentText()
		for i in range(6):
			self.tray_assemblys[i].load(self.sb_tray_assemblys[i].value(), self.page.cbInstitution.currentText())
			self.tools_sensor[i].load(self.sb_tools[i].value(), self.page.cbInstitution.currentText())
		self.tray_component_sensor.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		#self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def unloadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tray_assemblys[i].clear()
			self.tools_sensor[i].clear()
			self.baseplates[i].clear()
			self.sensors[i].clear()

		self.tray_component_sensor.clear()
		#self.tray_assembly.clear()
		self.batch_araldite.clear()
		self.batch_tape_50.clear()
		self.batch_tape_120.clear()

	@enforce_mode(['editing','creating'])
	def loadToolSensor(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		result = self.tools_sensor[which].load(self.sb_tools[which].value(), self.page.cbInstitution.currentText())
		self.updateIssues()

	@enforce_mode(['editing','creating', 'searching'])
	def loadBaseplate(self, *args, **kwargs):
		if 'row' in kwargs.keys():
			which = kwargs['row']
		else:
			sender_name = str(self.page.sender().objectName())
			which = int(sender_name[-1]) - 1
		# load remote if exists, else load local
		print("baseplate position:",which)
		load_source = "remote"
		if not self.baseplates[which].load_remote(self.le_baseplates[which].text(),full=False):
			self.baseplates[which].load(self.le_baseplates[which].text())
			load_source = "local"
		print("          loaded from {}".format(load_source))
		print("          kind:",self.baseplates[which].kind_of_part)
		print("          ID:",self.baseplates[which].ID)
		print("          material:",self.baseplates[which].material)
		print()
		self.updateIssues()

	@enforce_mode(['editing','creating', 'searching'])
	def loadSensor(self, *args, **kwargs):
		if 'row' in kwargs.keys():
			which = kwargs['row']
		else:
			sender_name = str(self.page.sender().objectName())
			which = int(sender_name[-1]) - 1
		# load remote if exists, else load local
		print("sensor position:",which)
		load_source = "remote"
		if not self.sensors[which].load_remote(self.le_sensors[which].text(),full=False):
			self.sensors[which].load(self.le_sensors[which].text())
			load_source = "local"
		print("       loaded from {}".format(load_source))
		print("       kind:",self.sensors[which].kind_of_part)
		print("       ID:",self.sensors[which].ID)
		print("       channel density:",self.sensors[which].channel_density)
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadTrayComponentSensor(self, *args, **kwargs):
		self.tray_component_sensor.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadTrayAssembly(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = (int(sender_name[-1]) - 1)*2
		result = self.tray_assemblys[which].load(self.sb_tray_assemblys[which].value(), self.page.cbInstitution.currentText())
		result = self.tray_assemblys[which+1].load(self.sb_tray_assemblys[which].value(), self.page.cbInstitution.currentText())
		self.updateIssues()
		#self.tray_assembly.load(self.page.sbTrayAssembly.value(), self.page.cbInstitution.currentText())
		#self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadBatchAraldite(self, *args, **kwargs):
		self.batch_araldite.load(self.page.leBatchAraldite.text())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadTape50(self, *args, **kwargs):
		self.batch_tape_50.load(self.page.leTape50.text())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadTape120(self, *args, **kwargs):
		self.batch_tape_120.load(self.page.leTape120.text())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def switchAdhesive(self, *args, **kwargs):
		adhesive = self.page.cbAdhesive.currentText()
		if adhesive == "Tape":
			# clear araldite
			self.page.leBatchAraldite.clear()
		elif adhesive == "Araldite":  # Araldite
			self.page.leTape50.clear()
			self.page.leTape120.clear()
		else:
			self.page.leBatchAraldite.clear()
			self.page.leTape50.clear()
			self.page.leTape120.clear()
		self.updateElements()
		self.updateIssues()

	#NEW:  Add updateIssues and modify conditions accordingly
	@enforce_mode(['editing', 'creating'])
	def updateIssues(self,*args,**kwargs):
		issues = []
		objects = []

		mode_create    = self.mode == 'creating'

		# Insertion user:
		if self.page.cbUserPerformed.currentText() == "":
			issues.append(I_USER_DNE)

		# Tooling and supplies:
		if self.tray_component_sensor.ID is None:
			issues.append(I_TRAY_COMPONENT_DNE)
		else:
			objects.append(self.tray_component_sensor)

		#if self.tray_assembly.ID is None:
		#	issues.append(I_TRAY_ASSEMBLY_DNE)
		#else:
		#	objects.append(self.tray_assembly)
		if self.page.cbAdhesive.currentText() == "":
			issues.append(I_ADHESIVE_NOT_SELECTED)

		if self.page.cbAdhesive.currentText() == "Araldite":
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

		elif self.page.cbAdhesive.currentText() == "Tape":
			if self.batch_tape_50.ID is None and self.batch_tape_120.ID is None \
			  and self.page.leTape50.text() != "" and self.page.leTape120.text() != "":
				issues.append(I_TAPE_DNE)

			if self.batch_tape_50.ID is None:  # at least 50 um tape should exist
				issues.append(I_TAPE_50_DNE)
			else:
				objects.append(self.batch_tape_50)
				if not (self.batch_tape_50.date_expires is None or self.batch_tape_50.no_expiry == True):
					ydm =  self.batch_tape_50.date_expires.split('-')
					expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))   # ymd format for constructor
					if QtCore.QDate.currentDate() > expires:
						issues.append(I_TAPE_50_EXPIRED)
				if self.batch_tape_50.is_empty:
					issues.append(I_TAPE_50_EMPTY)

			if self.batch_tape_120.ID is None and self.page.leTape120.text() != "":
				issues.append(I_TAPE_120_DNE)
			else:
				objects.append(self.batch_tape_120)
				if not (self.batch_tape_120.date_expires is None or self.batch_tape_120.no_expiry == True):
					ydm =  self.batch_tape_120.date_expires.split('-')
					expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))   # ymd format for constructor
					if QtCore.QDate.currentDate() > expires:
						issues.append(I_TAPE_120_EXPIRED)
				if self.batch_tape_120.is_empty:
					issues.append(I_TAPE_120_EMPTY)
		elif self.page.cbAdhesive.currentText() == "Hybrid":
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

			if self.batch_tape_50.ID is None and self.batch_tape_120.ID is None \
			  and self.page.leTape50.text() != "" and self.page.leTape120.text() != "":
				issues.append(I_TAPE_DNE)

			if self.batch_tape_50.ID is None:  # at least 50 um tape should exist
				issues.append(I_TAPE_50_DNE)
			else:
				objects.append(self.batch_tape_50)
				if not (self.batch_tape_50.date_expires is None or self.batch_tape_50.no_expiry == True):
					ydm =  self.batch_tape_50.date_expires.split('-')
					expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))   # ymd format for constructor
					if QtCore.QDate.currentDate() > expires:
						issues.append(I_TAPE_50_EXPIRED)
				if self.batch_tape_50.is_empty:
					issues.append(I_TAPE_50_EMPTY)

			if self.batch_tape_120.ID is None and self.page.leTape120.text() != "":
				issues.append(I_TAPE_120_DNE)
			else:
				objects.append(self.batch_tape_120)
				if not (self.batch_tape_120.date_expires is None or self.batch_tape_120.no_expiry == True):
					ydm =  self.batch_tape_120.date_expires.split('-')
					expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))   # ymd format for constructor
					if QtCore.QDate.currentDate() > expires:
						issues.append(I_TAPE_120_EXPIRED)
				if self.batch_tape_120.is_empty:
					issues.append(I_TAPE_120_EMPTY)

		# Now, loop over each row and check for missing/bad input
		tray_assemblys_selected = [_.value() for _ in self.sb_tray_assemblys]
		sensor_tools_selected   = [_.value() for _ in self.sb_tools     ]
		baseplates_selected     = [_.text() for _ in self.le_baseplates  ]
		sensors_selected        = [_.text() for _ in self.le_sensors     ]
		versions_selected       = [_.currentText() for _ in self.cb_versions]
		serials_selected        = [_.value() for _ in self.sb_serials]

		# note: >2 bc of every tray is repeated in the list
		tray_assembly_duplicates = [_ for _ in range(6) if tray_assemblys_selected[_] >= 0 and tray_assemblys_selected.count(tray_assemblys_selected[_])>2]
		sensor_tool_duplicates   = [_ for _ in range(6) if sensor_tools_selected[_] >= 0 and sensor_tools_selected.count(sensor_tools_selected[_])>1]
		baseplate_duplicates     = [_ for _ in range(6) if baseplates_selected[_]   != "" and baseplates_selected.count(  baseplates_selected[_]  )>1]
		sensor_duplicates        = [_ for _ in range(6) if sensors_selected[_]      != "" and sensors_selected.count(     sensors_selected[_]     )>1]
		# serial_duplicates        = [_ for _ in range(6) if serials_selected[_]      >= 0 and serials_selected.count(     serials_selected[_]     )>1]

		if tray_assembly_duplicates:
			issues.append(I_TRAY_ASSEMBLY_DUPLICATE.format(', '.join([str(_+1) for _ in tray_assembly_duplicates])))
		if sensor_tool_duplicates:
			issues.append(I_TOOL_SENSOR_DUPLICATE.format(', '.join([str(_+1) for _ in sensor_tool_duplicates])))
		if baseplate_duplicates:
			issues.append(I_BASEPLATE_DUPLICATE.format(', '.join([str(_+1) for _ in baseplate_duplicates])))
		if sensor_duplicates:
			issues.append(I_SENSOR_DUPLICATE.format(', '.join([str(_+1) for _ in sensor_duplicates])))
		# if serial_duplicates:
		# 	issues.append(I_SERIAL_DUPLICATE.format(', '.join([str(_+1) for _ in serial_duplicates])))

		rows_empty           = []
		rows_full            = []
		rows_incomplete      = []

		rows_tray_assembly_dne = []
		rows_baseplate_dne   = []
		rows_tool_sensor_dne = []
		rows_sensor_dne      = []
		rows_version_dne      = []
		rows_serial_dne      = []

		for i in range(6):
			num_parts = 0
			has_version = False
			has_serial = False
			tmp_id = self.step_sensor.ID

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

			# version and serial number must exist
			if versions_selected[i] != "":
				has_version = True
			if serials_selected[i] >0:
				has_serial = True

			# NOTE:  TODO:  geometry, channel_density must match
			if baseplates_selected[i] != "" and sensors_selected[i] != "" \
					and not self.baseplates[i].ID is None and not self.sensors[i].ID is None:
				# Check for compatibility bw two objects:
				if self.baseplates[i].geometry != self.sensors[i].geometry:
					issues.append(I_BASEPLATE_SENSOR_SHAPE.format(self.baseplates[i].ID,    self.baseplates[i].geometry, \
																  self.sensors[i].ID, self.sensors[i].geometry))
				# NEW: Full baseplate doesn't have channel density
				if self.baseplates[i].geometry != 'Full' and self.baseplates[i].channel_density != self.sensors[i].channel_density:
					issues.append(I_BASEPLATE_SENSOR_CHANNEL.format(self.baseplates[i].ID,    self.baseplates[i].channel_density, \
																  self.sensors[i].ID, self.sensors[i].channel_density))

			# note: only count toward filled row if the rest of the row is nonempty
			# ...unless BOTH rows are empty, in which case throw an error!
			if i%2 == 1:  # 1, 3, 5 (posns 2, 4, 6)
				# check whether both rows are empty
				if tray_assemblys_selected[i] >=0 \
                  and i-1 in rows_empty and num_parts == 0:
					# current and previous rows are both empty
					issues.append(I_LONE_TRAY.format(i-1, i))

			if tray_assemblys_selected[i] >= 0 and num_parts != 0:
				num_parts += 1
				objects.append(self.tray_assemblys[i])
				if self.tray_assemblys[i].ID is None:
					rows_tray_assembly_dne.append(i)

			if num_parts == 0:
				rows_empty.append(i)
			elif num_parts == 4: #and has_version and has_serial:  # version and serial can be empty
				rows_full.append(i)
			else:
				rows_incomplete.append(i)


		if not (len(rows_full) or len(rows_incomplete)):
			issues.append(I_NO_PARTS_SELECTED)
		if rows_incomplete:
			issues.append(I_ROWS_INCOMPLETE.format(', '.join(map(str,rows_incomplete))))
		if rows_tray_assembly_dne:
			issues.append(I_TRAY_ASSEMBLY_DNE.format(', '.join([str(_+1) for _ in rows_tray_assembly_dne])))
		if rows_baseplate_dne:
			issues.append(I_BASEPLATE_DNE.format(', '.join([str(_+1) for _ in rows_baseplate_dne])))
		if rows_tool_sensor_dne:
			issues.append(I_TOOL_SENSOR_DNE.format(', '.join([str(_+1) for _ in rows_tool_sensor_dne])))
		if rows_sensor_dne:
			issues.append(I_SENSOR_DNE.format(', '.join([str(_+1) for _ in rows_sensor_dne])))
		if not self.page.ckCheckFeet.isChecked():
			issues.append(I_NO_TOOL_CHK)

		# NEW: Check for parent (only when creating)
		if mode_create:
			for i in range (6):
				if baseplates_selected[i] != "":
					temp_baseplate = parts.baseplate()
					if not temp_baseplate.load_remote(baseplates_selected[i]):
						temp_baseplate.load(baseplates_selected[i])
					if temp_baseplate.ID != None and temp_baseplate.protomodule != None:
						issues.append(I_BASEPLATE_ON_PROTO.format(temp_baseplate.ID, i, temp_baseplate.protomodule))
				if sensors_selected[i] != "":
					temp_sensor = parts.sensor()
					if not temp_sensor.load_remote(sensors_selected[i]):
						temp_sensor.load(sensors_selected[i])
					if temp_sensor.ID != None and temp_sensor.protomodule != None:
						issues.append(I_SENSOR_ON_PROTO.format(temp_sensor.ID, i, temp_sensor.protomodule))
			# NEW: Check if protomodule already exists
			for i in range(6):
				if self.le_protomodules[i].text() != "":
					temp_protomodule = parts.protomodule()
					if not temp_protomodule.load_remote(self.le_protomodules[i].text()):
						temp_protomodule.load(self.le_protomodules[i].text())
					if temp_protomodule.ID != None:
						issues.append(I_PROTO_NAME_EXISTS.format(self.le_protomodules[i].text(), i))

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
		tmp_step = assembly.step_sensor()
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
		# NEW:  Search for all steps at this institution, then create the next in order
		if self.page.cbInstitution.currentText() == "":  return
		part_file_name = os.sep.join([ fm.DATADIR, 'partlist', 'step_sensors.json' ])
		with open(part_file_name, 'r') as opfl:
			part_list = json.load(opfl)
		tmp_inst = self.page.cbInstitution.currentText()
		ids = []
		for part_id, date in part_list.items():
			inst, num = part_id.split("_")
			if inst == tmp_inst:
				ids.append(int(num))
		if ids:
			tmp_ID = max(ids) + 1
		else:
			tmp_ID = 0
		self.page.sbID.setValue(tmp_ID)

		tmp_step = assembly.step_sensor()
		tmp_exists = tmp_step.load("{}_{}".format(tmp_inst, tmp_ID))
		if not tmp_exists:
			self.step_sensor.new("{}_{}".format(tmp_inst, tmp_ID))
			self.mode = 'creating'
			self.updateElements()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_step = assembly.step_sensor()
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
		trays = []
		tools = []
		sensors = []
		baseplates = []
		protomodules = []
		for i in range(6):
			trays.append(     self.sb_tray_assemblys[i].value() if self.sb_tray_assemblys[i].value() >= 0 else None)
			tools.append(       self.sb_tools[i].value()        if self.sb_tools[i].value()        >= 0 else None)
			sensors.append(     self.le_sensors[i].text()      if self.le_sensors[i].text() != "" else None)
			baseplates.append(  self.le_baseplates[i].text()   if self.le_baseplates[i].text() != "" else None)
			# protomodules.append( self.le_protomodules[i].text() if self.le_baseplates[i].text() != "" else None )
			# Auto name the proto module
			if self.le_baseplates[i].text() != "" and self.le_sensors[i].text() != "":
				# protomodules.append("P{}_{}".format(self.le_baseplates[i].text(), self.le_sensors[i].text()))
				if self.le_protomodules[i].text() != "":
					protomodules.append(self.le_protomodules[i].text())
				# protomodules.append(self.make_name(i))
			else:
				protomodules.append(None)
		#self.step_sensor.asmbl_tray_names = trays
		#self.step_sensor.snsr_tool_names = tools
		self.step_sensor.sensors      = sensors
		self.step_sensor.baseplates   = baseplates
		self.step_sensor.protomodules = protomodules


		# Add protomodule ID to baseplate, sensor lists; create protomodule if it doesn't exist:
		for i in range(6):
			if baseplates[i] is None:
				continue
			temp_plt = self.baseplates[i]
			temp_sensor = self.sensors[i]
			temp_protomodule = parts.protomodule()
			# Attempt to load.  If fails, create new:
			if not temp_protomodule.load(protomodules[i]):
				temp_protomodule.new(protomodules[i], baseplate_=temp_plt, sensor_=temp_sensor)
			temp_protomodule.step_sensor    = self.step_sensor.ID
			temp_protomodule.version = self.cb_versions[i].currentText()
			temp_protomodule.serial_number = self.sb_serials[i].value()
			temp_protomodule.manufacturer = self.page.cbInstitution.currentText()
			temp_protomodule.save()

			self.baseplates[i].step_sensor = self.step_sensor.ID
			self.baseplates[i].protomodule = temp_protomodule.ID
			self.baseplates[i].save()
			self.sensors[i].step_sensor = self.step_sensor.ID
			self.sensors[i].protomodule = temp_protomodule.ID
			self.sensors[i].save()

		# set sensor step properties (which implicitly set the protomodule vars):
		# since these call protomodule.save(), must be called second
		self.step_sensor.record_insertion_user = str(self.page.cbUserPerformed.currentText()) \
		    if self.page.cbUserPerformed.currentText()!='' else None
		# Save all times as UTC
		pydt = self.page.dtRunStart.dateTime().toPyDateTime().astimezone(datetime.timezone.utc)
		self.step_sensor.run_begin_timestamp = str(pydt) # sec UTC
		pydt = self.page.dtRunStop.dateTime().toPyDateTime().astimezone(datetime.timezone.utc)
		self.step_sensor.run_end_timestamp   = str(pydt)
		
		inst = self.page.cbInstitution.currentText()
		self.step_sensor.glue_batch_num = self.page.leBatchAraldite.text() \
		    if self.page.leBatchAraldite.text() else None
		self.step_sensor.batch_tape_50 = self.page.leTape50.text() \
            if self.page.leTape50.text() != "" else None
		self.step_sensor.batch_tape_120 = self.page.leTape120.text() \
            if self.page.leTape120.text() != "" else None
		#self.step_sensor.asmbl_tray_name = "{}_{}".format(inst, self.page.sbTrayAssembly.value()) \
		#    if self.page.sbTrayAssembly.value() >= 0 else None
		self.step_sensor.comp_tray_name = "{}_{}".format(inst, self.page.sbTrayComponent.value()) \
		    if self.page.sbTrayComponent.value() >= 0 else None

		self.step_sensor.asmbl_tray_names = [None if trays[i] is None else "{}_{}".format(inst, trays[i]) for i in range(6)]
		self.step_sensor.snsr_tool_names  = [None if tools[i] is None else "{}_{}".format(inst, tools[i]) for i in range(6)]
		self.step_sensor.snsr_tool_feet_chk = self.page.ckCheckFeet.isChecked()

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


	def isRowClear(self, row):
		return (self.sb_tools[row].value() == -1 or self.sb_tools[row].value() is None) \
               and self.le_sensors[row].text() == "" \
               and self.le_baseplates[row].text() == ""

	def clearRow(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		# self.sb_tools[which].setValue(-1)
		self.sb_tools[which].clear()
		self.le_sensors[which].clear()
		self.le_baseplates[which].clear()
		self.cb_versions[which].clear()
		self.sb_serials[which].clear()
		self.le_protomodules[which].clear()
		# clear tray assembly only if current and neighboring rows are clear
		uprow   = which if which%2==0 else which-1
		downrow = which if which%2!=0 else which+1
		#print("Rows {}, {} are clear: {}, {}".format(uprow, downrow, self.isRowClear(uprow), self.isRowClear(downrow)))
		if self.isRowClear(uprow) and self.isRowClear(downrow):
			self.sb_tray_assemblys[which].setValue(-1)
			self.sb_tray_assemblys[which].clear()
		self.updateIssues()

	def doSearch(self,*args,**kwargs):
		tmp_class = getattr(parts, self.search_part, None)
		if tmp_class is None:
			tmp_class = getattr(supplies, self.search_part)
		tmp_part = tmp_class()

		# Search local-only parts:  open part file
		part_file_name = os.sep.join([ fm.DATADIR, 'partlist', self.search_part+'s.json' ])
		with open(part_file_name, 'r') as opfl:
			part_list = json.load(opfl)

		for part_id, date in part_list.items():
			# If already added by DB query, skip:
			if len(self.page.lwPartList.findItems("{} {}".format(self.search_part, part_id), \
			                                      QtCore.Qt.MatchExactly)) > 0:
				continue
			if self.search_part == 'baseplate':
				# Search for one thing:  NOT already assigned to a protomod
				tmp_part.load(part_id)
				if tmp_part.protomodule is None:
					self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))
			elif self.search_part == 'sensor':
				tmp_part.load(part_id)
				if tmp_part.protomodule is None:
					self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))
			elif self.search_part == 'batch_araldite':  # araldite, no restrictions
				self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))
			elif self.search_part == 'batch_tape_50':
				self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))
			elif self.search_part == 'batch_tape_120':
				self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))
		
		# NEW: Search remote parts in central DB (only for sensors and baseplates)
		if self.search_part in ['baseplate', 'sensor']:
			partlistdir_remote = os.sep.join([fm.DATADIR, 'partlist_remote'])
			obj_list_remote = os.sep.join([partlistdir_remote, self.search_part+'s.json'])

			# if sensor remote part list doesn't exist, fetch from DB
			if not os.path.exists(obj_list_remote) and self.search_part == 'sensor':
				print("Sensor remote part list doesn't exist, will fetch from DB")
				self.page.leSearchStatus.setText('Fetching remote sensor list...')
				fm.fetchRemoteDB(self.search_part,location=self.page.cbInstitution.currentText())

			with open(obj_list_remote, 'r') as opfl:
				part_data = json.load(opfl)
				for part in part_data['parts']:
					# Only list parts at this institution
					if part['location'] != self.page.cbInstitution.currentText(): continue
					part_id = part['serial_number']
					# If already added by DB query, skip:
					if len(self.page.lwPartList.findItems("{} {}".format(self.search_part, part_id), \
														QtCore.Qt.MatchExactly)) > 0: continue
					# need to load full part to check parent -- TOO SLOW!!!
					# tmp_part.load_remote(part_id, full=True)
					# if tmp_part.protomodule is None:
					self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))

		# Sort search results
		self.page.lwPartList.sortItems()

		self.page.leSearchStatus.setText('{}: row {}'.format(self.search_part, self.search_row))
		self.mode = 'searching'
		self.updateElements()

	def finishSearch(self,*args,**kwargs):
		row = self.page.lwPartList.currentRow()
		if self.page.lwPartList.item(row) is None:
			return
		name_ = self.page.lwPartList.item(row).text().split()[1:]
		name = " ".join(name_)
		if self.search_part in ['baseplate', 'sensor']:
			le_to_fill = getattr(self, 'le_{}s'.format(self.search_part))[self.search_row]
		elif self.search_part == "batch_araldite":  # araldite
			le_to_fill = self.page.leBatchAraldite
		elif self.search_part == "batch_tape_50":  # araldite
			le_to_fill = self.page.leTape50
		elif self.search_part == "batch_tape_120":  # araldite
			le_to_fill = self.page.leTape120
		le_to_fill.setText(name)

		self.page.lwPartList.clear()
		self.page.leSearchStatus.clear()
		self.mode = 'creating'
		if self.search_part in ['baseplate', 'sensor']:
			getattr(self, 'load'+self.search_part.capitalize())(row=self.search_row)  # load part object
		elif self.search_part == "batch_araldite":
			self.loadBatchAraldite()
		elif self.search_part == "batch_tape_50":
			self.loadTape50()
		elif self.search_part == "batch_tape_120":
			self.loadTape120()
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
		batch_araldite = self.page.leBatchAraldite.text()
		if batch_araldite != "":
			self.setUIPage('Supplies',batch_araldite=batch_araldite)
		else:
			self.mode = 'searching'
			self.search_part = 'batch_araldite'
			self.search_row = None
			self.doSearch()

	def goTrayComponent(self,*args,**kwargs):
		tray_component_sensor = self.page.sbTrayComponent.value()
		self.setUIPage('Tooling',tray_component_sensor=tray_component_sensor,institution=self.page.cbInstitution.currentText())

	def goTrayAssembly(self,*args,**kwargs):
		#tray_assembly = self.page.sbTrayAssembly.value()
		#self.setUIPage('Tooling',tray_assembly=tray_assembly,institution=self.page.cbInstitution.currentText())
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1 # last character of sender name is integer 1 through 6; subtract one for zero index
		tray = self.sb_tray_assemblys[which].value()
		self.setUIPage('Tooling',tray_assembly=tray,institution=self.page.cbInstitution.currentText())

	def goTape50(self,*args,**kwargs):
		batch_tape_50 = self.page.leTape50.text()
		if batch_tape_50 != "":
			self.setUIPage('Supplies',batch_tape_50=batch_tape_50)
		else:
			self.mode = 'searching'
			self.search_part = 'batch_tape_50'
			self.search_row = None
			self.doSearch()

	def goTape120(self,*args,**kwargs):
		batch_tape_120 = self.page.leTape120.text()
		if batch_tape_120 != "":
			self.setUIPage('Supplies',batch_tape_120=batch_tape_120)
		else:
			self.mode = 'searching'
			self.search_part = 'batch_tape_120'
			self.search_row = None
			self.doSearch()


	def setRunStartNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtRunStart.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtRunStart.setTime(QtCore.QTime(*localtime[3:6]))

	def setRunStopNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtRunStop.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtRunStop.setTime(QtCore.QTime(*localtime[3:6]))

	def setNextSerial(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1

		# Check that all fields are filled
		if not (self.sensors[which].ID != None and self.baseplates[which].ID != None\
			and self.cb_versions[which].currentIndex() != -1): #and self.sb_serials[which].value() >=1):
			print("!! Not all fields are filled for position {} to auto-name".format(which))
			return

		# print("!! setting next serial for position {}".format(which))
		# NEW:  Search for all protomodules at this institution, then create the next in order
		if self.page.cbInstitution.currentText() == "":  return
		part_file_name = os.sep.join([ fm.DATADIR, 'partlist', 'protomodules.json' ])
		with open(part_file_name, 'r') as opfl:
			part_list = json.load(opfl)
		tmp_inst = self.page.cbInstitution.currentText()
		serials = []
		for part_id, date in part_list.items():
			if is_proper_name(part_id) and part_id[7:9] == NAME_INSTITUTION[tmp_inst]\
       		and not ('None' in self.sensors[which].kind_of_part)\
            and not ('None' in self.baseplates[which].kind_of_part):
				name = 'P'
				name += NAME_DENSITY[self.sensors[which].channel_density]
				name += NAME_GEOMETRY[self.sensors[which].geometry]
				name += NAME_THICKNESS[self.sensors[which].sen_type]
				name += NAME_MATERIAL[self.baseplates[which].material]
				name += NAME_VERSION[self.cb_versions[which].currentText()]
				if name in part_id:
					match = re.search(r'[1-9]', part_id[7:])
					s = int(part_id[7:][match.start():])
					serials.append(s)
		if serials:
			tmp_serial = max(serials) + 1
		else:
			tmp_serial = 1
		self.sb_serials[which].setValue(tmp_serial)
		self.le_protomodules[which].setText(self.make_name(which))
		self.update_info()

	def update_protoID(self, *args, **kwargs):
		for i in range(6):
			# print("updating state for {}".format(i))
			# print("params: {} {} {}".format(self.le_sensors[i].text(), self.le_baseplates[i].text(), self.cb_versions[i].currentIndex(), self.sb_serials[i].value()))
			# Update name if the pamams are not empty
			if  self.le_sensors[i].text() != "" and self.le_baseplates[i].text() != ""\
			and self.cb_versions[i].currentIndex() != -1 and self.sb_serials[i].value() >=1:
				print("updating state for position {}".format(i))
				if self.sensors[i].ID is None and self.baseplates[i].ID is None:
					if not self.sensors[i].load_remote(self.le_sensors[i].text()):
						self.sensors[i].load(   self.le_sensors[i].text())
					if not self.baseplates[i].load_remote(self.le_baseplates[i].text()):
						self.baseplates[i].load(   self.le_baseplates[i].text())
				if self.sensors[i].ID is not None and self.baseplates[i].ID is not None and self.cb_versions[i].currentText() != '' and self.sb_serials[i].value() != 0:
					self.le_protomodules[i].setText(self.make_name(i))
		self.updateIssues()

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

	def make_name(self,i):
		# print("channel_density: {} geometry: {} sen_type: {} material: {} version: {} serial: {}".format(self.sensors[i].channel_density, self.sensors[i].geometry, self.sensors[i].sen_type, self.baseplates[i].material, self.cb_versions[i].currentText(), self.sb_serials[i].value()))
		name = 'P'
		name += NAME_DENSITY[self.sensors[i].channel_density]
		name += NAME_GEOMETRY[self.sensors[i].geometry]
		name += NAME_THICKNESS[self.sensors[i].sen_type]
		name += NAME_MATERIAL[self.baseplates[i].material]
		name += NAME_VERSION[self.cb_versions[i].currentText()]
		name += '-' # TBD: may need to delete
		name += NAME_INSTITUTION[self.page.cbInstitution.currentText()]
		name += str(self.sb_serials[i].value()).zfill(4)
		return name

	def has_non_integer_characters(self,input_string):
		for char in input_string:
			if not char.isdigit():
				return True
		return False
