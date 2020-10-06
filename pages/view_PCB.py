PAGE_NAME = "view_pcb"
PARTTYPE = "PCB"
DEBUG = False

INDEX_SIZE = {
	8:0,
	"8":0,
	6:1,
	"6":1,
}

INDEX_SHAPE = {
	'full':0,
	'half':1,
	'five':2,
	'three':3,
	'semi':4,
	'semi(-)':5,
	'choptwo':6,
}

INDEX_CHIRALITY = {
	'achiral':0,
	'left':1,
	'right':2,
}

INDEX_CHECK = {
	'yes':0,
	'pass':0,
	True:0,
	'no':1,
	'fail':1,
	False:1,
}

INDEX_INSTITUTION = {
	'CERN':0,
	'FNAL':1,
	'UCSB':2,
	'UMN':3,
}

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
		self.page.sbID.valueChanged.connect(self.update_info)

		self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoShipment.clicked.connect(self.goShipment)

		self.page.pbDeleteComment.clicked.connect(self.deleteComment)
		self.page.pbAddComment.clicked.connect(self.addComment)

		self.page.pbGoStepPcb.clicked.connect(self.goStepPcb)
		self.page.pbGoModule.clicked.connect(self.goModule)

		self.page.pbAddToPlotter.clicked.connect(self.addToPlotter)
		self.page.pbGoPlotter.clicked.connect(self.goPlotter)


	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbID.value()
		else:
			self.page.sbID.setValue(ID)

		self.pcb_exists = self.pcb.load(ID)

		self.page.listShipments.clear()
		for shipment in self.pcb.shipments:
			print(self.pcb.shipments)
			self.page.listShipments.addItem(str(shipment))

		self.page.leInsertUser.setText(  "" if self.pcb.insertion_user is None else self.pcb.insertion_user)
		self.page.leLocation.setText(    "" if self.pcb.location     is None else self.pcb.location    )
		self.page.leIdentifier.setText(  "" if self.pcb.identifier   is None else self.pcb.identifier  )
		self.page.leManufacturer.setText("" if self.pcb.manufacturer is None else self.pcb.manufacturer)
		self.page.cbSize.setCurrentIndex(       INDEX_SIZE.get(       self.pcb.size,-1)        )
		self.page.cbShape.setCurrentIndex(      INDEX_SHAPE.get(      self.pcb.shape,-1)       )
		self.page.cbChirality.setCurrentIndex(  INDEX_CHIRALITY.get(  self.pcb.chirality,-1)   )
		self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.pcb.institution, -1))
		self.page.sbChannels.setValue(-1 if self.pcb.channels is None else self.pcb.channels)
		self.page.sbRotation.setValue(-1 if self.pcb.rotation is None else self.pcb.rotation)
		if self.page.sbChannels.value() == -1: self.page.sbChannels.clear()
		if self.page.sbRotation.value() == -1: self.page.sbRotation.clear()

		self.page.listComments.clear()
		for comment in self.pcb.comments:
			self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		self.page.leDaq.setText("" if self.pcb.daq is None else self.pcb.daq)
		self.page.cbInspection.setCurrentIndex(INDEX_CHECK.get(self.pcb.inspection, -1))
		self.page.cbDaqOK.setCurrentIndex(     INDEX_CHECK.get(self.pcb.daq_ok    , -1))
		self.page.dsbFlatness.setValue( -1 if self.pcb.flatness  is None else self.pcb.flatness )
		self.page.dsbThickness.setValue(-1 if self.pcb.thickness is None else self.pcb.thickness)
		if self.page.dsbFlatness.value()  == -1: self.page.dsbFlatness.clear()
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()

		self.page.sbStepPcb.setValue(-1 if self.pcb.step_pcb is None else self.pcb.step_pcb)
		self.page.sbModule.setValue( -1 if self.pcb.module   is None else self.pcb.module  )
		if self.page.sbStepPcb.value() == -1: self.page.sbStepPcb.clear()
		if self.page.sbModule.value()  == -1: self.page.sbModule.clear()

		self.page.listDaqData.clear()
		for daq in self.pcb.daq_data:
			self.page.listDaqData.addItem(daq)

		self.updateElements()


	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		pcb_exists      = self.pcb_exists
		shipments_exist = self.page.listShipments.count() > 0
		daq_data_exists = self.page.listDaqData.count()   > 0

		step_pcb_exists = self.page.sbStepPcb.value() >=0
		module_exists   = self.page.sbModule.value()  >=0

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbID.setEnabled(mode_view)
				
		self.page.pbNew.setEnabled(    mode_view and not pcb_exists  )
		self.page.pbEdit.setEnabled(   mode_view and     pcb_exists  )
		self.page.pbSave.setEnabled(   mode_editing or mode_creating )
		self.page.pbCancel.setEnabled( mode_editing or mode_creating )

		self.page.pbGoShipment.setEnabled(mode_view and shipments_exist)

		self.page.leInsertUser.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.leLocation.setReadOnly(     not (mode_creating or mode_editing) )
		self.page.leIdentifier.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.leManufacturer.setReadOnly( not (mode_creating or mode_editing) )
		self.page.cbSize.setEnabled(               mode_creating or mode_editing  )
		self.page.cbShape.setEnabled(              mode_creating or mode_editing  )
		self.page.cbChirality.setEnabled(          mode_creating or mode_editing  )
		self.page.cbInstitution.setEnabled(        mode_creating or mode_editing  )
		self.page.sbChannels.setReadOnly(     not (mode_creating or mode_editing) )
		self.page.sbRotation.setReadOnly(     not (mode_creating or mode_editing) )

		self.page.pbDeleteComment.setEnabled(mode_creating or mode_editing)
		self.page.pbAddComment.setEnabled(   mode_creating or mode_editing)
		self.page.pteWriteComment.setEnabled(mode_creating or mode_editing)

		self.page.leDaq.setReadOnly(        not (mode_creating or mode_editing) )
		self.page.cbInspection.setEnabled(       mode_creating or mode_editing  )
		self.page.cbDaqOK.setEnabled(            mode_creating or mode_editing  )
		self.page.dsbFlatness.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.dsbThickness.setReadOnly( not (mode_creating or mode_editing) )

		self.page.sbStepPcb.setEnabled(mode_view and step_pcb_exists)
		self.page.sbModule.setEnabled( mode_view and module_exists  )

		self.page.pbAddToPlotter.setEnabled(mode_view and daq_data_exists)
		self.page.pbGoPlotter.setEnabled(   mode_view and daq_data_exists)


	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if not self.pcb_exists:
			ID = self.page.sbID.value()
			self.mode = 'creating'
			self.pcb.new(ID)
			self.updateElements()
		else:
			pass

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if self.pcb_exists:
			self.mode = 'editing'
			self.updateElements()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):

		self.pcb.insertion_user = str(self.page.leInsertUser.text()    )   if str(self.page.leInsertUser.text()        ) else None
		self.pcb.location     = str(self.page.leLocation.text()        )   if str(self.page.leLocation.text()          ) else None
		self.pcb.identifier   = str(self.page.leIdentifier.text()      )   if str(self.page.leIdentifier.text()        ) else None
		self.pcb.manufacturer = str(self.page.leManufacturer.text()    )   if str(self.page.leManufacturer.text()      ) else None
		self.pcb.size         = str(self.page.cbSize.currentText()     )   if str(self.page.cbSize.currentText()       ) else None
		self.pcb.shape        = str(self.page.cbShape.currentText()    )   if str(self.page.cbShape.currentText()      ) else None
		self.pcb.chirality    = str(self.page.cbChirality.currentText())   if str(self.page.cbChirality.currentText()  ) else None
		self.pcb.institution  = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None
		self.pcb.channels     =     self.page.sbChannels.value()           if     self.page.sbChannels.value() >=0       else None
		self.pcb.rotation     =     self.page.sbRotation.value()           if     self.page.sbRotation.value() >=0       else None

		num_comments = self.page.listComments.count()
		self.pcb.comments = []
		for i in range(num_comments):
			self.pcb.comments.append(str(self.page.listComments.item(i).text()))

		self.pcb.daq        = str(self.page.leDaq.text()              ) if str(self.page.leDaq.text()              ) else None
		self.pcb.inspection = str(self.page.cbInspection.currentText()) if str(self.page.cbInspection.currentText()) else None
		self.pcb.daq_ok     = str(self.page.cbDaqOK.currentText()     ) if str(self.page.cbDaqOK.currentText()     ) else None
		self.pcb.flatness   =     self.page.dsbFlatness.value()         if     self.page.dsbFlatness.value()  >=0    else None
		self.pcb.thickness  =     self.page.dsbThickness.value()        if     self.page.dsbThickness.value() >=0    else None

		self.pcb.save()
		self.mode = 'view'
		self.update_info()



	@enforce_mode(['editing','creating'])
	def deleteComment(self,*args,**kwargs):
		row = self.page.listComments.currentRow()
		if row >= 0:
			self.page.listComments.takeItem(row)

	@enforce_mode(['editing','creating'])
	def addComment(self,*args,**kwargs):
		text = str(self.page.pteWriteComment.toPlainText())
		if text:
			self.page.listComments.addItem(text)
			self.page.pteWriteComment.clear()

	@enforce_mode('view')
	def goShipment(self,*args,**kwargs):
		item = self.page.listShipments.currentItem()
		if not (item is None):
			self.setUIPage('shipments',ID=str(item.text()))

	@enforce_mode('view')
	def goModule(self,*args,**kwargs):
		ID = self.page.sbModule.value()
		if ID >= 0:
			self.setUIPage('modules',ID=ID)
	
	@enforce_mode('view')
	def goStepPcb(self,*args,**kwargs):
		ID = self.page.sbStepPcb.value()
		if ID >= 0:
			self.setUIPage('PCBs',ID=ID)

	@enforce_mode('view')
	def addToPlotter(self,*args,**kwargs):
		print("not implemented yet - waiting for plotter page to be implemented")

	@enforce_mode('view')
	def goPlotter(self,*args,**kwargs):
		self.setUIPage('plotter',which='daq')




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
