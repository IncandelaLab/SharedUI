from PyQt5 import QtCore
import time
import datetime

from filemanager import fm

NO_DATE = [2000,1,1]

PAGE_NAME = "view_pcb_step"
OBJECTTYPE = "PCB_step"
DEBUG = False

INDEX_INSTITUTION = {
    'CERN':0,
    'FNAL':1,
    'UCSB':2,
    'UMN':3,
}

STATUS_NO_ISSUES = "valid (no issues)"
STATUS_ISSUES    = "invalid (issues present)"

# tooling and supplies
I_TRAY_COMPONENT_DNE = "sensor component tray does not exist or is not selected"
I_TRAY_ASSEMBLY_DNE  = "assembly tray does not exist or is not selected"
I_BATCH_ARALDITE_DNE     = "araldite batch does not exist or is not selected"
I_BATCH_ARALDITE_EXPIRED = "araldite batch has expired"
I_BATCH_LOCTITE_DNE      = "loctite batch does not exist or is not selected"
I_BATCH_LOCTITE_EXPIRED  = "loctite batch has expired"

# baseplates
I_BASEPLATE_NOT_READY    = "baseplate(s) in position(s) {} is not ready for sensor application. reason: {}"

# kapton inspection
#I_KAPTON_INSPECTION_NOT_DONE = "kapton inspection not done for position(s) {}"
#I_KAPTON_INSPECTION_ON_EMPTY = "kapton inspection checked for empty position(s) {}"

# rows / positions
I_NO_PARTS_SELECTED     = "no parts have been selected"
I_ROWS_INCOMPLETE       = "positions {} are partially filled"
I_TOOL_SENSOR_DNE       = "sensor tool(s) in position(s) {} do not exist"
I_BASEPLATE_DNE         = "baseplate(s) in position(s) {} do not exist"
I_SENSOR_DNE            = "sensor(s) in position(s) {} do not exist"
I_PCB_DNE               = "pcb(s) in position(s) {} do not exist"
I_PROTO_DNE             = "protomodule(s) in position(s) {} do not exist"
#I_MODULE_DNE            = "module(s) in position(s) {} do not exist"
I_TOOL_PCB_DUPLICATE    = "same PCB tool is selected on multiple positions: {}"
I_BASEPLATE_DUPLICATE   = "same baseplate is selected on multiple positions: {}"
I_SENSOR_DUPLICATE      = "same sensor is selected on multiple positions: {}"
I_PCB_DUPLICATE         = "same PCB is selected on multiple positions: {}"
I_PROTO_DUPLICATE       = "same protomodule is selected on multiple positions: {}"
I_MODULE_DUPLICATE      = "same module is selected on multiple positions: {}"

# compatibility
I_SIZE_MISMATCH   = "size mismatch between some selected objects"
I_SIZE_MISMATCH_6 = "* list of 6-inch objects selected: {}"
I_SIZE_MISMATCH_8 = "* list of 8-inch objects selected: {}"

# institution
I_INSTITUTION = "some selected objects are not at this institution: {}"

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
		self.tools_pcb    = [fm.tool_pcb()    for _ in range(6)]
		self.pcbs         = [fm.pcb()         for _ in range(6)]
		self.protomodules = [fm.protomodule() for _ in range(6)]
		self.modules      = [fm.module()      for _ in range(6)]
		#baseplates aren't used/considered
		#self.baseplates = [fm.baseplate() for _ in range(6)]
		self.tray_component_sensor = fm.tray_component_sensor()
		self.tray_assembly         = fm.tray_assembly()
		self.batch_araldite        = fm.batch_araldite()
		self.batch_loctite         = fm.batch_loctite()

		self.step_pcb = fm.step_pcb()
		self.step_pcb_exists = None

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

		self.sb_pcbs = [
			self.page.sbPcb1,
			self.page.sbPcb2,
			self.page.sbPcb3,
			self.page.sbPcb4,
			self.page.sbPcb5,
			self.page.sbPcb6,
		]
		self.pb_go_pcbs = [
			self.page.pbGoPcb1,
			self.page.pbGoPcb2,
			self.page.pbGoPcb3,
			self.page.pbGoPcb4,
			self.page.pbGoPcb5,
			self.page.pbGoPcb6,
		]

		self.sb_protomodules = [
			self.page.sbProtomodule1,
			self.page.sbProtomodule2,
			self.page.sbProtomodule3,
			self.page.sbProtomodule4,
			self.page.sbProtomodule5,
			self.page.sbProtomodule6,
		]
		self.pb_go_protomodules = [
			self.page.pbGoProtomodule1,
			self.page.pbGoProtomodule2,
			self.page.pbGoProtomodule3,
			self.page.pbGoProtomodule4,
			self.page.pbGoProtomodule5,
			self.page.pbGoProtomodule6,
		]

		self.sb_modules = [
			self.page.sbModule1,
			self.page.sbModule2,
			self.page.sbModule3,
			self.page.sbModule4,
			self.page.sbModule5,
			self.page.sbModule6,
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
			self.pb_go_tools[i].clicked.connect(       self.goTool       )
			self.pb_go_pcbs[i].clicked.connect(        self.goPcb        )
			self.pb_go_protomodules[i].clicked.connect(self.goProtomodule)
			self.pb_go_modules[i].clicked.connect(     self.goModule     )

			self.sb_tools[i].editingFinished.connect(       self.loadToolSensor )
			self.sb_pcbs[i].editingFinished.connect(        self.loadPcb        )
			self.sb_protomodules[i].editingFinished.connect(self.loadProtomodule)
			self.sb_modules[i].editingFinished.connect(     self.loadModule     )

		self.page.cbInstitution.currentIndexChanged.connect( self.loadAllTools )

		self.page.sbTrayComponent.editingFinished.connect( self.loadTrayComponentSensor )
		self.page.sbTrayAssembly.editingFinished.connect(  self.loadTrayAssembly        )
		self.page.sbBatchAraldite.editingFinished.connect( self.loadBatchAraldite       )
		#May or may not need to add this check box
		#self.page.sbBatchLoctite.editingFinished.connect(  self.loadBatchLoctite        )

		self.page.sbID.valueChanged.connect(self.update_info)

		self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoBatchAraldite.clicked.connect(self.goBatchAraldite)
		self.page.pbGoTrayAssembly.clicked.connect(self.goTrayAssembly)
		self.page.pbGoTrayComponent.clicked.connect(self.goTrayComponent)

		#self.page.pbDatePerformedNow.clicked.connect(self.setDatePerformedNow)
		self.page.pbRunStartNow     .clicked.connect(self.setRunStartNow)

	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbID.value()
		else:
			self.page.sbID.setValue(ID)

		self.step_pcb_exists = self.step_pcb.load(ID)

		if self.step_pcb_exists:
			self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.step_pcb.institution, -1))

			self.page.leUserPerformed.setText(self.step_pcb.user_performed)
			self.page.leLocation.setText(self.step_pcb.location)

			#date_performed = self.step_pcb.date_performed  #Now redundant
			#if not (date_performed is None):
			#	self.page.dPerformed.setDate(QtCore.QDate(*self.step_pcb.date_performed))
			#else:
			#	self.page.dPerformed.setDate(QtCore.QDate(*NO_DATE))

			run_start = self.step_pcb.run_start
			run_stop  = self.step_pcb.run_stop
			if run_start is None:
				self.page.dtRunStart.setDate(QtCore.QDate(*NO_DATE))
				self.page.dtRunStart.setTime(QtCore.QTime(0,0,0))
			else:
				localtime = list(time.localtime(run_start))
				self.page.dtRunStart.setDate(QtCore.QDate(*localtime[0:3]))
				self.page.dtRunStart.setTime(QtCore.QTime(*localtime[3:6]))

			self.page.leCureTemperature.setText(self.step_pcb.cure_temperature)
			self.page.leCureHumidity.setText(self.step_pcb.cure_humidity)

			self.page.sbBatchAraldite.setValue(self.step_pcb.batch_araldite if not (self.step_pcb.batch_araldite is None) else -1)
			self.page.sbTrayAssembly.setValue( self.step_pcb.tray_assembly  if not (self.step_pcb.tray_assembly  is None) else -1)
			self.page.sbTrayComponent.setValue(self.step_pcb.tray_component_pcb if not (self.step_pcb.tray_component_pcb is None) else -1)

			if not (self.step_pcb.tools is None):
				for i in range(6):
					self.sb_tools[i].setValue(self.step_pcb.tools[i] if not (self.step_pcb.tools[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_tools[i].setValue(-1)

			if not (self.step_pcb.pcbs is None):
				for i in range(6):
					self.sb_pcbs[i].setValue(self.step_pcb.pcbs[i] if not (self.step_pcb.pcbs[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_pcbs[i].setValue(-1)

			if not (self.step_pcb.protomodules is None):
				for i in range(6):
					self.sb_protomodules[i].setValue(self.step_pcb.protomodules[i] if not (self.step_pcb.protomodules[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_protomodules[i].setValue(-1)

			if not (self.step_pcb.modules is None):
				for i in range(6):
					self.sb_modules[i].setValue(self.step_pcb.modules[i] if not (self.step_pcb.modules[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_modules[i].setValue(-1)

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
				self.sb_pcbs[i].setValue(-1)
				self.sb_protomodules[i].setValue(-1)
				self.sb_modules[i].setValue(-1)
		
		for i in range(6):
			if self.sb_tools[i].value()        == -1:self.sb_tools[i].clear()
			if self.sb_pcbs[i].value()         == -1:self.sb_pcbs[i].clear()
			if self.sb_protomodules[i].value() == -1:self.sb_protomodules[i].clear()
			if self.sb_modules[i].value()      == -1:self.sb_modules[i].clear()

		if self.page.sbBatchAraldite.value() == -1:self.page.sbBatchAraldite.clear()
		if self.page.sbTrayComponent.value() == -1:self.page.sbTrayComponent.clear()
		if self.page.sbTrayAssembly.value()  == -1:self.page.sbTrayAssembly.clear()	
		
		self.updateElements()

	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'
		tools_exist        = [_.value()>=0 for _ in self.sb_tools       ]
		pcbs_exist         = [_.value()>=0 for _ in self.sb_pcbs        ]
		protomodules_exist = [_.value()>=0 for _ in self.sb_protomodules]
		modules_exist      = [_.value()>=0 for _ in self.sb_modules     ]
		step_pcb_exists    = self.step_pcb_exists

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbID.setEnabled(mode_view)

		self.page.cbInstitution.setEnabled(mode_creating or mode_editing)

		#self.page.pbDatePerformedNow.setEnabled(mode_creating or mode_editing)
		self.page.pbRunStartNow     .setEnabled(mode_creating or mode_editing)

		self.page.leUserPerformed  .setReadOnly(mode_view)
		self.page.leLocation       .setReadOnly(mode_view)
		#self.page.dPerformed       .setReadOnly(mode_view)
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
			self.sb_tools[i].setReadOnly(       mode_view)
			self.sb_pcbs[i].setReadOnly(        mode_view)
			self.sb_protomodules[i].setReadOnly(mode_view)
			self.sb_modules[i].setReadOnly(     mode_view)
			self.pb_go_tools[i].setEnabled(       mode_view and tools_exist[i]       )
			self.pb_go_pcbs[i].setEnabled(        mode_view and pcbs_exist[i]        )
			self.pb_go_protomodules[i].setEnabled(mode_view and protomodules_exist[i])
			self.pb_go_modules[i].setEnabled(     mode_view and modules_exist[i]     )

		self.page.pbNew.setEnabled(    mode_view and not step_pcb_exists )
		self.page.pbEdit.setEnabled(   mode_view and     step_pcb_exists )
		self.page.pbSave.setEnabled(   mode_creating or mode_editing     )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing     )



	#NEW:  Add all load() functions

	@enforce_mode(['editing','creating'])
	def loadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tools_pcb[i].load(self.sb_tools[i].value(),       self.page.cbInstitution.currentText())
			self.pcbs[i].load(        self.sb_pcbs[i].value()        )
			self.protomodules[i].load(self.sb_protomodules[i].value())
			self.modules[i].load(     self.sb_modules[i].value()     )

		self.tray_component_sensor.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.batch_araldite.load(       self.page.sbBatchAraldite.value())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadAllTools(self,*args,**kwargs):  # Same as above, but load only tools:
		self.step_pcb.institution = self.page.cbInstitution.currentText()
		for i in range(6):
			self.tools_pcb[i].load(self.sb_tools[i].value(),       self.page.cbInstitution.currentText())
		self.tray_component_sensor.load(self.page.sbTrayComponent.value(), self.page.cbInstitution.currentText())
		self.tray_assembly.load(        self.page.sbTrayAssembly.value(),  self.page.cbInstitution.currentText())
		self.batch_araldite.load(       self.page.sbBatchAraldite.value())
		self.updateIssues()


	@enforce_mode(['editing','creating'])
	def unloadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tools_pcb[i].clear()
			self.pcbs[i].clear()
			self.protomodules[i].clear()
			self.modules[i].clear()

		self.tray_component_sensor.clear()
		self.tray_assembly.clear()
		self.batch_araldite.clear()

	@enforce_mode(['editing','creating'])
	def loadToolSensor(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.tools_pcb[which].load(self.sb_tools[which].value(), self.page.cbInstitution.currentText())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadBaseplate(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.baseplates[which].load(self.sb_baseplates[which].value())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadPcb(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.pcbs[which].load(self.sb_pcbs[which].value())
		self.updateIssues()

	#New
	@enforce_mode(['editing','creating'])
	def loadProtomodule(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.protomodules[which].load(self.sb_protomodules[which].value())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadModule(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.modules[which].load(self.sb_modules[which].value())
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

	#May not need this one
	#@enforce_mode(['editing','creating'])
	#def loadBatchLoctite(slef, *args, **kwargs):
	#	self.batch_loctite.load(self.page.sbBatchLoctite.value())
	#	self.updateIssues()



	#**WARNING:**  Currently unmodified!

	#NEW:  Add updateIssues and modify conditions accordingly
	@enforce_mode(['editing', 'creating'])
	def updateIssues(self,*args,**kwargs):
		issues = []
		objects = []

		if self.step_pcb.institution == None:
			issues.append(I_INSTITUTION_NOT_SELECTED)

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
				expires = datetime.date(*self.batch_araldite.date_expires)
				today = datetime.date(*time.localtime()[:3])
				if today > expires:
					issues.append(I_BATCH_ARALDITE_EXPIRED)
			if self.batch_araldite.is_empty:
				issues.append(I_BATCH_ARALDITE_EMPTY)

		#New
		#sb_tools and _baseplates are gone...but pcbs, protomodules, modules aren't.
		pcb_tools_selected    = [_.value() for _ in self.sb_tools       ]
		pcbs_selected         = [_.value() for _ in self.sb_pcbs        ]
		protomodules_selected = [_.value() for _ in self.sb_protomodules]
		modules_selected      = [_.value() for _ in self.sb_modules     ]

		pcb_tool_duplicates    = [_ for _ in range(6) if pcb_tools_selected[_]    >= 0 and pcb_tools_selected.count(   pcb_tools_selected[_]   )>1]
		pcb_duplicates         = [_ for _ in range(6) if pcbs_selected[_]         >= 0 and pcbs_selected.count(        pcbs_selected[_]        )>1]
		protomodule_duplicates = [_ for _ in range(6) if protomodules_selected[_] >= 0 and protomodules_selected.count(protomodules_selected[_])>1]
		module_duplicates      = [_ for _ in range(6) if modules_selected[_]      >= 0 and modules_selected.count(     modules_selected[_]     )>1]

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
		rows_module_dne      = []


		for i in range(6):
			num_parts = 0

			if pcb_tools_selected[i] >= 0:
				num_parts += 1
				objects.append(self.tools_pcb[i])
				if self.tools_pcb[i].ID is None:
					rows_tool_dne.append(i)

			"""if baseplates_selected[i] >= 0:
				num_parts += 1
				objects.append(self.baseplates[i])
				if self.baseplates[i].ID is None:
					rows_baseplate_dne.append(i)
			else:
				ready, reason = self.baseplates[i].ready_step_pcb(self.page.sbID.value())
				if not ready:
					#NOTE:  May need to be replaced by PCB_NOT_READY...
					issues.append(I_BASEPLATE_NOT_READY.format(i,reason))
			"""


			if pcbs_selected[i] >= 0:
				num_parts += 1
				objects.append(self.pcbs[i])
				if self.pcbs[i].ID is None:
					rows_pcb_dne.append(i)

			if protomodules_selected[i] >= 0:
				num_parts += 1
				objects.append(self.protomodules[i])
				if self.protomodules[i].ID is None:
					rows_protomodule_dne.append(i)

			if modules_selected[i] >= 0:
				num_parts += 1
				objects.append(self.modules[i])
				if self.modules[i].ID is None:
					rows_module_dne.append(i)


			if num_parts == 0:
				rows_empty.append(i)
			elif num_parts == 4: #2:
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
		#if rows_module_dne:
		#	issues.append(I_MODULE_DNE.format(     ', '.join([str(_+1) for _ in rows_module_dne])))

		objects_6in = []
		objects_8in = []
		objects_not_here = []

		for obj in objects:

			size = getattr(obj, "size", None)
			if size in [6.0, 6, '6']:
				objects_6in.append(obj)
			if size in [8.0, 8, '8']:
				objects_8in.append(obj)

			institution = getattr(obj, "institution", None)
			if not (institution in [None, self.page.cbInstitution.currentText()]):  #self.MAC]):
				objects_not_here.append(obj)

		if len(objects_6in) and len(objects_8in):
			issues.append(I_SIZE_MISMATCH)
			issues.append(I_SIZE_MISMATCH_6.format(', '.join([str(_) for _ in objects_6in])))
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
		if not self.step_pcb_exists:
			ID = self.page.sbID.value()
			self.mode = 'creating'
			self.step_pcb.new(ID)
			self.updateElements()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if self.step_pcb_exists:
			self.mode = 'editing'
			self.updateElements()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):
		self.step_pcb.institution = self.page.cbInstitution.currentText()

		self.step_pcb.user_performed = str( self.page.leUserPerformed.text() )
		self.step_pcb.location = str( self.page.leLocation.text() )

		#if self.page.dPerformed.date().year() == NO_DATE[0]:
		#	self.step_pcb.date_performed = None
		#else:
		#	self.step_pcb.date_performed = [*self.page.dPerformed.date().getDate()]

		if self.page.dtRunStart.date().year() == NO_DATE[0]:
			self.step_pcb.run_start = None
		else:
			self.step_pcb.run_start = self.page.dtRunStart.dateTime().toTime_t()


		self.step_pcb.cure_humidity    = str(self.page.leCureHumidity.text())
		self.step_pcb.cure_temperature = str(self.page.leCureTemperature.text())

		tools        = []
		pcbs         = []
		protomodules = []
		modules      = []
		for i in range(6):
			tools.append(       self.sb_tools[i].value()        if self.sb_tools[i].value()        >= 0 else None)
			pcbs.append(        self.sb_pcbs[i].value()         if self.sb_pcbs[i].value()         >= 0 else None)
			protomodules.append(self.sb_protomodules[i].value() if self.sb_protomodules[i].value() >= 0 else None)
			modules.append(     self.sb_modules[i].value()      if self.sb_modules[i].value()      >= 0 else None)
		self.step_pcb.tools        = tools
		self.step_pcb.pcbs         = pcbs
		self.step_pcb.protomodules = protomodules
		self.step_pcb.modules      = modules

		self.step_pcb.tray_component_pcb    = self.page.sbTrayComponent.value() if self.page.sbTrayComponent.value() >= 0 else None
		self.step_pcb.tray_assembly         = self.page.sbTrayAssembly.value()  if self.page.sbTrayAssembly.value()  >= 0 else None
		self.step_pcb.batch_araldite        = self.page.sbBatchAraldite.value() if self.page.sbBatchAraldite.value() >= 0 else None


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
				temp_module.thickness      = self.protomodules[i].thickness
				temp_module.channels       = self.protomodules[i].channels
				temp_module.size           = self.protomodules[i].size
				temp_module.shape          = self.protomodules[i].shape
				temp_module.chirality      = self.protomodules[i].chirality

				temp_module.baseplate      = self.protomodules[i].baseplate
				temp_module.sensor         = self.protomodules[i].sensor
				temp_module.protomodule    = self.protomodules[i].ID
				temp_module.pcb            = self.pcbs[i].ID
				temp_module.step_kapton    = self.protomodules[i].step_kapton
				temp_module.step_sensor    = self.protomodules[i].step_sensor
				temp_module.step_pcb       = self.step_pcb.ID

				temp_module.save()

			self.pcbs[i].step_pcb = self.step_pcb.ID
			self.pcbs[i].module = modules[i]
			self.pcbs[i].save()
			self.protomodules[i].step_pcb = self.step_pcb.ID
			self.protomodules[i].module = modules[i]
			self.protomodules[i].save()

		self.step_pcb.save()
		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()


	def goTool(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1 # last character of sender name is integer 1 through 6; subtract one for zero index
		tool = self.sb_tools[which].value()
		self.setUIPage('tooling',tool_pcb=tool)

	def goPcb(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		pcb = self.sb_pcbs[which].value()
		self.setUIPage('PCBs',ID=pcb)

	def goProtomodule(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		protomodule = self.sb_protomodules[which].value()
		self.setUIPage('protomodules',ID=protomodule)

	def goModule(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		module = self.sb_modules[which].value()
		self.setUIPage('modules',ID=module)

	def goBatchAraldite(self,*args,**kwargs):
		batch_araldite = self.page.sbBatchAraldite.value()
		self.setUIPage('supplies',batch_araldite=batch_araldite)

	def goTrayComponent(self,*args,**kwargs):
		tray_component_pcb = self.page.sbTrayComponent.value()
		self.setUIPage('tooling',tray_component_pcb=tray_component_pcb)

	def goTrayAssembly(self,*args,**kwargs):
		tray_assembly = self.page.sbTrayAssembly.value()
		print(tray_assembly)
		self.setUIPage('tooling',tray_assembly=tray_assembly)
	
	#def setDatePerformedNow(self, *args, **kwargs):
	#	self.page.dPerformed.setDate(QtCore.QDate(*time.localtime()[:3]))

	def setRunStartNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtRunStart.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtRunStart.setTime(QtCore.QTime(*localtime[3:6]))


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
