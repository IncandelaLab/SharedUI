from filemanager import parts
import os
import shutil
import glob

from PyQt5.QtWidgets import QFileDialog, QWidget


PAGE_NAME = "view_module"
DEBUG = False

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

INDEX_INSPECTION = {
	'pass':0,
	'fail':1,
}

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

INDEX_GRADE = {
	'Green':0,
	'Yellow':1,
	'Red':2,
}


class Filewindow(QWidget):
	def __init__(self):
		super(Filewindow, self).__init__()

	def getdir(self,*args,**kwargs):
		#fname, fmt = QFileDialog.getOpenFileName(self, 'Open file', '~',"(*.jpg *.png *.xml)")
		dname = str(QFileDialog.getExistingDirectory(self, "Select directory"))
		return dname


class func(object):
	def __init__(self,fm,userManager,page,setUIPage,setSwitchingEnabled):
		self.userManager = userManager
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.module = parts.module()
		self.module_exists = None
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
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoStepSensor.clicked.connect(   self.goStepSensor   )
		self.page.pbGoStepPcb.clicked.connect(      self.goStepPcb      )
		self.page.pbGoBaseplate.clicked.connect(    self.goBaseplate    )
		self.page.pbGoSensor.clicked.connect(       self.goSensor       )
		self.page.pbGoPcb.clicked.connect(          self.goPcb          )
		self.page.pbGoProtomodule.clicked.connect(  self.goProtomodule  )

		self.page.pbDeleteComment.clicked.connect(self.deleteComment)
		self.page.pbAddComment.clicked.connect(self.addComment)

		self.fwnd = Filewindow()
		self.page.pbAddFiles.clicked.connect(self.getFile)
		self.page.pbDeleteFile.clicked.connect(self.deleteFile)


	@enforce_mode(['view', 'editing'])
	def update_info(self,ID=None,do_load=True,*args,**kwargs):
		if ID is None:
			ID = self.page.leID.text()
		else:
			self.page.leID.setText(ID)
		
		self.module_exists = (ID == self.module.ID)
		
		self.page.cbInsertUser.clear()
		auth_users = self.userManager.getAuthorizedUsers(PAGE_NAME)
		self.index_users = {auth_users[i]:i for i in range(len(auth_users))}
		for user in self.index_users.keys():
			self.page.cbInsertUser.addItem(user)

		if not self.module.record_insertion_user in self.index_users.keys() and len(self.index_users.keys())!=0 and not self.module.record_insertion_user is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.module.record_insertion_user] = max(self.index_users.values()) + 1
			self.page.cbInsertUser.addItem(self.module.initiated_by_user)
		self.page.cbInsertUser.setCurrentIndex(self.index_users.get(self.module.record_insertion_user, -1))
		self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.module.location, -1))
		#self.page.leLocation.setText("" if self.module.institution_location is None else self.module.institution_location)

		# characteristics
		self.page.cbShape.setCurrentIndex(      INDEX_SHAPE.get(      self.module.geometry    , -1)  )
		self.page.cbResolution.setCurrentIndex( INDEX_TYPE.get(       self.module.channel_density, -1))
		self.page.cbGrade.setCurrentIndex(      INDEX_GRADE.get(      self.module.grade    , -1)  )
		self.page.cbInspection.setCurrentIndex( INDEX_INSPECTION.get( self.module.pre_inspection,  -1))

		# parts and steps
		if self.module.step_sensor:
			tmp_inst, tmp_id = self.module.step_sensor.split("_")
			self.page.sbStepSensor.setValue(int(tmp_id))
			self.page.cbInstitutionStepSensor.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))
		else:
			self.page.sbStepSensor.clear()
			self.page.cbInstitutionStepSensor.setCurrentIndex(-1)
		if self.module.step_pcb:
			tmp_inst, tmp_id = self.module.step_pcb.split("_")
			self.page.sbStepPcb.setValue(int(tmp_id))
			self.page.cbInstitutionStepPcb.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))
		else:
			self.page.sbStepPcb.clear()
			self.page.cbInstitutionStepPcb.setCurrentIndex(-1)

		# NOTE - TBD - may have to remove/comment
		self.page.leBaseplate.setText(    "" if self.module.baseplate     is None else self.module.baseplate     )
		self.page.leSensor.setText(       "" if self.module.sensor        is None else self.module.sensor        )
		self.page.lePcb.setText(          "" if self.module.pcb           is None else self.module.pcb           )
		self.page.leProtomodule.setText(  "" if self.module.protomodule   is None else self.module.protomodule   )
		if self.page.sbStepSensor.value()  == -1:  self.page.sbStepSensor.clear()
		if self.page.sbStepPcb.value()     == -1:  self.page.sbStepPcb.clear()
		if self.page.leBaseplate.text()    == -1:  self.page.leBaseplate.clear()
		if self.page.leSensor.text()       == -1:  self.page.leSensor.clear()
		if self.page.lePcb.text()          == -1:  self.page.lePcb.clear()
		if self.page.leProtomodule.text()  == -1:  self.page.leProtomodule.clear()

		self.page.ckWirebondingCompleted.setChecked(False if self.module.final_inspxn_ok is None else self.module.final_inspxn_ok)


		# comments
		self.page.listComments.clear()
		if self.module.comments:
			for comment in self.module.comments:
				self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()


		self.page.listFiles.clear()
		for f in self.module.test_files if self.module.test_files else []:
			name = os.path.split(f)[1]
			self.page.listFiles.addItem(name)

		self.page.dsbOffsetTranslationX.setValue( -1 if self.module.pcb_plcment_x_offset is None else self.module.pcb_plcment_x_offset )
		self.page.dsbOffsetTranslationY.setValue( -1 if self.module.pcb_plcment_y_offset is None else self.module.pcb_plcment_y_offset )
		self.page.dsbOffsetRotation.setValue(    -1 if self.module.pcb_plcment_ang_offset    is None else self.module.pcb_plcment_ang_offset )
		self.page.dsbThickness.setValue(-1 if self.module.thickness   is None else self.module.thickness  )
		self.page.dsbFlatness.setValue( -1 if self.module.flatness  is None else self.module.flatness   )
		if self.page.dsbOffsetTranslationX.value() == -1: self.page.dsbOffsetTranslationX.clear()
		if self.page.dsbOffsetTranslationY.value() == -1: self.page.dsbOffsetTranslationY.clear()
		if self.page.dsbOffsetRotation.value() == -1: self.page.dsbOffsetRotation.clear()
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()
		if self.page.dsbFlatness.value()  == -1: self.page.dsbFlatness.clear()

		self.updateElements()


	@enforce_mode(['view','editing'])
	def updateElements(self):
		if not self.mode == "view":
			self.page.leStatus.setText(self.mode)

		module_exists   = self.module_exists

		step_sensor_exists   = self.page.sbStepSensor.value() >= 0 and \
		                       self.page.cbInstitutionStepSensor.currentText() != ""
		step_pcb_exists      = self.page.sbStepPcb.value()    >= 0 and \
		                       self.page.cbInstitutionStepPcb.currentText() != ""
		baseplate_exists   = self.page.leBaseplate.text()   != ""
		sensor_exists      = self.page.leSensor.text()      != ""
		pcb_exists         = self.page.lePcb.text()         != ""
		protomodule_exists = self.page.leProtomodule.text() != ""


		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'

		self.setMainSwitchingEnabled(mode_view) 
		self.page.leID.setReadOnly(not mode_view)

		self.page.pbLoad.setEnabled(mode_view)
		self.page.pbEdit  .setEnabled( mode_view and     module_exists )
		self.page.pbSave  .setEnabled( mode_editing   )
		self.page.pbCancel.setEnabled( mode_editing   )

		# characteristics
		# Note: most non-editable b/c either fixed or filled in w/ assembly pages
		#self.page.leLocation.setReadOnly(   not mode_editing )
		self.page.cbInstitution.setEnabled(     mode_editing )
		self.page.cbInsertUser.setEnabled(      mode_editing )
		self.page.cbInspection.setEnabled(      mode_editing )

		# parts and steps
		self.page.pbGoStepSensor.setEnabled(   mode_view and step_sensor_exists   )
		self.page.pbGoStepPcb.setEnabled(      mode_view and step_pcb_exists      )
		self.page.pbGoBaseplate.setEnabled(    mode_view and baseplate_exists     )
		self.page.pbGoSensor.setEnabled(       mode_view and sensor_exists        )
		self.page.pbGoPcb.setEnabled(          mode_view and pcb_exists           )
		self.page.pbGoProtomodule.setEnabled(  mode_view and protomodule_exists   )

		# comments
		self.page.pbDeleteComment.setEnabled(mode_editing)
		self.page.pbAddComment.setEnabled(   mode_editing)
		self.page.pteWriteComment.setEnabled(mode_editing)

		self.page.pbAddFiles.setEnabled(  mode_editing)
		self.page.pbDeleteFile.setEnabled(mode_editing)


	# NEW:
	@enforce_mode('view')
	def loadPart(self,*args,**kwargs):
		if self.page.leID.text == "":
			self.page.leStatus.setText("input an ID")
			return
		# Check whether baseplate exists:
		tmp_module = parts.module()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_module.load(tmp_ID)
		if not tmp_exists:  # DNE; good to create
			self.page.leStatus.setText("module DNE")
			self.update_info(do_load=False)
		else:
			self.module = tmp_module
			self.page.leStatus.setText("module exists")
			self.update_info()


	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_module = parts.module()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_module.load(tmp_ID)
		if not tmp_exists:
			self.page.leStatus.setText("does not exist")
		else:
			self.module = tmp_module
			self.mode = 'editing'
			self.update_info()

	@enforce_mode('editing')
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode('editing')
	def saveEditing(self,*args,**kwargs):
		# characteristics
		self.module.record_insertion_user  = str(self.page.cbInsertUser.currentText())  if str(self.page.cbInsertUser.currentText())  else None
		#self.module.institution_location        = str(self.page.leLocation.text()        ) if str(self.page.leLocation.text())             else None
		self.module.location     = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None
		self.module.final_inspxn_ok      = str(self.page.cbInspection.currentText())  if str(self.page.cbInspection.currentText())  else None

		# comments
		num_comments = self.page.listComments.count()
		self.module.comments = [self.page.listComments.item(i).text() for i in range(num_comments)]
		if num_comments == 0:  self.module.comments = ';;'

		self.module.pcb_plcment_x_offset = self.page.dsbOffsetTranslationX.value() if self.page.dsbOffsetTranslationX.value() >=0 else None
		self.module.pcb_plcment_y_offset = self.page.dsbOffsetTranslationY.value() if self.page.dsbOffsetTranslationY.value() >=0 else None
		self.module.offset_rotation      = self.page.dsbOffsetRotation.value()    if self.page.dsbOffsetRotation.value()    >=0 else None
		self.module.flatness = self.page.dsbOffsetFlatness.value()    if self.page.dsbFlatness.value()    >=0 else None
		self.module.thickness = self.page.dsbOffsetThickness.value()    if self.page.dsbThickness.value()    >=0 else None

		self.module.save()
		self.mode = 'view'
		self.update_info()

		self.xmlModList.append(self.module.ID)



	def xmlModified(self):
		return self.xmlModList

	def xmlModifiedReset(self):
		self.xmlModList = []


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
	def goBaseplate(self,*args,**kwargs):
		ID = self.page.leBaseplate.text()
		if ID != "":
			self.setUIPage('Baseplates',ID=ID)

	@enforce_mode('view')
	def goSensor(self,*args,**kwargs):
		ID = self.page.leSensor.text()
		if ID != "":
			self.setUIPage('Sensors',ID=ID)

	@enforce_mode('view')
	def goPcb(self,*args,**kwargs):
		ID = self.page.lePcb.text()
		if ID != "":
			self.setUIPage('PCBs',ID=ID)

	@enforce_mode('view')
	def goProtomodule(self,*args,**kwargs):
		ID = self.page.leProtomodule.text()
		if ID != "":
			self.setUIPage('Protomodules',ID=ID)

	@enforce_mode('view')
	def goStepSensor(self,*args,**kwargs):
		tmp_id = self.page.sbStepSensor.value()
		tmp_inst = self.page.cbInstitutionStepSensor.currentText()
		if tmp_id >= 0 and tmp_inst != "":
			self.setUIPage('1. Sensor - pre-assembly',ID="{}_{}".format(tmp_inst, tmp_id))

	@enforce_mode('view')
	def goStepPcb(self,*args,**kwargs):
		tmp_id = self.page.sbStepPcb.value()
		tmp_inst = self.page.cbInstitutionStepPcb.currentText()
		if tmp_id >= 0 and tmp_inst != "":
			self.setUIPage('3. PCB - pre-assembly',ID="{}_{}".format(tmp_inst, tmp_id))


	@enforce_mode('editing')
	def getFile(self,*args,**kwargs):
		f = self.fwnd.getdir()
		if f == '':  return
		files = glob.glob(f + '/**/*.png', recursive=True) + glob.glob(f + '/**/*.jpg', recursive=True)
		if files != []:
			# Need to call this to ensure that necessary dirs for storing item are created
			self.module.save()
			for f in files:
				fname = os.path.split(f)[1]  # Name of file
				fdir, fname_ = self.module.get_filedir_filename()
				tmp_filepath = (fdir + '/' + fname).rsplit('.', 1)  # Only want the last . to get replaced...
				new_filepath = "_upload.".join(tmp_filepath)
				shutil.copyfile(f, new_filepath)
				self.page.listComments.addItem(new_filepath)
				self.module.test_files.append(new_filepath)
			self.update_info()
		else:
			print("WARNING:  Failed to find PNG files in chosen directory!")

	@enforce_mode('editing')
	def deleteFile(self,*args,**kwargs):
		row = self.page.listFiles.currentRow()
		if row >= 0:
			fname = self.page.listFiles.item(row).text()
			self.page.listFiles.takeItem(row)
			# Now need to remove the file...
			fdir, fname_ = self.module.get_filedir_filename()
			new_filepath = fdir + '/' + fname
			os.remove(new_filepath)
			self.module.test_files.remove(new_filepath)
			self.update_info()

	def filesToUpload(self):
		# Return a list of all files to upload to DB
		if self.module is None:
			return []
		else:
			return self.module.filesToUpload()


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
