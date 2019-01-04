nstr = lambda v:'' if v is None else str(v)

PAGE_NAME = "view_sensor"
DEBUG = False

class func(object):
	def __init__(self,fm,page,setUIPage):
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage
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
					print("mode is {}, needed {} for function {} with args {} kwargs {}".format(
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


	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:ID = self.page.sbSensorID.value()
		info = self.fm.loadSensorDetails(ID)

		if info is None:
			self.page.leIdentifier.setText("")
			self.page.leType.setText("")
			self.page.leSize.setText("")
			self.page.leChannels.setText("")
			self.page.leManufacturer.setText("")
			self.page.leOnModule.setText("")

		else:
			self.page.leIdentifier.setText(nstr(info["identifier"]))
			self.page.leType.setText(nstr(info["type"]))
			self.page.leSize.setText(nstr(info["size"]))
			self.page.leChannels.setText(nstr(info["channels"]))
			self.page.leManufacturer.setText(nstr(info["manufacturer"]))
			self.page.leOnModule.setText(nstr(info["onModuleID"]))

	@enforce_mode('view')
	def goModule(self,*args,**kwargs):
		ID = self.page.leOnModule.text()
		if len(ID) > 0:
			try:
				ID = int(ID)
			except:
				return
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