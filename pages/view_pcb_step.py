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
I_PART_NOT_READY    = "{}(s) in position(s) {} is not ready for pcb application. reason: {}"
I_PCB_PROTOMODULE_SHAPE = "pcb {} has shape {} but protomodule {} has shape {}"
I_PCB_PROTOMODULE_CHANNEL = "pcb {} has channel density {} but protomodule {} has channel density {}"
I_MOD_EXISTS = "module {} already exists!"

# rows / positions
I_NO_PARTS_SELECTED     = "no parts have been selected"
I_ROWS_INCOMPLETE       = "positions {} are partially filled"
I_TRAY_ASSEMBLY_DNE     = "assembly tray(s) in position(s) {} do not exist"
I_TOOL_SENSOR_DNE       = "sensor tool(s) in position(s) {} do not exist"
I_BASEPLATE_DNE         = "baseplate(s) in position(s) {} do not exist"
I_SENSOR_DNE            = "sensor(s) in position(s) {} do not exist"
I_PCB_DNE               = "pcb(s) in position(s) {} do not exist"
I_PROTO_DNE             = "protomodule(s) in position(s) {} do not exist"
I_TRAY_ASSEMBLY_DUPLICATE = "same assembly tray is selected on multiple positions: {}"
I_TOOL_PCB_DUPLICATE    = "same PCB tool is selected on multiple positions: {}"
I_BASEPLATE_DUPLICATE   = "same baseplate is selected on multiple positions: {}"
I_SENSOR_DUPLICATE      = "same sensor is selected on multiple positions: {}"
I_PCB_DUPLICATE         = "same PCB is selected on multiple positions: {}"
I_PROTO_DUPLICATE       = "same protomodule is selected on multiple positions: {}"
I_LONE_TRAY             = "assembly tray entered, but rows {} and {} are empty"

# compatibility
I_SIZE_MISMATCH   = "size mismatch between some selected objects"
I_SIZE_MISMATCH_8 = "* list of 8-inch objects selected: {}"

# institution
I_INSTITUTION = "some selected objects are not at this institution: {}"

# Missing user
I_USER_DNE = "no pcb step user selected"

# supply batch empty
I_BATCH_ARALDITE_EMPTY = "araldite batch is empty"
I_TAPE_50_EMPTY = "50um tape batch is empty"
I_TAPE_120_EMPTY = "120um tape batch is empty"

# NEW
I_INSTITUTION_NOT_SELECTED = "no institution selected"

I_NO_TOOL_CHK = "pickup tool feet have not been checked"


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
					dt.setDate(QtCore.QDate(*NO_DATE))
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
			elif self.step_pcb.glue_batch_num != None:
				self.page.cbAdhesive.setCurrentIndex(0)
				self.page.leBatchAraldite.setText(self.step_pcb.glue_batch_num)
				self.page.leTape50.setText("")
				self.page.leTape120.setText("")
			else:
				self.page.cbAdhesive.setCurrentIndex(1)
				self.page.leBatchAraldite.setText("")
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
			self.page.dtRunStart.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtRunStart.setTime(QtCore.QTime(0,0,0))
			self.page.dtRunStop.setDate(QtCore.QDate(*NO_DATE))
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

		self.page.leBatchAraldite  .setReadOnly(mode_view or mode_searching)
		self.page.leTextAraldite.setEnabled(not (mode_view or mode_searching or adhesive!="Araldite"))
		self.page.leTape50      .setEnabled(not (mode_view or mode_searching or adhesive!="Tape"))
		self.page.leTextTape50  .setEnabled(not (mode_view or mode_searching or adhesive!="Tape"))
		self.page.leTape120     .setEnabled(not (mode_view or mode_searching or adhesive!="Tape"))
		self.page.leTextTape120 .setEnabled(not (mode_view or mode_searching or adhesive!="Tape"))

		self.page.pbGoTrayComponent.setEnabled(mode_view and self.page.sbTrayComponent.value() >= 0)
		#self.page.pbGoTrayAssembly .setEnabled(mode_view and self.page.sbTrayAssembly .value() >= 0)
		self.page.pbGoBatchAraldite.setEnabled((mode_creating or (mode_view and self.page.leBatchAraldite.text() != "")) and adhesive == "Araldite")
		self.page.pbGoTape50.setEnabled((mode_creating or (mode_view and self.page.leTape50.text() != "")) and adhesive == "Tape")
		self.page.pbGoTape120.setEnabled((mode_creating or (mode_view and self.page.leTape120.text() != "")) and adhesive == "Tape")

		for i in range(6):
			self.sb_tray_assemblys[i].setReadOnly(mode_view)
			self.sb_tools[i].setReadOnly(       mode_view)
			self.le_pcbs[i].setReadOnly(        mode_view)
			self.le_protomodules[i].setReadOnly(mode_view)
			self.le_modules[i].setReadOnly(     mode_view)
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


	@enforce_mode(['editing','creating'])
	def loadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tray_assemblys[i].load(self.sb_tray_assemblys[i].value(), self.page.cbInstitution.currentText())
			self.tools_pcb[i].load(self.sb_tools[i].value(),       self.page.cbInstitution.currentText())
			self.pcbs[i].load(        self.le_pcbs[i].text()        )
			self.protomodules[i].load(self.le_protomodules[i].text())
			self.modules[i].load(     self.le_modules[i].text()     )

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

	@enforce_mode(['editing','creating'])
	def loadBaseplate(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.baseplates[which].load(self.le_baseplates[which].text())
		self.updateIssues()

	@enforce_mode(['editing','creating', 'searching'])
	def loadPcb(self, *args, **kwargs):
		if 'row' in kwargs.keys():
			which = kwargs['row']
		else:
			sender_name = str(self.page.sender().objectName())
			which = int(sender_name[-1]) - 1
		self.pcbs[which].load(self.le_pcbs[which].text())
		self.updateIssues()

	#New
	@enforce_mode(['editing','creating', 'searching'])
	def loadProtomodule(self, *args, **kwargs):
		if 'row' in kwargs.keys():
			which = kwargs['row']
		else:
			sender_name = str(self.page.sender().objectName())
			which = int(sender_name[-1]) - 1
		self.protomodules[which].load(self.le_protomodules[which].text())
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
		else:  # Araldite
			self.page.leTape50.clear()
			self.page.leTape120.clear()
		self.updateElements()
		self.updateIssues()

	#NEW:  Add updateIssues and modify conditions accordingly
	@enforce_mode(['editing', 'creating'])
	def updateIssues(self,*args,**kwargs):
		issues = []
		objects = []

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
				if not (self.batch_tape_50.date_expires is None):
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
				if not (self.batch_tape_120.date_expires is None):
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
						issues.append(I_PART_NOT_READY.format('pcb',i,reason))

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
					issues.append(I_PCB_PROTOMODULE_CHANNEL.format(self.pcbs[i].ID, self.protomodules[i].channel_density, \
                                                                    self.pcbs[i].ID, self.protomodules[i].channel_density))

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
			modules.append(     self.le_modules[i].text()      if self.le_modules[i].text()      != "" else None)
	
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
		self.sb_tools[which].setValue(-1)
		self.sb_tools[which].clear()
		self.le_pcbs[which].clear()
		self.le_protomodules[which].clear()
		# clear tray assembly only if current and neighboring rows are clear
		uprow   = which if which%2==0 else which-1
		downrow = which if which%2!=0 else which+1
		#print("Rows {}, {} are clear: {}, {}".format(uprow, downrow, self.isRowClear(uprow), self.isRowClear(downrow)))
		if self.isRowClear(uprow) and self.isRowClear(downrow):
			self.sb_tray_assemblys[which].setValue(-1)
			self.sb_tray_assemblys[which].clear()
		self.update_info()

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
			self.setUIPage('PCBs',ID=pcb)
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
