nstr = lambda v:''  if v is None else str(v)
nflt = lambda v:0.0 if v is None else float(v)
nint = lambda v:0   if v is None else int(v)

PAGE_NAME = "view_pcb"
DEBUG = False

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.info = None
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
		self.page.sbPCBID.valueChanged.connect(self.update_info)
		self.page.pbGoModule.clicked.connect(self.goModule)

		self.page.pbPCBNew.clicked.connect(self.startCreating)
		self.page.pbPCBEdit.clicked.connect(self.startEditing)
		self.page.pbPCBSave.clicked.connect(self.saveEditig)
		self.page.pbPCBCancel.clicked.connect(self.cancelEditing)


	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:ID = self.page.sbPCBID.value()
		self.info = self.fm.loadPCBDetails(ID)
		self.updateElements(use_info = True)

	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		if use_info:
			if self.info is None:
				self.page.leIdentifier.setText("")
				self.page.dsbThickness.setValue(0.0)
				self.page.dsbThickness.clear()
				self.page.dsbFlatness.setValue(0.0)
				self.page.dsbFlatness.clear()
				self.page.dsbSize.setValue(0.0)
				self.page.dsbSize.clear()
				self.page.sbChannels.setValue(0)
				self.page.sbChannels.clear()
				self.page.leManufacturer.setText("")
				self.page.sbOnModule.setValue(-1)
				self.page.sbOnModule.clear()

			else:
				self.page.leIdentifier.setText(nstr(self.info["identifier"]))
				self.page.dsbThickness.setValue(nflt(self.info["thickness"]))
				self.page.dsbFlatness.setValue(nflt(self.info["flatness"]))
				self.page.dsbSize.setValue(nflt(self.info["size"]))
				self.page.sbChannels.setValue(nint(self.info["channels"]))
				self.page.leManufacturer.setText(nstr(self.info["manufacturer"]))
				self.page.sbOnModule.setValue(nint(self.info["onModuleID"]))

		self.page.pbPCBNew.setEnabled(    (self.mode == 'view') and     (self.info is None) )
		self.page.pbPCBEdit.setEnabled(   (self.mode == 'view') and not (self.info is None) )
		self.page.pbPCBSave.setEnabled(    self.mode in ['editing','creating'] )
		self.page.pbPCBCancel.setEnabled(  self.mode in ['editing','creating'] )

		self.setMainSwitchingEnabled( self.mode == 'view' )

		self.page.pbGoModule.setEnabled( (self.mode == 'view') and (self.page.sbOnModule.value()>=0) )
		self.page.sbPCBID.setEnabled(     self.mode == 'view' )
		self.page.leIdentifier.setReadOnly(   not (self.mode in ['editing','creating']) )
		self.page.dsbThickness.setReadOnly(   not (self.mode in ['editing','creating']) )
		self.page.dsbFlatness.setReadOnly(    not (self.mode in ['editing','creating']) )
		self.page.dsbSize.setReadOnly(        not (self.mode in ['editing','creating']) )
		self.page.sbChannels.setReadOnly(     not (self.mode in ['editing','creating']) )
		self.page.leManufacturer.setReadOnly( not (self.mode in ['editing','creating']) )
		self.page.sbOnModule.setReadOnly(     not (self.mode in ['editing','creating']) )

	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if self.info is None:
			self.mode = 'creating'
			self.updateElements()
		else:
			pass

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if self.info is None:
			pass
		else:
			self.mode = 'editing'
			self.updateElements()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditig(self,*args,**kwargs):
		ID = self.page.sbPCBID.value()
		details = {
			'identifier'   : str(self.page.leIdentifier.text()),
			'thickness'    : self.page.dsbThickness.value(),
			'flatness'     : self.page.dsbFlatness.value(),
			'size'         : self.page.dsbSize.value(),
			'channels'     : self.page.sbChannels.value(),
			'manufacturer' : str(self.page.leManufacturer.text()),
			'onModuleID'   : self.page.sbOnModule.value(),
			}
		new = self.mode == 'creating'
		self.fm.changePCBDetails(ID,details,new)
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
			self.page.sbPCBID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))