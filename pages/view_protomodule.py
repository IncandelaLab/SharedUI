from filemanager import fm

PAGE_NAME = "view_protomodule"
OBJECTTYPE = "protomodule"
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

INDEX_INSPECTION = {
	'pass':0,
	True:0,
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

		self.protomodule        = fm.protomodule()
		self.protomodule_exists = None

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
		#self.page.sbID.valueChanged.connect(self.update_info)
		self.page.leID.textChanged.connect(self.update_info)

		# No longer used; only created in production steps
		#self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoShipment.clicked.connect(self.goShipment)

		self.page.pbDeleteComment.clicked.connect(self.deleteComment)
		self.page.pbAddComment.clicked.connect(self.addComment)

		self.page.pbGoStepSensor.clicked.connect(self.goStepSensor)
		self.page.pbGoSensor.clicked.connect(self.goSensor)
		self.page.pbGoBaseplate.clicked.connect(self.goBaseplate)
		self.page.pbGoStepPcb.clicked.connect(self.goStepPcb)
		self.page.pbGoModule.clicked.connect(self.goModule)



	@enforce_mode(['view', 'editing', 'creating'])
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			#ID = self.page.sbID.value()
			ID = self.page.leID.text()
		else:
			#self.page.sbID.setValue(ID)
			self.page.leID.setText(ID)

		self.protomodule_exists = self.protomodule.load(ID)

		#self.page.leID.setText(self.protomodule.ID)

		self.page.listShipments.clear()
		for shipment in self.protomodule.shipments:
			self.page.listShipments.addItem(str(shipment))

		self.page.leInsertUser.setText(  "" if self.protomodule.insertion_user is None else   self.protomodule.insertion_user)
		self.page.leLocation.setText(    "" if self.protomodule.location     is None else     self.protomodule.location    )
		self.page.cbShape.setCurrentIndex(    INDEX_SHAPE.get(    self.protomodule.shape    ,-1))
		self.page.cbChirality.setCurrentIndex(INDEX_CHIRALITY.get(self.protomodule.chirality,-1))
		self.page.dsbThickness.setValue( -1 if self.protomodule.thickness is None else self.protomodule.thickness )
		self.page.sbChannels.setValue(   -1 if self.protomodule.channels  is None else self.protomodule.channels  )
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()
		if self.page.sbChannels.value()   == -1: self.page.sbChannels.clear()

		self.page.listComments.clear()
		for comment in self.protomodule.comments:
			self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		self.page.sbStepSensor.setValue(-1 if self.protomodule.step_sensor is None else self.protomodule.step_sensor)
		#self.page.sbSensor.setValue(    -1 if self.protomodule.sensor      is None else self.protomodule.sensor     )
		self.page.leSensor.setText(     "" if self.protomodule.sensor      is None else self.protomodule.sensor     )
		#self.page.sbBaseplate.setValue( -1 if self.protomodule.baseplate   is None else self.protomodule.baseplate  )
		self.page.leBaseplate.setText(  "" if self.protomodule.baseplate   is None else self.protomodule.baseplate  )
		if self.page.sbStepSensor.value() == -1: self.page.sbStepSensor.clear()
		#if self.page.sbSensor.value()     == -1: self.page.sbSensor.clear()
		#if self.page.sbBaseplate.value()  == -1: self.page.sbBaseplate.clear()

		self.page.cbCheckCracks.setCurrentIndex(   INDEX_INSPECTION.get(self.protomodule.check_cracks    , -1))
		self.page.cbCheckGlueSpill.setCurrentIndex(INDEX_INSPECTION.get(self.protomodule.check_glue_spill, -1))
		self.page.cbInstitution.setCurrentIndex(   INDEX_INSTITUTION.get(self.protomodule.institution, -1)    )
		self.page.dsbOffsetTranslationX.setValue( -1 if self.protomodule.offset_translation_x is None else self.protomodule.offset_translation_x )
		self.page.dsbOffsetTranslationY.setValue( -1 if self.protomodule.offset_translation_y is None else self.protomodule.offset_translation_y )
		self.page.dsbOffsetRotation.setValue(    -1 if self.protomodule.offset_rotation    is None else self.protomodule.offset_rotation    )
		self.page.dsbFlatness.setValue(          -1 if self.protomodule.flatness           is None else self.protomodule.flatness           )
		if self.page.dsbOffsetTranslationX.value() == -1: self.page.dsbOffsetTranslationX.clear()
		if self.page.dsbOffsetTranslationY.value() == -1: self.page.dsbOffsetTranslationY.clear()
		if self.page.dsbOffsetRotation.value() == -1: self.page.dsbOffsetRotation.clear()
		if self.page.dsbFlatness.value() == -1: self.page.dsbFlatness.clear()

		self.page.sbStepPcb.setValue(-1 if self.protomodule.step_pcb is None else self.protomodule.step_pcb)
		#self.page.sbModule.setValue( -1 if self.protomodule.module   is None else self.protomodule.module  )
		self.page.leModule.setText("" if self.protomodule.module is None else self.protomodule.module)
		if self.page.sbStepPcb.value() == -1: self.page.sbStepPcb.clear()
		#if self.page.sbModule.value() == -1: self.page.sbModule.clear()

		self.updateElements()

	@enforce_mode(['view','editing','creating'])
	def updateElements(self):
		self.page.leStatus.setText(self.mode)

		protomodule_exists = self.protomodule_exists
		shipments_exist    = self.page.listShipments.count() > 0

		step_sensor_exists = self.page.sbStepSensor.value() >=0
		#sensor_exists      = self.page.sbSensor.value()     >=0
		sensor_exists      = self.page.leSensor.text()      !=""
		#baseplate_exists   = self.page.sbBaseplate.value()  >=0
		baseplate_exists   = self.page.leBaseplate.text()   !=""
		step_pcb_exists    = self.page.sbStepPcb.value()    >=0
		#module_exists      = self.page.sbModule.value()     >=0
		module_exists      = self.page.leModule.text()      !=""

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'
		
		self.setMainSwitchingEnabled(mode_view)
		#self.page.sbID.setEnabled(mode_view)
		self.page.leID.setReadOnly(not mode_view)

		#self.page.pbNew.setEnabled(     mode_view and not protomodule_exists )
		self.page.pbEdit.setEnabled(    mode_view and     protomodule_exists )
		self.page.pbSave.setEnabled(    mode_editing or mode_creating )
		self.page.pbCancel.setEnabled(  mode_editing or mode_creating )

		self.page.pbGoShipment.setEnabled(mode_view and shipments_exist)

		self.page.leInsertUser.setReadOnly(not (mode_creating or mode_editing) )
		self.page.leLocation.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.cbShape.setEnabled(           mode_creating or mode_editing  )
		self.page.cbChirality.setEnabled(       mode_creating or mode_editing  )
		self.page.cbInstitution.setEnabled(     mode_creating or mode_editing  )
		self.page.dsbThickness.setReadOnly(not (mode_creating or mode_editing) )
		self.page.sbChannels.setReadOnly(  not (mode_creating or mode_editing) )

		self.page.pbDeleteComment.setEnabled(mode_creating or mode_editing)
		self.page.pbAddComment.setEnabled(   mode_creating or mode_editing)
		self.page.pteWriteComment.setEnabled(mode_creating or mode_editing)

		self.page.pbGoStepSensor.setEnabled( mode_view and step_sensor_exists )
		self.page.pbGoSensor.setEnabled(     mode_view and sensor_exists      )
		self.page.pbGoBaseplate.setEnabled(  mode_view and baseplate_exists   )
		self.page.pbGoStepPcb.setEnabled(    mode_view and step_pcb_exists    )
		self.page.pbGoModule.setEnabled(     mode_view and module_exists      )

		self.page.dsbOffsetTranslationX.setReadOnly( not (mode_creating or mode_editing) )
		self.page.dsbOffsetTranslationY.setReadOnly( not (mode_creating or mode_editing) )
		self.page.dsbOffsetRotation.setReadOnly(    not (mode_creating or mode_editing) )
		self.page.dsbFlatness.setReadOnly(          not (mode_creating or mode_editing) )
		self.page.cbCheckCracks.setEnabled(              mode_creating or mode_editing  )
		self.page.cbCheckGlueSpill.setEnabled(           mode_creating or mode_editing  )







	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		print("THIS IS OLD AND BROKEN; has not been updated.  Do not use this.")
		if not self.protomodule_exists:
		#	ID = self.page.sbID.value()
			ID = self.page.leID.value()
			self.mode = 'creating'
			self.protomodule.new(ID)
			self.updateElements()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_protomodule = fm.protomodule()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_protomodule.load(tmp_ID)
		if not tmp_exists:
			self.page.leStatus.load(tmp_ID)
		else:
			self.protomodule = tmp_protomodule
			self.mode = 'editing'
			self.update_info()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):

		self.protomodule.insertion_user = str(self.page.leInsertUser.text()      ) if str(self.page.leInsertUser.text()      ) else None
		self.protomodule.location     = str(self.page.leLocation.text()          ) if str(self.page.leLocation.text()        ) else None
		self.protomodule.shape        = str(self.page.cbShape.currentText()      ) if str(self.page.cbShape.currentText()    ) else None
		self.protomodule.chirality    = str(self.page.cbChirality.currentText()  ) if str(self.page.cbChirality.currentText()) else None
		self.protomodule.institution  = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None
		self.protomodule.thickness    =     self.page.dsbThickness.value()         if self.page.dsbThickness.value() >=0 else None
		self.protomodule.channels     =     self.page.sbChannels.value()           if self.page.sbChannels.value()   >=0 else None

		num_comments = self.page.listComments.count()
		self.protomodule.comments = []
		for i in range(num_comments):
			self.protomodule.comments.append(str(self.page.listComments.item(i).text()))

		self.protomodule.offset_translation	= self.page.dsbOffsetTranslation.value() if self.page.dsbOffsetTranslation.value() >=0 else None
		self.protomodule.offset_rotation	= self.page.dsbOffsetRotation.value()    if self.page.dsbOffsetRotation.value()    >=0 else None
		self.protomodule.flatness	        = self.page.dsbFlatness.value()          if self.page.dsbFlatness.value()          >=0 else None
		self.protomodule.check_cracks	    = str(self.page.cbCheckCracks.currentText()   ) if str(self.page.cbCheckCracks.currentText()   ) else None
		self.protomodule.check_glue_spill	= str(self.page.cbCheckGlueSpill.currentText()) if str(self.page.cbCheckGlueSpill.currentText()) else None

		self.protomodule.save()
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
	def goStepSensor(self,*args,**kwargs):
		ID = self.page.sbStepSensor.value()
		if ID >= 0:
			self.setUIPage('sensor placement steps',ID=ID)
	
	@enforce_mode('view')
	def goSensor(self,*args,**kwargs):
		#ID = self.page.sbSensor.value()
		ID = self.page.leSensor.text()
		#if ID >= 0:
		if ID != "":
			self.setUIPage('sensors',ID=ID)

	@enforce_mode('view')
	def goBaseplate(self,*args,**kwargs):
		#ID = self.page.sbBaseplate.value()
		ID = self.page.leBaseplate.text()
		#if ID >= 0:
		if ID != "":
			self.setUIPage('baseplates',ID=ID)

	@enforce_mode('view')
	def goStepPcb(self,*args,**kwargs):
		ID = self.page.sbStepPcb.value()
		if ID >=0:
			self.setUIPage('PCB placement steps',ID=ID)

	@enforce_mode('view')
	def goModule(self,*args,**kwargs):
		#ID = self.page.sbModule.value()
		ID = self.page.leModule.value()
		#if ID >= 0:
		if ID != "":
			self.setUIPage('modules',ID=ID)
		else:
			return



	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is str):
				raise TypeError("Expected type <str> for ID; got <{}>".format(type(ID)))
			#if ID < 0:
			#	raise ValueError("ID cannot be negative")
			#self.page.sbID.setValue(ID)
			self.page.leID.setText(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
