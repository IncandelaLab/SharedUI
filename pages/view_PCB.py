from filemanager import parts
import os
import shutil
import glob

from PyQt5.QtWidgets import QFileDialog, QWidget

PAGE_NAME = "view_pcb"
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


class Filewindow(QWidget):
	def __init__(self):
		super(Filewindow, self).__init__()

	def getdir(self,*args,**kwargs):
		#fname, fmt = QFileDialog.getOpenFileName(self, 'Open file', '~',"(*.root)")
		dname = str(QFileDialog.getExistingDirectory(self, "Select directory"))
		return dname


class func(object):
	def __init__(self,fm,userManager,page,setUIPage,setSwitchingEnabled):
		self.userManager = userManager
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.pcb = parts.pcb()
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
		self.page.leID.textChanged.connect(self.loadPart)
		# self.page.pbLoad.clicked.connect(self.loadPart)
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


	@enforce_mode(['view', 'editing', 'creating'])
	def update_info(self,ID=None,do_load=True,*args,**kwargs):
		if ID is None:
			ID = self.page.leID.text()
		else:
			self.page.leID.setText(ID)

		self.pcb_exists = (ID == self.pcb.ID)
		
		self.page.cbInsertUser.clear()
		auth_users = self.userManager.getAuthorizedUsers(PAGE_NAME)
		self.index_users = {auth_users[i]:i for i in range(len(auth_users))}
		for user in self.index_users.keys():
			self.page.cbInsertUser.addItem(user)

		if not self.pcb.record_insertion_user in self.index_users.keys() and len(self.index_users.keys())!=0 and not self.pcb.record_insertion_user is None:
			# Insertion user is not in user page...fine for now, just add user to the dropdown
			self.index_users[self.pcb.record_insertion_user] = max(self.index_users.values()) + 1
			self.page.cbInsertUser.addItem(self.pcb.record_insertion_user)
		self.page.cbInsertUser.setCurrentIndex(self.index_users.get(self.pcb.record_insertion_user, -1))

		self.page.cbInstitution.setCurrentIndex(   INDEX_INSTITUTION.get(    self.pcb.location, -1)   )
		#self.page.leLocation.setText(    "" if self.pcb.institution_location       is None else self.pcb.institution_location    )

		self.page.leBarcode.setText(     "" if self.pcb.barcode        is None else self.pcb.barcode     )
		self.page.cbResolution.setCurrentIndex(INDEX_CHANNEL.get(self.pcb.channel_density,-1))
		# may be unnecessary now
		self.page.cbShape.setCurrentIndex(         INDEX_SHAPE.get(          self.pcb.geometry,-1)          )

		self.page.listComments.clear()
		if self.pcb.comments:
			for comment in self.pcb.comments.split(';;'):
				self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		self.page.dsbFlatness.setValue( -1 if (self.pcb.flatness  is None) or (self.pcb.flatness == "None") else float(self.pcb.flatness) )
		self.page.dsbThickness.setValue(-1 if (self.pcb.thickness is None) or (self.pcb.thickness == "None") else float(self.pcb.thickness) )
		if self.page.dsbFlatness.value()  == -1: self.page.dsbFlatness.clear()
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()
		self.page.cbGrade.setCurrentIndex(  INDEX_GRADE.get( self.pcb.grade.lower().capitalize(), -1) if type(self.pcb.grade) is str else -1)


		"""if self.pcb.step_pcb:
			tmp_inst, tmp_id = self.pcb.step_pcb.split("_")
			self.page.sbStepPcb.setValue(int(tmp_id))
			self.page.cbInstitutionStep.setCurrentIndex(INDEX_INSTITUTION.get(tmp_inst, -1))
		else:
			self.page.sbStepPcb.clear()
			self.page.cbInstitutionStep.setCurrentIndex(-1)

		self.page.leModule.setText(  "" if self.pcb.module   is None else self.pcb.module)
		"""
		# ;;-separated list of files
		self.page.listFiles.clear()
		if self.pcb.test_files:
			for f in self.pcb.test_files.split(";;"):
				#name = os.path.split(f)[1]
				self.page.listFiles.addItem(f)

		self.updateElements()


	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		if not self.mode == "view":
			self.page.leStatus.setText(self.mode)

		pcb_exists      = self.pcb_exists

		"""step_pcb_exists = self.page.sbStepPcb.value() >=0 and \
		                  self.page.cbInstitutionStep.currentText() != ""
		module_exists   = self.page.leModule.text()  != ""
		"""

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'

		self.setMainSwitchingEnabled(mode_view)
		self.page.leID.setReadOnly(not mode_view)
		
		# self.page.pbLoad.setEnabled(mode_view)
		self.page.pbNew.setEnabled(    mode_view and not pcb_exists  )
		self.page.pbEdit.setEnabled(   mode_view and     pcb_exists  )
		self.page.pbSave.setEnabled(   mode_editing or mode_creating )
		self.page.pbCancel.setEnabled( mode_editing or mode_creating )

		self.page.cbInsertUser.setEnabled(         mode_creating or mode_editing  )
		self.page.cbInstitution.setEnabled(        mode_creating or mode_editing  )
		#self.page.leLocation.setReadOnly(     not (mode_creating or mode_editing) )

		self.page.leBarcode.setReadOnly(      not (mode_creating or mode_editing) )
		#self.page.cbType.setEnabled(               mode_creating or mode_editing  )
		self.page.cbResolution.setEnabled(         mode_creating or mode_editing  )
		self.page.cbShape.setEnabled(              mode_creating or mode_editing  )
		self.page.cbGrade.setEnabled(              mode_creating or mode_editing  )

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
		tmp_pcb = parts.pcb()
		tmp_ID = self.page.leID.text()

		# NEW: Load from central DB if not found locally
		if tmp_pcb.load(tmp_ID):  # exist locally
			self.pcb = tmp_pcb
			self.update_info()
			self.page.leStatus.setText("pcb exists locally")
		elif tmp_pcb.load_remote(tmp_ID, full=True):  # exist in central DB
			self.pcb = tmp_pcb
			print("\n!! Loading pcb {} from central DB".format(tmp_ID))
			print("kind of part: {}".format(self.pcb.kind_of_part))
			print("record_insertion_user: {}".format(self.pcb.record_insertion_user))
			print("thickness: {}, type {}".format(self.pcb.thickness, type(self.pcb.thickness)))
			print("flatness: {}".format(self.pcb.flatness))
			print("grade: {}".format(self.pcb.grade))
			self.update_info()
			self.page.leStatus.setText("PCB only exists in central DB")
		else:  # DNE; good to create
			self.update_info()
			self.page.leStatus.setText("PCB DNE")

		# tmp_exists = tmp_pcb.load(tmp_ID)
		# if not tmp_exists:  # DNE; good to create
		# 	self.page.leStatus.setText("PCB DNE")
		# 	self.update_info()
		# else:
		# 	self.pcb = tmp_pcb
		# 	self.page.leStatus.setText("PCB exists")
		# 	self.update_info()

	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if self.page.leID.text() == "":
			self.page.leStatus.setText("input an ID")
			return
		tmp_pcb = parts.pcb()
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
		tmp_pcb = parts.pcb()
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

		self.pcb.record_insertion_user  = str(self.page.cbInsertUser.currentText())  if str(self.page.cbInsertUser.currentText())  else None
		self.pcb.location     = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None
		#self.pcb.institution_location        = str(self.page.leLocation.text()         )  if str(self.page.leLocation.text()          ) else None

		self.pcb.barcode         = str(self.page.leBarcode.text()          )  if str(self.page.leBarcode.text()           ) else None
		self.pcb.channel_density      = str(self.page.cbResolution.currentText())  if str(self.page.cbResolution.currentText()       ) else None
		#self.pcb.type            = str(self.page.cbType.currentText()      )  if str(self.page.cbType.currentText()       ) else None
		#self.pcb.num_rocs        = self.page.sbNumRocs.value()  if self.page.sbNumRocs.value()  >=0 else None
		#self.pcb.channels        = self.page.sbChannels.value() if self.page.sbChannels.value() >=0 else None
		self.pcb.geometry           = str(self.page.cbShape.currentText()     )  if str(self.page.cbShape.currentText()      ) else None

		num_comments = self.page.listComments.count()
		self.pcb.comments = ';;'.join([self.page.listComments.item(i).text() for i in range(num_comments)])

		self.pcb.flatness   =     self.page.dsbFlatness.value()         if     self.page.dsbFlatness.value()  >=0    else None
		self.pcb.thickness  =     self.page.dsbThickness.value()        if     self.page.dsbThickness.value() >=0    else None
		self.pcb.grade      = str(self.page.cbGrade.currentText())      if str(self.page.cbGrade.currentText())      else None

		self.pcb.save()
		self.mode = 'view'
		self.update_info()

		self.xmlModList.append(self.pcb.ID)

		self.pcb.generate_xml()


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
			self.pcb.save()
			for f in files:
				fname = os.path.split(f)[1]  # Name of file
				fdir, fname_ = self.pcb.get_filedir_filename()
				tmp_filepath = (fdir + '/' + fname).rsplit('.', 1)  # Only want the last . to get replaced...
				new_filepath = "_upload.".join(tmp_filepath)
				shutil.copyfile(f, new_filepath)
				self.page.listComments.addItem(new_filepath)
				if self.fsobj_pt.test_files:
					self.fsobj_pt.test_files += ';;' + tmp_filename
				else:
					self.pcb.test_files = new_filepath
			self.update_info()
		else:
			print("WARNING:  Failed to find root files in chosen directory!")

	@enforce_mode(['editing', 'creating'])
	def deleteFile(self,*args,**kwargs):
		row = self.page.listFiles.currentRow()
		if row >= 0:
			fname = self.page.listFiles.item(row).text()
			#self.page.listFiles.takeItem(row)
			# Now need to remove the file...
			#fdir, fname_ = self.pcb.get_filedir_filename()
			#new_filepath = fdir + '/' + fname
			os.remove(fname) #new_filepath)
			#self.pcb.test_file_name.remove(new_filepath)
			if self.pcb.test_files.replace(fname+";;", "") == fname+";;":
				# if substr;; not found, is probably at the end of the list, so:
				self.pcb.test_files.replace(fname, "")
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
