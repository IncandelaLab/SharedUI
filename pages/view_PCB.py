from filemanager import fm
import os
import shutil
import glob

from PyQt5.QtWidgets import QFileDialog, QWidget

PAGE_NAME = "view_pcb"
PARTTYPE = "PCB"
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

INDEX_RESOLUTION = {
	'HD':0,
	'LD':1,
}

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
	'HEPHY':4,
	'HPK':5,
}

INDEX_RESOLUTION_TYPE = {
	'HD':0,
	'LD':1,
}

INDEX_GRADE = {
	'A':0,
	'B':1,
	'C':2,
}

class Filewindow(QWidget):
	def __init__(self):
		super(Filewindow, self).__init__()

	def getdir(self,*args,**kwargs):
		#fname, fmt = QFileDialog.getOpenFileName(self, 'Open file', '~',"(*.root)")
		dname = str(QFileDialog.getExistingDirectory(self, "Select directory"))
		print("File dialog:  got directory", fname)
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
		#self.page.sbID.valueChanged.connect(self.update_info)
		#self.page.leID.textChanged.connect(self.update_info)

		self.page.pbLoad.clicked.connect(self.loadPart)

		self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoShipment.clicked.connect(self.goShipment)

		self.page.pbDeleteComment.clicked.connect(self.deleteComment)
		self.page.pbAddComment.clicked.connect(self.addComment)

		self.page.pbGoStepPcb.clicked.connect(self.goStepPcb)
		self.page.pbGoModule.clicked.connect(self.goModule)

		#self.page.pbAddToPlotter.clicked.connect(self.addToPlotter)
		#self.page.pbGoPlotter.clicked.connect(self.goPlotter)

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
			#ID = self.page.sbID.value()
			ID = self.page.leID.text()
		else:
			#self.page.sbID.setValue(ID)
			self.page.leID.setText(ID)
		#if do_load:
		#	self.pcb_exists = self.pcb.load(ID)
		#else:
		#	self.pcb_exists = False
		
		#self.page.leID.setText(self.pcb.ID)

		self.page.listShipments.clear()
		for shipment in self.pcb.shipments:
			self.page.listShipments.addItem(str(shipment))

		#self.page.leInsertUser.setText(  "" if self.pcb.insertion_user is None else self.pcb.insertion_user)
		self.page.leLocation.setText(    "" if self.pcb.location       is None else self.pcb.location    )
		self.page.leBarcode.setText(     "" if self.pcb.barcode        is None else self.pcb.barcode     )
		self.page.leManufacturer.setText("" if self.pcb.manufacturer   is None else self.pcb.manufacturer)
		self.page.cbType.setCurrentIndex(          INDEX_TYPE.get(           self.pcb.type,-1)           )
		self.page.cbResolutionType.setCurrentIndex(INDEX_RESOLUTION_TYPE.get(self.pcb.resolution_type,-1))
		self.page.cbShape.setCurrentIndex(         INDEX_SHAPE.get(          self.pcb.shape,-1)          )
		#self.page.cbChirality.setCurrentIndex(     INDEX_CHIRALITY.get(      self.pcb.chirality,-1)      )
		self.page.cbGrade.setCurrentIndex(         INDEX_GRADE.get(          self.pcb.grade, -1)         )
		self.page.cbInstitution.setCurrentIndex(   INDEX_INSTITUTION.get(    self.pcb.institution, -1)   )
		if not self.pcb.insertion_user in self.index_users.keys() and not self.pcb.insertion_user is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.pcb.insertion_user] = max(self.index_users.values()) + 1
			self.page.cbInsertUser.addItem(self.pcb.insertion_user)
		self.page.cbInsertUser.setCurrentIndex(self.index_users.get(self.pcb.insertion_user, -1))
		self.page.sbChannels.setValue(-1 if self.pcb.channels is None else self.pcb.channels)
		self.page.sbNumRocs.setValue( -1 if self.pcb.num_rocs is None else self.pcb.num_rocs)
		if self.page.sbChannels.value() == -1: self.page.sbChannels.clear()

		self.page.listComments.clear()
		for comment in self.pcb.comments:
			self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		#self.page.leDaq.setText("" if self.pcb.daq is None else self.pcb.daq)
		self.page.cbGrade.setCurrentIndex(INDEX_GRADE.get(self.pcb.grade, -1))
		#self.page.cbDaqOK.setCurrentIndex(     INDEX_CHECK.get(self.pcb.daq_ok    , -1))
		self.page.dsbFlatness.setValue( -1 if self.pcb.flatness  is None else self.pcb.flatness )
		self.page.dsbThickness.setValue(-1 if self.pcb.thickness is None else self.pcb.thickness)
		if self.page.dsbFlatness.value()  == -1: self.page.dsbFlatness.clear()
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()

		self.page.sbStepPcb.setValue(-1 if self.pcb.step_pcb is None else self.pcb.step_pcb)
		#self.page.sbModule.setValue( -1 if self.pcb.module   is None else self.pcb.module  )
		self.page.leModule.setText(  "" if self.pcb.module   is None else self.pcb.module)
		if self.page.sbStepPcb.value() == -1: self.page.sbStepPcb.clear()
		#if self.page.sbModule.value()  == -1: self.page.sbModule.clear()

		#self.page.listDaqData.clear()
		#for daq in self.pcb.daq_data:
		#	self.page.listDaqData.addItem(daq)

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
		shipments_exist = self.page.listShipments.count() > 0
		#daq_data_exists = self.page.listDaqData.count()   > 0

		step_pcb_exists = self.page.sbStepPcb.value() >=0
		#module_exists   = self.page.sbModule.value()  >=0
		module_exists   = self.page.leModule.text()  != ""

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'

		self.setMainSwitchingEnabled(mode_view)
		#self.page.sbID.setEnabled(mode_view)
		self.page.leID.setReadOnly(not mode_view)
		
		self.page.pbLoad.setEnabled(mode_view)

		self.page.pbNew.setEnabled(    mode_view and not pcb_exists  )
		self.page.pbEdit.setEnabled(   mode_view and     pcb_exists  )
		self.page.pbSave.setEnabled(   mode_editing or mode_creating )
		self.page.pbCancel.setEnabled( mode_editing or mode_creating )

		self.page.pbGoShipment.setEnabled(mode_view and shipments_exist)

		#self.page.leInsertUser.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.leLocation.setReadOnly(     not (mode_creating or mode_editing) )
		self.page.leBarcode.setReadOnly(      not (mode_creating or mode_editing) )
		self.page.leManufacturer.setReadOnly( not (mode_creating or mode_editing) )
		self.page.cbType.setEnabled(               mode_creating or mode_editing  )
		self.page.cbResolutionType.setEnabled(     mode_creating or mode_editing  )
		self.page.cbShape.setEnabled(              mode_creating or mode_editing  )
		self.page.cbGrade.setEnabled(              mode_creating or mode_editing  )
		#self.page.cbChirality.setEnabled(          mode_creating or mode_editing  )
		self.page.cbInstitution.setEnabled(        mode_creating or mode_editing  )
		self.page.cbInsertUser.setEnabled(         mode_creating or mode_editing  )
		self.page.sbNumRocs.setReadOnly(      not (mode_creating or mode_editing) )
		self.page.sbChannels.setReadOnly(     not (mode_creating or mode_editing) )

		self.page.pbDeleteComment.setEnabled(mode_creating or mode_editing)
		self.page.pbAddComment.setEnabled(   mode_creating or mode_editing)
		self.page.pteWriteComment.setEnabled(mode_creating or mode_editing)

		#self.page.leDaq.setReadOnly(        not (mode_creating or mode_editing) )
		self.page.cbGrade.setEnabled(            mode_creating or mode_editing  )
		#self.page.cbDaqOK.setEnabled(            mode_creating or mode_editing  )
		self.page.dsbFlatness.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.dsbThickness.setReadOnly( not (mode_creating or mode_editing) )

		#self.page.pbAddToPlotter.setEnabled(mode_view and daq_data_exists)
		#self.page.pbGoPlotter.setEnabled(   mode_view and daq_data_exists)

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
			#ID = self.page.leID.text()
			#self.sensor.new(ID)
			#self.mode = 'creating'  # update_info needs mode==view
			self.page.leStatus.setText("PCB DNE")
			self.update_info(do_load=False)
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
			self.updateElements()
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
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):

		#self.pcb.insertion_user  = str(self.page.leInsertUser.text()      )   if str(self.page.leInsertUser.text()        ) else None
		self.pcb.location        = str(self.page.leLocation.text()        )   if str(self.page.leLocation.text()          ) else None
		self.pcb.barcode         = str(self.page.leBarcode.text()         )   if str(self.page.leBarcode.text()           ) else None
		self.pcb.manufacturer    = str(self.page.leManufacturer.text()    )   if str(self.page.leManufacturer.text()      ) else None
		self.pcb.type            = str(self.page.cbType.currentText()     )   if str(self.page.cbType.currentText()       ) else None
		self.pcb.resolution_type = str(self.page.cbResolutionType.currentText()) \
                                                                              if str(self.page.cbType.currentText()       ) else None
		self.pcb.shape           = str(self.page.cbShape.currentText()    )   if str(self.page.cbShape.currentText()      ) else None
		self.pcb.grade           = str(self.page.cbGrade.currentText()    )   if str(self.page.cbGrade.currentText()      ) else None
		#self.pcb.chirality       = str(self.page.cbChirality.currentText())   if str(self.page.cbChirality.currentText()  ) else None
		self.pcb.institution     = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None
		self.pcb.insertion_user  = str(self.page.cbInsertUser.currentText())  if str(self.page.cbInsertUser.currentText())  else None
		self.pcb.num_rocs        = self.page.sbNumRocs.value()  if self.page.sbNumRocs.value()  >=0 else None
		self.pcb.channels        = self.page.sbChannels.value() if self.page.sbChannels.value() >=0 else None

		num_comments = self.page.listComments.count()
		self.pcb.comments = []
		for i in range(num_comments):
			self.pcb.comments.append(str(self.page.listComments.item(i).text()))

		#self.pcb.daq        = str(self.page.leDaq.text()              ) if str(self.page.leDaq.text()              ) else None
		self.pcb.grade      = str(self.page.cbGrade.currentText())      if str(self.page.cbGrade.currentText())      else None
		#self.pcb.daq_ok     = str(self.page.cbDaqOK.currentText()     ) if str(self.page.cbDaqOK.currentText()     ) else None
		self.pcb.flatness   =     self.page.dsbFlatness.value()         if     self.page.dsbFlatness.value()  >=0    else None
		self.pcb.thickness  =     self.page.dsbThickness.value()        if     self.page.dsbThickness.value() >=0    else None

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
	def goShipment(self,*args,**kwargs):
		item = self.page.listShipments.currentItem()
		if not (item is None):
			self.setUIPage('shipments',ID=str(item.text()))

	@enforce_mode('view')
	def goModule(self,*args,**kwargs):
		#ID = self.page.sbModule.value()
		#if ID >= 0:
		ID = self.page.leModule.text()
		if ID != "":
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


	@enforce_mode(['editing', 'creating'])
	def getFile(self,*args,**kwargs):
		f = self.fwnd.getdir()
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

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
