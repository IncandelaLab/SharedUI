from PyQt5 import QtCore
import time
import datetime
import os
import json

from filemanager import fm, parts, tools, supplies, assembly

NO_DATE = [2022,1,1]

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
	'CMU':6,
	'TTU':7,
	'IHEP':8,
	'TIFR':9,
	'NTU':10,
	'FSU':11,
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
	'Ti/Kapton'  : 'T',
	'CF/Kapton'  : 'C'
}
NAME_VERSION = {
	'preseries'  : 'X',
	'production' : '0'  # TBD, currently set to X
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
I_TAPE_120_DNE = "125um tape batch does not exist or is not selected"
I_TAPE_120_EXPIRED = "125um tape batch has expired"
I_TAPE_DNE = "at least one tape batch is required"
I_ADHESIVE_NOT_SELECTED = "no adhesive type is selected"

# parts
I_PART_NOT_READY    = "{}(s) in position(s) {} is not ready for hexaboard application. reason: {}"
I_PCB_PROTOMODULE_SHAPE = "hexaboard {} has shape {} but protomodule {} has shape {}"
I_PCB_PROTOMODULE_CHANNEL = "hexaboard {} has channel density {} but protomodule {} has channel density {}"
I_MOD_EXISTS = "module {} already exists!"
I_PCB_ON_MODULE = "hexaboard {} on position {} is already assembled on module {}"
I_PROTO_ON_MODULE = "protomodule {} on position {} is already assembled on module {}"

# rows / positions
I_NO_PARTS_SELECTED     = "no parts have been selected"
I_ROWS_INCOMPLETE       = "positions {} are partially filled"
I_TRAY_ASSEMBLY_DNE     = "assembly tray(s) in position(s) {} do not exist"
I_TOOL_SENSOR_DNE       = "sensor tool(s) in position(s) {} do not exist"
I_BASEPLATE_DNE         = "baseplate(s) in position(s) {} do not exist"
I_SENSOR_DNE            = "sensor(s) in position(s) {} do not exist"
I_PCB_DNE               = "hexaboard(s) in position(s) {} do not exist"
I_PROTO_DNE             = "protomodule(s) in position(s) {} do not exist"
I_TRAY_ASSEMBLY_DUPLICATE = "same assembly tray is selected on multiple positions: {}"
I_TOOL_PCB_DUPLICATE    = "same hexaboard tool is selected on multiple positions: {}"
I_BASEPLATE_DUPLICATE   = "same baseplate is selected on multiple positions: {}"
I_SENSOR_DUPLICATE      = "same sensor is selected on multiple positions: {}"
I_PCB_DUPLICATE         = "same hexaboard is selected on multiple positions: {}"
I_PROTO_DUPLICATE       = "same protomodule is selected on multiple positions: {}"
I_LONE_TRAY             = "assembly tray entered, but rows {} and {} are empty"

# compatibility
I_SIZE_MISMATCH   = "size mismatch between some selected objects"
I_SIZE_MISMATCH_8 = "* list of 8-inch objects selected: {}"

# institution
I_INSTITUTION = "some selected objects are not at this institution: {}"

# Missing user
I_USER_DNE = "no hexaboard step user selected"

# supply batch empty
I_BATCH_ARALDITE_EMPTY = "araldite batch is empty"
I_TAPE_50_EMPTY = "50um tape batch is empty"
I_TAPE_120_EMPTY = "125um tape batch is empty"

# NEW
I_INSTITUTION_NOT_SELECTED = "no institution selected"

I_NO_TOOL_CHK = "pickup tool feet have not been checked"

# module
I_MODULE_NAME_EXISTS = "module name {} on position {} already exists"


class func(object):
	def __init__(self,fm,userManager,page,setUIPage,setSwitchingEnabled):
		self.userManager = userManager
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		#New stuff
		self.tray_assemblys = [tools.tray_assembly() for _ in range(6)]
		self.tools_pcb    = [tools.tool_pcb()    for _ in range(6)]
		self.pcbs         = [parts.pcb()         for _ in range(6)]
		self.baseplates   = [parts.baseplate()   for _ in range(6)]
		self.sensors      = [parts.sensor()      for _ in range(6)]
		self.protomodules = [parts.protomodule() for _ in range(6)]
		self.modules      = [parts.module()      for _ in range(6)]
		self.tray_component_pcb = tools.tray_component_pcb()
		self.batch_araldite     = supplies.batch_araldite()
		self.batch_tape_50         = supplies.batch_tape_50()
		self.batch_tape_120        = supplies.batch_tape_120()

		self.step_pcb = assembly.step_pcb()
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
		self.loadStep()

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
		self.le_pcbs = [
			self.page.lePcb1,
			self.page.lePcb2,
			self.page.lePcb3,
			self.page.lePcb4,
			self.page.lePcb5,
			self.page.lePcb6,
		]
		self.pb_go_pcbs = [
			self.page.pbGoPcb1,
			self.page.pbGoPcb2,
			self.page.pbGoPcb3,
			self.page.pbGoPcb4,
			self.page.pbGoPcb5,
			self.page.pbGoPcb6,
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
			self.page.pbGoProtomodule1,
			self.page.pbGoProtomodule2,
			self.page.pbGoProtomodule3,
			self.page.pbGoProtomodule4,
			self.page.pbGoProtomodule5,
			self.page.pbGoProtomodule6,
		]
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

		for i in range(6):
			# was editingFinished()
			self.sb_tray_assemblys[i].valueChanged.connect(self.loadTrayAssembly)
			self.pb_go_tray_assemblys[i].clicked.connect(self.goTrayAssembly)

			self.pb_go_tools[i].clicked.connect(       self.goTool       )
			self.pb_go_pcbs[i].clicked.connect(        self.goPcb        )
			self.pb_go_protomodules[i].clicked.connect(self.goProtomodule)
			self.pb_go_modules[i].clicked.connect(     self.goModule     )

			self.sb_tools[i].editingFinished.connect(       self.loadToolPcb )
			self.le_pcbs[i].textChanged.connect(        self.loadPcb        )
			self.le_protomodules[i].textChanged.connect(self.loadProtomodule)
			self.le_modules[i].textChanged.connect(self.updateIssues)

			self.pb_clears[i].clicked.connect(self.clearRow)

		self.page.pbGenerate.clicked.connect( self.update_moduleID )

		self.page.pbAddPart.clicked.connect(self.finishSearch)
		self.page.pbCancelSearch.clicked.connect(self.cancelSearch)

		self.page.ckCheckFeet.stateChanged.connect(self.updateIssues)
		self.page.cbUserPerformed.activated.connect(self.updateIssues)

		self.page.sbID.valueChanged.connect(self.loadStep)
		self.page.cbInstitution.currentIndexChanged.connect(self.loadStep)

		# was editingFinished
		self.page.sbTrayComponent.valueChanged.connect( self.loadTrayComponentPCB )
		#self.page.sbTrayAssembly.editingFinished.connect(  self.loadTrayAssembly        )
		self.page.leBatchAraldite.textEdited.connect(self.loadBatchAraldite)
		self.page.leTape50.textEdited.connect( self.loadTape50 )
		self.page.leTape120.textEdited.connect( self.loadTape120 )

		self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)
		self.page.pbLoad.clicked.connect(self.loadSensorStep)

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
			tmp_id, tmp_inst = ID.split("_")
			self.page.sbID.setValue(tmp_id)
			self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))

		self.step_pcb_exists = False
		if getattr(self.step_pcb, 'ID', None) != None:
			self.step_pcb_exists = (ID == self.step_pcb.ID)

		self.page.listIssues.clear()
		self.page.leStatus.clear()
		localtime = time.localtime()

		if self.step_pcb_exists:

			if not self.step_pcb.record_insertion_user in self.index_users.keys() and not self.step_pcb.record_insertion_user is None:
				# Insertion user was deleted from user page...just add user to the dropdown
				self.index_users[self.step_pcb.record_insertion_user] = max(self.index_users.values()) + 1
				self.page.cbUserPerformed.addItem(self.step_pcb.record_insertion_user)
			self.page.cbUserPerformed.setCurrentIndex(self.index_users.get(self.step_pcb.record_insertion_user, -1))

			times_to_set = [(self.step_pcb.run_begin_timestamp,  self.page.dtRunStart),
			                (self.step_pcb.run_end_timestamp,   self.page.dtRunStop)]
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


			if self.step_pcb.glue_batch_num is None and self.step_pcb.batch_tape_120 is None:
				self.page.cbAdhesive.setCurrentIndex(-1)
				self.page.leBatchAraldite.setText("")
				self.page.leTape50.setText("")
				self.page.leTape120.setText("")
			elif self.step_pcb.glue_batch_num != None and self.step_pcb.batch_tape_120 is None:
				self.page.cbAdhesive.setCurrentIndex(0)
				self.page.leBatchAraldite.setText(self.step_pcb.glue_batch_num)
				self.page.leTape50.setText("")
				self.page.leTape120.setText("")
			elif self.step_pcb.glue_batch_num is None and self.step_pcb.batch_tape_120 != None:
				self.page.cbAdhesive.setCurrentIndex(1)
				self.page.leBatchAraldite.setText("")
				self.page.leTape50.setText(self.step_pcb.batch_tape_50)
				self.page.leTape120.setText(self.step_pcb.batch_tape_120)
			else:  # Hybrid
				self.page.cbAdhesive.setCurrentIndex(2)
				self.page.leBatchAraldite.setText(self.step_pcb.glue_batch_num)
				self.page.leTape50.setText(self.step_pcb.batch_tape_50)
				self.page.leTape120.setText(self.step_pcb.batch_tape_120)
			#self.page.leBatchAraldite.setText(self.step_pcb.glue_batch_num if not (self.step_pcb.glue_batch_num is None) else "")
			#self.page.sbTrayAssembly.setValue( self.step_pcb.asmbl_tray_num if not (self.step_pcb.asmbl_tray_name  is None) else -1)
			self.page.sbTrayComponent.setValue(self.step_pcb.comp_tray_num if not (self.step_pcb.comp_tray_num is None) else -1)

			if not (self.step_pcb.asmbl_tray_names is None):
				trays = self.step_pcb.asmbl_tray_nums
				for i in [0, 2, 4]:  # 0/1, 2/3, 4/5
					# note: if first is filled + second is empty, will erroneously set to     -1 - avoid
					if trays[i] is None and trays[i+1] is None:
						self.sb_tray_assemblys[i].setValue(-1)
					elif trays[i] is None:
						self.sb_tray_assemblys[i].setValue(trays[i+1])
					else:
						self.sb_tray_assemblys[i].setValue(trays[i])
				#self.sb_tray_assemblys[i].setValue(trays[i] if trays[i] != None else     -1)
			else:
				for i in range(6):
					self.sb_tray_assemblys[i].setValue(-1)
			if not (self.step_pcb.pcb_tool_names is None):
				tools = self.step_pcb.pcb_tool_nums
				for i in range(6):
					self.sb_tools[i].setValue(tools[i] if not (tools[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_tools[i].setValue(-1)

			if not (self.step_pcb.pcbs is None):
				for i in range(6):
					self.le_pcbs[i].setText(str(self.step_pcb.pcbs[i]) if not (self.step_pcb.pcbs[i] is None) else "")
			else:
				for i in range(6):
					self.le_pcbs[i].setText("")

			if not (self.step_pcb.protomodules is None):
				for i in range(6):
					self.le_protomodules[i].setText(str(self.step_pcb.protomodules[i]) if not (self.step_pcb.protomodules[i] is None) else "")
			else:
				for i in range(6):
					self.le_protomodules[i].setText("")

			if not (self.step_pcb.modules is None):
				for i in range(6):
					self.le_modules[i].setText(str(self.step_pcb.modules[i]) if not (self.step_pcb.modules[i] is None) else "")
			else:
				for i  in range(6):
					self.le_modules[i].setText("")

			self.page.ckCheckFeet.setChecked(self.step_pcb.pcb_tool_feet_chk if not (self.step_pcb.pcb_tool_feet_chk is None) else False)

		else:
			self.page.cbUserPerformed.setCurrentIndex(-1)
			self.page.dtRunStart.setDate(QtCore.QDate(localtime.tm_year, 1, 1))
			self.page.dtRunStart.setTime(QtCore.QTime(0,0,0))
			self.page.dtRunStop.setDate(QtCore.QDate(localtime.tm_year, 1, 1))
			self.page.dtRunStop.setTime(QtCore.QTime(0,0,0))

			self.page.leBatchAraldite.setText("")
			self.page.leTape50.setText("")
			self.page.leTape120.setText("")
			self.page.sbTrayComponent.setValue(-1)
			#self.page.sbTrayAssembly.setValue(-1)
			for i in range(6):
				self.sb_tray_assemblys[i].setValue(-1)
				self.sb_tools[i].setValue(-1)
				self.le_pcbs[i].setText("")
				self.le_protomodules[i].setText("")
				self.le_modules[i].setText("")
			self.page.ckCheckFeet.setChecked(False)

		
		for i in range(6):
			if self.sb_tray_assemblys[i].value() == -1:  self.sb_tray_assemblys[i].clear()
			if self.sb_tools[i].value()        == -1:  self.sb_tools[i].clear()
		
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
		pcbs_exist         = [_.text()!="" for _ in self.le_pcbs        ]
		protomodules_exist = [_.text()!="" for _ in self.le_protomodules]
		modules_exist      = [_.text()!="" for _ in self.le_modules     ]
		step_pcb_exists    = self.step_pcb_exists
		adhesive = self.page.cbAdhesive.currentText()

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbID.setEnabled(mode_view)
		self.page.cbInstitution.setEnabled(mode_view)  # mode_creating or mode_editing)

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
		
		self.page.leMaxSensorStep.setReadOnly(True)
		self.page.pbLoad.setEnabled(mode_creating or mode_editing)
		self.page.sbSensorStep.setReadOnly(mode_view)

		self.page.pbGoTrayComponent.setEnabled(mode_view and self.page.sbTrayComponent.value() >= 0)
		#self.page.pbGoTrayAssembly .setEnabled(mode_view and self.page.sbTrayAssembly .value() >= 0)
		self.page.pbGoBatchAraldite.setEnabled((mode_creating or mode_editing or (mode_view and self.page.leBatchAraldite.text() != "")) and (adhesive == "Araldite" or adhesive == "Hybrid"))
		self.page.pbGoTape50.setEnabled((mode_creating or mode_editing or (mode_view and self.page.leTape50.text() != "")) and (adhesive == "Tape" or adhesive == "Hybrid"))
		self.page.pbGoTape120.setEnabled((mode_creating or mode_editing or (mode_view and self.page.leTape120.text() != "")) and (adhesive == "Tape" or adhesive == "Hybrid"))

		for i in range(6):
			self.sb_tray_assemblys[i].setReadOnly(mode_view)
			self.sb_tools[i].setReadOnly(       mode_view)
			self.le_pcbs[i].setReadOnly(        mode_view)
			self.le_protomodules[i].setReadOnly(mode_view)
			self.le_modules[i].setReadOnly(     mode_view)  # turn on maual change module name
			self.pb_go_tray_assemblys[i].setEnabled(mode_creating or (mode_view and self.sb_tray_assemblys[i].value() != -1) )
			self.pb_go_tools[i].setEnabled(       mode_view and tools_exist[i]       )
			self.pb_go_pcbs[i].setEnabled(        mode_creating or (mode_view and self.le_pcbs[i].text()            != "") )
			self.pb_go_protomodules[i].setEnabled(mode_creating or (mode_view and self.le_protomodules[i].text()    != "") )
			self.pb_go_modules[i].setEnabled(     mode_view and modules_exist[i]     )
			self.pb_clears[i].setEnabled(mode_creating or mode_editing)

		self.page.pbNew.setEnabled(    mode_view)# and not step_pcb_exists )
		self.page.pbEdit.setEnabled(   mode_view and     step_pcb_exists )
		self.page.pbSave.setEnabled(   mode_creating or mode_editing     )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing     )
		self.page.pbGenerate.setEnabled(mode_creating or mode_editing)

		self.page.ckCheckFeet.setEnabled(not mode_view)

		self.page.pbAddPart     .setEnabled(mode_searching)
		self.page.pbCancelSearch.setEnabled(mode_searching)


		# NEW:  Update pb's based on search result
		for i in range(6):
			self.pb_go_tools[i]       .setText("" if self.sb_tools[i].value()        < 0  else "go to")
			self.pb_go_modules[i].setText("" if self.le_modules[i].text() == "" else "go to")
			for btn, ledit in [[self.pb_go_pcbs[i],         self.le_pcbs[i]],
			                   [self.pb_go_protomodules[i], self.le_protomodules[i]]]:
				btn.setText("select" if ledit.text() == "" else "go to")
			
		aral = self.page.leBatchAraldite.text()
		self.page.pbGoBatchAraldite.setText("select" if aral == "" else "go to")
		t50 = self.page.leTape50.text()
		self.page.pbGoTape50.setText("select" if t50 == "" else "go to")
		t120 = self.page.leTape120.text()
		self.page.pbGoTape120.setText("select" if t120 == "" else "go to")

		# self.setMaxSensorStep()


	@enforce_mode(['editing','creating'])
	def loadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tray_assemblys[i].load(self.sb_tray_assemblys[i].value(), self.page.cbInstitution.currentText())
			self.tools_pcb[i].load(self.sb_tools[i].value(),       self.page.cbInstitution.currentText())
			load_source = "remote"
			if not self.pcbs[i].load_remote(self.le_pcbs[i].text(),full=False):
				self.pcbs[i].load(self.le_pcbs[i].text())
				load_source = "local"
			if self.pcbs[i].ID:
				print("hexaboard {} loaded from {}".format(self.pcbs[i].ID,load_source))
			if not self.protomodules[i].load_remote(self.le_protomodules[i].text(),full=False):
				self.protomodules[i].load(self.le_protomodules[i].text())
				load_source = "local"
			if self.protomodules[i].ID:
				print("protomodule {} loaded from {}".format(self.protomodules[i].ID,load_source))
			# self.protomodules[i].load(self.le_protomodules[i].text())
			# self.pcbs[i].load(        self.le_pcbs[i].text()        )
			# self.modules[i].load(     self.le_modules[i].text()     )

		self.tray_component_pcb.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		#self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.batch_araldite.load(       self.page.leBatchAraldite.text())
		self.batch_tape_50.load(self.page.leTape50.text())
		self.batch_tape_120.load(self.page.leTape120.text())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadAllTools(self,*args,**kwargs):  # Same as above, but load only tools:
		self.step_pcb.institution = self.page.cbInstitution.currentText()
		for i in range(6):
			self.tray_assemblys[i].load(self.sb_tray_assemblys[i].value(), self.page.cbInstitution.currentText())
			self.tools_pcb[i].load(self.sb_tools[i].value(),       self.page.cbInstitution.currentText())
		self.tray_component_pcb.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		#self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.batch_araldite.load(       self.page.leBatchAraldite.text())
		self.updateIssues()


	@enforce_mode(['editing','creating'])
	def unloadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tray_assemblys[i].clear()
			self.tools_pcb[i].clear()
			self.pcbs[i].clear()
			self.protomodules[i].clear()
			self.modules[i].clear()

		self.tray_component_pcb.clear()
		#self.tray_assembly.clear()
		self.batch_araldite.clear()
		self.batch_tape_50.clear()
		self.batch_tape_120.clear()

	@enforce_mode(['editing','creating'])
	def loadToolPcb(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.tools_pcb[which].load(self.sb_tools[which].value(), self.page.cbInstitution.currentText())
		self.updateIssues()

	@enforce_mode(['editing','creating', 'searching'])
	def loadPcb(self, *args, **kwargs):
		if 'row' in kwargs.keys():
			which = kwargs['row']
		else:
			sender_name = str(self.page.sender().objectName())
			which = int(sender_name[-1]) - 1
		# load remote if exists, else load local
		print("Hexaboard position:",which)
		load_source = "remote"
		if not self.pcbs[which].load_remote(self.le_pcbs[which].text(),full=False):
			self.pcbs[which].load(self.le_pcbs[which].text())
			load_source = "local"
		print("    loaded from {}".format(load_source))
		print("    kind:",self.pcbs[which].kind_of_part)
		print("    ID:",self.pcbs[which].ID)
		print("    density:",self.pcbs[which].channel_density)
		print()
		# self.pcbs[which].load(self.le_pcbs[which].text())
		self.updateIssues()

	#New
	@enforce_mode(['editing','creating', 'searching'])
	def loadProtomodule(self, *args, **kwargs):
		if 'row' in kwargs.keys():
			which = kwargs['row']
		else:
			sender_name = str(self.page.sender().objectName())
			which = int(sender_name[-1]) - 1
		# load remote if exists, else load local
		print("protomodule position:",which)
		load_source = "remote"
		if not self.protomodules[which].load_remote(self.le_protomodules[which].text(),full=False):
			self.protomodules[which].load(self.le_protomodules[which].text())
			load_source = "local"
		print("       loaded from {}".format(load_source))
		print("       kind:",self.protomodules[which].kind_of_part)
		print("       ID:",self.protomodules[which].ID)
		print("       channel density:",self.protomodules[which].channel_density)
		# self.protomodules[which].load(self.le_protomodules[which].text())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadModule(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.modules[which].load(self.le_modules[which].text())
		self.updateIssues()


	@enforce_mode(['editing','creating'])
	def loadTrayComponentPCB(self, *args, **kwargs):
		self.tray_component_pcb.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
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

		if self.page.cbUserPerformed.currentText() == "":
			issues.append(I_USER_DNE)

		# tooling and supplies--copied over
		if self.tray_component_pcb.ID is None:
			issues.append(I_TRAY_COMPONENT_DNE)
		else:
			objects.append(self.tray_component_pcb)

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
					ydm = self.batch_araldite.date_expires.split('-')
					expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))  #datetime.date(*self.batch_araldite.date_expires)
					if QtCore.QDate.currentDate() > expires:
						issues.append(I_BATCH_ARALDITE_EXPIRED)
				if self.batch_araldite.is_empty:
					issues.append(I_BATCH_ARALDITE_EMPTY)

		elif self.page.cbAdhesive.currentText() == "Tape":
			if self.batch_tape_50.ID is None and self.batch_tape_120.ID is None \
			  and self.page.leTape50.text() != "" and self.page.leTape120.text() != "":
				issues.append(I_TAPE_DNE)

			if self.batch_tape_50.ID is None and self.page.leTape50.text() != "":
				issues.append(I_TAPE_50_DNE)
			else:
				objects.append(self.batch_tape_50)
				if not (self.batch_tape_50.date_expires is None or self.batch_tape_50.no_expiry == True):
					ydm =  self.batch_tape_50.date_expires.split('-')
					expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))   # ymd format for c     onstructor
					if QtCore.QDate.currentDate() > expires:
						issues.append(I_TAPE_50_EXPIRED)
				if self.batch_tape_50.is_empty:
					issues.append(I_TAPE_50_EMPTY)

			if self.batch_tape_120.ID is None:
				issues.append(I_TAPE_120_DNE)
			else:
				objects.append(self.batch_tape_120)
				if not (self.batch_tape_120.date_expires is None or self.batch_tape_120.no_expiry == True):
					ydm =  self.batch_tape_120.date_expires.split('-')
					expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))   # ymd format for c     onstructor
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
					ydm = self.batch_araldite.date_expires.split('-')
					expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))  #datetime.date(*self.batch_araldite.date_expires)
					if QtCore.QDate.currentDate() > expires:
						issues.append(I_BATCH_ARALDITE_EXPIRED)
				if self.batch_araldite.is_empty:
					issues.append(I_BATCH_ARALDITE_EMPTY)
			if self.batch_tape_50.ID is None and self.batch_tape_120.ID is None \
			  and self.page.leTape50.text() != "" and self.page.leTape120.text() != "":
				issues.append(I_TAPE_DNE)

			if self.batch_tape_50.ID is None and self.page.leTape50.text() != "":
				issues.append(I_TAPE_50_DNE)
			else:
				objects.append(self.batch_tape_50)
				if not (self.batch_tape_50.date_expires is None or self.batch_tape_50.no_expiry == True):
					ydm =  self.batch_tape_50.date_expires.split('-')
					expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))   # ymd format for c     onstructor
					if QtCore.QDate.currentDate() > expires:
						issues.append(I_TAPE_50_EXPIRED)
				if self.batch_tape_50.is_empty:
					issues.append(I_TAPE_50_EMPTY)

			if self.batch_tape_120.ID is None:
				issues.append(I_TAPE_120_DNE)
			else:
				objects.append(self.batch_tape_120)
				if not (self.batch_tape_120.date_expires is None or self.batch_tape_120.no_expiry == True):
					ydm =  self.batch_tape_120.date_expires.split('-')
					expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))   # ymd format for c     onstructor
					if QtCore.QDate.currentDate() > expires:
						issues.append(I_TAPE_120_EXPIRED)
				if self.batch_tape_120.is_empty:
					issues.append(I_TAPE_120_EMPTY)

		#New
		#sb_tools and _baseplates are gone...but pcbs, protomodules, modules aren't.
		tray_assemblys_selected = [_.value() for _ in self.sb_tray_assemblys]
		pcb_tools_selected    = [_.value() for _ in self.sb_tools       ]
		pcbs_selected         = [_.text() for _ in self.le_pcbs         ]
		protomodules_selected = [_.text() for _ in self.le_protomodules ]
		modules_selected      = [_.text() for _ in self.le_modules      ]

		tray_assembly_duplicates = [_ for _ in range(6) if tray_assemblys_selected[_] >= 0 and tray_assemblys_selected.count(tray_assemblys_selected[_])>2]
		pcb_tool_duplicates    = [_ for _ in range(6) if pcb_tools_selected[_]    >= 0 and pcb_tools_selected.count(   pcb_tools_selected[_]   )>1]
		pcb_duplicates         = [_ for _ in range(6) if pcbs_selected[_]         != "" and pcbs_selected.count(        pcbs_selected[_]        )>1]
		protomodule_duplicates = [_ for _ in range(6) if protomodules_selected[_] != "" and protomodules_selected.count(protomodules_selected[_])>1]
		module_duplicates      = [_ for _ in range(6) if modules_selected[_]      != "" and modules_selected.count(     modules_selected[_]     )>1]

		if tray_assembly_duplicates:
			issues.append(I_TRAY_ASSEMBLY_DUPLICATE.format(', '.join([str(_+1) for _ in tray_assembly_duplicates])))
		if pcb_tool_duplicates:
			issues.append(I_TOOL_PCB_DUPLICATE.format(', '.join([str(_+1) for _ in pcb_tool_duplicates])))
		if pcb_duplicates:
			issues.append(I_PCB_DUPLICATE.format(', '.join(     [str(_+1) for _ in pcb_duplicates])))
		if protomodule_duplicates:
			issues.append(I_PROTO_DUPLICATE.format(', '.join(   [str(_+1) for _ in protomodule_duplicates])))
		if module_duplicates:
			issues.append(I_MODULE_DUPLICATE.format(', '.join(  [str(_+1) for _ in module_duplicates])))

		rows_empty           = []
		rows_full            = []
		rows_incomplete      = []

		rows_tray_assembly_dne = []
		rows_tool_dne        = []
		rows_pcb_dne         = []
		rows_protomodule_dne = []

		for i in range(6):
			num_parts = 0
			tmp_id = self.step_pcb.ID

			if pcb_tools_selected[i] >= 0:
				num_parts += 1
				objects.append(self.tools_pcb[i])
				if self.tools_pcb[i].ID is None:
					rows_tool_dne.append(i)

			if pcbs_selected[i] != "":
				num_parts += 1
				objects.append(self.pcbs[i])
				if self.pcbs[i].ID is None:
					rows_pcb_dne.append(i)
				else:
					ready, reason = self.pcbs[i].ready_step_pcb(tmp_id)
					if not ready:
						issues.append(I_PART_NOT_READY.format('hexaboard',i,reason))

			if protomodules_selected[i] != "":
				num_parts += 1
				objects.append(self.protomodules[i])
				if self.protomodules[i].ID is None:
					rows_protomodule_dne.append(i)
				else:
					ready, reason = self.protomodules[i].ready_step_pcb(tmp_id)
					if not ready:
						issues.append(I_PART_NOT_READY.format('protomodule',i,reason))

			if modules_selected[i] != "":
				# make sure module DNE, AND is not already part of this step
				tmp_mod = parts.module()
				if tmp_mod.load(modules_selected[i]) and tmp_mod.step_pcb != self.step_pcb.ID:
					issues.append(I_MOD_EXISTS.format(modules_selected[i]))
				tmp_mod.clear()
				num_parts += 1

			# NOTE:  TODO:  geometry, channel_density must match
			if pcbs_selected[i] != "" and protomodules_selected[i] != "" \
			        and not self.pcbs[i].ID is None and not self.protomodules[i].ID is None:
				# Check for compatibility bw two objects:
				if self.pcbs[i].geometry != self.protomodules[i].geometry:
					issues.append(I_PCB_PROTOMODULE_SHAPE.format(self.pcbs[i].ID, self.pcbs[i].geometry, \
                                                                  self.protomodules[i].ID, self.protomodules[i].geometry))
				if self.pcbs[i].channel_density != self.protomodules[i].channel_density:
					issues.append(I_PCB_PROTOMODULE_CHANNEL.format(self.pcbs[i].ID, self.pcbs[i].channel_density, \
                                                                    self.protomodules[i].ID, self.protomodules[i].channel_density))

			# note: only count toward filled row if the rest of the row is nonempty
			# ...unless both rows are empty, in which case throw error
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
			elif num_parts == 5:
				rows_full.append(i)
			else:
				rows_incomplete.append(i)


		if not (len(rows_full) or len(rows_incomplete)):
			issues.append(I_NO_PARTS_SELECTED)
		if rows_incomplete:
			issues.append(I_ROWS_INCOMPLETE.format(', '.join(map(str,rows_incomplete))))
		if rows_tray_assembly_dne:
			issues.append(I_TRAY_ASSEMBLY_DNE.format(', '.join([str(_+1) for _ in rows_tray_assembly_dne])))
		if rows_pcb_dne:
			issues.append(I_PCB_DNE.format(        ', '.join([str(_+1) for _ in rows_pcb_dne])))
		if rows_protomodule_dne:
			issues.append(I_PROTO_DNE.format(      ', '.join([str(_+1) for _ in rows_protomodule_dne])))
		if not self.page.ckCheckFeet.isChecked():
			issues.append(I_NO_TOOL_CHK)

		# NEW: Check for parent (only when creating)
		if mode_create:
			for i in range (6):
				if pcbs_selected[i] != "":
					temp_pcb = parts.pcb()
					if not temp_pcb.load_remote(pcbs_selected[i]):
						temp_pcb.load(pcbs_selected[i])
					if temp_pcb.ID != None and temp_pcb.module != None:
						issues.append(I_PCB_ON_MODULE.format(temp_pcb.ID, i, temp_pcb.module))
				if protomodules_selected[i] != "":
					temp_protomodule = parts.protomodule()
					if not temp_protomodule.load_remote(protomodules_selected[i]):
						temp_protomodule.load(protomodules_selected[i])
					if temp_protomodule.ID != None and temp_protomodule.module != None:
						issues.append(I_PROTO_ON_MODULE.format(temp_protomodule.ID, i, temp_protomodule.module))
			# NEW: Check if module already exists
			for i in range(6):
				if self.le_modules[i].text() != "":
					temp_module = parts.module()
					if not temp_module.load_remote(self.le_modules[i].text()):
						temp_module.load(self.le_modules[i].text())
					if temp_module.ID != None:
						issues.append(I_PROTO_NAME_EXISTS.format(self.le_modules[i].text(), i))

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

	# @enforce_mode('view')
	def loadSensorStep(self,*args,**kwargs):
		if self.page.sbSensorStep.value() == -1:  return
		if self.page.cbInstitution.currentText() == "":  return
		tmp_step = assembly.step_sensor()
		tmp_ID = self.page.sbSensorStep.value()
		tmp_inst = self.page.cbInstitution.currentText()
		tmp_exists = tmp_step.load("{}_{}".format(tmp_inst, tmp_ID))
		if not tmp_exists:
			self.update_info()
			print("Sensor step {} does not exist".format(tmp_ID))
		else:
			if not (tmp_step.protomodules is None):
				for i in range(6):
					self.le_protomodules[i].setText(str(tmp_step.protomodules[i]) if not (tmp_step.protomodules[i] is None) else "")
					if not (tmp_step.asmbl_tray_nums[i] is None):
						self.sb_tray_assemblys[i].setValue(tmp_step.asmbl_tray_nums[i])
					# self.sb_tray_assemblys[i].setValue(tmp_step.asmbl_tray_nums[i] if not (tmp_step.asmbl_tray_nums[i] is None) else -1)
			self.update_info()
			print("Sensor step {} loaded".format(tmp_ID))

	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		# NEW:  Search for all steps at this institution, then create the next in order
		if self.page.cbInstitution.currentText() == "":  return
		part_file_name = os.sep.join([ fm.DATADIR, 'partlist', 'step_pcbs.json' ])
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

		tmp_step = assembly.step_pcb()
		tmp_exists = tmp_step.load("{}_{}".format(tmp_inst, tmp_ID))
		if not tmp_exists:
			self.step_pcb.new("{}_{}".format(tmp_inst, tmp_ID))
			self.mode = 'creating'
			self.updateElements()
			self.setMaxSensorStep()

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
			self.setMaxSensorStep()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.unloadAllObjects()
		if self.mode == 'creating':  self.step_pcb.clear()
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):
		trays        = []
		tools        = []
		pcbs         = []
		protomodules = []
		modules      = []
		for i in range(6):
			trays.append(     self.sb_tray_assemblys[i].value() if self.sb_tray_assemblys[i].value() >= 0 else None)
			tools.append(       self.sb_tools[i].value()        if self.sb_tools[i].value()        >= 0 else None)
			pcbs.append(        self.le_pcbs[i].text()         if self.le_pcbs[i].text()         != "" else None)
			protomodules.append(self.le_protomodules[i].text() if self.le_protomodules[i].text() != "" else None)
			# modules.append(     self.le_modules[i].text()      if self.le_modules[i].text()      != "" else None)
			# Auto generate module name from protomodule
			if self.le_modules[i].text() != "":
				modules.append(self.le_modules[i].text())
			else:
				modules.append(None)
	
		self.step_pcb.pcbs         = pcbs
		self.step_pcb.protomodules = protomodules
		self.step_pcb.modules      = modules


		for i in range(6):
			if pcbs[i] is None:
				# Row is empty, continue
				continue
			temp_pcb = self.pcbs[i]
			temp_proto = self.protomodules[i]
			temp_baseplate = self.baseplates[i]
			temp_sensor = self.sensors[i]
			temp_module = parts.module()
			# Check for existence
			if not temp_module.load(modules[i]):
				temp_module.new(modules[i], pcb_=temp_pcb, protomodule_=temp_proto)
			temp_module.baseplate = self.protomodules[i].baseplate
			temp_module.sensor = self.protomodules[i].sensor
			temp_module.step_sensor = self.protomodules[i].step_sensor
			temp_module.step_pcb = self.step_pcb.ID
			temp_module.manufacturer = self.page.cbInstitution.currentText()
			temp_module.save()

			self.pcbs[i].step_pcb = self.step_pcb.ID
			self.pcbs[i].module = temp_module.ID
			self.pcbs[i].save()
			self.protomodules[i].step_pcb = self.step_pcb.ID
			self.protomodules[i].module = temp_module.ID
			self.protomodules[i].save()

			temp_baseplate.load(temp_proto.baseplate)
			temp_sensor.load(temp_proto.sensor)
			temp_baseplate.module = temp_module.ID
			temp_sensor.module = temp_module.ID
			temp_baseplate.save()
			temp_sensor.save()

		self.step_pcb.record_insertion_user = str(self.page.cbUserPerformed.currentText()) \
			if self.page.cbUserPerformed.currentText()!='' else None
		# Save all times as UTC	
		pydt = self.page.dtRunStart.dateTime().toPyDateTime().astimezone(datetime.timezone.utc)
		self.step_pcb.run_begin_timestamp = str(pydt) # sec UTC
		pydt = self.page.dtRunStop.dateTime().toPyDateTime().astimezone(datetime.timezone.utc)
		self.step_pcb.run_end_timestamp   = str(pydt)

		inst = self.page.cbInstitution.currentText()
		self.step_pcb.glue_batch_num = self.page.leBatchAraldite.text() \
			if self.page.leBatchAraldite.text() else None
		self.step_pcb.batch_tape_50 = self.page.leTape50.text() \
			if self.page.leTape50.text() != "" else None
		self.step_pcb.batch_tape_120 = self.page.leTape120.text() \
			if self.page.leTape120.text() != "" else None
		#self.step_pcb.asmbl_tray_name = "{}_{}".format(inst, self.page.sbTrayAssembly.value()) \
		#	if self.page.sbTrayAssembly.value() >= 0 else None
		self.step_pcb.comp_tray_name = "{}_{}".format(inst, self.page.sbTrayComponent.value()) \
			if self.page.sbTrayComponent.value() >= 0 else None

		self.step_pcb.asmbl_tray_names = [None if trays[i] is None else "{}_{}".format(inst, trays[i]) for i in range(6)]
		self.step_pcb.pcb_tool_names = [None if tools[i] is None else "{}_{}".format(inst, tools[i]) for i in range(6)]
		self.step_pcb.pcb_tool_feet_chk = self.page.ckCheckFeet.isChecked()

		self.step_pcb.save()
		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()

	def isRowClear(self, row):
		return (self.sb_tools[row].value() == -1 or self.sb_tools[row].value() is None) \
		  and self.le_pcbs[row].text() == "" \
		  and self.le_protomodules[row].text() == ""

	def clearRow(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		print("Clearing row {}".format(which))
		self.sb_tools[which].setValue(-1)
		self.sb_tools[which].clear()
		self.le_pcbs[which].clear()
		self.le_protomodules[which].clear()
		self.le_modules[which].clear()
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
			if self.search_part == 'pcb':
				# Search for one thing:  NOT already assigned to a mod
				tmp_part.load(part_id)  # db query already done
				if tmp_part.module is None:
					self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))
				#self.loadPcb()
			elif self.search_part == 'protomodule':
				tmp_part.load(part_id)  # db query already done
				if tmp_part.module is None:
					self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))
			elif self.search_part == 'batch_araldite':  # araldite, no restrictions
				self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))
			elif self.search_part == 'batch_tape_50':
				self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))
			elif self.search_part == 'batch_tape_120':
				self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))
			#else:
			#	self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))

		# NEW: Search remote parts in central DB (only for pcbs and protomodules)
		if self.search_part in ['pcb', 'protomodule']:
			partlistdir_remote = os.sep.join([fm.DATADIR, 'partlist_remote'])
			obj_list_remote = os.sep.join([partlistdir_remote, self.search_part+'s.json'])

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
		if self.search_part in ['pcb', 'protomodule']:
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
		self.setUIPage('Tooling',tool_pcb=tool,institution=self.page.cbInstitution.currentText())

	def goPcb(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		pcb = self.le_pcbs[which].text()
		if pcb != "":
			self.setUIPage('Hexaboards',ID=pcb)
		else:
			self.mode = 'searching'
			self.search_part = 'pcb'
			self.search_row = which
			self.doSearch()

	def goProtomodule(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		protomodule = self.le_protomodules[which].text()
		if protomodule != "":
			self.setUIPage('Protomodules',ID=protomodule)
		else:
			self.mode = 'searching'
			self.search_part = 'protomodule'
			self.search_row = which
			self.doSearch()

	def goModule(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		module = self.le_modules[which].text()
		self.setUIPage('Modules',ID=module)

	def goBatchAraldite(self,*args,**kwargs):
		#batch_araldite = self.page.sbBatchAraldite.value()
		batch_araldite = self.page.leBatchAraldite.text()
		if batch_araldite != "":
			self.setUIPage('Supplies',batch_araldite=batch_araldite)
		else:
			self.mode = "searching"
			self.search_part = 'batch_araldite'
			self.search_row = None
			self.doSearch()

	def goTrayComponent(self,*args,**kwargs):
		tray_component_pcb = self.page.sbTrayComponent.value()
		self.setUIPage('Tooling',tray_component_pcb=tray_component_pcb)

	def goTrayAssembly(self,*args,**kwargs):
		#tray_assembly = self.page.sbTrayAssembly.value()
		#self.setUIPage('Tooling',tray_assembly=tray_assembly)
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

	def setMaxSensorStep(self,*args,**kwargs):
		# NEW:  Search for all sensor steps at this institution, then set the max value
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
			tmp_ID = max(ids)
		else:
			tmp_ID = 0
		self.page.leMaxSensorStep.setText(str(tmp_ID))
		self.page.sbSensorStep.setMaximum(tmp_ID)
		self.page.sbSensorStep.setValue(tmp_ID)

	def update_moduleID(self,*args,**kwargs):
		# update module name from protomodule name
		for i in range(6):
			if self.le_protomodules[i].text() != "" and is_proper_name(self.le_protomodules[i].text()):
				self.le_modules[i].setText("M"+self.le_protomodules[i].text()[1:])
			else:
				self.le_modules[i].setText("")
		self.updateIssues()