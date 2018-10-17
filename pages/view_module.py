class func(object):

	def __init__(self,fm,page,setUIPage):
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage

		self.ivModuleID = None
		self.ivDataName = None
		self.ivData     = None

		self.rig()
		self.update_info()


	def rig(self):
		self.page.sbModuleID.valueChanged.connect(self.update_info)
		self.page.pbGoBaseplate.clicked.connect(self.goBaseplate)
		self.page.pbGoSensor.clicked.connect(self.goSensor)
		self.page.pbGoPCB.clicked.connect(self.goPCB)

		self.page.cbIVCurves.currentIndexChanged.connect(self.updateIVData)
		self.page.ckPlotAsc.stateChanged.connect(self.updateIVPlot)
		self.page.ckPlotDesc.stateChanged.connect(self.updateIVPlot)
		self.page.cbRawXAxis.currentIndexChanged.connect(self.updateIVPlot)
		self.page.cbRawYAxis.currentIndexChanged.connect(self.updateIVPlot)
		self.page.tabBinsRaw.currentChanged.connect(self.updateIVPlot)

	def update_info(self,ID=None):
		if ID is None:ID = self.page.sbModuleID.value()
		info, IVtests = self.fm.loadModuleDetails(ID)
		
		if info is None:
			self.page.leBaseplateID.setText( '' )
			self.page.leSensorID.setText(    '' )
			self.page.lePCBID.setText(       '' )
			self.page.leThickness.setText(   '' )

		else:
			self.page.leBaseplateID.setText( info['baseplate'])
			self.page.leSensorID.setText(    info['sensor']   )
			self.page.lePCBID.setText(       info['PCB']      )
			self.page.leThickness.setText(   info['thickness'])

		self.page.cbIVCurves.clear()
		if not (IVtests is None):
			self.page.cbIVCurves.addItems(IVtests)

	def updateIVData(self,index):
		#print("")
		#print("Beginning updateIVData")
		if self.page.cbIVCurves.currentIndex() == -1:
			#print("index -1 : data set to None")
			self.ivData = None
			self.ivDataName = None
			self.ivModuleID = self.page.sbModuleID.value()
			#print("")
			self.updateIVPlot()
			return

		if self.page.sbModuleID.value() == self.ivModuleID and self.page.cbIVCurves.currentText() == self.ivDataName:
			#print("Neither module ID nor text selection have changed : not changing data")
			#print("")
			return
		
		#print("New module ID ({} -> {}) or text ({} -> {}) - load new dataset!".format(self.ivModuleID,self.page.sbModuleID.value(),self.ivDataName,self.page.cbIVCurves.currentText()))
		self.ivModuleID = self.page.sbModuleID.value()
		self.ivDataName = self.page.cbIVCurves.currentText()
		self.ivData     = self.fm.loadModuleIV(self.ivModuleID,self.ivDataName)
		#print("")
		self.updateIVPlot()

	def updateIVPlot(self,*args,**kwargs):
		print("Update plot!")





	def goBaseplate(self):
		ID = self.page.leBaseplateID.text()
		if len(ID) > 0:
			try:
				ID = int(ID)
			except:
				return
			self.setUIPage('baseplates',ID=ID)
		else:
			return

	def goSensor(self):
		ID = self.page.leSensorID.text()
		if len(ID) > 0:
			try:
				ID = int(ID)
			except:
				return
			self.setUIPage('sensors',ID=ID)
		else:
			return

	def goPCB(self):
		ID = self.page.lePCBID.text()
		if len(ID) > 0:
			try:
				ID = int(ID)
			except:
				return
			self.setUIPage('PCBs',ID=ID)
		else:
			return




	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is int):
				raise TypeError("Expected type <int> for ID; got <{}>".format(type(ID)))
			if ID < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbModuleID.setValue(ID)
