nstr = lambda v:''  if v is None else str(v)
nflt = lambda v:0.0 if v is None else float(v)

PAGE_NAME = "view_baseplate"
DEBUG = False

class func(object):
	
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.currentBaseplateExists = None
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


	@enforce_mode('view')
	def update_info(self,ID=None):
		"""Loads info on the selected baseplate ID and updates UI elements accordingly"""
		if ID is None:ID = self.page.sbBaseplateID.value()
		self.info = self.fm.loadBaseplateDetails(ID)
		self.updateElements(use_info = True)

	@enforce_mode(['view','editing_corners'])
	def updateElements(self,use_info=False):
		if use_info:
			if self.info is None:
				self.currentBaseplateExists = False
				self.page.leIdentifier.setText('')
				self.page.leMaterial.setText('')
				self.page.dsbNomThickness.setValue(0.0)
				self.page.dsbFlatness.setValue(0.0)
				self.page.dsbSize.setValue(0.0)
				self.page.leManufacturer.setText('')
				self.page.leOnModule.setText('')
				self.page.dsbC0.clear()
				self.page.dsbC1.clear()
				self.page.dsbC2.clear()
				self.page.dsbC3.clear()
				self.page.dsbC4.clear()
				self.page.dsbC5.clear()
			else:
				self.currentBaseplateExists = True
				self.page.leIdentifier.setText(nstr(self.info['identifier']))
				self.page.leMaterial.setText(nstr(self.info['material']))
				self.page.dsbNomThickness.setValue(nflt(self.info['nomthickness']))
				self.page.dsbFlatness.setValue(nflt(self.info['flatness']))
				self.page.dsbSize.setValue(nflt(self.info['size']))
				self.page.leManufacturer.setText(nstr(self.info['manufacturer']))
				self.page.leOnModule.setText(nstr(self.info['onModuleID']))
				self.page.dsbC0.clear() if self.info['c0'] is None else self.page.dsbC0.setValue(self.info['c0'])
				self.page.dsbC1.clear() if self.info['c1'] is None else self.page.dsbC1.setValue(self.info['c1'])
				self.page.dsbC2.clear() if self.info['c2'] is None else self.page.dsbC2.setValue(self.info['c2'])
				self.page.dsbC3.clear() if self.info['c3'] is None else self.page.dsbC3.setValue(self.info['c3'])
				self.page.dsbC4.clear() if self.info['c4'] is None else self.page.dsbC4.setValue(self.info['c4'])
				self.page.dsbC5.clear() if self.info['c5'] is None else self.page.dsbC5.setValue(self.info['c5'])

		self.page.pbEditCornerHeights.setEnabled( self.mode == 'view'                                    )
		self.page.pbGoModule.setEnabled(          self.mode == 'view'                                    )
		self.page.sbBaseplateID.setEnabled(       self.mode == 'view'                                    )
		self.page.pbSaveCorners.setEnabled(       self.mode == 'editing_corners'                         )
		self.page.pbCancelCorners.setEnabled(     self.mode == 'editing_corners'                         )
		self.page.dsbC0.setEnabled(               self.mode in ['editing_corners', 'creating_baseplate'] )
		self.page.dsbC1.setEnabled(               self.mode in ['editing_corners', 'creating_baseplate'] )
		self.page.dsbC2.setEnabled(               self.mode in ['editing_corners', 'creating_baseplate'] )
		self.page.dsbC3.setEnabled(               self.mode in ['editing_corners', 'creating_baseplate'] )
		self.page.dsbC4.setEnabled(               self.mode in ['editing_corners', 'creating_baseplate'] )
		self.page.dsbC5.setEnabled(               self.mode in ['editing_corners', 'creating_baseplate'] )
		self.setMainSwitchingEnabled(             self.mode == 'view'                                    )

		self.page.pbBaseplateNew.setEnabled(    self.mode == 'view'               )
		self.page.pbBaseplateEdit.setEnabled(   self.mode == 'view'               )
		self.page.pbBaseplateSave.setEnabled(   self.mode == 'creating_baseplate' )
		self.page.pbBaseplateCancel.setEnabled( self.mode == 'creating_baseplate' )

	@enforce_mode('view')
	def startEditingCorners(self,*args,**kwargs):
		ID = self.page.sbBaseplateID.value()
		if self.currentBaseplateExists:
			self.mode = 'editing_corners'
			self.updateElements()

	@enforce_mode('editing_corners')
	def cancelEditingCorners(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode('editing_corners')
	def saveEditingCorners(self,*args,**kwargs):
		ID = self.page.sbBaseplateID.value()
		values  = [_.value() for _ in self.corners]
		changes = {'c{}'.format(i):_ for i,_ in enumerate(values)}
		changes.update([['flatness',round(max(values)-min(values),6)]])
		self.fm.changeBaseplateDetails(ID,changes)

		self.mode='view'
		self.update_info()


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
			self.page.sbBaseplateID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to view_baseplate")
		self.update_info()
		# later change this to only update if the baseplate loaded has changed