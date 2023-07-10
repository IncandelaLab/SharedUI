from filemanager import parts

PAGE_NAME = "view_sensor"
OBJECTTYPE = "sensor"
DEBUG = False

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

INDEX_TYPE = {
	'120um':0,
	'200um':1,
	'300um':2,
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

INDEX_INSPECTION = {
	'pass':0,
	True:0,
	'fail':1,
	False:1,
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

		self.sensor = parts.sensor()
		self.sensor_exists = False

		self.mode = 'setup'

		# NEW
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
		self.mode = 'view'
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


	@enforce_mode(['view', 'editing', 'creating'])
	def update_info(self,ID=None,do_load=True,*args,**kwargs):
		if ID is None:
			ID = self.page.leID.text()
		else:
			self.page.leID.setText(ID)

		self.sensor_exists = (ID == self.sensor.ID)

		self.page.cbInsertUser.clear()
		auth_users = self.userManager.getAuthorizedUsers(PAGE_NAME)
		self.index_users = {auth_users[i]:i for i in range(len(auth_users))}
		for user in self.index_users.keys():
			self.page.cbInsertUser.addItem(user)

		if not self.sensor.record_insertion_user in self.index_users.keys() and len(self.index_users.keys())!=0 and not self.sensor.record_insertion_user is None:
			self.index_users[self.sensor.record_insertion_user] = max(self.index_users.values()) + 1
			self.page.cbInsertUser.addItem(self.sensor.record_insertion_user)
		self.page.cbInsertUser.setCurrentIndex(self.index_users.get(self.sensor.record_insertion_user, -1))

		self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.sensor.location, -1))
		#self.page.leLocation.setText(    "" if self.sensor.institution_location     is None else self.sensor.institution_location    )

		self.page.leBarcode.setText(   "" if self.sensor.barcode     is None else self.sensor.barcode     )
		self.page.cbType.setCurrentIndex(       INDEX_TYPE.get(       self.sensor.sen_type,            -1))
		self.page.cbShape.setCurrentIndex(      INDEX_SHAPE.get(      self.sensor.geometry,           -1))
		self.page.cbChannelDensity.setCurrentIndex(INDEX_CHANNEL.get( self.sensor.channel_density, -1))
		self.page.cbInspection.setCurrentIndex( INDEX_INSPECTION.get( self.sensor.visual_inspection,      -1))
		self.page.cbGrade         .setCurrentIndex(INDEX_GRADE      .get(self.sensor.grade          , -1))

		self.page.listComments.clear()
		if self.sensor.comments:
			for comment in self.sensor.comments.split(';;'):
				self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()


		"""if self.sensor.step_sensor:
			tmp_inst, tmp_id = self.sensor.step_sensor.split("_")
			self.page.sbStepSensor.setValue(int(tmp_id))
			self.page.cbInstitutionStep.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))
		else:
			self.page.sbStepSensor.clear()
			self.page.cbInstitutionStep.setCurrentIndex(-1)
		self.page.leProtomodule.setText("" if self.sensor.protomodule is None else self.sensor.protomodule)
		self.page.leModule.setText(     "" if self.sensor.module      is None else self.sensor.module)
		"""
		self.updateElements()


	@enforce_mode(['view','editing','creating'])
	def updateElements(self):
		if not self.mode == "view":
			self.page.leStatus.setText(self.mode)

		sensor_exists      = self.sensor_exists
		"""step_sensor_exists = self.page.sbStepSensor.value()  >= 0 and \
		                     self.page.cbInstitutionStep.currentText() != ""
		protomodule_exists = self.page.leProtomodule.text()  != ""
		module_exists      = self.page.leModule.text()       != ""
		"""
		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'
		
		self.setMainSwitchingEnabled(mode_view)
		self.page.leID.setReadOnly(not mode_view)

		self.page.pbLoad.setEnabled(mode_view)
		self.page.pbNew.setEnabled(     mode_view and not sensor_exists )
		self.page.pbEdit.setEnabled(    mode_view and     sensor_exists )
		self.page.pbSave.setEnabled(    mode_editing or mode_creating )
		self.page.pbCancel.setEnabled(  mode_editing or mode_creating )


		self.page.cbInsertUser.setEnabled(         mode_creating or mode_editing  )
		self.page.cbInstitution.setEnabled(        mode_creating or mode_editing  )
		#self.page.leLocation.setReadOnly(     not (mode_creating or mode_editing) )

		self.page.leBarcode.setReadOnly(      not (mode_creating or mode_editing) )
		self.page.cbType.setEnabled(               mode_creating or mode_editing  )
		self.page.cbShape.setEnabled(              mode_creating or mode_editing  )
		self.page.cbChannelDensity.setEnabled(     mode_creating or mode_editing  )

		self.page.cbInspection.setEnabled(   mode_creating or mode_editing   )
		self.page.cbGrade.setEnabled(              mode_creating or mode_editing  )


		self.page.pbDeleteComment.setEnabled(mode_creating or mode_editing)
		self.page.pbAddComment.setEnabled(   mode_creating or mode_editing)
		self.page.pteWriteComment.setEnabled(mode_creating or mode_editing)

		"""self.page.pbGoStepSensor.setEnabled( mode_view and step_sensor_exists)
		self.page.pbGoProtomodule.setEnabled(mode_view and protomodule_exists)
		self.page.pbGoModule.setEnabled(     mode_view and module_exists     )
		"""


	# NEW:
	@enforce_mode('view')
	def loadPart(self,*args,**kwargs):
		if self.page.leID.text == "":
			self.page.leStatus.setText("input an ID")
			return
		# Check whether baseplate exists:
		tmp_sensor = parts.sensor()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_sensor.load(tmp_ID)
		if not tmp_exists:  # DNE; good to create
			self.page.leStatus.setText("sensor DNE")
			self.update_info()
		else:
			# pass
			self.sensor = tmp_sensor
			self.page.leStatus.setText("sensor exists")
			self.update_info()


	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if self.page.leID.text() == "":
			self.page.leStatus.setText("input an ID")
			return
		tmp_sensor = parts.sensor()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_sensor.load(tmp_ID)

		if not tmp_exists:
			ID = self.page.leID.text()
			self.sensor.new(ID)
			self.mode = 'creating'
			self.update_info()
		else:
			self.page.leStatus.setText("already exists")

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_sensor = parts.sensor()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_sensor.load(tmp_ID)
		if not tmp_exists:
			self.page.leStatus.setText("does not exist")
		else:
			self.sensor = tmp_sensor
			self.mode = 'editing'
			self.update_info()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.sensor.clear()
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):

		self.sensor.record_insertion_user  = str(self.page.cbInsertUser.currentText())     if str(self.page.cbInsertUser.currentText())  else None
		self.sensor.location     = str(self.page.cbInstitution.currentText())    if str(self.page.cbInstitution.currentText()) else None
		#self.sensor.institution_location        = str(self.page.leLocation.text()          )    if str(self.page.leLocation.text()    )       else None
		self.sensor.barcode         = str(self.page.leBarcode.text()           )    if str(self.page.leBarcode.text()     )       else None
		self.sensor.sen_type            = str(self.page.cbType.currentText()       )    if str(self.page.cbType.currentText() )       else None
		self.sensor.geometry           = str(self.page.cbShape.currentText()      )    if str(self.page.cbShape.currentText())       else None
		# NOTE:  channel_density is no longer auto-set
		#self.sensor.channel_density = str(self.page.cbChannelDensity.currentText()) if str(self.page.cbChannelDensity.currentText()) else None
		self.sensor.grade           = str(self.page.cbGrade.currentText())          if str(self.page.cbGrade.currentText())       else None

		num_comments = self.page.listComments.count()
		self.sensor.comments = ';;'.join([self.page.listComments.item(i).text() for i in range(num_comments)])

		self.sensor.visual_inspection = str(self.page.cbInspection.currentText()) if str(self.page.cbInspection.currentText()) else None

		self.sensor.save()
		self.mode = 'view'
		self.update_info()

		self.xmlModList.append(self.sensor.ID)

		self.sensor.generate_xml()


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
		if self.sensor is None:
			return []
		else:
			return self.sensor.filesToUpload()

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
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
