from filemanager import fm
from PyQt5 import QtCore
import time
import os
import shutil

# NEW, experimental
from PyQt5.QtWidgets import QFileDialog, QWidget


PAGE_NAME = "view_module"
DEBUG = False
SITE_SEP = ', '
NO_DATE = [2000,1,1]

INDEX_SHAPE = {
	'Full':0,
	'Top':1,
	'Bottom':2,
	'Left':3,
	'Right':4,
	'Five':5,
	'Full+Three':6
}

INDEX_GRADE = {
	'A':0,
	'B':1,
	'C':2,
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
}


def separate_sites(sites_string):
	s = sites_string
	for char in SITE_SEP:
		s=s.replace(char, '\n')
	sites = [_ for _ in s.splitlines() if _]
	return sites


# EXPERIMENTAL

class Filewindow(QWidget):
	def __init__(self):
		super(Filewindow, self).__init__()

	def getfile(self,*args,**kwargs):
		fname, fmt = QFileDialog.getOpenFileName(self, 'Open file', '~',"(*.jpg *.png *.xml)")
		print("File dialog:  got file", fname)
		return fname


class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.module = fm.module()
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
		#self.page.sbID.valueChanged.connect(self.update_info)
		#self.page.leID.textChanged.connect(self.update_info)

		self.page.pbLoad.clicked.connect(self.loadPart)

		#self.page.pbNew.clicked.connect(self.startCreating)
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

		#self.page.pbIvAddToPlotter.clicked.connect( self.ivAddToPlotter )
		#self.page.pbIvGoPlotter.clicked.connect(    self.ivGoPlotter    )
		#self.page.pbDaqAddToPlotter.clicked.connect(self.daqAddToPlotter)
		#self.page.pbDaqGoPlotter.clicked.connect(   self.daqGoPlotter   )

		# NEW, experimental
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
		if do_load:
			self.module_exists = self.module.load(ID)
		else:
			self.module_exists = False
		
		self.module_exists = (ID == self.module.ID)
		
		self.page.leLocation.setText("" if self.module.location is None else self.module.location)

		# characteristics
		#self.page.sbChannels.setValue(  -1 if self.module.channels    is None else self.module.channels   )
		self.page.dsbThickness.setValue(-1 if self.module.thickness   is None else self.module.thickness  )
		self.page.dsbFlatness.setValue( -1 if self.module.flatness    is None else self.module.flatness   )
		self.page.cbShape.setCurrentIndex(      INDEX_SHAPE.get(      self.module.shape    , -1)  )
		self.page.cbGrade.setCurrentIndex(      INDEX_GRADE.get(      self.module.grade    , -1)  )
		self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.module.institution, -1))
		self.page.cbInspection.setCurrentIndex( INDEX_INSPECTION.get( self.module.inspection,  -1))
		if not self.module.insertion_user in self.index_users.keys() and not self.module.insertion_user is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.module.insertion_user] = max(self.index_users.values()) + 1
			self.page.cbInsertUser.addItem(self.module.insertion_user)
		self.page.cbInsertUser.setCurrentIndex(self.index_users.get(self.module.insertion_user, -1))
		#if self.page.sbChannels.value()   == -1: self.page.sbChannels.clear()
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()
		if self.page.dsbFlatness.value()  == -1: self.page.dsbFlatness.clear()

		# parts and steps
		self.page.sbStepSensor.setValue(   -1 if self.module.step_sensor   is None else self.module.step_sensor   )
		self.page.sbStepPcb.setValue(      -1 if self.module.step_pcb      is None else self.module.step_pcb      )
		self.page.leBaseplate.setText(    "" if self.module.baseplate     is None else self.module.baseplate     )
		self.page.leSensor.setText(       "" if self.module.sensor        is None else self.module.sensor        )
		self.page.lePcb.setText(          "" if self.module.pcb           is None else self.module.pcb           )
		self.page.leProtomodule.setText(  "" if self.module.protomodule   is None else self.module.protomodule   )
		if self.page.sbStepSensor.value()   == -1:  self.page.sbStepSensor.clear()
		if self.page.sbStepPcb.value()      == -1:  self.page.sbStepPcb.clear()
		if self.page.leBaseplate.text()    == -1:  self.page.leBaseplate.clear()
		if self.page.leSensor.text()       == -1:  self.page.leSensor.clear()
		if self.page.lePcb.text()          == -1:  self.page.lePcb.clear()
		if self.page.leProtomodule.text()  == -1:  self.page.leProtomodule.clear()

		self.page.ckWirebondingCompleted.setChecked(False if self.module.wirebonding_completed is None else self.module.wirebonding_completed)


		# comments
		self.page.listComments.clear()
		for comment in self.module.comments:
			self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()


		self.page.listFiles.clear()
		for f in self.module.test_files:
			name = os.path.split(f)[1]
			self.page.listFiles.addItem(name)

		self.page.dsbOffsetTranslationX.setValue( -1 if self.module.offset_translation_x is None else self.module.offset_translation_x )
		self.page.dsbOffsetTranslationY.setValue( -1 if self.module.offset_translation_y is None else self.module.offset_translation_y )
		self.page.dsbOffsetRotation.setValue(    -1 if self.module.offset_rotation    is None else self.module.offset_rotation    )
		if self.page.dsbOffsetTranslationX.value() == -1: self.page.dsbOffsetTranslationX.clear()
		if self.page.dsbOffsetTranslationY.value() == -1: self.page.dsbOffsetTranslationY.clear()
		if self.page.dsbOffsetRotation.value() == -1: self.page.dsbOffsetRotation.clear()

		self.updateElements()

	@enforce_mode(['view','editing','creating'])
	def updateElements(self):
		if not self.mode == "view":
			self.page.leStatus.setText(self.mode)

		module_exists   = self.module_exists

		step_sensor_exists   = self.page.sbStepSensor.value()    >= 0
		step_pcb_exists      = self.page.sbStepPcb.value()       >= 0
		baseplate_exists   = self.page.leBaseplate.text()   != ""
		sensor_exists      = self.page.leSensor.text()      != ""
		pcb_exists         = self.page.lePcb.text()         != ""
		protomodule_exists = self.page.leProtomodule.text() != ""


		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'

		self.setMainSwitchingEnabled(mode_view) 
		self.page.leID.setReadOnly(not mode_view)

		self.page.pbLoad.setEnabled(mode_view)

		self.page.pbEdit  .setEnabled( mode_view and     module_exists )
		self.page.pbSave  .setEnabled( mode_creating or mode_editing   )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing   )

		# characteristics
		#self.page.leInsertUser.setReadOnly( not (mode_creating or mode_editing) )
		self.page.leLocation.setReadOnly(   not (mode_creating or mode_editing) )
		#self.page.sbChannels.setReadOnly(   not (mode_creating or mode_editing) )
		#self.page.dsbFlatness.setReadOnly(  not (mode_creating or mode_editing) )
		#self.page.dsbThickness.setReadOnly( not (mode_creating or mode_editing) )
		#self.page.cbShape.setEnabled(            mode_creating or mode_editing  )
		#self.page.cbChirality.setEnabled(        mode_creating or mode_editing  )
		#self.page.cbGrade.setEnabled(            mode_creating or mode_editing  )
		self.page.cbInstitution.setEnabled(      mode_creating or mode_editing  )
		self.page.cbInsertUser.setEnabled(       mode_creating or mode_editing  )
		self.page.cbInspection.setEnabled(       mode_creating or mode_editing  )

		# parts and steps
		self.page.pbGoStepSensor.setEnabled(   mode_view and step_sensor_exists   )
		self.page.pbGoStepPcb.setEnabled(      mode_view and step_pcb_exists      )
		self.page.pbGoBaseplate.setEnabled(    mode_view and baseplate_exists     )
		self.page.pbGoSensor.setEnabled(       mode_view and sensor_exists        )
		self.page.pbGoPcb.setEnabled(          mode_view and pcb_exists           )
		self.page.pbGoProtomodule.setEnabled(  mode_view and protomodule_exists   )

		# comments
		self.page.pbDeleteComment.setEnabled(mode_creating or mode_editing)
		self.page.pbAddComment.setEnabled(   mode_creating or mode_editing)
		self.page.pteWriteComment.setEnabled(mode_creating or mode_editing)

		self.page.pbAddFiles.setEnabled(mode_creating or mode_editing)
		self.page.pbDeleteFile.setEnabled(mode_creating or mode_editing)

		#self.page.dsbOffsetTranslationX.setReadOnly( not (mode_creating or mode_editing) )
		#self.page.dsbOffsetTranslationY.setReadOnly( not (mode_creating or mode_editing) )
		#self.page.dsbOffsetRotation.setReadOnly(    not (mode_creating or mode_editing) )

#	# NEW, experimental
#	@enforce_mode(['creating', 'editing'])
#	def addFiles(self,*args,**kwargs):
#		# Open up dialogue box, take note of selected file name
#		getfile()  # VERY experimental...


	# NEW:
	@enforce_mode('view')
	def loadPart(self,*args,**kwargs):
		if self.page.leID.text == "":
			self.page.leStatus.setText("input an ID")
			return
		# Check whether baseplate exists:
		tmp_module = fm.module()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_module.load(tmp_ID)
		if not tmp_exists:  # DNE; good to create
			#ID = self.page.leID.text()
			#self.sensor.new(ID)
			#self.mode = 'creating'  # update_info needs mode==view
			self.page.leStatus.setText("module DNE")
			self.update_info(do_load=False)
		else:
			self.module = tmp_module
			self.page.leStatus.setText("module exists")
			self.update_info()


	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		print("ERROR:  This is outdated and should not be used.")
		assert(False)
		if not self.module_exists:
			ID = self.page.sbID.value()
			self.mode = 'creating'
			self.module.new(ID)
			self.updateElements()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_module = fm.module()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_module.load(tmp_ID)
		if not tmp_exists:
			self.page.leStatus.setText("does not exist")
		else:
			self.module = tmp_module
			self.mode = 'editing'
			self.update_info()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):
		# characteristics
		#self.module.insertion_user = str(self.page.leInsertUser.text()   ) if str(self.page.leInsertUser.text())         else None
		self.module.location        = str(self.page.leLocation.text()        ) if str(self.page.leLocation.text())             else None
		#self.module.channels        =     self.page.sbChannels.value()         if self.page.sbChannels.value()   >= 0          else None
		self.module.flatness        =     self.page.dsbFlatness.value()        if self.page.dsbFlatness.value()  >= 0          else None
		self.module.thickness       =     self.page.dsbThickness.value()       if self.page.dsbThickness.value() >= 0          else None
		#self.module.shape           = str(self.page.cbShape.currentText()    ) if str(self.page.cbShape.currentText()        ) else None
		#self.module.chirality       = str(self.page.cbChirality.currentText()) if str(self.page.cbChirality.currentText()    ) else None
		self.module.institution     = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None
		self.module.insertion_user  = str(self.page.cbInsertUser.currentText())  if str(self.page.cbInsertUser.currentText())  else None
		#self.module.grade           = str(self.page.cbGrade.currentText())       if str(self.page.cbGrade.currentText())       else None
		self.module.inspection      = str(self.page.cbInspection.currentText())  if str(self.page.cbInspection.currentText())  else None

		# comments
		num_comments = self.page.listComments.count()
		self.module.comments = []
		for i in range(num_comments):
			self.module.comments.append(str(self.page.listComments.item(i).text()))

		self.protomodule.offset_translation_x = self.page.dsbOffsetTranslationX.value() if self.page.dsbOffsetTranslationX.value() >=0 else None
		self.module.offset_translation_y = self.page.dsbOffsetTranslationY.value() if self.page.dsbOffsetTranslationY.value() >=0 else None
		self.module.offset_rotation      = self.page.dsbOffsetRotation.value()    if self.page.dsbOffsetRotation.value()    >=0 else None

		self.module.save()
		self.mode = 'view'
		self.update_info()

		self.xmlModList.append(self.module.ID)



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
	def goBaseplate(self,*args,**kwargs):
		#ID = self.page.sbBaseplate.value()
		#if ID>=0:
		ID = self.page.leBaseplate.text()
		if ID != "":
			self.setUIPage('baseplates',ID=ID)

	@enforce_mode('view')
	def goSensor(self,*args,**kwargs):
		#ID = self.page.sbSensor.value()
		#if ID>=0:
		ID = self.page.leSensor.text()
		if ID != "":
			self.setUIPage('sensors',ID=ID)

	@enforce_mode('view')
	def goPcb(self,*args,**kwargs):
		#ID = self.page.sbPcb.value()
		#if ID>=0:
		ID = self.page.lePcb.text()
		if ID != "":
			self.setUIPage('PCBs',ID=ID)

	@enforce_mode('view')
	def goProtomodule(self,*args,**kwargs):
		#ID = self.page.sbProtomodule.value()
		#if ID>=0:
		ID = self.page.leProtomodule.text()
		if ID != "":
			self.setUIPage('protomodules',ID=ID)

	@enforce_mode('view')
	def goStepSensor(self,*args,**kwargs):
		ID = self.page.sbStepSensor.value()
		if ID>=0:
			self.setUIPage('sensor placement steps',ID=ID)

	@enforce_mode('view')
	def goStepPcb(self,*args,**kwargs):
		ID = self.page.sbStepPcb.value()
		if ID>=0:
			self.setUIPage('PCB placement steps',ID=ID)

	@enforce_mode('view')
	def ivAddToPlotter(self,*args,**kwargs):
		print("not implemented yet - waiting for plotter page to be implemented")

	@enforce_mode('view')
	def ivGoPlotter(self,*args,**kwargs):
		self.setUIPage('plotter',which='iv')

	@enforce_mode('view')
	def daqAddToPlotter(self,*args,**kwargs):
		print("not implemented yet - waiting for plotter page to be implemented")

	@enforce_mode('view')
	def daqGoPlotter(self,*args,**kwargs):
		self.setUIPage('plotter',which='daq')


	@enforce_mode(['editing', 'creating'])
	def getFile(self,*args,**kwargs):
		f = self.fwnd.getfile()
		if f:
			# Need to call this to ensure that necessary dirs for storing item are created
			print("Got file.  Saving to ensure creation of filemanager location...")
			self.module.save()

			fname = os.path.split(f)[1]  # Name of file
			fdir, fname_ = self.module.get_filedir_filename()
			#new_filepath = fdir + '/' + fname
			tmp_filepath = (fdir + '/' + fname).rsplit('.', 1)  # Only want the last . to get replaced...
			new_filepath = "_upload.".join(tmp_filepath)
			print("GETFILE:  Copying file", f, "to", new_filepath)
			shutil.copyfile(f, new_filepath)
			self.page.listComments.addItem(new_filepath)
			self.module.test_files.append(new_filepath)
			self.update_info()

	@enforce_mode(['editing', 'creating'])
	def deleteFile(self,*args,**kwargs):
		row = self.page.listFiles.currentRow()
		if row >= 0:
			fname = self.page.listFiles.item(row).text()
			self.page.listFiles.takeItem(row)
			# Now need to remove the file...
			fdir, fname_ = self.module.get_filedir_filename()
			new_filepath = fdir + '/' + fname
			print("REMOVING FILE", new_filepath)
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
			#if ID < 0:
			#	raise ValueError("ID cannot be negative")
			self.page.leID.setText(ID)
			self.loadPart()

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
