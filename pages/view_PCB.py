from filemanager import fm
import os
import shutil
import glob

from PyQt5.QtWidgets import QFileDialog, QWidget

PAGE_NAME = "view_pcb"
DEBUG = False

INDEX_TYPE = {
	'HGCROCV1':0,
	'HGCROCV2':1,
	'HGCROCV3':2,
	'SKIROCV1':3,
	'SKIROCV2':4,
	'SKIROCV3':5,
	'HGCROC dummy':6,
}

INDEX_SHAPE = {
	'Full':0,
	'Top':1,
	'Bottom':2,
	'Left':3,
	'Right':4,
	'Five':5,
	'Full+Three':6
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
	'HEPHY':4,
	'HPK':5,
}

INDEX_RESOLUTION = {
	'HD':0,
	'LD':1,
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
		#fname, fmt = QFileDialog.getOpenFileName(self, 'Open file', '~',"(*.root)")
		dname = str(QFileDialog.getExistingDirectory(self, "Select directory"))
		return dname


class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.pcb = fm.pcb()
		self.pcb_exists = False
		self.mode = 'setup'

		# NEW:
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

		self.page.pbGoStepPcb.clicked.connect(self.goStepPcb)
		self.page.pbGoModule.clicked.connect(self.goModule)

		self.page.pbDeleteComment.clicked.connect(self.deleteComment)
		self.page.pbAddComment.clicked.connect(self.addComment)

		self.fwnd = Filewindow()
		self.page.pbAddFiles.clicked.connect(self.getFile)
		self.page.pbDeleteFile.clicked.connect(self.deleteFile)

		auth_users = fm.userManager.getAuthorizedUsers(PAGE_NAME)
		self.index_users = {auth_users[i]:i for i in range(len(auth_users))}
		for user in self.index_users.keys():
			self.page.cbInsertUser.addItem(user)


	@enforce_mode(['view', 'editing', 'creating'])
	def update_info(self,ID=None,do_load=True,*args,**kwargs):
		if ID is None:
			ID = self.page.leID.text()
		else:
			self.page.leID.setText(ID)

		self.pcb_exists = (ID == self.pcb.ID)
		
		if not self.pcb.insertion_user in self.index_users.keys() and not self.pcb.insertion_user is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.pcb.insertion_user] = max(self.index_users.values()) + 1
			self.page.cbInsertUser.addItem(self.pcb.insertion_user)
		self.page.cbInsertUser.setCurrentIndex(self.index_users.get(self.pcb.insertion_user, -1))

		self.page.cbInstitution.setCurrentIndex(   INDEX_INSTITUTION.get(    self.pcb.institution, -1)   )
		self.page.leLocation.setText(    "" if self.pcb.location       is None else self.pcb.location    )

		self.page.leBarcode.setText(     "" if self.pcb.barcode        is None else self.pcb.barcode     )
		self.page.leManufacturer.setText("" if self.pcb.manufacturer   is None else self.pcb.manufacturer)
		self.page.cbType.setCurrentIndex(          INDEX_TYPE.get(           self.pcb.type,-1)           )
		self.page.cbResolution.setCurrentIndex(INDEX_RESOLUTION.get(self.pcb.resolution,-1))
		self.page.sbNumRocs.setValue( -1 if self.pcb.num_rocs is None else self.pcb.num_rocs)
		self.page.sbChannels.setValue(-1 if self.pcb.channels is None else self.pcb.channels)
		if self.page.sbChannels.value() == -1: self.page.sbChannels.clear()
		self.page.cbShape.setCurrentIndex(         INDEX_SHAPE.get(          self.pcb.shape,-1)          )

		self.page.listComments.clear()
		for comment in self.pcb.comments:
			self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		self.page.dsbFlatness.setValue( -1 if self.pcb.flatness  is None else self.pcb.flatness )
		self.page.dsbThickness.setValue(-1 if self.pcb.thickness is None else self.pcb.thickness)
		if self.page.dsbFlatness.value()  == -1: self.page.dsbFlatness.clear()
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()
		self.page.cbGrade.setCurrentIndex(         INDEX_GRADE.get(          self.pcb.grade, -1)         )


		if self.pcb.step_pcb:
			tmp_inst, tmp_id = self.pcb.step_pcb.split("_")
			self.page.sbStepPcb.setValue(int(tmp_id))
			self.page.cbInstitutionStep.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))
		else:
			self.page.sbStepPcb.clear()
			self.page.cbInstitutionStep.setCurrentIndex(-1)

		self.page.leModule.setText(  "" if self.pcb.module   is None else self.pcb.module)

		self.page.listFiles.clear()
		for f in self.pcb.test_files:
			name = os.path.split(f)[1]
			self.page.listFiles.addItem(name)

		self.updateElements()


	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		if not self.mode == "view":
			self.page.leStatus.setText(self.mode)

		pcb_exists      = self.pcb_exists

		step_pcb_exists = self.page.sbStepPcb.value() >=0 and \
		                  self.page.cbInstitutionStep.currentText() != ""
		module_exists   = self.page.leModule.text()  != ""

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'

		self.setMainSwitchingEnabled(mode_view)
		self.page.leID.setReadOnly(not mode_view)
		
		self.page.pbLoad.setEnabled(mode_view)
		self.page.pbNew.setEnabled(    mode_view and not pcb_exists  )
		self.page.pbEdit.setEnabled(   mode_view and     pcb_exists  )
		self.page.pbSave.setEnabled(   mode_editing or mode_creating )
		self.page.pbCancel.setEnabled( mode_editing or mode_creating )

		self.page.cbInsertUser.setEnabled(         mode_creating or mode_editing  )
		self.page.cbInstitution.setEnabled(        mode_creating or mode_editing  )
		self.page.leLocation.setReadOnly(     not (mode_creating or mode_editing) )

		self.page.leBarcode.setReadOnly(      not (mode_creating or mode_editing) )
		self.page.leManufacturer.setReadOnly( not (mode_creating or mode_editing) )
		self.page.cbType.setEnabled(               mode_creating or mode_editing  )
		self.page.cbResolution.setEnabled(         mode_creating or mode_editing  )
		self.page.cbShape.setEnabled(              mode_creating or mode_editing  )
		self.page.cbGrade.setEnabled(              mode_creating or mode_editing  )
		self.page.sbNumRocs.setReadOnly(      not (mode_creating or mode_editing) )
		self.page.sbChannels.setReadOnly(     not (mode_creating or mode_editing) )

		self.page.pbDeleteComment.setEnabled(mode_creating or mode_editing)
		self.page.pbAddComment.setEnabled(   mode_creating or mode_editing)
		self.page.pteWriteComment.setEnabled(mode_creating or mode_editing)

		self.page.dsbFlatness.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.dsbThickness.setReadOnly( not (mode_creating or mode_editing) )
		self.page.cbGrade.setEnabled(            mode_creating or mode_editing  )

		self.page.pbAddFiles.setEnabled(mode_creating or mode_editing)
		self.page.pbDeleteFile.setEnabled(mode_creating or mode_editing)


	# NEW:
	@enforce_mode('view')
	def loadPart(self,*args,**kwargs):
		if self.page.leID.text == "":
			self.page.leStatus.setText("input an ID")
			return
		# Check whether baseplate exists:
		tmp_pcb = fm.pcb()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_pcb.load(tmp_ID)
		if not tmp_exists:  # DNE; good to create
			self.page.leStatus.setText("PCB DNE")
			self.update_info()
		else:
			self.pcb = tmp_pcb
			self.page.leStatus.setText("PCB exists")
			self.update_info()

	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if self.page.leID.text() == "":
			self.page.leStatus.setText("input an ID")
			return
		tmp_pcb = fm.pcb()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_pcb.load(tmp_ID)
		if not tmp_exists:
			ID = self.page.leID.text()
			self.pcb.new(ID)
			self.mode = 'creating'
			self.update_info()
		else:
			self.page.leStatus.setText("already exists")

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_pcb = fm.pcb()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_pcb.load(tmp_ID)
		if not tmp_exists:
			self.page.leStatus.setText("does not exist")
		else:
			self.pcb = tmp_pcb
			self.mode = 'editing'
			self.update_info()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.pcb.clear()
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):

		self.pcb.insertion_user  = str(self.page.cbInsertUser.currentText())  if str(self.page.cbInsertUser.currentText())  else None
		self.pcb.institution     = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None
		self.pcb.location        = str(self.page.leLocation.text()         )  if str(self.page.leLocation.text()          ) else None

		self.pcb.barcode         = str(self.page.leBarcode.text()          )  if str(self.page.leBarcode.text()           ) else None
		self.pcb.manufacturer    = str(self.page.leManufacturer.text()     )  if str(self.page.leManufacturer.text()      ) else None
		self.pcb.resolution      = str(self.page.cbResolution.currentText())  if str(self.page.cbType.currentText()       ) else None
		self.pcb.type            = str(self.page.cbType.currentText()      )  if str(self.page.cbType.currentText()       ) else None
		self.pcb.num_rocs        = self.page.sbNumRocs.value()  if self.page.sbNumRocs.value()  >=0 else None
		self.pcb.channels        = self.page.sbChannels.value() if self.page.sbChannels.value() >=0 else None
		self.pcb.shape           = str(self.page.cbShape.currentText()     )  if str(self.page.cbShape.currentText()      ) else None

		num_comments = self.page.listComments.count()
		self.pcb.comments = []
		for i in range(num_comments):
			self.pcb.comments.append(str(self.page.listComments.item(i).text()))

		self.pcb.flatness   =     self.page.dsbFlatness.value()         if     self.page.dsbFlatness.value()  >=0    else None
		self.pcb.thickness  =     self.page.dsbThickness.value()        if     self.page.dsbThickness.value() >=0    else None
		self.pcb.grade      = str(self.page.cbGrade.currentText())      if str(self.page.cbGrade.currentText())      else None

		self.pcb.save()
		self.mode = 'view'
		self.update_info()

		self.xmlModList.append(self.pcb.ID)


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
	def goModule(self,*args,**kwargs):
		ID = self.page.leModule.text()
		if ID != "":
			self.setUIPage('Modules',ID=ID)
	
	@enforce_mode('view')
	def goStepPcb(self,*args,**kwargs):
		tmp_id = self.page.sbStepPcb.value()
		tmp_inst = self.page.cbInstitutionStep.currentText()
		if tmp_id >= 0 and tmp_inst != "":
			self.setUIPage('3. PCB - pre-assembly',ID="{}_{}".format(tmp_inst, tmp_id))


	@enforce_mode(['editing', 'creating'])
	def getFile(self,*args,**kwargs):
		f = self.fwnd.getdir()
		if f == '':  return
		# Directory containing root files.  Search recursively for roots:
		files = glob.glob(f + '/**/*.root', recursive=True)
		if files != []:
			# Need to call this to ensure that necessary dirs for storing item are created
			print("Got files.  Saving to ensure creation of filemanager location...")
			self.pcb.save()
			for f in files:
				fname = os.path.split(f)[1]  # Name of file
				fdir, fname_ = self.pcb.get_filedir_filename()
				tmp_filepath = (fdir + '/' + fname).rsplit('.', 1)  # Only want the last . to get replaced...
				new_filepath = "_upload.".join(tmp_filepath)
				print("GETFILE:  Copying file", f, "to", new_filepath)
				shutil.copyfile(f, new_filepath)
				self.page.listComments.addItem(new_filepath)
				self.pcb.test_files.append(new_filepath)
			self.update_info()
		else:
			print("WARNING:  Failed to find root files in chosen directory!")

	@enforce_mode(['editing', 'creating'])
	def deleteFile(self,*args,**kwargs):
		row = self.page.listFiles.currentRow()
		if row >= 0:
			fname = self.page.listFiles.item(row).text()
			self.page.listFiles.takeItem(row)
			# Now need to remove the file...
			fdir, fname_ = self.pcb.get_filedir_filename()
			new_filepath = fdir + '/' + fname
			print("REMOVING FILE", new_filepath)
			os.remove(new_filepath)
			self.pcb.test_files.remove(new_filepath)
			self.update_info()


	def filesToUpload(self):
		# Return a list of all files to upload to DB
		if self.pcb is None:
			return []
		else:
			return self.pcb.filesToUpload()


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
