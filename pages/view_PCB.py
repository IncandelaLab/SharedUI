PAGE_NAME = "view_pcb"
PARTTYPE = "PCB"
DEBUG = False

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.pcb = fm.pcb()
		self.pcb_exists = None

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
		if ID is None:
			ID = self.page.sbPCBID.value()
		else:
			self.page.sbPCBID.setValue(ID)

		self.pcb_exists = self.pcb.load(ID)

		if self.pcb_exists:
			self.page.leIdentifier.setText(   self.pcb.identifier   )

			thickness = self.pcb.thickness
			if thickness:
				self.page.dsbThickness.setValue(thickness)
			else:
				self.page.dsbThickness.setValue(0)
				self.page.dsbThickness.clear()

			flatness = self.pcb.flatness
			if not (flatness is None):
				self.page.dsbFlatness.setValue(flatness)
			else:
				self.page.dsbFlatness.setValue(-1)
				self.page.dsbFlatness.clear()

			size = self.pcb.size
			if size:
				self.page.dsbSize.setValue(size)
			else:
				self.page.dsbSize.setValue(0)
				self.page.dsbSize.clear()


			channels = self.pcb.channels
			if channels:
				self.page.sbChannels.setValue(channels)
			else:
				self.page.sbChannels.setValue(0)
				self.page.sbChannels.clear()

			self.page.leManufacturer.setText( self.pcb.manufacturer )
			
			module = self.pcb.module
			if not (module is None):
				self.page.sbOnModule.setValue(module)
			else:
				self.page.sbOnModule.setValue(-1)
				self.page.sbOnModule.clear()

		else:
			self.page.leIdentifier.setText("")
			self.page.dsbThickness.setValue(0)
			self.page.dsbThickness.clear()
			self.page.dsbFlatness.setValue(-1)
			self.page.dsbFlatness.clear()
			self.page.dsbSize.setValue(0)
			self.page.dsbSize.clear()
			self.page.sbChannels.setValue(0)
			self.page.sbChannels.clear()
			self.page.leManufacturer.setText("")
			self.page.sbOnModule.setValue(-1)
			self.page.sbOnModule.clear()

		self.updateElements()

	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'
		pcb_exists    = self.pcb_exists
		module_exists = self.page.sbOnModule.value() >= 0
		#protomodul exists

		self.setMainSwitchingEnabled(mode_view)
				
		self.page.pbPCBNew.setEnabled(    mode_view and not pcb_exists  )
		self.page.pbPCBEdit.setEnabled(   mode_view and     pcb_exists  )
		self.page.pbPCBSave.setEnabled(   mode_editing or mode_creating )
		self.page.pbPCBCancel.setEnabled( mode_editing or mode_creating )

		self.page.pbGoModule.setEnabled( mode_view and module_exists )
		self.page.sbPCBID.setEnabled(    mode_view )
		self.page.leIdentifier.setReadOnly(   not (mode_editing or mode_creating) )
		self.page.dsbThickness.setReadOnly(   not (mode_editing or mode_creating) )
		self.page.dsbFlatness.setReadOnly(    not (mode_editing or mode_creating) )
		self.page.dsbSize.setReadOnly(        not (mode_editing or mode_creating) )
		self.page.sbChannels.setReadOnly(     not (mode_editing or mode_creating) )
		self.page.leManufacturer.setReadOnly( not (mode_editing or mode_creating) )
		self.page.sbOnModule.setReadOnly(     not (mode_editing or mode_creating) )

	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if not self.pcb_exists:
			ID = self.page.sbPCBID.value()
			self.mode = 'creating'
			self.pcb.new(ID)
			self.updateElements()
		else:
			pass

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if not self.pcb_exists:
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
		self.pcb.identifier   = str(self.page.leIdentifier.text())
		self.pcb.manufacturer = str(self.page.leManufacturer.text())

		self.pcb.thickness    = self.page.dsbThickness.value() if self.page.dsbThickness.value() >  0 else None
		self.pcb.flatness     = self.page.dsbFlatness.value()  if self.page.dsbFlatness.value()  >= 0 else None
		self.pcb.size         = self.page.dsbSize.value()      if self.page.dsbSize.value()      >  0 else None
		self.pcb.channels     = self.page.sbChannels.value()   if self.page.sbChannels.value()   >  0 else None
		self.pcb.onModuleID   = self.page.sbOnModule.value()   if self.page.sbOnModule.value()   >= 0 else None
		
		self.pcb.save()
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