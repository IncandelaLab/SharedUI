PAGE_NAME = "view_sensor"
OBJECTTYPE = "sensor"
DEBUG = False

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.sensor = fm.sensor()
		self.sensor_exists = None

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
		self.page.sbSensorID.valueChanged.connect(self.update_info)
		self.page.pbGoModule.clicked.connect(self.goModule)
		self.page.pbSensorNew.clicked.connect(self.startCreating)
		self.page.pbSensorEdit.clicked.connect(self.startEditing)
		self.page.pbSensorSave.clicked.connect(self.saveEditing)
		self.page.pbSensorCancel.clicked.connect(self.cancelEditing)



	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbSensorID.value()
		else:
			self.page.sbSensorID.setValue(ID)

		self.sensor_exists = self.sensor.load(ID)

		if self.sensor_exists:
			self.page.leIdentifier.setText(   self.sensor.identifier   )
			self.page.leType.setText(         self.sensor.type         )

			size = self.sensor.size
			if size:
				self.page.dsbSize.setValue(size)
			else:
				self.page.dsbSize.setValue(0)
				self.page.dsbSize.clear()

			channels = self.sensor.channels
			if channels:
				self.page.sbChannels.setValue(channels)
			else:
				self.page.sbChannels.setValue(0)
				self.page.sbChannels.clear()

			self.page.leManufacturer.setText( self.sensor.manufacturer )

			module = self.sensor.module
			if not (module is None):
				self.page.sbOnModule.setValue(module)
			else:
				self.page.sbOnModule.setValue(-1)
				self.page.sbOnModule.clear()

		else:
			self.page.leIdentifier.setText("")
			self.page.leType.setText("")
			self.page.dsbSize.setValue(0)
			self.page.dsbSize.clear()
			self.page.sbChannels.setValue(0)
			self.page.sbChannels.clear()
			self.page.leManufacturer.setText("")
			self.page.sbOnModule.setValue(-1)
			self.page.sbOnModule.clear()

		self.updateElements()

	@enforce_mode(['view','editing','creating'])
	def updateElements(self):
		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'
		module_exists = self.page.sbOnModule.value() >= 0
		sensor_exists = self.sensor_exists
		#protomodule_exists

		self.setMainSwitchingEnabled(mode_view)

		self.page.pbSensorNew.setEnabled(     mode_view and not sensor_exists )
		self.page.pbSensorEdit.setEnabled(    mode_view and     sensor_exists )
		self.page.pbSensorSave.setEnabled(    mode_editing or mode_creating )
		self.page.pbSensorCancel.setEnabled(  mode_editing or mode_creating )
		self.page.pbGoModule.setEnabled(      mode_view and module_exists ) 
		self.page.sbSensorID.setEnabled(      mode_view )
		self.page.leIdentifier.setReadOnly(   not (mode_creating or mode_editing))
		self.page.leType.setReadOnly(         not (mode_creating or mode_editing))
		self.page.dsbSize.setReadOnly(        not (mode_creating or mode_editing))
		self.page.sbChannels.setReadOnly(     not (mode_creating or mode_editing))
		self.page.leManufacturer.setReadOnly( not (mode_creating or mode_editing))
		self.page.sbOnModule.setReadOnly(     not (mode_creating or mode_editing))

	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if not self.sensor_exists:
			ID = self.page.sbSensorID.value()
			self.mode = 'creating'
			self.sensor.new(ID)
			self.updateElements()
		else:
			pass

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if not self.sensor_exists:
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
		self.sensor.identifier   = str(self.page.leIdentifier.text())
		self.sensor.type         = str(self.page.leType.text())
		self.sensor.manufacturer = str(self.page.leManufacturer.text())

		self.sensor.size     = self.page.dsbSize.value()    if self.page.dsbSize.value()    >  0 else None
		self.sensor.channels = self.page.sbChannels.value() if self.page.sbChannels.value() >  0 else None
		self.sensor.module   = self.page.sbOnModule.value() if self.page.sbOnModule.value() >= 0 else None
		
		self.sensor.save()
		self.mode = 'view'
		self.update_info()

	@enforce_mode('view')
	def goModule(self,*args,**kwargs):
		ID = self.page.sbOnModule.value()
		if ID >= 0:
			self.setUIPage('modules',ID=ID)
		else:
			return

	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is int):
				raise TypeError("Expected type <int> for ID; got <{}>".format(type(ID)))
			if ID < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbSensorID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))