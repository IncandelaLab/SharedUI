from PyQt4 import QtCore
import time

NO_DATE = [2000,1,1]

PAGE_NAME = "view_sensor_step"
OBJECTTYPE = "sensor_step"
DEBUG = False

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.step_sensor = fm.step_sensor()
		self.step_sensor_exists = None

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

		self.sb_sensors = [
			self.page.sbSensor1,
			self.page.sbSensor2,
			self.page.sbSensor3,
			self.page.sbSensor4,
			self.page.sbSensor5,
			self.page.sbSensor6,
		]
		self.pb_go_sensors = [
			self.page.pbGoSensor1,
			self.page.pbGoSensor2,
			self.page.pbGoSensor3,
			self.page.pbGoSensor4,
			self.page.pbGoSensor5,
			self.page.pbGoSensor6,
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

		self.sb_protomodules = [
			self.page.sbProtoModule1,
			self.page.sbProtoModule2,
			self.page.sbProtoModule3,
			self.page.sbProtoModule4,
			self.page.sbProtoModule5,
			self.page.sbProtoModule6,
		]
		self.pb_go_protomodules = [
			self.page.pbGoProtoModule1,
			self.page.pbGoProtoModule2,
			self.page.pbGoProtoModule3,
			self.page.pbGoProtoModule4,
			self.page.pbGoProtoModule5,
			self.page.pbGoProtoModule6,
		]

		for i in range(6):
			self.pb_go_tools[i].clicked.connect(       self.goTool       )
			self.pb_go_sensors[i].clicked.connect(     self.goSensor     )
			self.pb_go_baseplates[i].clicked.connect(  self.goBaseplate  )
			self.pb_go_protomodules[i].clicked.connect(self.goProtomodule)

		self.page.sbID.valueChanged.connect(self.update_info)

		self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoBatchAraldite.clicked.connect(self.goBatchAraldite)
		self.page.pbGoBatchLoctite.clicked.connect(self.goBatchLoctite)
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
			ID = self.page.sbID.setValue(ID)

		self.step_sensor_exists = self.step_sensor.load(ID)

		if self.step_sensor_exists:
			self.page.leUserPerformed.setText(self.step_sensor.user_performed)

			date_performed = self.step_sensor.date_performed
			if not (date_performed is None):
				self.page.dPerformed.setDate(QtCore.QDate(*self.step_sensor.date_performed))
			else:
				self.page.dPerformed.setDate(QtCore.QDate(*NO_DATE))

			cure_start = self.step_sensor.cure_start
			cure_stop  = self.step_sensor.cure_stop
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

			self.page.leCureDuration.setText(str(int(self.step_sensor.cure_duration)) if not (self.step_sensor.cure_duration is None) else "")
			self.page.leCureTemperature.setText(self.step_sensor.cure_temperature)
			self.page.leCureHumidity.setText(self.step_sensor.cure_humidity)

			self.page.sbBatchAraldite.setValue(self.step_sensor.batch_araldite if not (self.step_sensor.batch_araldite is None) else -1)
			self.page.sbBatchLoctite.setValue( self.step_sensor.batch_loctite  if not (self.step_sensor.batch_loctite  is None) else -1)
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
					self.sb_sensors[i].setValue(self.step_sensor.sensors[i] if not (self.step_sensor.sensors[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_sensors[i].setValue(-1)

			if not (self.step_sensor.baseplates is None):
				for i in range(6):
					self.sb_baseplates[i].setValue(self.step_sensor.baseplates[i] if not (self.step_sensor.baseplates[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_baseplates[i].setValue(-1)

			if not (self.step_sensor.protomodules is None):
				for i in range(6):
					self.sb_protomodules[i].setValue(self.step_sensor.protomodules[i] if not (self.step_sensor.protomodules[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_protomodules[i].setValue(-1)

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
			self.page.sbBatchLoctite.setValue(-1)
			self.page.sbTrayComponent.setValue(-1)
			self.page.sbTrayAssembly.setValue(-1)
			for i in range(6):
				self.sb_tools[i].setValue(-1)
				self.sb_sensors[i].setValue(-1)
				self.sb_baseplates[i].setValue(-1)
				self.sb_protomodules[i].setValue(-1)

		for i in range(6):
			if self.sb_tools[i].value()        == -1:self.sb_tools[i].clear()
			if self.sb_sensors[i].value()      == -1:self.sb_sensors[i].clear()
			if self.sb_baseplates[i].value()   == -1:self.sb_baseplates[i].clear()
			if self.sb_protomodules[i].value() == -1:self.sb_protomodules[i].clear()

		if self.page.sbBatchAraldite.value() == -1:self.page.sbBatchAraldite.clear()
		if self.page.sbBatchLoctite.value()  == -1:self.page.sbBatchLoctite.clear()
		if self.page.sbTrayComponent.value() == -1:self.page.sbTrayComponent.clear()
		if self.page.sbTrayAssembly.value()  == -1:self.page.sbTrayAssembly.clear()

		self.updateElements()

	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'
		tools_exist        = [_.value()>=0 for _ in self.sb_tools       ]
		sensors_exist      = [_.value()>=0 for _ in self.sb_sensors     ]
		baseplates_exist   = [_.value()>=0 for _ in self.sb_baseplates  ]
		protomodules_exist = [_.value()>=0 for _ in self.sb_protomodules]
		step_sensor_exists = self.step_sensor_exists

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
		self.page.sbBatchLoctite   .setReadOnly(mode_view)

		self.page.pbGoTrayComponent.setEnabled(mode_view and self.page.sbTrayComponent.value() >= 0)
		self.page.pbGoTrayAssembly .setEnabled(mode_view and self.page.sbTrayAssembly .value() >= 0)
		self.page.pbGoBatchAraldite.setEnabled(mode_view and self.page.sbBatchAraldite.value() >= 0)
		self.page.pbGoBatchLoctite .setEnabled(mode_view and self.page.sbBatchLoctite .value() >= 0)

		for i in range(6):
			self.sb_tools[i].setReadOnly(       mode_view)
			self.sb_sensors[i].setReadOnly(     mode_view)
			self.sb_baseplates[i].setReadOnly(  mode_view)
			self.sb_protomodules[i].setReadOnly(mode_view)
			self.pb_go_tools[i].setEnabled(       mode_view and tools_exist[i]       )
			self.pb_go_sensors[i].setEnabled(     mode_view and sensors_exist[i]     )
			self.pb_go_baseplates[i].setEnabled(  mode_view and baseplates_exist[i]  )
			self.pb_go_protomodules[i].setEnabled(mode_view and protomodules_exist[i])

		self.page.pbNew.setEnabled(    mode_view and not step_sensor_exists )
		self.page.pbEdit.setEnabled(   mode_view and     step_sensor_exists )
		self.page.pbSave.setEnabled(   mode_creating or mode_editing        )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing        )


	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if not self.step_sensor_exists:
			ID = self.page.sbID.value()
			self.mode = 'creating'
			self.step_sensor.new(ID)
			self.updateElements()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if self.step_sensor_exists:
			self.mode = 'editing'
			self.updateElements()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):
		
		self.step_sensor.user_performed = str( self.page.leUserPerformed.text() )

		if self.page.dPerformed.date().year() == NO_DATE[0]:
			self.step_sensor.date_performed = None
		else:
			self.step_sensor.date_performed = [*self.page.dPerformed.date().getDate()]

		if self.page.dtCureStart.date().year() == NO_DATE[0]:
			self.step_sensor.cure_start = None
		else:
			self.step_sensor.cure_start = self.page.dtCureStart.dateTime().toTime_t()

		if self.page.dtCureStop.date().year() == NO_DATE[0]:
			self.step_sensor.cure_stop = None
		else:
			self.step_sensor.cure_stop  = self.page.dtCureStop.dateTime().toTime_t()

		self.step_sensor.cure_humidity    = str(self.page.leCureHumidity.text())
		self.step_sensor.cure_temperature = str(self.page.leCureTemperature.text())

		tools = []
		sensors = []
		baseplates = []
		protomodules = []
		for i in range(6):
			tools.append(       self.sb_tools[i].value()        if self.sb_tools[i].value()        >= 0 else None)
			sensors.append(     self.sb_sensors[i].value()      if self.sb_sensors[i].value()      >= 0 else None)
			baseplates.append(  self.sb_baseplates[i].value()   if self.sb_baseplates[i].value()   >= 0 else None)
			protomodules.append(self.sb_protomodules[i].value() if self.sb_protomodules[i].value() >= 0 else None)
		self.step_sensor.tools        = tools
		self.step_sensor.sensors      = sensors
		self.step_sensor.baseplates   = baseplates
		self.step_sensor.protomodules = protomodules

		self.step_sensor.tray_component_sensor = self.page.sbTrayComponent.value() if self.page.sbTrayComponent.value() >= 0 else None
		self.step_sensor.tray_assembly         = self.page.sbTrayAssembly.value()  if self.page.sbTrayAssembly.value()  >= 0 else None
		self.step_sensor.batch_araldite        = self.page.sbBatchAraldite.value() if self.page.sbBatchAraldite.value() >= 0 else None
		self.step_sensor.batch_loctite         = self.page.sbBatchLoctite.value()  if self.page.sbBatchLoctite.value()  >= 0 else None

		self.step_sensor.save()
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
		sensor = self.sb_sensors[which].value()
		self.setUIPage('sensors',ID=sensor)

	def goBaseplate(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		baseplate = self.sb_baseplates[which].value()
		self.setUIPage('baseplates',ID=baseplate)

	def goProtomodule(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		protomodule = self.sb_protomodules[which].value()
		self.setUIPage('protomodules',ID=protomodule)

	def goBatchAraldite(self,*args,**kwargs):
		batch_araldite = self.page.sbBatchAraldite.value()
		self.setUIPage('supplies',batch_araldite=batch_araldite)

	def goBatchLoctite(self,*args,**kwargs):
		batch_loctite = self.page.sbBatchLoctite.value()
		self.setUIPage('supplies',batch_loctite=batch_loctite)

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
