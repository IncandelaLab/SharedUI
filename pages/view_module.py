from filemanager import fm
from PyQt5 import QtCore
import time

PAGE_NAME = "view_module"
DEBUG = False
SITE_SEP = ', '
NO_DATE = [2000,1,1]

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

INDEX_INSPECTION = {
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
}


def separate_sites(sites_string):
	s = sites_string
	for char in SITE_SEP:
		s=s.replace(char, '\n')
	sites = [_ for _ in s.splitlines() if _]
	return sites

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

		self.page.pbGoShipment.clicked.connect(self.goShipment)

		self.page.pbGoStepKapton.clicked.connect(   self.goStepKapton   )
		self.page.pbGoStepSensor.clicked.connect(   self.goStepSensor   )
		self.page.pbGoStepPcb.clicked.connect(      self.goStepPcb      )
		self.page.pbGoBaseplate.clicked.connect(    self.goBaseplate    )
		self.page.pbGoSensor.clicked.connect(       self.goSensor       )
		self.page.pbGoPcb.clicked.connect(          self.goPcb          )
		self.page.pbGoProtomodule.clicked.connect(  self.goProtomodule  )

		self.page.pbDeleteComment.clicked.connect(self.deleteComment)
		self.page.pbAddComment.clicked.connect(self.addComment)

		self.page.pbIvAddToPlotter.clicked.connect( self.ivAddToPlotter )
		self.page.pbIvGoPlotter.clicked.connect(    self.ivGoPlotter    )
		self.page.pbDaqAddToPlotter.clicked.connect(self.daqAddToPlotter)
		self.page.pbDaqGoPlotter.clicked.connect(   self.daqGoPlotter   )




	@enforce_mode(['view', 'editing', 'creating'])
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.leID.text()
		else:
			self.page.leID.setText(ID)
		
		self.module_exists = self.module.load(ID)
		
		# shipments and location
		self.page.leInsertUser.setText("" if self.module.insertion_user is None else self.module.insertion_user)
		self.page.leLocation.setText("" if self.module.location is None else self.module.location)
		self.page.listShipments.clear()
		for shipment in self.module.shipments:
			self.page.listShipments.addItem(str(shipment))

		# characteristics
		self.page.sbChannels.setValue(  -1 if self.module.channels    is None else self.module.channels   )
		self.page.dsbThickness.setValue(-1 if self.module.thickness   is None else self.module.thickness  )
		self.page.cbShape.setCurrentIndex(      INDEX_SHAPE.get(      self.module.shape    , -1)  )
		self.page.cbChirality.setCurrentIndex(  INDEX_CHIRALITY.get(  self.module.chirality, -1)  )
		self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.module.institution, -1))
		if self.page.sbChannels.value()   == -1: self.page.sbChannels.clear()
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()

		# parts and steps
		self.page.sbStepKapton.setValue(   -1 if self.module.step_kapton   is None else self.module.step_kapton   )
		self.page.sbStepSensor.setValue(   -1 if self.module.step_sensor   is None else self.module.step_sensor   )
		self.page.sbStepPcb.setValue(      -1 if self.module.step_pcb      is None else self.module.step_pcb      )
		self.page.leBaseplate.setText(    "" if self.module.baseplate     is None else self.module.baseplate     )
		self.page.leSensor.setText(       "" if self.module.sensor        is None else self.module.sensor        )
		self.page.lePcb.setText(          "" if self.module.pcb           is None else self.module.pcb           )
		self.page.leProtomodule.setText(  "" if self.module.protomodule   is None else self.module.protomodule   )
		if self.page.sbStepKapton.value()   == -1:  self.page.sbStepKapton.clear()
		if self.page.sbStepSensor.value()   == -1:  self.page.sbStepSensor.clear()
		if self.page.sbStepPcb.value()      == -1:  self.page.sbStepPcb.clear()
		if self.page.leBaseplate.text()    == -1:  self.page.leBaseplate.clear()
		if self.page.leSensor.text()       == -1:  self.page.leSensor.clear()
		if self.page.lePcb.text()          == -1:  self.page.lePcb.clear()
		if self.page.leProtomodule.text()  == -1:  self.page.leProtomodule.clear()


		# comments
		self.page.listComments.clear()
		for comment in self.module.comments:
			self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		# finished module qualification
		self.page.ckHvCablesAttached.setChecked(False if self.module.hv_cables_attached is None else self.module.hv_cables_attached)
		self.page.leHvCablesAttachedUser.setText("" if self.module.hv_cables_attached_user is None else self.module.hv_cables_attached_user )
		self.page.leUnbiasedDaq.setText(         "" if self.module.unbiased_daq            is None else self.module.unbiased_daq            )
		self.page.leUnbiasedDaqUser.setText(     "" if self.module.unbiased_daq_user       is None else self.module.unbiased_daq_user       )
		self.page.leIv.setText(                  "" if self.module.iv                      is None else self.module.iv                      )
		self.page.leIvUser.setText(              "" if self.module.iv_user                 is None else self.module.iv_user                 )
		self.page.leBiasedDaq.setText(           "" if self.module.biased_daq              is None else self.module.biased_daq              )
		self.page.leBiasedDaqVoltage.setText(    "" if self.module.biased_daq_voltage      is None else self.module.biased_daq_voltage      )
		self.page.cbUnbiasedDaqOK.setCurrentIndex(INDEX_INSPECTION.get(self.module.unbiased_daq_ok, -1))
		self.page.cbIvOK.setCurrentIndex(         INDEX_INSPECTION.get(self.module.iv_ok          , -1))
		self.page.cbBiasedDaqOK.setCurrentIndex(  INDEX_INSPECTION.get(self.module.biased_daq_ok  , -1))

		# iv datasets
		self.page.listIvData.clear()
		for iv in self.module.iv_data:
			self.page.listIvData.addItem(iv)

		# daq datasets
		self.page.listDaqData.clear()
		for daq in self.module.daq_data:
			self.page.listDaqData.addItem(daq)

		self.updateElements()

	@enforce_mode(['view','editing','creating'])
	def updateElements(self):
		if not self.mode == "view":
			self.page.leStatus.setText(self.mode)

		module_exists   = self.module_exists
		shipments_exist = self.page.listShipments.count() > 0
		daq_data_exists = self.page.listDaqData.count()   > 0
		iv_data_exists  = self.page.listIvData.count()    > 0

		step_kapton_exists   = self.page.sbStepKapton.value()    >= 0
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

		# shipments and location
		self.page.pbGoShipment.setEnabled(mode_view and shipments_exist)

		# characteristics
		self.page.leInsertUser.setReadOnly( not (mode_creating or mode_editing) )
		self.page.leLocation.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.sbChannels.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.dsbThickness.setReadOnly( not (mode_creating or mode_editing) )
		self.page.cbShape.setEnabled(            mode_creating or mode_editing  )
		self.page.cbChirality.setEnabled(        mode_creating or mode_editing  )
		self.page.cbInstitution.setEnabled(      mode_creating or mode_editing  )

		# parts and steps
		self.page.pbGoStepKapton.setEnabled(   mode_view and step_kapton_exists   )
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

		# finished module qualification
		self.page.ckHvCablesAttached.setEnabled( mode_creating or mode_editing )
		self.page.leHvCablesAttachedUser.setReadOnly( not (mode_creating or mode_editing) )
		self.page.leUnbiasedDaq.setReadOnly(          not (mode_creating or mode_editing) )
		self.page.leUnbiasedDaqUser.setReadOnly(      not (mode_creating or mode_editing) )
		self.page.leIv.setReadOnly(                   not (mode_creating or mode_editing) )
		self.page.leIvUser.setReadOnly(               not (mode_creating or mode_editing) )
		self.page.leBiasedDaq.setReadOnly(            not (mode_creating or mode_editing) )
		self.page.leBiasedDaqVoltage.setReadOnly(     not (mode_creating or mode_editing) )
		self.page.cbUnbiasedDaqOK.setEnabled( mode_creating or mode_editing )
		self.page.cbIvOK.setEnabled(          mode_creating or mode_editing )
		self.page.cbBiasedDaqOK.setEnabled(   mode_creating or mode_editing )

		# iv datasets
		self.page.pbIvAddToPlotter.setEnabled(mode_view and iv_data_exists)
		self.page.pbIvGoPlotter.setEnabled(   mode_view and iv_data_exists)

		# daq datasets
		self.page.pbDaqAddToPlotter.setEnabled(mode_view and daq_data_exists)
		self.page.pbDaqGoPlotter.setEnabled(   mode_view and daq_data_exists)


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
			self.update_info()
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
		self.module.insertion_user = str(self.page.leInsertUser.text()   ) if str(self.page.leInsertUser.text())         else None
		self.module.location    = str(self.page.leLocation.text()        ) if str(self.page.leLocation.text())           else None
		self.module.channels    =     self.page.sbChannels.value()         if self.page.sbChannels.value()   >= 0          else None
		self.module.thickness   =     self.page.dsbThickness.value()       if self.page.dsbThickness.value() >= 0          else None
		self.module.shape       = str(self.page.cbShape.currentText()    ) if str(self.page.cbShape.currentText()        ) else None
		self.module.chirality   = str(self.page.cbChirality.currentText()) if str(self.page.cbChirality.currentText()    ) else None
		self.module.institution = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None

		# comments
		num_comments = self.page.listComments.count()
		self.module.comments = []
		for i in range(num_comments):
			self.module.comments.append(str(self.page.listComments.item(i).text()))

		# finished module qualification
		self.module.hv_cables_attached  = self.page.ckHvCablesAttached.isChecked()
		self.module.hv_cables_attached_user = str(self.page.leHvCablesAttachedUser.text()) if str(self.page.leHvCablesAttachedUser.text()) else None
		self.module.unbiased_daq            = str(self.page.leUnbiasedDaq.text()         ) if str(self.page.leUnbiasedDaq.text()         ) else None
		self.module.unbiased_daq_user       = str(self.page.leUnbiasedDaqUser.text()     ) if str(self.page.leUnbiasedDaqUser.text()     ) else None
		self.module.iv                      = str(self.page.leIv.text()                  ) if str(self.page.leIv.text()                  ) else None
		self.module.iv_user                 = str(self.page.leIvUser.text()              ) if str(self.page.leIvUser.text()              ) else None
		self.module.biased_daq              = str(self.page.leBiasedDaq.text()           ) if str(self.page.leBiasedDaq.text()           ) else None
		self.module.biased_daq_voltage      = str(self.page.leBiasedDaqVoltage.text()    ) if str(self.page.leBiasedDaqVoltage.text()    ) else None
		self.module.unbiased_daq_ok = str(self.page.cbUnbiasedDaqOK.currentText()) if str(self.page.cbUnbiasedDaqOK.currentText()) else None
		self.module.iv_ok           = str(self.page.cbIvOK.currentText()         ) if str(self.page.cbIvOK.currentText()         ) else None
		self.module.biased_daq_ok   = str(self.page.cbBiasedDaqOK.currentText()  ) if str(self.page.cbBiasedDaqOK.currentText()  ) else None

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
		ID = self.page.lePcb.value()
		if ID != "":
			self.setUIPage('PCBs',ID=ID)

	@enforce_mode('view')
	def goProtomodule(self,*args,**kwargs):
		#ID = self.page.sbProtomodule.value()
		#if ID>=0:
		ID = self.page.leProtomodule.value()
		if ID != "":
			self.setUIPage('protomodules',ID=ID)

	@enforce_mode('view')
	def goShipment(self,*args,**kwargs):
		item = self.page.listShipments.currentItem()
		if not (item is None):
			self.setUIPage('shipments',ID=str(item.text()))

	@enforce_mode('view')
	def goStepKapton(self,*args,**kwargs):
		ID = self.page.sbStepKapton.value()
		if ID>=0:
			self.setUIPage('kapton placement steps',ID=ID)

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




	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is str):
				raise TypeError("Expected type <str> for ID; got <{}>".format(type(ID)))
			#if ID < 0:
			#	raise ValueError("ID cannot be negative")
			self.page.sbID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
