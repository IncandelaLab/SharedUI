from filemanager import parts
from PyQt5 import QtGui

PAGE_NAME = "view_baseplate"
OBJECTTYPE = "baseplate"
DEBUG = False

INDEX_MATERIAL = {
	'CuW/Kapton':0,
	'PCB/Kapton':1,
}

INDEX_SHAPE = {
	'Full':0,
	'Top':1,
	'Bottom':2,
	'Left':3,
	'Right':4,
	'Five':5,
	'Full+Three':6,
}

INDEX_CHECK = {
	'pass':0,
	True:0,
	'fail':1,
	False:1,
}

#TBD
INDEX_INSTITUTION = {
	'CERN':0,
	'FNAL':1,
	'UCSB':2,
	'UMN':3,
	'HEPHY':4,
	'HPK':5,
	'CMU':6,
	'TTU':7,
	'IHEP':8,
	'TIFR':9,
	'NTU':10,
	'FSU':11
}

INDEX_CHANNEL = {
	'HD':0,
	'LD':1,
}

INDEX_GRADE = {
	'Green':0,
	'Yellow':1,
	'Red':2,
}

class func(object):
	def __init__(self,fm,userManager,page,setUIPage,setSwitchingEnabled):
		self.userManager = userManager
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.baseplate_exists = False
		self.baseplate = parts.baseplate()

		self.mode = 'setup'

		# NEW:  List of all modified XML files
		self.xmlModList = []

		# NEW:  Fix image location
		pixmap = QtGui.QPixmap("pages_ui/pages_ui/baseplate_frame_80.png")

		self.page.plt_image.setPixmap(pixmap)


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
		self.page.pbLoad.clicked.connect(self.loadPart)
		self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoStepSensor.clicked.connect(self.goStepSensor)
		self.page.pbGoProtomodule.clicked.connect(self.goProtomodule)
		self.page.pbGoModule.clicked.connect(self.goModule)

		self.page.pbDeleteComment.clicked.connect(self.deleteComment)
		self.page.pbAddComment.clicked.connect(self.addComment)


	@enforce_mode(['view', 'editing', 'creating']) # NEW:  Now allowed in editing, creating mode
	def update_info(self,do_load=True,ID=None):
		"""Loads info on the selected baseplate ID and updates UI elements accordingly"""
		if ID is None:
			ID = self.page.leID.text()
		else:
			self.page.leID.setText(ID)

		self.baseplate_exists = (ID == self.baseplate.ID)

		# Moved - get available users and fill cbInsertUser
		self.page.cbInsertUser.clear()
		auth_users = self.userManager.getAuthorizedUsers(PAGE_NAME)
		self.index_users = {auth_users[i]:i for i in range(len(auth_users))}
		for user in self.index_users.keys():
			self.page.cbInsertUser.addItem(user)

		# was insertion_user
		if not self.baseplate.record_insertion_user in self.index_users.keys() and len(self.index_users.keys())!=0  and not self.baseplate.record_insertion_user is None:
			self.index_users[self.baseplate.record_insertion_user] = max(self.index_users.values()) + 1
			self.page.cbInsertUser.addItem(self.baseplate.record_insertion_user)
		self.page.cbInsertUser.setCurrentIndex(self.index_users.get(self.baseplate.record_insertion_user, -1))

		self.page.cbInstitution   .setCurrentIndex(INDEX_INSTITUTION.get(self.baseplate.location    , -1))
		#self.page.leLocation      .setText("" if self.baseplate.institution_location is None else self.baseplate.institution_location)

		self.page.leBarcode       .setText("" if self.baseplate.barcode  is None else self.baseplate.barcode )
		self.page.cbMaterial      .setCurrentIndex(INDEX_MATERIAL   .get(self.baseplate.material       , -1))
		# was shape
		self.page.cbShape         .setCurrentIndex(INDEX_SHAPE      .get(self.baseplate.geometry          , -1))
		self.page.cbChannelDensity.setCurrentIndex(INDEX_CHANNEL    .get(self.baseplate.channel_density, -1))

		self.page.listComments.clear()
		if self.baseplate.comments:
			for comment in self.baseplate.comments.split(';;'):
				self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()


		self.page.dsbThickness.setValue(-1 if self.baseplate.thickness is None else self.baseplate.thickness)
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()
		self.page.dsbFlatness .setValue(-1 if self.baseplate.flatness  is None else self.baseplate.flatness )
		if self.page.dsbFlatness.value() == -1: self.page.dsbFlatness.clear()
		self.page.cbGrade         .setCurrentIndex(INDEX_GRADE      .get(self.baseplate.grade          , -1))

		"""if self.baseplate.step_sensor:
			tmp_inst, tmp_id = self.baseplate.step_sensor.split("_")
			self.page.sbStepSensor.setValue(int(tmp_id))
			self.page.cbInstitutionStep.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))
		else:
			self.page.sbStepSensor.clear()
			self.page.cbInstitutionStep.setCurrentIndex(-1)
		if self.page.sbStepSensor.value() == -1: self.page.sbStepSensor.clear()
		self.page.leProtomodule.setText("" if self.baseplate.protomodule is None else self.baseplate.protomodule)
		self.page.leModule.setText(     "" if self.baseplate.module      is None else self.baseplate.module)
		"""
		self.updateElements()


	@enforce_mode(['view','editing','creating'])
	def updateElements(self):
		self.page.leStatus.setText(self.mode)

		baseplate_exists = self.baseplate_exists
		"""step_sensor_exists   = self.page.sbStepSensor.value() >= 0 and \
		                       self.page.cbInstitutionStep.currentText() != ""
		protomodule_exists   = self.page.leProtomodule.text() != ""
		module_exists        = self.page.leModule.text()      != ""
		"""
		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'

		self.setMainSwitchingEnabled(mode_view)
		self.page.leID.setReadOnly(not mode_view)

		self.page.pbLoad.setEnabled(   mode_view )
		self.page.pbNew.setEnabled(    mode_view and not baseplate_exists )
		self.page.pbEdit.setEnabled(   mode_view and     baseplate_exists )
		self.page.pbSave.setEnabled(   mode_creating or mode_editing )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing )


		self.page.cbInsertUser.setEnabled(      mode_creating or mode_editing  )
		self.page.cbInstitution.setEnabled(     mode_creating or mode_editing  )
		#self.page.leLocation.setReadOnly(  not (mode_creating or mode_editing) )

		self.page.leBarcode.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.cbMaterial.setEnabled(        mode_creating or mode_editing  )
		self.page.cbShape.setEnabled(           mode_creating or mode_editing  )
		self.page.cbChannelDensity.setEnabled(  mode_creating or mode_editing  )

		self.page.dsbThickness.setEnabled(      mode_creating or mode_editing  )
		self.page.dsbFlatness.setEnabled(       mode_creating or mode_editing  )
		self.page.cbGrade.setEnabled(           mode_creating or mode_editing  )

		self.page.pbDeleteComment.setEnabled(   mode_creating or mode_editing  )
		self.page.pbAddComment.setEnabled(      mode_creating or mode_editing  )
		self.page.pteWriteComment.setEnabled(   mode_creating or mode_editing  )

		"""self.page.pbGoStepSensor.setEnabled(    mode_view and step_sensor_exists)
		self.page.pbGoProtomodule.setEnabled(   mode_view and protomodule_exists)
		self.page.pbGoModule.setEnabled(        mode_view and module_exists)
		"""


	# NEW:
	@enforce_mode('view')
	def loadPart(self,*args,**kwargs):
		if self.page.leID.text == "":
			self.page.leStatus.setText("input an ID")
			return
		# Check whether baseplate exists:
		tmp_baseplate = parts.baseplate()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_baseplate.load(tmp_ID)
		if not tmp_exists:  # DNE; good to create
			self.page.leStatus.setText("baseplate DNE")
			self.update_info()
		else:
			self.baseplate = tmp_baseplate
			self.page.leStatus.setText("baseplate exists")
			self.update_info()


	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if self.page.leID.text() == "":
			self.page.leStatus.setText("input an ID")
			return
		# Check whether baseplate exists:
		tmp_baseplate = parts.baseplate()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_baseplate.load(tmp_ID)
		if not tmp_exists:  # DNE; good to create
			ID = self.page.leID.text()
			self.baseplate.new(ID)
			self.mode = 'creating'  # update_info needs mode==view
			self.update_info()
		else:
			self.page.leStatus.setText("already exists")

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_baseplate = parts.baseplate()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_baseplate.load(tmp_ID)
		if not tmp_exists:
			self.page.leStatus.setText("does not exist")
		else:
			self.baseplate = tmp_baseplate
			self.mode = 'editing'
			self.update_info()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.baseplate.clear()
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):

		self.baseplate.record_insertion_user    = str(self.page.cbInsertUser.currentText())  if str(self.page.cbInsertUser.currentText())  else None
		self.baseplate.location = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None
		#self.baseplate.institution_location          = str(self.page.leLocation.text())           if str(self.page.leLocation.text())           else None

		self.baseplate.barcode              = str(self.page.leBarcode.text())            if str(self.page.leBarcode.text())            else None
		self.baseplate.material             = str(self.page.cbMaterial.currentText())    if str(self.page.cbMaterial.currentText())    else None
		self.baseplate.geometry             = str(self.page.cbShape.currentText())       if str(self.page.cbShape.currentText())       else None
		self.baseplate.thickness            =     self.page.dsbThickness.value()         if self.page.dsbThickness.value() >=0         else None
		self.baseplate.flatness             =     self.page.dsbFlatness.value()          if self.page.dsbFlatness.value() >= 0         else None
		self.baseplate.channel_density      = str(self.page.cbChannelDensity.currentText()) if str(self.page.cbChannelDensity.currentText())  else None
		self.baseplate.grade                = str(self.page.cbGrade.currentText())       if str(self.page.cbGrade.currentText())       else None

		num_comments = self.page.listComments.count()
		self.baseplate.comments = ';;'.join([self.page.listComments.item(i).text() for i in range(num_comments)])

		self.baseplate.save()
		self.mode = 'view'
		self.update_info()

		self.xmlModList.append(self.baseplate.ID)

		self.baseplate.generate_xml()

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
	def goStepSensor(self,*args,**kwargs):
		tmp_id = self.page.sbStepSensor.value()
		tmp_inst = self.page.cbInstitutionStep.currentText()
		if tmp_id >= 0 and tmp_inst != "":
			self.setUIPage('1. Sensor - pre-assembly',ID="{}_{}".format(tmp_inst, tmp_id))
	
	@enforce_mode('view')
	def goProtomodule(self,*args,**kwargs):
		ID = self.page.leProtomodule.text()
		if ID != "":
			self.setUIPage('Protomodules',ID=ID)

	@enforce_mode('view')
	def goModule(self,*args,**kwargs):
		ID = self.page.leModule.text()
		if ID != "":
			self.setUIPage('Modules',ID=ID)


	def filesToUpload(self):
		# Return a list of all files to upload to DB
		if self.baseplate is None:
			return []
		else:
			return self.baseplate.filesToUpload()


	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is str):
				raise TypeError("Expected type <str> for ID; got <{}>".format(type(ID)))
			self.page.leID.setText(ID)
			self.loadPart()

	@enforce_mode('view')
	def changed_to(self):
		print("changed to view_baseplate")
		self.update_info()
