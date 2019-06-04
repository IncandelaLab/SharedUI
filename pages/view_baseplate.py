PAGE_NAME = "view_baseplate"
OBJECTTYPE = "baseplate"
DEBUG = False


class func(object):
	
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.currentBaseplateExists = None

		self.baseplate = fm.baseplate()

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
		self.mode='view'
		print("{} setup completed".format(PAGE_NAME))
		self.update_info()

	@enforce_mode('setup')
	def rig(self):
		self.page.sbBaseplateID.valueChanged.connect(self.update_info)
		self.page.pbGoModule.clicked.connect(self.goModule)
		self.page.pbEditCornerHeights.clicked.connect(self.startEditingCorners)
		self.page.pbSaveCorners.clicked.connect(self.saveEditingCorners)
		self.page.pbCancelCorners.clicked.connect(self.cancelEditingCorners)

		self.corners = [
			self.page.dsbC0,
			self.page.dsbC1,
			self.page.dsbC2,
			self.page.dsbC3,
			self.page.dsbC4,
			self.page.dsbC5
			]

		self.page.pbBaseplateNew.clicked.connect(self.startCreating)
		self.page.pbBaseplateEdit.clicked.connect(self.startEditing)
		self.page.pbBaseplateSave.clicked.connect(self.saveEditing)
		self.page.pbBaseplateCancel.clicked.connect(self.cancelEditing)


	@enforce_mode('view')
	def update_info(self,ID=None):
		"""Loads info on the selected baseplate ID and updates UI elements accordingly"""
		if ID is None:
			ID = self.page.sbBaseplateID.value()
		else:
			self.page.sbBaseplateID.setValue(ID)

		exists = self.baseplate.load(ID)
		if exists:
			self.currentBaseplateExists = True
			self.page.leIdentifier.setText(     self.baseplate.identifier   )
			self.page.leMaterial.setText(       self.baseplate.material     )

			if self.baseplate.nomthickness:
				self.page.dsbNomThickness.setValue(self.baseplate.nomthickness)
			else:
				self.page.dsbNomThickness.setValue(-1)
				self.page.dsbNomThickness.clear()

			if not (self.baseplate.flatness is None):
				self.page.dsbFlatness.setValue(self.baseplate.flatness)
			else:
				self.page.dsbFlatness.setValue(-1)
				self.page.dsbFlatness.clear()

			if self.baseplate.size:
				self.page.dsbSize.setValue(self.baseplate.size)
			else:
				self.page.dsbSize.setValue(-1)
				self.page.dsbSize.clear()

			self.page.leManufacturer.setText(   self.baseplate.manufacturer )
			
			if not (self.baseplate.module is None):
				self.page.sbOnModule.setValue(self.baseplate.module)
			else:
				self.page.sbOnModule.setValue(-1)
				self.page.sbOnModule.clear()

			# same for protomodule

			if not (self.baseplate.corner_heights is None):
				for i in range(6):
					self.corners[i].setValue(self.baseplate.corner_heights[i] if not (self.baseplate.corner_heights[i] is None) else -1)

		else:
			self.currentBaseplateExists = False
			self.page.leIdentifier.setText('')
			self.page.leMaterial.setText('')
			self.page.dsbNomThickness.setValue(-1.0)
			self.page.dsbNomThickness.clear()
			self.page.dsbFlatness.setValue(-1.0)
			self.page.dsbFlatness.clear()
			self.page.dsbSize.setValue(-1.0)
			self.page.dsbSize.clear()
			self.page.leManufacturer.setText('')
			self.page.sbOnModule.setValue(-1)
			self.page.sbOnModule.clear()
			for i in range(6):
				self.corners[i].setValue(-1)

		for i in range(6):
			if self.corners[i].value() < 0:self.corners[i].clear()

		self.updateElements()

	@enforce_mode(['view','editing_corners','editing','creating'])
	def updateElements(self):

		exists               = self.currentBaseplateExists
		module_exists        = self.page.sbOnModule.value()>=0
		#protomodule_exists   = 
		mode_view            = self.mode == 'view'
		mode_editing_corners = self.mode == 'editing_corners'
		mode_editing         = self.mode == 'editing'
		mode_creating        = self.mode == 'creating'

		self.page.pbEditCornerHeights.setEnabled( mode_view and exists )
		self.page.pbGoModule.setEnabled(          mode_view and module_exists )
		self.page.sbBaseplateID.setEnabled(       mode_view )
		self.page.pbSaveCorners.setEnabled(       mode_editing_corners )
		self.page.pbCancelCorners.setEnabled(     mode_editing_corners )
		self.page.dsbC0.setEnabled(               mode_editing_corners or mode_editing or mode_creating )
		self.page.dsbC1.setEnabled(               mode_editing_corners or mode_editing or mode_creating )
		self.page.dsbC2.setEnabled(               mode_editing_corners or mode_editing or mode_creating )
		self.page.dsbC3.setEnabled(               mode_editing_corners or mode_editing or mode_creating )
		self.page.dsbC4.setEnabled(               mode_editing_corners or mode_editing or mode_creating )
		self.page.dsbC5.setEnabled(               mode_editing_corners or mode_editing or mode_creating )
		self.setMainSwitchingEnabled(             mode_view )

		self.page.pbBaseplateNew.setEnabled(    mode_view and not exists )
		self.page.pbBaseplateEdit.setEnabled(   mode_view and     exists )
		self.page.pbBaseplateSave.setEnabled(   mode_creating or mode_editing )
		self.page.pbBaseplateCancel.setEnabled( mode_creating or mode_editing )

		self.page.leIdentifier.setReadOnly(    not (mode_creating or mode_editing) )
		self.page.leMaterial.setReadOnly(      not (mode_creating or mode_editing) )
		self.page.dsbNomThickness.setReadOnly( not (mode_creating or mode_editing) )
		# self.page.dsbFlatness.setReadOnly(     not (mode_creating or mode_editing) )
		self.page.dsbSize.setReadOnly(         not (mode_creating or mode_editing) )
		self.page.leManufacturer.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.sbOnModule.setReadOnly(      not (mode_creating or mode_editing) )

	@enforce_mode('view')
	def startEditingCorners(self,*args,**kwargs):
		#ID = self.page.sbBaseplateID.value()
		if self.currentBaseplateExists:
			self.mode = 'editing_corners'
			self.updateElements()

	@enforce_mode('editing_corners')
	def cancelEditingCorners(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode('editing_corners')
	def saveEditingCorners(self,*args,**kwargs):
		corner_heights = [_.value() for _ in self.corners]
		self.baseplate.corner_heights = [None if _<0 else _ for _ in corner_heights]
		self.baseplate.save()

		self.mode='view'
		self.update_info()

	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if not self.currentBaseplateExists:
			ID = self.page.sbBaseplateID.value()
			self.mode = 'creating'
			self.baseplate.new(ID)
			self.updateElements()
		else:
			pass

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if not self.currentBaseplateExists:
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
		corner_heights = [_.value() for _ in self.corners]
		self.baseplate.corner_heights = [None if _<0 else _ for _ in corner_heights]

		self.baseplate.identifier   = str(self.page.leIdentifier.text())
		self.baseplate.material     = str(self.page.leMaterial.text())

		nomthickness = self.page.dsbNomThickness.value()
		if nomthickness > 0:
			self.baseplate.nomthickness = nomthickness
		else:
			self.baseplate.nomthickness = None

		size = self.page.dsbSize.value()
		if size > 0:
			self.baseplate.size = size
		else:
			self.baseplate.size = None

		self.baseplate.manufacturer = str(self.page.leManufacturer.text())

		module = self.page.sbOnModule.value()
		if module >= 0:
			self.baseplate.module = module
		else:
			self.baseplate.module = None
			
		self.baseplate.save()
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
			self.page.sbBaseplateID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to view_baseplate")
		self.update_info()
		# later change this to only update if the baseplate loaded has changed
