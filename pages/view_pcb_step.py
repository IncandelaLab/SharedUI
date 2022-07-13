from PyQt5 import QtCore
import time
import datetime
import os
import json

from filemanager import fm

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
}

STATUS_NO_ISSUES = "valid (no issues)"
STATUS_ISSUES    = "invalid (issues present)"

# tooling and supplies
I_TRAY_COMPONENT_DNE = "sensor component tray does not exist or is not selected"
I_TRAY_ASSEMBLY_DNE  = "assembly tray does not exist or is not selected"
I_BATCH_ARALDITE_DNE     = "araldite batch does not exist or is not selected"
I_BATCH_ARALDITE_EXPIRED = "araldite batch has expired"

# parts
I_PART_NOT_READY    = "{}(s) in position(s) {} is not ready for pcb application. reason: {}"

# rows / positions
I_NO_PARTS_SELECTED     = "no parts have been selected"
I_ROWS_INCOMPLETE       = "positions {} are partially filled"
I_TOOL_SENSOR_DNE       = "sensor tool(s) in position(s) {} do not exist"
I_BASEPLATE_DNE         = "baseplate(s) in position(s) {} do not exist"
I_SENSOR_DNE            = "sensor(s) in position(s) {} do not exist"
I_PCB_DNE               = "pcb(s) in position(s) {} do not exist"
I_PROTO_DNE             = "protomodule(s) in position(s) {} do not exist"
I_TOOL_PCB_DUPLICATE    = "same PCB tool is selected on multiple positions: {}"
I_BASEPLATE_DUPLICATE   = "same baseplate is selected on multiple positions: {}"
I_SENSOR_DUPLICATE      = "same sensor is selected on multiple positions: {}"
I_PCB_DUPLICATE         = "same PCB is selected on multiple positions: {}"
I_PROTO_DUPLICATE       = "same protomodule is selected on multiple positions: {}"

# compatibility
I_SIZE_MISMATCH   = "size mismatch between some selected objects"
I_SIZE_MISMATCH_8 = "* list of 8-inch objects selected: {}"

# institution
I_INSTITUTION = "some selected objects are not at this institution: {}"

# Missing user
I_USER_DNE = "no pcb step user selected"

# supply batch empty
I_BATCH_ARALDITE_EMPTY = "araldite batch is empty"

# NEW
I_INSTITUTION_NOT_SELECTED = "no institution selected"

I_NO_TOOL_CHK = "pickup tool feet have not been checked"


class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		#New stuff
		self.tools_pcb    = [fm.tool_pcb()    for _ in range(6)]
		self.pcbs         = [fm.pcb()         for _ in range(6)]
		self.protomodules = [fm.protomodule() for _ in range(6)]
		self.modules      = [fm.module()      for _ in range(6)]
		self.tray_component_pcb = fm.tray_component_pcb()
		self.tray_assembly      = fm.tray_assembly()
		self.batch_araldite     = fm.batch_araldite()

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

		for i in range(6):
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

		self.page.sbTrayComponent.editingFinished.connect( self.loadTrayComponentPCB )
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
			self.page.sbID.setValue(tmp_id)
			self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))

		self.step_pcb_exists = False
		if getattr(self.step_pcb, 'ID', None) != None:
			self.step_pcb_exists = (ID == self.step_pcb.ID)

		self.page.listIssues.clear()
		self.page.leStatus.clear()

		if self.step_pcb_exists:

			if not self.step_pcb.user_performed in self.index_users.keys() and not self.step_pcb.user_performed is None:
				# Insertion user was deleted from user page...just add user to the dropdown
				self.index_users[self.step_pcb.user_performed] = max(self.index_users.values()) + 1
				self.page.cbUserPerformed.addItem(self.step_pcb.user_performed)
			self.page.cbUserPerformed.setCurrentIndex(self.index_users.get(self.step_pcb.user_performed, -1))
			self.page.leLocation.setText(self.step_pcb.location)

			times_to_set = [(self.step_pcb.run_start,  self.page.dtRunStart),
			                (self.step_pcb.run_stop,   self.page.dtRunStop)]
			for st, dt in times_to_set:
				if st is None:
					dt.setDate(QtCore.QDate(*NO_DATE))
					dt.setTime(QtCore.QTime(0,0,0))
				else:
					localtime = list(time.localtime(st))
					dt.setDate(QtCore.QDate(*localtime[0:3]))
					dt.setTime(QtCore.QTime(*localtime[3:6]))


			self.page.leBatchAraldite.setText(self.step_pcb.batch_araldite if not (self.step_pcb.batch_araldite is None) else -1)
			self.page.sbTrayAssembly.setValue( self.step_pcb.tray_assembly  if not (self.step_pcb.tray_assembly  is None) else -1)
			self.page.sbTrayComponent.setValue(self.step_pcb.tray_component_pcb if not (self.step_pcb.tray_component_pcb is None) else -1)

			if not (self.step_pcb.tools is None):
				for i in range(6):
					self.sb_tools[i].setValue(self.step_pcb.tools[i] if not (self.step_pcb.tools[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_tools[i].setValue(-1)

			if not (self.step_pcb.pcbs is None):
				print("self.pcbs:", self.step_pcb.pcbs)
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

			self.page.ckCheckFeet.setChecked(self.step_pcb.check_tool_feet if not (self.step_pcb.check_tool_feet is None) else False)

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
				self.le_pcbs[i].setText("")
				self.le_protomodules[i].setText("")
				self.le_modules[i].setText("")
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
		pcbs_exist         = [_.text()!="" for _ in self.le_pcbs        ]
		protomodules_exist = [_.text()!="" for _ in self.le_protomodules]
		modules_exist      = [_.text()!="" for _ in self.le_modules     ]
		step_pcb_exists    = self.step_pcb_exists

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbID.setEnabled(mode_view)
		self.page.cbInstitution.setEnabled(mode_view)  # mode_creating or mode_editing)

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
			self.sb_tools[i].setReadOnly(       mode_view)
			self.le_pcbs[i].setReadOnly(        mode_view)
			self.le_protomodules[i].setReadOnly(mode_view)
			self.le_modules[i].setReadOnly(     mode_view)
			self.pb_go_tools[i].setEnabled(       mode_view and tools_exist[i]       )
			self.pb_go_pcbs[i].setEnabled(        mode_creating or (mode_view and self.le_pcbs[i].text()            != "") )
			self.pb_go_protomodules[i].setEnabled(mode_creating or (mode_view and self.le_protomodules[i].text()    != "") )
			self.pb_go_modules[i].setEnabled(     mode_view and modules_exist[i]     )
			self.pb_clears[i].setEnabled(mode_creating or mode_editing)

		self.page.pbNew.setEnabled(    mode_view and not step_pcb_exists )
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


	#NEW:  Add all load() functions

	@enforce_mode(['editing','creating'])
	def loadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tools_pcb[i].load(self.sb_tools[i].value(),       self.page.cbInstitution.currentText())
			self.pcbs[i].load(        self.le_pcbs[i].text()        )
			self.protomodules[i].load(self.le_protomodules[i].text())
			self.modules[i].load(     self.le_modules[i].text()     )

		self.tray_component_pcb.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.batch_araldite.load(       self.page.leBatchAraldite.text())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadAllTools(self,*args,**kwargs):  # Same as above, but load only tools:
		self.step_pcb.institution = self.page.cbInstitution.currentText()
		for i in range(6):
			self.tools_pcb[i].load(self.sb_tools[i].value(),       self.page.cbInstitution.currentText())
		self.tray_component_pcb.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.batch_araldite.load(       self.page.leBatchAraldite.text())
		self.updateIssues()


	@enforce_mode(['editing','creating'])
	def unloadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tools_pcb[i].clear()
			self.pcbs[i].clear()
			self.protomodules[i].clear()
			self.modules[i].clear()

		self.tray_component_pcb.clear()
		self.tray_assembly.clear()
		self.batch_araldite.clear()

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
		self.baseplates[which].load(self.le_baseplates[which].text(), query_db=False)
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadPcb(self, *args, **kwargs):
		if 'row' in kwargs.keys():
			which = kwargs['row']
		else:
			sender_name = str(self.page.sender().objectName())
			which = int(sender_name[-1]) - 1
		self.pcbs[which].load(self.le_pcbs[which].text(), query_db=False)
		self.updateIssues()

	#New
	@enforce_mode(['editing','creating'])
	def loadProtomodule(self, *args, **kwargs):
		if 'row' in kwargs.keys():
			which = kwargs['row']
		else:
			sender_name = str(self.page.sender().objectName())
			which = int(sender_name[-1]) - 1
		self.protomodules[which].load(self.le_protomodules[which].text(), query_db=False)
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadModule(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.modules[which].load(self.le_modules[which].text(), query_db=False)
		self.updateIssues()


	@enforce_mode(['editing','creating'])
	def loadTrayComponentPCB(self, *args, **kwargs):
		self.tray_component_pcb.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
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
		if self.tray_component_pcb.ID is None:
			issues.append(I_TRAY_COMPONENT_DNE)
		else:
			objects.append(self.tray_component_pcb)

		if self.tray_assembly.ID is None:
			issues.append(I_TRAY_ASSEMBLY_DNE)
		else:
			objects.append(self.tray_assembly)

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
		#sb_tools and _baseplates are gone...but pcbs, protomodules, modules aren't.
		pcb_tools_selected    = [_.value() for _ in self.sb_tools       ]
		pcbs_selected         = [_.text() for _ in self.le_pcbs         ]
		protomodules_selected = [_.text() for _ in self.le_protomodules ]
		modules_selected      = [_.text() for _ in self.le_modules      ]

		pcb_tool_duplicates    = [_ for _ in range(6) if pcb_tools_selected[_]    >= 0 and pcb_tools_selected.count(   pcb_tools_selected[_]   )>1]
		pcb_duplicates         = [_ for _ in range(6) if pcbs_selected[_]         != "" and pcbs_selected.count(        pcbs_selected[_]        )>1]
		protomodule_duplicates = [_ for _ in range(6) if protomodules_selected[_] != "" and protomodules_selected.count(protomodules_selected[_])>1]
		module_duplicates      = [_ for _ in range(6) if modules_selected[_]      != "" and modules_selected.count(     modules_selected[_]     )>1]

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

		rows_tool_dne        = []
		rows_pcb_dne         = []
		rows_protomodule_dne = []

		for i in range(6):
			num_parts = 0
			tmp_id = "{}_{}".format(self.page.cbInstitution.currentText(), self.page.sbID.value())

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
				num_parts += 1

			print("NUM PARTS IS", num_parts)
			if num_parts == 0:
				rows_empty.append(i)
			elif num_parts == 4:
				rows_full.append(i)
			else:
				rows_incomplete.append(i)

		if not (len(rows_full) or len(rows_incomplete)):
			issues.append(I_NO_PARTS_SELECTED)

		if rows_incomplete:
			issues.append(I_ROWS_INCOMPLETE.format(', '.join(map(str,rows_incomplete))))


		if rows_pcb_dne:
			issues.append(I_PCB_DNE.format(        ', '.join([str(_+1) for _ in rows_pcb_dne])))
		if rows_protomodule_dne:
			issues.append(I_PROTO_DNE.format(      ', '.join([str(_+1) for _ in rows_protomodule_dne])))

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
		tmp_step = fm.step_pcb()
		tmp_ID = self.page.sbID.value()
		tmp_inst = self.page.cbInstitution.currentText()
		tmp_exists = tmp_step.load("{}_{}".format(tmp_inst, tmp_ID))
		if not tmp_exists:
			print("STEP NOW FOUND")
			self.update_info()
		else:
			print("STEP FOUND")
			self.step_pcb = tmp_step
			self.update_info()

	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if self.page.sbID.value() == -1:  return
		if self.page.cbInstitution.currentText() == "":  return
		tmp_step = fm.step_pcb()
		tmp_ID = self.page.sbID.value()
		tmp_inst = self.page.cbInstitution.currentText()
		tmp_exists = tmp_step.load("{}_{}".format(tmp_inst, tmp_ID))
		if not tmp_exists:
			ID = self.page.sbID.value()
			self.step_pcb.new("{}_{}".format(tmp_inst, tmp_ID))
			self.mode = 'creating'
			self.updateElements()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_step = fm.step_pcb()
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
		print("SAVING PCB STEP")
		self.step_pcb.institution = self.page.cbInstitution.currentText()

		self.step_pcb.user_performed = str(self.page.cbUserPerformed.currentText()) if str(self.page.cbUserPerformed.currentText()) else None
		self.step_pcb.location = str( self.page.leLocation.text() )

		self.step_pcb.run_start  = self.page.dtRunStart.dateTime().toTime_t()
		self.step_pcb.run_stop   = self.page.dtRunStop.dateTime().toTime_t()

		tools        = []
		pcbs         = []
		protomodules = []
		modules      = []
		for i in range(6):
			tools.append(       self.sb_tools[i].value()        if self.sb_tools[i].value()        >= 0 else None)
			pcbs.append(        self.le_pcbs[i].text()         if self.le_pcbs[i].text()         != "" else None)
			protomodules.append(self.le_protomodules[i].text() if self.le_protomodules[i].text() != "" else None)
			modules.append(     self.le_modules[i].text()      if self.le_modules[i].text()      != "" else None)
	
		self.step_pcb.tools        = tools
		self.step_pcb.pcbs         = pcbs
		self.step_pcb.protomodules = protomodules
		self.step_pcb.modules      = modules

		self.step_pcb.tray_component_pcb    = self.page.sbTrayComponent.value() if self.page.sbTrayComponent.value() >= 0 else None
		self.step_pcb.tray_assembly         = self.page.sbTrayAssembly.value()  if self.page.sbTrayAssembly.value()  >= 0 else None
		self.step_pcb.batch_araldite        = self.page.leBatchAraldite.text() if self.page.leBatchAraldite.text() != "" else None


		for i in range(6):
			if modules[i] is None:
				# Row is empty, continue
				continue
			temp_module = fm.module()
			module_exists = temp_module.load(protomodules[i])
			if not modules[i] is None:
				temp_module.new(modules[i])
				temp_module.new(modules[i])
				# Pull data from current step, PCB, protomodule:
				temp_module.institution    = self.step_pcb.institution
				temp_module.location       = self.step_pcb.location
				temp_module.insertion_user = self.step_pcb.user_performed
				temp_module.thickness      = self.protomodules[i].thickness + self.pcbs[i].thickness + 0.1
				temp_module.channels       = self.protomodules[i].channels
				temp_module.size           = self.protomodules[i].size
				temp_module.shape          = self.protomodules[i].shape
				temp_module.grade          = self.protomodules[i].grade

				temp_module.baseplate      = self.protomodules[i].baseplate
				temp_module.sensor         = self.protomodules[i].sensor
				temp_module.protomodule    = self.protomodules[i].ID
				temp_module.pcb            = self.pcbs[i].ID
				temp_module.step_sensor    = self.protomodules[i].step_sensor
				temp_module.step_pcb       = self.step_pcb.ID

				temp_module.save()

			self.pcbs[i].step_pcb = self.step_pcb.ID
			self.pcbs[i].module = modules[i]
			self.pcbs[i].save()
			self.protomodules[i].step_pcb = self.step_pcb.ID
			self.protomodules[i].module = modules[i]
			self.protomodules[i].save()

		self.step_pcb.check_tool_feet = self.page.ckCheckFeet.isChecked()

		print("SAVING STEP PCB OBJECT")
		self.step_pcb.save()
		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()


	def clearRow(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.sb_tools[which].clear()
		self.le_pcbs[which].clear()
		self.le_protomodules[which].clear()
		self.update_info()

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
			# Search for one thing:  NOT already assigned to a mod
			tmp_part.load(part_id, query_db=False)  # db query already done
			if tmp_part.module is None:
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
		print("SEARCH FINISHED, mode is", self.mode)

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
		self.setUIPage('Tooling',tool_pcb=tool)

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
		self.setUIPage('Supplies',batch_araldite=batch_araldite)

	def goTrayComponent(self,*args,**kwargs):
		tray_component_pcb = self.page.sbTrayComponent.value()
		self.setUIPage('Tooling',tray_component_pcb=tray_component_pcb)

	def goTrayAssembly(self,*args,**kwargs):
		tray_assembly = self.page.sbTrayAssembly.value()
		print(tray_assembly)
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
