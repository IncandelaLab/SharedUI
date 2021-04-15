from filemanager import fm
import os
import shutil

from PyQt5.QtWidgets import QFileDialog, QWidget

PAGE_NAME = "view_sensor"
OBJECTTYPE = "sensor"
DEBUG = False

INDEX_TYPE = {
	'100 um':0,
	'200 um':1,
	'300 um':2,
	'500 um':3,
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

INDEX_SEMI = {
	"P-type":0,
	"N-type":1,
}

INDEX_INSPECTION = {
	'pass':0,
	True:0,
	'fail':1,
	False:1,
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
	'HEPHY':4,
	'HPK':5,
}

"""
class Filewindow(QWidget):
	def __init__(self):
		super(Filewindow, self).__init__()

	def getfile(self,*args,**kwargs):
		fname, fmt = QFileDialog.getOpenFileName(self, 'Open file', '~',"(*.jpg *.png *.xml)")
		print("File dialog:  got file", fname)
		return fname
"""

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.sensor = fm.sensor()
		self.sensor_exists = None

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

		#self.corners = [
		#	self.page.dsbC0,
		#	self.page.dsbC1,
		#	self.page.dsbC2,
		#	self.page.dsbC3,
		#	self.page.dsbC4,
		#	self.page.dsbC5
		#]

		#self.fwnd = Filewindow()
		#self.page.pbAddFiles.clicked.connect(self.getFile)
		#self.page.pbDeleteFile.clicked.connect(self.deleteFile)


	@enforce_mode(['view', 'editing', 'creating'])
	def update_info(self,ID=None,do_load=True,*args,**kwargs):
		if ID is None:
			#ID = self.page.sbID.value()
			ID = self.page.leID.text()
		else:
			#self.page.sbID.setValue(ID)
			self.page.leID.setText(ID)
		if do_load:
			self.sensor_exists = self.sensor.load(ID)
		else:
			self.sensor_exists = False

		#self.page.leID.setText(self.sensor.ID)

		self.page.listShipments.clear()
		for shipment in self.sensor.shipments:
			self.page.listShipments.addItem(str(shipment))

		self.page.leLocation.setText(    "" if self.sensor.location     is None else self.sensor.location    )
		self.page.leBarcode.setText( "" if self.sensor.barcode          is None else self.sensor.barcode     )
		self.page.cbType.setCurrentIndex(       INDEX_TYPE.get(       self.sensor.type,  -1)      )
		self.page.cbShape.setCurrentIndex(      INDEX_SHAPE.get(      self.sensor.shape, -1)      )
		self.page.leInsertUser.setText("" if self.sensor.insertion_user is None else self.sensor.insertion_user)
		self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.sensor.institution, -1))
		self.page.sbChannels.setValue(-1 if self.sensor.channels        is None else self.sensor.channels)

		if self.page.sbChannels.value() == -1:  self.page.sbChannels.clear()

		self.page.listComments.clear()
		for comment in self.sensor.comments:
			self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		#if self.sensor.corner_heights is None: 
		#	for corner in self.corners: 
		#		corner.setValue(-1) 
		#		corner.clear() 
		#else: 
		#	for i,corner in enumerate(self.corners): 
		#		corner.setValue(-1 if self.sensor.corner_heights[i] is None else self.sensor.corner_heights[i]) 
		#		if corner.value() == -1: corner.clear() 
 
		#self.page.leFlatness.setText("" if self.sensor.flatness is None else str(round(self.sensor.flatness,DISPLAY_PRECISION)))
		#self.page.dsbThickness.setValue(-1 if self.sensor.thickness is None else self.sensor.thickness) 
		#if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear() 
 
		self.page.sbStepKapton.setValue(-1 if self.sensor.step_kapton is None else self.sensor.step_kapton) 
		if self.page.sbStepKapton.value() == -1: self.page.sbStepKapton.clear() 
 
		#self.page.cbCheckEdgesFirm.setCurrentIndex(INDEX_CHECK.get(self.sensor.check_edges_firm, -1)) 
		self.page.cbCheckGlueSpill.setCurrentIndex(INDEX_CHECK.get(self.sensor.check_glue_spill, -1)) 
		#self.page.dsbKaptonFlatness.setValue(-1 if self.sensor.kapton_flatness is None else self.sensor.kapton_flatness) 
		#if self.page.dsbKaptonFlatness.value() == -1: self.page.dsbKaptonFlatness.clear()


		self.page.cbInspection.setCurrentIndex(INDEX_INSPECTION.get(self.sensor.inspection,-1))

		self.page.sbStepSensor.setValue( -1 if self.sensor.step_sensor is None else self.sensor.step_sensor)
		#self.page.sbProtomodule.setValue(-1 if self.sensor.protomodule is None else self.sensor.protomodule)
		#self.page.sbModule.setValue(     -1 if self.sensor.module      is None else self.sensor.module     )
		self.page.leProtomodule.setText("" if self.sensor.protomodule is None else self.sensor.protomodule)
		self.page.leModule.setText(     "" if self.sensor.module      is None else self.sensor.module)
		if self.page.sbStepSensor.value()  == -1: self.page.sbStepSensor.clear()
		#if self.page.sbProtomodule.value() == -1: self.page.sbProtomodule.clear()
		#if self.page.sbModule.value()      == -1: self.page.sbModule.clear()

		#self.page.listFiles.clear()
		#for f in self.sensor.test_files:
		#	name = os.path.split(f)[1]
		#	self.page.listFiles.addItem(name)

		self.updateElements()


	@enforce_mode(['view','editing','creating'])
	def updateElements(self):
		if not self.mode == "view":
			self.page.leStatus.setText(self.mode)

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'
		
		step_kapton_exists = self.page.sbStepKapton.value()  >=0
		sensor_exists      = self.sensor_exists
		shipments_exist    = self.page.listShipments.count() > 0
		step_sensor_exists = self.page.sbStepSensor.value()  >= 0
		#protomodule_exists = self.page.sbProtomodule.value() >= 0
		#module_exists      = self.page.sbModule.value() >= 0
		protomodule_exists = self.page.leProtomodule.text()  != ""
		module_exists      = self.page.leModule.text()       != ""

		self.setMainSwitchingEnabled(mode_view)
		#self.page.sbID.setEnabled(mode_view)
		self.page.leID.setReadOnly(not mode_view)

		self.page.pbLoad.setEnabled(mode_view)

		self.page.pbNew.setEnabled(     mode_view and not sensor_exists )
		self.page.pbEdit.setEnabled(    mode_view and     sensor_exists )
		self.page.pbSave.setEnabled(    mode_editing or mode_creating )
		self.page.pbCancel.setEnabled(  mode_editing or mode_creating )

		self.page.pbGoShipment.setEnabled(mode_view and shipments_exist)

		self.page.leInsertUser.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.leLocation.setReadOnly(     not (mode_creating or mode_editing) )
		self.page.leBarcode.setReadOnly(      not (mode_creating or mode_editing) )
		self.page.cbType.setEnabled(               mode_creating or mode_editing  )
		self.page.cbShape.setEnabled(              mode_creating or mode_editing  )
		self.page.cbInstitution.setEnabled(        mode_creating or mode_editing  )
		self.page.sbChannels.setReadOnly(     not (mode_creating or mode_editing) )

		self.page.pbDeleteComment.setEnabled(mode_creating or mode_editing)
		self.page.pbAddComment.setEnabled(   mode_creating or mode_editing)
		self.page.pteWriteComment.setEnabled(mode_creating or mode_editing)

		#for corner in self.corners:
		#	corner.setReadOnly(not (mode_creating or mode_editing))
		#self.page.dsbThickness.setReadOnly(not (mode_creating or mode_editing))

		self.page.pbGoStepKapton.setEnabled(mode_view and step_kapton_exists)
		#self.page.cbCheckEdgesFirm.setEnabled(mode_creating or mode_editing)
		self.page.cbCheckGlueSpill.setEnabled(mode_creating or mode_editing)
		#self.page.dsbKaptonFlatness.setReadOnly(not (mode_creating or mode_editing))

		self.page.cbInspection.setEnabled(   mode_creating or mode_editing   )
		self.page.pbGoStepSensor.setEnabled( mode_view and step_sensor_exists)
		self.page.pbGoProtomodule.setEnabled(mode_view and protomodule_exists)
		self.page.pbGoModule.setEnabled(     mode_view and module_exists     )

		#self.page.pbAddFiles.setEnabled(mode_creating or mode_editing)
		#self.page.pbDeleteFile.setEnabled(mode_creating or mode_editing)


	# NEW:
	@enforce_mode('view')
	def loadPart(self,*args,**kwargs):
		if self.page.leID.text == "":
			self.page.leStatus.setText("input an ID")
			return
		# Check whether baseplate exists:
		tmp_sensor = fm.sensor()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_sensor.load(tmp_ID)
		if not tmp_exists:  # DNE; good to create
			#ID = self.page.leID.text()
			#self.sensor.new(ID)
			#self.mode = 'creating'  # update_info needs mode==view
			self.page.leStatus.setText("sensor DNE")
			self.update_info(do_load=False)
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
		tmp_sensor = fm.sensor()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_sensor.load(tmp_ID)

		if not tmp_exists:
			ID = self.page.leID.text()
			self.sensor.new(ID)
			self.mode = 'creating'
			self.updateElements()
		else:
			self.page.leStatus.setText("already exists")

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_sensor = fm.sensor()
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
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):

		self.sensor.insertion_user = str(self.page.leInsertUser.text()      ) if str(self.page.leInsertUser.text()  )       else None
		self.sensor.location     = str(self.page.leLocation.text()          ) if str(self.page.leLocation.text()    )       else None
		self.sensor.barcode      = str(self.page.leBarcode.text()           ) if str(self.page.leBarcode.text()     )       else None
		self.sensor.type         = str(self.page.cbType.currentText()       ) if str(self.page.cbType.currentText() )       else None
		self.sensor.shape        = str(self.page.cbShape.currentText()      ) if str(self.page.cbShape.currentText())       else None
		self.sensor.institution  = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None
		self.sensor.channels     =     self.page.sbChannels.value()           if     self.page.sbChannels.value() >=0       else None

		num_comments = self.page.listComments.count()
		self.sensor.comments = []
		for i in range(num_comments):
			self.sensor.comments.append(str(self.page.listComments.item(i).text()))

		#self.sensor.corner_heights = [_.value() if _.value()>=0 else None for _ in self.corners]
		#self.sensor.thickness = self.page.dsbThickness.value() if self.page.dsbThickness.value()>=0 else None

		self.sensor.check_edges_firm = str(self.page.cbCheckEdgesFirm.currentText()) if str(self.page.cbCheckEdgesFirm.currentText()) else None
		self.sensor.check_glue_spill = str(self.page.cbCheckGlueSpill.currentText()) if str(self.page.cbCheckGlueSpill.currentText()) else None
		self.sensor.kapton_flatness  =     self.page.dsbKaptonFlatness.value()       if self.page.dsbKaptonFlatness.value() >=0       else None

		self.sensor.inspection = str(self.page.cbInspection.currentText()) if str(self.page.cbInspection.currentText()) else None

		self.sensor.save()
		self.mode = 'view'
		self.update_info()

		self.xmlModList.append(self.sensor.ID)


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


	"""
	@enforce_mode(['editing', 'creating'])
	def getFile(self,*args,**kwargs):
		f = self.fwnd.getfile()
		if f:
			# Need to call this to ensure that necessary dirs for storing item are created
			print("Got file.  Saving to ensure creation of filemanager location...")
			self.sensor.save()

			fname = os.path.split(f)[1]  # Name of file
			fdir, fname_ = self.sensor.get_filedir_filename()
			new_filepath = fdir + '/' + fname
			print("GETFILE:  Copying file", f, "to", new_filepath)
			shutil.copyfile(f, new_filepath)
			self.page.listComments.addItem(new_filepath)
			self.sensor.test_files.append(new_filepath)
			self.update_info()

	@enforce_mode(['editing', 'creating'])
	def deleteFile(self,*args,**kwargs):
		row = self.page.listFiles.currentRow()
		if row >= 0:
			fname = self.page.listFiles.item(row).text()
			self.page.listFiles.takeItem(row)
			# Now need to remove the file...
			fdir, fname_ = self.sensor.get_filedir_filename()
			new_filepath = fdir + '/' + fname
			print("REMOVING FILE", new_filepath)
			os.remove(new_filepath)
			self.sensor.test_files.remove(new_filepath)
			self.update_info()
	"""

	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			#if not (type(ID) is int):
			#	raise TypeError("Expected type <int> for ID; got <{}>".format(type(ID)))
			#if ID < 0:
			#	raise ValueError("ID cannot be negative")
			#self.page.sbID.setValue(ID)
			if not (type(ID) is str):
				raise TypeError("Expected type <str> for ID; got <{}>".format(type(ID)))
			self.page.leID.setText(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
