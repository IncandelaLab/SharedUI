nstr = lambda v:'' if v is None else str(v)

PAGE_NAME = "view_baseplate"
DEBUG = False

class func(object):
	
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.currentBaseplateExists = None
		self.editing = False

		self.is_setup = False

	def must_be_setup(function):
		def wrapper(self,*args,**kwargs):
			if self.is_setup:
				if DEBUG:print("page {} called {} with args {} and kwargs {} after setup. Executing.".format(PAGE_NAME, function, args, kwargs))
				return function(self,*args,**kwargs)
			else:
				print("Warning: page {} called {} with args {} and kwargs {} before setup. Not executing.".format(PAGE_NAME, function, args, kwargs))
				return
		return wrapper

	def setup(self):
		if not self.is_setup:
			self.rig()
			print("set up view_baseplate")
			self.is_setup = True

			self.update_info()

		else:
			print("warning: page {} setup function called after setup.".format(PAGE_NAME))


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

		# self.page.dsbC0.valueChanged.connect()
		# self.page.dsbC1.valueChanged.connect()
		# self.page.dsbC2.valueChanged.connect()
		# self.page.dsbC3.valueChanged.connect()
		# self.page.dsbC4.valueChanged.connect()
		# self.page.dsbC5.valueChanged.connect()

	@must_be_setup
	def update_info(self,ID=None):
		if ID is None:ID = self.page.sbBaseplateID.value()
		info = self.fm.loadBaseplateDetails(ID)

		if info is None:
			self.currentBaseplateExists = False
			self.page.leIdentifier.setText('')
			self.page.leMaterial.setText('')
			self.page.leNomThickness.setText('')
			self.page.leFlatness.setText('')
			self.page.leSize.setText('')
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
			self.page.leIdentifier.setText(nstr(info['identifier']))
			self.page.leMaterial.setText(nstr(info['material']))
			self.page.leNomThickness.setText(nstr(info['nomthickness']))
			self.page.leFlatness.setText(nstr(info['flatness']))
			self.page.leSize.setText(nstr(info['size']))
			self.page.leManufacturer.setText(nstr(info['manufacturer']))
			self.page.leOnModule.setText(nstr(info['onModuleID']))
			self.page.dsbC0.clear() if info['c0'] is None else self.page.dsbC0.setValue(info['c0'])
			self.page.dsbC1.clear() if info['c1'] is None else self.page.dsbC1.setValue(info['c1'])
			self.page.dsbC2.clear() if info['c2'] is None else self.page.dsbC2.setValue(info['c2'])
			self.page.dsbC3.clear() if info['c3'] is None else self.page.dsbC3.setValue(info['c3'])
			self.page.dsbC4.clear() if info['c4'] is None else self.page.dsbC4.setValue(info['c4'])
			self.page.dsbC5.clear() if info['c5'] is None else self.page.dsbC5.setValue(info['c5'])

	@must_be_setup
	def udpateElements(self):
		self.page.pbEditCornerHeights.setEnabled(not self.editing)
		self.page.pbGoModule.setEnabled(not self.editing)
		self.page.sbBaseplateID.setEnabled(not self.editing)
		self.page.pbSaveCorners.setEnabled(self.editing)
		self.page.pbCancelCorners.setEnabled(self.editing)
		self.page.dsbC0.setEnabled(self.editing)
		self.page.dsbC1.setEnabled(self.editing)
		self.page.dsbC2.setEnabled(self.editing)
		self.page.dsbC3.setEnabled(self.editing)
		self.page.dsbC4.setEnabled(self.editing)
		self.page.dsbC5.setEnabled(self.editing)
		self.setMainSwitchingEnabled(not self.editing)

	@must_be_setup
	def startEditingCorners(self,*args,**kwargs):
		ID = self.page.sbBaseplateID.value()
		if self.currentBaseplateExists:
			self.editing = True
			self.udpateElements()

	@must_be_setup
	def cancelEditingCorners(self,*args,**kwargs):
		if self.editing:
			self.editing=False
			self.udpateElements()
			self.update_info()
		else:
			print("Warning: tried to cancel editing corners while not editing corners")

	@must_be_setup
	def saveEditingCorners(self,*args,**kwargs):
		if self.editing:
			ID = self.page.sbBaseplateID.value()
			values  = [_.value() for _ in self.corners]
			changes = {'c{}'.format(i):_ for i,_ in enumerate(values)}
			changes.update([['flatness',round(max(values)-min(values),6)]])
			self.fm.changeBaseplateDetails(ID,changes)
			self.editing=False
			self.udpateElements()
			self.update_info()
		else:
			print("Warning: tried to save editing corners while not editing corners")


	@must_be_setup
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

	@must_be_setup
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is int):
				raise TypeError("Expected type <int> for ID; got <{}>".format(type(ID)))
			if ID < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbBaseplateID.setValue(ID)

	@must_be_setup
	def changed_to(self):
		print("changed to view_baseplate")
		self.update_info()
		# later change this to only update if the baseplate loaded has changed