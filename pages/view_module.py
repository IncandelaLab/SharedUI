from PyQt4 import QtCore
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
		self.page.sbID.valueChanged.connect(self.update_info)

		self.page.pbNew.clicked.connect(self.startCreating)
		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

		self.page.pbGoShipment.clicked.connect(self.goShipment)

		self.page.pbGoStepKapton.clicked.connect(   self.goStepKapton   )
		self.page.pbGoStepKapton_2.clicked.connect( self.goStepKapton_2 )
		self.page.pbGoStepSensor.clicked.connect(   self.goStepSensor   )
		self.page.pbGoStepPcb.clicked.connect(      self.goStepPcb      )
		self.page.pbGoBaseplate.clicked.connect(    self.goBaseplate    )
		self.page.pbGoSensor.clicked.connect(       self.goSensor       )
		self.page.pbGoPcb.clicked.connect(          self.goPcb          )
		self.page.pbGoProtomodule.clicked.connect(  self.goProtomodule  )

		self.page.pbDeleteComment.clicked.connect(self.deleteComment)
		self.page.pbAddComment.clicked.connect(self.addComment)

		self.page.pbCureStartNow.clicked.connect(self.cureStartNow)
		self.page.pbCureStopNow.clicked.connect( self.cureStopNow )

		self.page.pbIvAddToPlotter.clicked.connect( self.ivAddToPlotter )
		self.page.pbIvGoPlotter.clicked.connect(    self.ivGoPlotter    )
		self.page.pbDaqAddToPlotter.clicked.connect(self.daqAddToPlotter)
		self.page.pbDaqGoPlotter.clicked.connect(   self.daqGoPlotter   )




	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbID.value()
		else:
			self.page.sbID.setValue(ID)

		self.module_exists = self.module.load(ID)
		
		# shipments and location
		self.page.leLocation.setText("" if self.module.location is None else self.module.location)
		self.page.listShipments.clear()
		for shipment in self.module.shipments:
			self.page.listShipments.addItem(str(shipment))

		# characteristics
		self.page.leNumKaptons.setText( "" if self.module.num_kaptons is None else self.module.num_kaptons)
		self.page.sbChannels.setValue(  -1 if self.module.channels    is None else self.module.channels   )
		self.page.dsbThickness.setValue(-1 if self.module.thickness   is None else self.module.thickness  )
		self.page.sbRotation.setValue(  -1 if self.module.rotation    is None else self.module.rotation   )
		self.page.cbSize.setCurrentIndex(     INDEX_SIZE.get(     self.module.size     , -1))
		self.page.cbShape.setCurrentIndex(    INDEX_SHAPE.get(    self.module.shape    , -1))
		self.page.cbChirality.setCurrentIndex(INDEX_CHIRALITY.get(self.module.chirality, -1))
		if self.page.sbChannels.value()   == -1: self.page.sbChannels.clear()
		if self.page.dsbThickness.value() == -1: self.page.dsbThickness.clear()
		if self.page.sbRotation.value()   == -1: self.page.sbRotation.clear()

		# parts and steps
		self.page.sbStepKapton.setValue(   -1 if self.module.step_kapton   is None else self.module.step_kapton   )
		self.page.sbStepKapton_2.setValue( -1 if self.module.step_kapton_2 is None else self.module.step_kapton_2 )
		self.page.sbStepSensor.setValue(   -1 if self.module.step_sensor   is None else self.module.step_sensor   )
		self.page.sbStepPcb.setValue(      -1 if self.module.step_pcb      is None else self.module.step_pcb      )
		self.page.sbBaseplate.setValue(    -1 if self.module.baseplate     is None else self.module.baseplate     )
		self.page.sbSensor.setValue(       -1 if self.module.sensor        is None else self.module.sensor        )
		self.page.sbPcb.setValue(          -1 if self.module.pcb           is None else self.module.pcb           )
		self.page.sbProtomodule.setValue(  -1 if self.module.protomodule   is None else self.module.protomodule   )
		if self.page.sbStepKapton.value()   == -1:self.page.sbStepKapton.clear()
		if self.page.sbStepKapton_2.value() == -1:self.page.sbStepKapton_2.clear()
		if self.page.sbStepSensor.value()   == -1:self.page.sbStepSensor.clear()
		if self.page.sbStepPcb.value()      == -1:self.page.sbStepPcb.clear()
		if self.page.sbBaseplate.value()    == -1:self.page.sbBaseplate.clear()
		if self.page.sbSensor.value()       == -1:self.page.sbSensor.clear()
		if self.page.sbPcb.value()          == -1:self.page.sbPcb.clear()
		if self.page.sbProtomodule.value()  == -1:self.page.sbProtomodule.clear()

		# comments
		self.page.listComments.clear()
		for comment in self.module.comments:
			self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		# pre-wirebonding qualification
		self.page.cbCheckEdgeContact.setCurrentIndex(INDEX_INSPECTION.get(self.module.check_glue_edge_contact, -1))
		self.page.cbCheckGlueSpill.setCurrentIndex(  INDEX_INSPECTION.get(self.module.check_glue_spill  , -1))
		self.page.cbUnbondedDaqOK.setCurrentIndex(   INDEX_INSPECTION.get(self.module.unbonded_daq_ok   , -1))
		self.page.leUnbondedDaq.setText(    "" if self.module.unbonded_daq      is None else self.module.unbonded_daq     )
		self.page.leUnbondedDaqUser.setText("" if self.module.unbonded_daq_user is None else self.module.unbonded_daq_user)

		# wirebonding
		self.page.ckWirebonding.setChecked(       False if self.module.wirebonding          is None else self.module.wirebonding         )
		self.page.ckTestBonds.setChecked(         False if self.module.test_bonds           is None else self.module.test_bonds          )
		self.page.ckTestBondsPulled.setChecked(   False if self.module.test_bonds_pulled    is None else self.module.test_bonds_pulled   )
		self.page.ckTestBondsRebonded.setChecked( False if self.module.test_bonds_rebonded  is None else self.module.test_bonds_rebonded )
		self.page.ckWirebondsInspected.setChecked(False if self.module.wirebonds_inspected  is None else self.module.wirebonds_inspected )
		self.page.ckWirebondsRepaired.setChecked( False if self.module.wirebonds_repaired   is None else self.module.wirebonds_repaired  )
		self.page.leWirebondingUser.setText(      "" if self.module.wirebonding_user         is None else self.module.wirebonding_user        )
		self.page.leWirebondsRepairedUser.setText("" if self.module.wirebonds_repaired_user  is None else self.module.wirebonds_repaired_user )
		self.page.leTestBondsPulledUser.setText(  "" if self.module.test_bonds_pulled_user   is None else self.module.test_bonds_pulled_user  )
		self.page.leTestBondsRebondedUser.setText("" if self.module.test_bonds_rebonded_user is None else self.module.test_bonds_rebonded_user)
		self.page.pteUnbondedSites.setPlainText(        "" if self.module.wirebonding_unbonded_sites          is None else SITE_SEP.join(self.module.wirebonding_unbonded_sites         ))
		self.page.pteWirebondsDamaged.setPlainText(     "" if self.module.wirebonds_damaged       is None else SITE_SEP.join(self.module.wirebonds_damaged      ))
		self.page.pteWirebondsRepairedList.setPlainText("" if self.module.wirebonds_repaired_list is None else SITE_SEP.join(self.module.wirebonds_repaired_list))
		self.page.cbTestBondsPulledOK.setCurrentIndex(  INDEX_INSPECTION.get(self.module.test_bonds_pulled_ok  , -1))
		self.page.cbTestBondsRebondedOK.setCurrentIndex(INDEX_INSPECTION.get(self.module.test_bonds_rebonded_ok, -1))

		# wirebonding qualification
		self.page.ckWirebondingFinalInspection.setChecked(False if self.module.wirebonding_final_inspection is None else self.module.wirebonding_final_inspection)
		self.page.leWirebondingFinalInspectionUser.setText("" if self.module.wirebonding_final_inspection_user is None else self.module.wirebonding_final_inspection_user)
		self.page.cbWirebondingFinalInspectionOK.setCurrentIndex(INDEX_INSPECTION.get(self.module.wirebonding_final_inspection_ok,-1))

		# encapsulation
		self.page.ckEncapsulation.setChecked(False if self.module.encapsulation is None else self.module.encapsulation)
		self.page.leEncapsulationUser.setText("" if self.module.encapsulation_user is None else self.module.encapsulation_user)
		self.page.cbEncapsulationInspection.setCurrentIndex(INDEX_INSPECTION.get(self.module.encapsulation_inspection,-1))
		if self.module.encapsulation_cure_start is None:
			self.page.dtCureStart.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStart.setTime(QtCore.QTime(0,0,0))
		else:
			localtime = list(time.localtime(self.module.encapsulation_cure_start))
			self.page.dtCureStart.setDate(QtCore.QDate(*localtime[0:3]))
			self.page.dtCureStart.setTime(QtCore.QTime(*localtime[3:6]))

		if self.module.encapsulation_cure_stop is None:
			self.page.dtCureStop.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStop.setTime(QtCore.QTime(0,0,0))
		else:
			localtime = list(time.localtime(self.module.encapsulation_cure_stop))
			self.page.dtCureStop.setDate(QtCore.QDate(*localtime[0:3]))
			self.page.dtCureStop.setTime(QtCore.QTime(*localtime[3:6]))

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
		module_exists   = self.module_exists
		shipments_exist = self.page.listShipments.count() > 0
		daq_data_exists = self.page.listDaqData.count()   > 0
		iv_data_exists  = self.page.listIvData.count()    > 0

		step_kapton_exists   = self.page.sbStepKapton.value()    >= 0
		step_kapton_2_exists = self.page.sbStepKapton_2.value()  >= 0
		step_sensor_exists   = self.page.sbStepSensor.value()    >= 0
		step_pcb_exists      = self.page.sbStepPcb.value()       >= 0
		baseplate_exists   = self.page.sbBaseplate.value()   >= 0
		sensor_exists      = self.page.sbSensor.value()      >= 0
		pcb_exists         = self.page.sbPcb.value()         >= 0
		protomodule_exists = self.page.sbProtomodule.value() >= 0

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'

		self.setMainSwitchingEnabled(mode_view) 
		self.page.sbID.setEnabled(mode_view)

		self.page.pbNew   .setEnabled( mode_view and not module_exists )
		self.page.pbEdit  .setEnabled( mode_view and     module_exists )
		self.page.pbSave  .setEnabled( mode_creating or mode_editing   )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing   )

		# shipments and location
		self.page.pbGoShipment.setEnabled(mode_view and shipments_exist)

		# characteristics
		self.page.sbChannels.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.dsbThickness.setReadOnly( not (mode_creating or mode_editing) )
		self.page.sbRotation.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.cbSize.setEnabled(      mode_creating or mode_editing )
		self.page.cbShape.setEnabled(     mode_creating or mode_editing )
		self.page.cbChirality.setEnabled( mode_creating or mode_editing )

		# parts and steps
		self.page.pbGoStepKapton.setEnabled(   mode_view and step_kapton_exists   )
		self.page.pbGoStepKapton_2.setEnabled( mode_view and step_kapton_2_exists )
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

		# pre-wirebonding qualification
		self.page.cbCheckEdgeContact.setEnabled( mode_creating or mode_editing )
		self.page.cbCheckGlueSpill.setEnabled(   mode_creating or mode_editing )
		self.page.cbUnbondedDaqOK.setEnabled(    mode_creating or mode_editing )
		self.page.leUnbondedDaq.setReadOnly(     not (mode_creating or mode_editing) )
		self.page.leUnbondedDaqUser.setReadOnly( not (mode_creating or mode_editing) )

		# wirebonding
		self.page.ckWirebonding.setEnabled(        mode_creating or mode_editing )
		self.page.ckTestBonds.setEnabled(          mode_creating or mode_editing )
		self.page.ckTestBondsPulled.setEnabled(    mode_creating or mode_editing )
		self.page.ckTestBondsRebonded.setEnabled(  mode_creating or mode_editing )
		self.page.ckWirebondsInspected.setEnabled( mode_creating or mode_editing )
		self.page.ckWirebondsRepaired.setEnabled(  mode_creating or mode_editing )
		self.page.leWirebondingUser.setReadOnly(        not (mode_creating or mode_editing) )
		self.page.leWirebondsRepairedUser.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.leTestBondsPulledUser.setReadOnly(    not (mode_creating or mode_editing) )
		self.page.leTestBondsRebondedUser.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.pteUnbondedSites.setReadOnly(         not (mode_creating or mode_editing) )
		self.page.pteWirebondsDamaged.setReadOnly(      not (mode_creating or mode_editing) )
		self.page.pteWirebondsRepairedList.setReadOnly( not (mode_creating or mode_editing) )
		self.page.cbTestBondsPulledOK.setEnabled(   mode_creating or mode_editing )
		self.page.cbTestBondsRebondedOK.setEnabled( mode_creating or mode_editing )

		# wirebonding qualification
		self.page.ckWirebondingFinalInspection.setEnabled( mode_creating or mode_editing )
		self.page.leWirebondingFinalInspectionUser.setReadOnly( not (mode_creating or mode_editing) )
		self.page.cbWirebondingFinalInspectionOK.setEnabled( mode_creating or mode_editing )

		# encapsulation
		self.page.ckEncapsulation.setEnabled( mode_creating or mode_editing )
		self.page.leEncapsulationUser.setReadOnly( not (mode_creating or mode_editing) )
		self.page.cbEncapsulationInspection.setEnabled( mode_creating or mode_editing )
		self.page.dtCureStart.setReadOnly( not (mode_creating or mode_editing) )
		self.page.dtCureStop.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.pbCureStartNow.setEnabled( mode_creating or mode_editing )
		self.page.pbCureStopNow.setEnabled(  mode_creating or mode_editing )

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


	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if not self.module_exists:
			ID = self.page.sbID.value()
			self.mode = 'creating'
			self.module.new(ID)
			self.updateElements()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if self.module_exists:
			self.mode = 'editing'
			self.updateElements()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):
		# characteristics
		self.module.channels  = self.page.sbChannels.value()   if self.page.sbChannels.value()   >= 0 else None
		self.module.thickness = self.page.dsbThickness.value() if self.page.dsbThickness.value() >= 0 else None
		self.module.rotation  = self.page.sbRotation.value()   if self.page.sbRotation.value()   >= 0 else None
		self.module.size      = str(self.page.cbSize.currentText()     ) if str(self.page.cbSize.currentText()     ) else None
		self.module.shape     = str(self.page.cbShape.currentText()    ) if str(self.page.cbShape.currentText()    ) else None
		self.module.chirality = str(self.page.cbChirality.currentText()) if str(self.page.cbChirality.currentText()) else None

		# comments
		num_comments = self.page.listComments.count()
		self.module.comments = []
		for i in range(num_comments):
			self.module.comments.append(str(self.page.listComments.item(i).text()))

		# pre-wirebonding qualification
		self.module.check_glue_edge_contact = str(self.page.cbCheckEdgeContact.currentText()) if str(self.page.cbCheckEdgeContact.currentText()) else None
		self.module.check_glue_spill        = str(self.page.cbCheckGlueSpill.currentText()  ) if str(self.page.cbCheckGlueSpill.currentText()  ) else None
		self.module.unbonded_daq_ok         = str(self.page.cbUnbondedDaqOK.currentText()   ) if str(self.page.cbUnbondedDaqOK.currentText()   ) else None
		self.module.unbonded_daq            = str(self.page.leUnbondedDaq.text()    ) if str(self.page.leUnbondedDaq.text()    ) else None
		self.module.unbonded_daq_user       = str(self.page.leUnbondedDaqUser.text()) if str(self.page.leUnbondedDaqUser.text()) else None

		# wirebonding
		self.module.wirebonding              = self.page.ckWirebonding.isChecked()
		self.module.test_bonds               = self.page.ckTestBonds.isChecked()
		self.module.test_bonds_pulled        = self.page.ckTestBondsPulled.isChecked()
		self.module.test_bonds_rebonded      = self.page.ckTestBondsRebonded.isChecked()
		self.module.wirebonds_inspected      = self.page.ckWirebondsInspected.isChecked()
		self.module.wirebonds_repaired       = self.page.ckWirebondsRepaired.isChecked()
		self.module.wirebonding_user         = str(self.page.leWirebondingUser.text()      ) if str(self.page.leWirebondingUser.text()      ) else None
		self.module.wirebonds_repaired_user  = str(self.page.leWirebondsRepairedUser.text()) if str(self.page.leWirebondsRepairedUser.text()) else None
		self.module.test_bonds_pulled_user   = str(self.page.leTestBondsPulledUser.text()  ) if str(self.page.leTestBondsPulledUser.text()  ) else None
		self.module.test_bonds_rebonded_user = str(self.page.leTestBondsRebondedUser.text()) if str(self.page.leTestBondsRebondedUser.text()) else None
		self.module.wirebonding_unbonded_sites = separate_sites(str(self.page.pteUnbondedSites.toPlainText()        )) if str(self.page.pteUnbondedSites.toPlainText()        ) else None
		self.module.wirebonds_damaged          = separate_sites(str(self.page.pteWirebondsDamaged.toPlainText()     )) if str(self.page.pteWirebondsDamaged.toPlainText()     ) else None
		self.module.wirebonds_repaired_list    = separate_sites(str(self.page.pteWirebondsRepairedList.toPlainText())) if str(self.page.pteWirebondsRepairedList.toPlainText()) else None
		self.module.test_bonds_pulled_ok   = str(self.page.cbTestBondsPulledOK.currentText()  ) if str(self.page.cbTestBondsPulledOK.currentText()  ) else None
		self.module.test_bonds_rebonded_ok = str(self.page.cbTestBondsRebondedOK.currentText()) if str(self.page.cbTestBondsRebondedOK.currentText()) else None

		# wirebonding qualification
		self.module.wirebonding_final_inspection      = self.page.ckWirebondingFinalInspection.isChecked()
		self.module.wirebonding_final_inspection_user = str(self.page.leWirebondingFinalInspectionUser.text()     ) if str(self.page.leWirebondingFinalInspectionUser.text()     ) else None
		self.module.wirebonding_final_inspection_ok   = str(self.page.cbWirebondingFinalInspectionOK.currentText()) if str(self.page.cbWirebondingFinalInspectionOK.currentText()) else None

		# encapsulation
		self.module.encapsulation            = self.page.ckEncapsulation.isChecked()
		self.module.encapsulation_user       = str(self.page.leEncapsulationUser.text()             ) if str(self.page.leEncapsulationUser.text()             ) else None
		self.module.encapsulation_inspection = str(self.page.cbEncapsulationInspection.currentText()) if str(self.page.cbEncapsulationInspection.currentText()) else None
		if self.page.dtCureStart.date().year() == NO_DATE[0]:
			self.module.encapsulation_cure_start = None
		else:
			self.module.encapsulation_cure_start = self.page.dtCureStart.dateTime().toTime_t()
		if self.page.dtCureStop.date().year() == NO_DATE[0]:
			self.module.encapsulation_cure_stop = None
		else:
			self.module.encapsulation_cure_stop = self.page.dtCureStop.dateTime().toTime_t()

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



	@enforce_mode(['editing','creating'])
	def cureStartNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStart.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStart.setTime(QtCore.QTime(*localtime[3:6]))

	@enforce_mode(['editing','creating'])
	def cureStopNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStop.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStop.setTime(QtCore.QTime(*localtime[3:6]))

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
		ID = self.page.sbBaseplate.value()
		if ID>=0:
			self.setUIPage('baseplates',ID=ID)

	@enforce_mode('view')
	def goSensor(self,*args,**kwargs):
		ID = self.page.sbSensor.value()
		if ID>=0:
			self.setUIPage('sensors',ID=ID)

	@enforce_mode('view')
	def goPcb(self,*args,**kwargs):
		ID = self.page.sbPcb.value()
		if ID>=0:
			self.setUIPage('PCBs',ID=ID)

	@enforce_mode('view')
	def goProtomodule(self,*args,**kwargs):
		ID = self.page.sbProtomodule.value()
		if ID>=0:
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
	def goStepKapton_2(self,*args,**kwargs):
		ID = self.page.sbStepKapton_2.value()
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
			if not (type(ID) is int):
				raise TypeError("Expected type <int> for ID; got <{}>".format(type(ID)))
			if ID < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
