from filemanager import parts

PAGE_NAME = "view_protomodule"
OBJECTTYPE = "protomodule"
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

INDEX_SHAPE = {
	'Full':0,
	'Top':1,
	'Bottom':2,
	'Left':3,
	'Right':4,
	'Five':5,
	'Full+Three':6,
}

INDEX_TYPE = {
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

		self.protomodule        = parts.protomodule()
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
		self.page.leID.textChanged.connect(self.loadPart)
		# self.page.pbLoad.clicked.connect(self.loadPart)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoStepSensor.clicked.connect(self.goStepSensor)
		self.page.pbGoSensor.clicked.connect(self.goSensor)
		self.page.pbGoBaseplate.clicked.connect(self.goBaseplate)
		self.page.pbGoStepPcb.clicked.connect(self.goStepPcb)
		self.page.pbGoModule.clicked.connect(self.goModule)

		self.page.pbDeleteComment.clicked.connect(self.deleteComment)
		self.page.pbAddComment.clicked.connect(self.addComment)


	@enforce_mode(['view', 'editing'])
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.leID.text()
		else:
			self.page.leID.setText(ID)

		self.protomodule_exists = (ID == self.protomodule.ID)

		self.page.cbInsertUser.clear()
		auth_users = self.userManager.getAuthorizedUsers(PAGE_NAME)
		self.index_users = {auth_users[i]:i for i in range(len(auth_users))}
		for user in self.index_users.keys():
			self.page.cbInsertUser.addItem(user)

		if not self.protomodule.record_insertion_user in self.index_users.keys() and len(self.index_users.keys())!=0 and not self.protomodule.record_insertion_user is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.protomodule.record_insertion_user] = max(self.index_users.values()) + 1
			self.page.cbInsertUser.addItem(self.protomodule.record_insertion_user)
		self.page.cbInsertUser.setCurrentIndex(self.index_users.get(self.protomodule.record_insertion_user, -1))

		self.page.cbInstitution.setCurrentIndex(   INDEX_INSTITUTION.get(self.protomodule.location, -1)    )
		#self.page.leLocation.setText(    "" if self.protomodule.institution_location     is None else     self.protomodule.institution_location    )

		self.page.cbType.setCurrentIndex(     INDEX_TYPE.get(     self.protomodule.channel_density, -1))
		self.page.cbShape.setCurrentIndex(    INDEX_SHAPE.get(    self.protomodule.geometry    ,-1))
		self.page.cbGrade.setCurrentIndex(    INDEX_GRADE.get(    self.protomodule.grade    ,-1))
		#self.page.sbChannels.setValue(   -1 if self.protomodule.channels  is None else self.protomodule.channels  )
		#if self.page.sbChannels.value()   == -1: self.page.sbChannels.clear()

		self.page.listComments.clear()
		if self.protomodule.comments:
			for comment in self.protomodule.comments.split(';;'):
				self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		if self.protomodule.step_sensor:
			tmp_inst, tmp_id = self.protomodule.step_sensor.split("_")
			self.page.sbStepSensor.setValue(int(tmp_id))
			self.page.cbInstitutionStepSensor.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))
		else:
			self.page.sbStepSensor.clear()
			self.page.cbInstitutionStepSensor.setCurrentIndex(-1)

		self.page.leSensor.setText(     "" if self.protomodule.sensor      is None else str(self.protomodule.sensor)     )
		self.page.leBaseplate.setText(  "" if self.protomodule.baseplate   is None else str(self.protomodule.baseplate)  )

		self.page.dsbOffsetTranslationX.setValue(-1 if self.protomodule.snsr_x_offst is None else self.protomodule.snsr_x_offst )
		self.page.dsbOffsetTranslationY.setValue(-1 if self.protomodule.snsr_y_offst is None else self.protomodule.snsr_y_offst )
		self.page.dsbOffsetRotation.setValue(    -1 if self.protomodule.snsr_ang_offst    is None else self.protomodule.snsr_ang_offst    )
		self.page.dsbFlatness.setValue(          -1 if self.protomodule.flatness           is None else self.protomodule.flatness           )
		self.page.dsbThickness.setValue( -1 if self.protomodule.thickness is None else self.protomodule.thickness )
		if self.page.dsbOffsetTranslationX.value() == -1: self.page.dsbOffsetTranslationX.clear()
		if self.page.dsbOffsetTranslationY.value() == -1: self.page.dsbOffsetTranslationY.clear()
		if self.page.dsbOffsetRotation.value() == -1: self.page.dsbOffsetRotation.clear()
		if self.page.dsbFlatness.value() == -1: self.page.dsbFlatness.clear()
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()

		if self.protomodule.step_pcb:
			tmp_inst, tmp_id = self.protomodule.step_pcb.split("_")
			self.page.sbStepPcb.setValue(int(tmp_id))
			self.page.cbInstitutionStepPcb.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))
		else:
			self.page.sbStepPcb.clear()
			self.page.cbInstitutionStepPcb.setCurrentIndex(-1)

		self.page.leModule.setText("" if self.protomodule.module is None else self.protomodule.module)

		self.updateElements()

	@enforce_mode(['view','editing'])
	def updateElements(self):
		if not self.mode == "view":
			self.page.leStatus.setText(self.mode)

		protomodule_exists = self.protomodule_exists

		step_sensor_exists = self.page.sbStepSensor.value() >=0 and \
		                     self.page.cbInstitutionStepSensor.currentText() != ""
		sensor_exists      = self.page.leSensor.text()      !=""
		baseplate_exists   = self.page.leBaseplate.text()   !=""
		step_pcb_exists    = self.page.sbStepPcb.value()    >=0 and \
		                     self.page.cbInstitutionStepPcb.currentText() != ""
		module_exists      = self.page.leModule.text()      !=""

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		
		self.setMainSwitchingEnabled(mode_view)
		self.page.leID.setReadOnly(not mode_view)

		# self.page.pbLoad.setEnabled(mode_view)

		self.page.pbEdit.setEnabled(    mode_view and     protomodule_exists )
		self.page.pbSave.setEnabled(    mode_editing )
		self.page.pbCancel.setEnabled(  mode_editing )

		#self.page.leLocation.setReadOnly(  not mode_editing )
		#self.page.cbType.setEnabled(           mode_editing )
		#self.page.cbShape.setEnabled(          mode_editing )
		# self.page.cbInstitution.setEnabled(    mode_editing )
		# self.page.cbInsertUser.setEnabled(     mode_editing )
		self.page.dsbThickness.setReadOnly(not mode_editing )

		self.page.pbDeleteComment.setEnabled(mode_editing)
		self.page.pbAddComment.setEnabled(   mode_editing)
		self.page.pteWriteComment.setEnabled(mode_editing)

		self.page.pbGoStepSensor.setEnabled( mode_view and step_sensor_exists )
		self.page.pbGoSensor.setEnabled(     mode_view and sensor_exists      )
		self.page.pbGoBaseplate.setEnabled(  mode_view and baseplate_exists   )
		self.page.pbGoStepPcb.setEnabled(    mode_view and step_pcb_exists    )
		self.page.pbGoModule.setEnabled(     mode_view and module_exists      )

		# Disable editting assemply data
		# self.page.dsbOffsetTranslationX.setReadOnly( not mode_editing )
		# self.page.dsbOffsetTranslationY.setReadOnly( not mode_editing )
		# self.page.dsbOffsetRotation.setReadOnly(     not mode_editing )
		# self.page.dsbFlatness.setReadOnly(           not mode_editing )
		# self.page.dsbThickness.setReadOnly(          not mode_editing )



	# NEW:
	@enforce_mode('view')
	def loadPart(self,*args,**kwargs):
		if self.page.leID.text == "":
			self.page.leStatus.setText("input an ID")
			return
		# Check whether baseplate exists:
		tmp_protomodule = parts.protomodule()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_protomodule.load(tmp_ID)
		if not tmp_exists:  # DNE; good to create
			self.page.leStatus.setText("protomodule DNE")
			self.update_info()
		else:
			self.protomodule = tmp_protomodule
			self.page.leStatus.setText("protomodule exists")
			self.update_info()



	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_protomodule = parts.protomodule()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_protomodule.load(tmp_ID)
		if not tmp_exists:
			self.page.leStatus.load(tmp_ID)
		else:
			self.protomodule = tmp_protomodule
			self.mode = 'editing'
			self.update_info()

	@enforce_mode('editing')
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode('editing')
	def saveEditing(self,*args,**kwargs):

		self.protomodule.pcb_plcment_x_offset = self.page.dsbOffsetTranslationX.value() if self.page.dsbOffsetTranslationX.value() >=0 else None 
		self.protomodule.pcb_plcment_y_offset = self.page.dsbOffsetTranslationY.value() if self.page.dsbOffsetTranslationY.value() >=0 else None 
		self.protomodule.offset_rotation      = self.page.dsbOffsetRotation.value()    if self.page.dsbOffsetRotation.value()    >=0 else None   
		self.protomodule.flatness = self.page.dsbFlatness.value()    if self.page.dsbFlatness.value()    >=0 else None
		self.protomodule.thickness = self.page.dsbThickness.value()    if self.page.dsbThickness.value()    >=0 else None

		num_comments = self.page.listComments.count()
		self.protomodule.comments = ';;'.join([self.page.listComments.item(i).text() for i in range(num_comments)])

		self.protomodule.save()
		self.mode = 'view'
		self.update_info()

	
	@enforce_mode('editing')
	def deleteComment(self,*args,**kwargs):
		row = self.page.listComments.currentRow()
		if row >= 0:
			self.page.listComments.takeItem(row)

	@enforce_mode('editing')
	def addComment(self,*args,**kwargs):
		text = str(self.page.pteWriteComment.toPlainText())
		if text:
			self.page.listComments.addItem(text)
			self.page.pteWriteComment.clear()

	@enforce_mode('view')
	def goStepSensor(self,*args,**kwargs):
		tmp_id = self.page.sbStepSensor.value()
		tmp_inst = self.page.cbInstitutionStepSensor.currentText()
		if tmp_id >= 0 and tmp_inst != "":
			self.setUIPage('1. Sensor - pre-assembly',ID="{}_{}".format(tmp_inst, tmp_id))

	@enforce_mode('view')
	def goSensor(self,*args,**kwargs):
		ID = self.page.leSensor.text()
		if ID != "":
			self.setUIPage('Sensors',ID=ID)

	@enforce_mode('view')
	def goBaseplate(self,*args,**kwargs):
		ID = self.page.leBaseplate.text()
		if ID != "":
			self.setUIPage('Baseplates',ID=ID)

	@enforce_mode('view')
	def goStepPcb(self,*args,**kwargs):
		tmp_id = self.page.sbStepPcb.value()
		tmp_inst = self.page.cbInstitutionStepPcb.currentText()
		if tmp_id >= 0 and tmp_inst != "":
			self.setUIPage('3. PCB - pre-assembly',ID="{}_{}".format(tmp_inst, tmp_id))

	@enforce_mode('view')
	def goModule(self,*args,**kwargs):
		ID = self.page.leModule.text()
		if ID != "":
			self.setUIPage('Modules',ID=ID)
		else:
			return


	def filesToUpload(self):
		# Return a list of all files to upload to DB
		if self.protomodule is None:
			return []
		else:
			return self.protomodule.filesToUpload()


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
