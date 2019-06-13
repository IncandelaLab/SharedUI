from PyQt4 import QtCore
import time

NO_DATE = [2000,1,1]

PAGE_NAME = "view_kapton_step"
OBJECTTYPE = "kapton_step"
DEBUG = False

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.step_kapton = fm.step_kapton()
		self.step_kapton_exists = None

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

		self.sb_baseplates = [
			self.page.sbBaseplate1,
			self.page.sbBaseplate2,
			self.page.sbBaseplate3,
			self.page.sbBaseplate4,
			self.page.sbBaseplate5,
			self.page.sbBaseplate6,
		]
		self.pb_go_baseplates = [
			self.page.pbGoBaseplate1,
			self.page.pbGoBaseplate2,
			self.page.pbGoBaseplate3,
			self.page.pbGoBaseplate4,
			self.page.pbGoBaseplate5,
			self.page.pbGoBaseplate6,
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
			self.pb_go_baseplates[i].clicked.connect(self.goBaseplate)

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

		self.step_kapton_exists = self.step_kapton.load(ID)

		if self.step_kapton_exists:
			self.page.leUserPerformed.setText(self.step_kapton.user_performed)

			date_performed = self.step_kapton.date_performed
			if not (date_performed is None):
				self.page.dPerformed.setDate(QtCore.QDate(*self.step_kapton.date_performed))
			else:
				self.page.dPerformed.setDate(QtCore.QDate(*NO_DATE))

			cure_start = self.step_kapton.cure_start
			cure_stop  = self.step_kapton.cure_stop
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

			self.page.leCureDuration.setText(str(int(self.step_kapton.cure_duration)) if not (self.step_kapton.cure_duration is None) else "")
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

			if not (self.step_kapton.baseplates is None):
				for i in range(6):
					self.sb_baseplates[i].setValue(self.step_kapton.baseplates[i] if not (self.step_kapton.baseplates[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_baseplates[i].setValue(-1)

			if not (self.step_kapton.kaptons_inspected is None):
				for i in range(6):
					self.ck_kaptons_inspected[i].setChecked(False if self.step_kapton.kaptons_inspected[i] is None else self.step_kapton.kaptons_inspected[i])
			else:
				for i in range(6):
					self.ck_kaptons_inspected[i].setChecked(False)

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
				self.sb_baseplates[i].setValue(-1)
				self.ck_kaptons_inspected[i].setChecked(False)

		for i in range(6):
			if self.sb_tools[i].value() == -1:self.sb_tools[i].clear()
			if self.sb_baseplates[i].value() == -1:self.sb_baseplates[i].clear()

		if self.page.sbBatchAraldite.value() == -1:self.page.sbBatchAraldite.clear()
		if self.page.sbTrayComponent.value() == -1:self.page.sbTrayComponent.clear()
		if self.page.sbTrayAssembly.value() == -1:self.page.sbTrayAssembly.clear()

		self.updateElements()

	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'
		tools_exist      = [_.value()>=0 for _ in self.sb_tools     ]
		baseplates_exist = [_.value()>=0 for _ in self.sb_baseplates]
		step_kapton_exists = self.step_kapton_exists

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
			self.sb_tools[i].setReadOnly(mode_view)
			self.sb_baseplates[i].setReadOnly(mode_view)
			self.pb_go_tools[i].setEnabled(     mode_view and tools_exist[i]     )
			self.pb_go_baseplates[i].setEnabled(mode_view and baseplates_exist[i])
			self.ck_kaptons_inspected[i].setEnabled(mode_creating or mode_editing)

		self.page.pbNew.setEnabled(    mode_view and not step_kapton_exists )
		self.page.pbEdit.setEnabled(   mode_view and     step_kapton_exists )
		self.page.pbSave.setEnabled(   mode_creating or mode_editing        )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing        )


	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if not self.step_kapton_exists:
			ID = self.page.sbID.value()
			self.mode = 'creating'
			self.step_kapton.new(ID)
			self.updateElements()
		else:
			pass

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if not self.step_kapton_exists:
			pass
		else:
			self.mode = 'editing'
			self.updateElements()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):

		self.step_kapton.user_performed = str( self.page.leUserPerformed.text() )

		if self.page.dPerformed.date().year() == NO_DATE[0]:
			self.step_kapton.date_performed = None
		else:
			self.step_kapton.date_performed = [*self.page.dPerformed.date().getDate()]

		if self.page.dtCureStart.date().year() == NO_DATE[0]:
			self.step_kapton.cure_start = None
		else:
			self.step_kapton.cure_start = self.page.dtCureStart.dateTime().toTime_t()

		if self.page.dtCureStop.date().year() == NO_DATE[0]:
			self.step_kapton.cure_stop = None
		else:
			self.step_kapton.cure_stop  = self.page.dtCureStop.dateTime().toTime_t()

		self.step_kapton.cure_humidity    = str(self.page.leCureHumidity.text())
		self.step_kapton.cure_temperature = str(self.page.leCureTemperature.text())

		tools = []
		baseplates = []
		kaptons_inspected = []
		for i in range(6):
			tools.append(self.sb_tools[i].value() if self.sb_tools[i].value() >= 0 else None)
			baseplates.append(self.sb_baseplates[i].value() if self.sb_baseplates[i].value() >= 0 else None)
			kaptons_inspected.append(self.ck_kaptons_inspected[i].isChecked() if self.sb_baseplates[i].value() >= 0 else None)
		self.step_kapton.tools = tools
		self.step_kapton.baseplates = baseplates
		self.step_kapton.kaptons_inspected = kaptons_inspected

		self.step_kapton.tray_component_sensor = self.page.sbTrayComponent.value() if self.page.sbTrayComponent.value() >= 0 else None
		self.step_kapton.tray_assembly         = self.page.sbTrayAssembly.value()  if self.page.sbTrayAssembly.value()  >= 0 else None
		self.step_kapton.batch_araldite        = self.page.sbBatchAraldite.value() if self.page.sbBatchAraldite.value() >= 0 else None

		self.step_kapton.save()		
		self.mode = 'view'
		self.update_info()

	def goTool(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1 # last character of sender name is integer 1 through 6; subtract one for zero index
		tool = self.sb_tools[which].value()
		self.setUIPage('tooling',tool_sensor=tool)

	def goBaseplate(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		baseplate = self.sb_baseplates[which].value()
		self.setUIPage('baseplates',ID=baseplate)

	def goBatchAraldite(self,*args,**kwargs):
		batch_araldite = self.page.sbBatchAraldite.value()
		self.setUIPage('supplies',batch_araldite=batch_araldite)

	def goTrayComponent(self,*args,**kwargs):
		tray_component_sensor = self.page.sbTrayComponent.value()
		self.setUIPage('tooling',tray_component_sensor=tray_component_sensor)

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
		self.update_info()
