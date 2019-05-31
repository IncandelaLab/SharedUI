from PyQt4 import QtCore
import time

NO_DATE = [2000,1,1]

PAGE_NAME = "view_pcb_step"
OBJECTTYPE = "PCB_step"
DEBUG = False

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.step_pcb = fm.step_pcb()
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

		self.page.sbID.valueChanged.connect(self.update_info)

		self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoBatchAraldite.clicked.connect(self.goBatchAraldite)
		self.page.pbGoTrayAssembly.clicked.connect(self.goTrayAssembly)
		self.page.pbGoTrayComponent.clicked.connect(self.goTrayComponent)

		self.page.pbDatePerformedNow.clicked.connect(self.setDatePerformedNow)
		self.page.pbCureStartNow    .clicked.connect(self.setCureStartNow)
		self.page.pbCureStopNow     .clicked.connect(self.setCureStopNow)

	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbID.value()
		else:
			self.page.sbID.setValue(ID)

		self.step_pcb_exists = self.step_pcb.load(ID)

		if self.step_pcb_exists:
			self.page.leUserPerformed.setText(self.step_pcb.user_performed)

			date_performed = self.step_pcb.date_performed
			if not (date_performed is None):
				self.page.dPerformed.setDate(QtCore.QDate(*self.step_pcb.date_performed))
			else:
				self.page.dPerformed.setDate(QtCore.QDate(*NO_DATE))

			cure_start = self.step_pcb.cure_start
			cure_stop  = self.step_pcb.cure_stop
			if cure_start is None:
				self.page.dtCureStart.setDate(QtCore.QDate(*NO_DATE))
				self.page.dtCureStart.setTime(QtCore.QTime(0,0,0))
			else:
				localtime = list(time.localtime(cure_start))
				self.page.dtCureStart.setDate(QtCore.QDate(*localtime[0:3]))
				self.page.dtCureStart.setTime(QtCore.QTime(*localtime[3:6]))

			if cure_stop is None:
				self.page.dtCureStop.setDate(QtCore.QDate(*NO_DATE))
				self.page.dtCureStop.setTime(QtCore.QTime(0,0,0))
			else:
				localtime = list(time.localtime(cure_stop))
				self.page.dtCureStop.setDate(QtCore.QDate(*localtime[0:3]))
				self.page.dtCureStop.setTime(QtCore.QTime(*localtime[3:6]))

			self.page.leCureDuration.setText(str(int(self.step_pcb.cure_duration)) if not (self.step_pcb.cure_duration is None) else "")
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
			self.page.leUserPerformed.setText("")
			self.page.dPerformed.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStart.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStart.setTime(QtCore.QTime(0,0,0))
			self.page.dtCureStop.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStop.setTime(QtCore.QTime(0,0,0))
			self.page.leCureDuration.setText("")
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

		self.page.pbDatePerformedNow.setEnabled(mode_creating or mode_editing)
		self.page.pbCureStartNow    .setEnabled(mode_creating or mode_editing)
		self.page.pbCureStopNow     .setEnabled(mode_creating or mode_editing)

		self.page.leUserPerformed  .setReadOnly(mode_view)
		self.page.dPerformed       .setReadOnly(mode_view)
		self.page.dtCureStart      .setReadOnly(mode_view)
		self.page.dtCureStop       .setReadOnly(mode_view)
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
		self.step_pcb.user_performed = str( self.page.leUserPerformed.text() )

		if self.page.dPerformed.date().year() == NO_DATE[0]:
			self.step_pcb.date_performed = None
		else:
			self.step_pcb.date_performed = [*self.page.dPerformed.date().getDate()]

		if self.page.dtCureStart.date().year() == NO_DATE[0]:
			self.step_pcb.cure_start = None
		else:
			self.step_pcb.cure_start = self.page.dtCureStart.dateTime().toTime_t()

		if self.page.dtCureStop.date().year() == NO_DATE[0]:
			self.step_pcb.cure_stop = None
		else:
			self.step_pcb.cure_stop  = self.page.dtCureStop.dateTime().toTime_t()

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

		self.step_pcb.save()
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
	
	def setDatePerformedNow(self, *args, **kwargs):
		self.page.dPerformed.setDate(QtCore.QDate(*time.localtime()[:3]))

	def setCureStartNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStart.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStart.setTime(QtCore.QTime(*localtime[3:6]))

	def setCureStopNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStop.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStop.setTime(QtCore.QTime(*localtime[3:6]))


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
