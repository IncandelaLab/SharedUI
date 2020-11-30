from filemanager import fm

PAGE_NAME = "view_baseplate"
OBJECTTYPE = "baseplate"
DEBUG = False

DISPLAY_PRECISION = 4

INDEX_SIZE = {
	8:0,
	"8":0,
	6:1,
	"6":1,
}

INDEX_MATERIAL = {
	'Cu':0,
	'CuW':1,
	'PCB':2,
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

		self.baseplate_exists = None
		self.baseplate = fm.baseplate()

		self.mode = 'setup'

		# NEW:  List of all modified XML files
		self.xmlModList = []


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
		#self.page.sbID.valueChanged.connect(self.update_info)
		# Experimental:
		self.page.leID.textChanged.connect( self.update_info )

		self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoShipment.clicked.connect(self.goShipment)

		self.page.pbDeleteComment.clicked.connect(self.deleteComment)
		self.page.pbAddComment.clicked.connect(self.addComment)

		self.page.pbGoStepKapton.clicked.connect(self.goStepKapton)

		self.page.pbGoStepSensor.clicked.connect(self.goStepSensor)
		self.page.pbGoProtomodule.clicked.connect(self.goProtomodule)

		self.page.pbGoModule.clicked.connect(self.goModule)

		self.corners = [
			self.page.dsbC0,
			self.page.dsbC1,
			self.page.dsbC2,
			self.page.dsbC3,
			self.page.dsbC4,
			self.page.dsbC5
			]


	@enforce_mode(['view', 'editing', 'creating']) # NEW:  Now allowed in editing, creating mode
	def update_info(self,ID=None):
		"""Loads info on the selected baseplate ID and updates UI elements accordingly"""
		# IMPORTANT CHANGE:  Baseplate load and existence check have been moved to startCreating/Editing()!
		# Uncommenting this to see what happens...
		if ID is None:
			ID = self.page.leID.text()
		else:
			#self.page.sbID.setValue(ID)
			self.page.leID.setText(ID)

		self.baseplate_exists = self.baseplate.load(ID)

		#self.page.leID.setText(self.baseplate.ID)

		self.page.listShipments.clear()
		for shipment in self.baseplate.shipments:
			self.page.listShipments.addItem(str(shipment))

		self.page.cbShape      .setCurrentIndex(INDEX_SHAPE.get(      self.baseplate.shape      , -1))
		self.page.cbChirality  .setCurrentIndex(INDEX_CHIRALITY.get(  self.baseplate.chirality  , -1))
		self.page.cbMaterial   .setCurrentIndex(INDEX_MATERIAL.get(   self.baseplate.material   , -1))
		self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.baseplate.institution, -1))
		self.page.leInsertUser   .setText("" if self.baseplate.insertion_user  is None else self.baseplate.insertion_user  )
		self.page.leBarcode      .setText("" if self.baseplate.barcode         is None else self.baseplate.barcode         )
		self.page.leLocation     .setText("" if self.baseplate.location        is None else self.baseplate.location        )
		self.page.leManufacturer .setText("" if self.baseplate.manufacturer    is None else self.baseplate.manufacturer    )
		self.page.dsbNomThickness.setValue(-1 if self.baseplate.nomthickness   is None else self.baseplate.nomthickness    )
		if self.page.dsbNomThickness.value() == -1: self.page.dsbNomThickness.clear()

		self.page.listComments.clear()
		for comment in self.baseplate.comments:
			self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		if self.baseplate.corner_heights is None:
			for corner in self.corners:
				corner.setValue(-1)
				corner.clear()
		else:
			for i,corner in enumerate(self.corners):
				corner.setValue(-1 if self.baseplate.corner_heights[i] is None else self.baseplate.corner_heights[i])
				if corner.value() == -1: corner.clear()

		self.page.leFlatness.setText("" if self.baseplate.flatness is None else str(round(self.baseplate.flatness,DISPLAY_PRECISION)))
		self.page.dsbThickness.setValue(-1 if self.baseplate.thickness is None else self.baseplate.thickness)
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()

		self.page.sbStepKapton.setValue(-1 if self.baseplate.step_kapton is None else self.baseplate.step_kapton)
		if self.page.sbStepKapton.value() == -1: self.page.sbStepKapton.clear()

		self.page.cbCheckEdgesFirm.setCurrentIndex(INDEX_CHECK.get(self.baseplate.check_edges_firm, -1))
		self.page.cbCheckGlueSpill.setCurrentIndex(INDEX_CHECK.get(self.baseplate.check_glue_spill, -1))
		self.page.dsbKaptonFlatness.setValue(-1 if self.baseplate.kapton_flatness is None else self.baseplate.kapton_flatness)
		if self.page.dsbKaptonFlatness.value() == -1: self.page.dsbKaptonFlatness.clear()

		self.page.sbStepSensor.setValue( -1 if self.baseplate.step_sensor is None else self.baseplate.step_sensor)
		#self.page.sbProtomodule.setValue(-1 if self.baseplate.protomodule is None else self.baseplate.protomodule)
		#self.page.sbModule.setValue(     -1 if self.baseplate.module      is None else self.baseplate.module     )
		self.page.leProtomodule.setText("" if self.baseplate.protomodule is None else self.baseplate.protomodule)
		self.page.leModule.setText(     "" if self.baseplate.module      is None else self.baseplate.module)
		if self.page.sbStepSensor.value()  == -1: self.page.sbStepSensor.clear()
		#if self.page.sbProtomodule.value() == -1: self.page.sbProtomodule.clear()
		#if self.page.sbModule.value()      == -1: self.page.sbModule.clear()

		self.updateElements()


	@enforce_mode(['view','editing_corners','editing','creating'])
	def updateElements(self):
		# NEW:
		self.page.leStatus.setText(self.mode)

		exists = self.baseplate_exists
		shipments_exist = self.page.listShipments.count() > 0

		step_kapton_exists   = self.page.sbStepKapton.value()   >=0
		step_senor_exists    = self.page.sbStepSensor.value()   >=0
		#protomodule_exists   = self.page.sbProtomodule.value()  >=0
		#module_exists        = self.page.sbModule.value()       >=0
		protomodule_exists   = self.page.leProtomodule.text() != ""
		module_exists        = self.page.leModule.text()      != ""

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'

		self.setMainSwitchingEnabled(mode_view)
		#self.page.sbID.setEnabled(mode_view)
		self.page.leID.setReadOnly(not mode_view)

		# MODIFIED:
		self.page.pbNew.setEnabled(    mode_view and not exists )
		self.page.pbEdit.setEnabled(   mode_view and     exists )
		self.page.pbSave.setEnabled(   mode_creating or mode_editing )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing )

		self.page.pbGoShipment.setEnabled(mode_view and shipments_exist)

		self.page.cbShape.setEnabled(               mode_creating or mode_editing  )
		self.page.cbChirality.setEnabled(           mode_creating or mode_editing  )
		self.page.cbInstitution.setEnabled(         mode_creating or mode_editing  )
		self.page.leInsertUser.setReadOnly(    not (mode_creating or mode_editing) )
		self.page.leBarcode.setReadOnly(       not (mode_creating or mode_editing) )
		self.page.leManufacturer.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.leLocation.setReadOnly(      not (mode_creating or mode_editing) )
		self.page.dsbNomThickness.setReadOnly( not (mode_creating or mode_editing) )

		self.page.pbDeleteComment.setEnabled(mode_creating or mode_editing)
		self.page.pbAddComment.setEnabled(   mode_creating or mode_editing)
		self.page.pteWriteComment.setEnabled(mode_creating or mode_editing)

		for corner in self.corners:
			corner.setReadOnly(not (mode_creating or mode_editing))
		self.page.dsbThickness.setReadOnly(not (mode_creating or mode_editing))

		self.page.pbGoStepKapton.setEnabled(mode_view and step_kapton_exists)
		self.page.cbCheckEdgesFirm.setEnabled(mode_creating or mode_editing)
		self.page.cbCheckGlueSpill.setEnabled(mode_creating or mode_editing)
		self.page.dsbKaptonFlatness.setReadOnly(not (mode_creating or mode_editing))

		self.page.pbGoStepSensor.setEnabled(mode_view and step_senor_exists)
		self.page.pbGoProtomodule.setEnabled(mode_view and protomodule_exists)
		self.page.pbGoModule.setEnabled(mode_view and module_exists)




	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if self.page.leID.text() == "":
			self.page.leStatus.setText("input an ID")
			return
		# Check whether baseplate exists:
		tmp_baseplate = fm.baseplate()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_baseplate.load(tmp_ID)
		#if not self.baseplate_exists:
		if not tmp_exists:  # DNE; good to create
			ID = self.page.leID.text()
			self.baseplate.new(ID)
			self.mode = 'creating'  # update_info needs mode==view
			self.updateElements()
		else:
			# pass
			self.page.leStatus.setText("already exists")

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_baseplate = fm.baseplate()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_baseplate.load(tmp_ID)
		#if not self.baseplate_exists:
		if not tmp_exists:
			#pass
			self.page.leStatus.setText("does not exist")
		else:
			self.baseplate = tmp_baseplate
			self.mode = 'editing'
			self.update_info()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):
		print("SAVING, ID=", self.baseplate.ID)

		self.baseplate.shape          = str(self.page.cbShape.currentText())       if str(self.page.cbShape.currentText())       else None
		self.baseplate.chirality      = str(self.page.cbChirality.currentText())   if str(self.page.cbChirality.currentText())   else None
		self.baseplate.material       = str(self.page.cbMaterial.currentText())    if str(self.page.cbMaterial.currentText())    else None
		self.baseplate.institution    = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None
		self.baseplate.insertion_user = str(self.page.leInsertUser.text())         if str(self.page.leInsertUser.text())         else None
		self.baseplate.manufacturer   = str(self.page.leManufacturer.text())       if str(self.page.leManufacturer.text())       else None
		self.baseplate.location       = str(self.page.leLocation.text())           if str(self.page.leLocation.text())           else None
		self.baseplate.barcode        = str(self.page.leBarcode.text())            if str(self.page.leBarcode.text())            else None
		self.baseplate.nomthickness   =     self.page.dsbNomThickness.value()      if self.page.dsbNomThickness.value() >=0      else None

		num_comments = self.page.listComments.count()
		self.baseplate.comments = []
		for i in range(num_comments):
			self.baseplate.comments.append(str(self.page.listComments.item(i).text()))

		self.baseplate.corner_heights = [_.value() if _.value()>=0 else None for _ in self.corners]
		self.baseplate.thickness = self.page.dsbThickness.value() if self.page.dsbThickness.value()>=0 else None

		self.baseplate.check_edges_firm = str(self.page.cbCheckEdgesFirm.currentText()) if str(self.page.cbCheckEdgesFirm.currentText()) else None
		self.baseplate.check_glue_spill = str(self.page.cbCheckGlueSpill.currentText()) if str(self.page.cbCheckGlueSpill.currentText()) else None
		self.baseplate.kapton_flatness  =     self.page.dsbKaptonFlatness.value()       if self.page.dsbKaptonFlatness.value() >=0       else None

		self.baseplate.save()
		self.mode = 'view'
		self.update_info()

		self.xmlModList.append(self.baseplate.ID)


	def xmlModified(self):
		return self.xmlModList

	def xmlModifiedReset(self):
		self.xmlModList = []



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
	def goStepKapton(self,*args,**kwargs):
		ID = self.page.sbStepKapton.value()
		if ID >= 0:
			self.setUIPage('kapton placement steps',ID=ID)


	@enforce_mode('view')
	def goStepSensor(self,*args,**kwargs):
		ID = self.page.sbStepSensor.value()
		if ID >= 0:
			self.setUIPage('sensor placement steps',ID=ID)
	
	@enforce_mode('view')
	def goProtomodule(self,*args,**kwargs):
		#ID = self.page.sbProtomodule.value()
		#if ID >= 0:
		ID = self.page.leProtomodule.text()
		if ID != "":
			self.setUIPage('protomodules',ID=ID)

	@enforce_mode('view')
	def goModule(self,*args,**kwargs):
		#ID = self.page.sbModule.value()
		#if ID >= 0:
		ID = self.page.leModule.text()
		if ID != "":
			self.setUIPage('modules',ID=ID)



	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			#if not (type(ID) is int):
			#	raise TypeError("Expected type <int> for ID; got <{}>".format(type(ID)))
			if not (type(ID) is str):
				raise TypeError("Expected type <str> for ID; got <{}>".format(type(ID)))
			#if ID < 0:
			#	raise ValueError("ID cannot be negative")
			self.page.leID.setText(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to view_baseplate")
		self.update_info()
