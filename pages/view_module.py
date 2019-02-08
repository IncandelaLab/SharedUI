from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg    as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

PAGE_NAME = "view_module"
DEBUG = False

USE_MICROAMP = True
MICRO = 1e6

LBL_TIME = 'time (seconds)'
LBL_VOLTAGE = 'voltage (volts)'
LBL_CURRENT = 'current ({})'.format('microamps' if USE_MICROAMP else 'amps')
LBL_VSOURCE = 'sourced voltage (volts)'
LABELS = [LBL_TIME,LBL_VOLTAGE,LBL_CURRENT,LBL_VSOURCE]


class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.ivModuleID = None
		self.ivDataName = None
		self.ivData     = None

		self.info = None
		self.IVtests = None
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
		self.setupFigures()
		self.rig()
		self.mode = 'view'
		print("{} setup completed".format(PAGE_NAME))
		self.update_info()

	@enforce_mode('setup')
	def setupFigures(self):
		self.fig = Figure()
		self.ax  = self.fig.add_subplot(111)
		self.fc  = FigureCanvas(self.fig)
		self.tb  = NavigationToolbar(self.fc,self.page)
		self.page.vlPlotIV.addWidget(self.tb)
		self.page.vlPlotIV.addWidget(self.fc)

	@enforce_mode('setup')
	def rig(self):
		self.page.sbModuleID.valueChanged.connect(self.update_info)
		self.page.pbGoBaseplate.clicked.connect(self.goBaseplate)
		self.page.pbGoSensor.clicked.connect(self.goSensor)
		self.page.pbGoPCB.clicked.connect(self.goPCB)
		self.page.pbGoKaptonStep.clicked.connect(self.goKaptonStep)
		self.page.pbGoSensorStep.clicked.connect(self.goSensorStep)
		self.page.pbGoPCBStep.clicked.connect(self.goPCBStep)

		self.page.cbIVCurves.currentIndexChanged.connect(self.updateIVData)
		self.page.ckPlotAsc.stateChanged.connect(self.updateIVPlot)
		self.page.ckPlotDesc.stateChanged.connect(self.updateIVPlot)
		self.page.cbBinsXAxis.currentIndexChanged.connect(self.updateIVPlot)
		self.page.cbBinsYAxis.currentIndexChanged.connect(self.updateIVPlot)
		self.page.cbRawXAxis.currentIndexChanged.connect(self.updateIVPlot)
		self.page.cbRawYAxis.currentIndexChanged.connect(self.updateIVPlot)
		self.page.tabBinsRaw.currentChanged.connect(self.updateIVPlot)

		self.page.pbModuleNew.clicked.connect(self.startCreating)
		self.page.pbModuleEdit.clicked.connect(self.startEditing)
		self.page.pbModuleSave.clicked.connect(self.saveEditig)
		self.page.pbModuleCancel.clicked.connect(self.cancelEditing)


	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:ID = self.page.sbModuleID.value()
		self.info, self.IVtests = self.fm.loadModuleDetails(ID)
		self.updateElements(use_info=True)
		#print(self.info)

	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info = False):
		if use_info:
			if self.info is None:
				self.page.sbBaseplateID.setValue( -1  );self.page.sbBaseplateID.clear()
				self.page.sbSensorID.setValue(    -1  );self.page.sbSensorID.clear()
				self.page.sbPCBID.setValue(       -1  );self.page.sbPCBID.clear()
				self.page.dsbThickness.setValue(  -1.0);self.page.dsbThickness.clear()
				self.page.sbKaptonStep.setValue(  -1  );self.page.sbKaptonStep.clear()
				self.page.sbSensorStep.setValue(  -1  );self.page.sbSensorStep.clear()
				self.page.sbPCBStep.setValue(     -1  );self.page.sbPCBStep.clear()

			else:
				self.page.sbBaseplateID.setValue( self.info['baseplate']  ) # Load values into UI elements
				self.page.sbSensorID.setValue(    self.info['sensor']     ) # 
				self.page.sbPCBID.setValue(       self.info['PCB']        ) # 
				self.page.dsbThickness.setValue(  self.info['thickness']  ) # 
				self.page.sbKaptonStep.setValue(  self.info['kaptonstep'] ) # 
				self.page.sbSensorStep.setValue(  self.info['sensorstep'] ) # 
				self.page.sbPCBStep.setValue(     self.info['PCBstep']    ) # 

				if self.info['baseplate']  == -1  : self.page.sbBaseplateID.clear() # clear UI elements with "empty" values
				if self.info['sensor']     == -1  : self.page.sbSensorID.clear()    #
				if self.info['PCB']        == -1  : self.page.sbPCBID.clear()       #
				if self.info['thickness']  == -1.0: self.page.dsbThickness.clear()  #
				if self.info['kaptonstep'] == -1  : self.page.sbKaptonStep.clear()  #
				if self.info['sensorstep'] == -1  : self.page.sbSensorStep.clear()  #
				if self.info['PCBstep']    == -1  : self.page.sbPCBStep.clear()     #



			self.page.cbIVCurves.clear()
			if not (self.IVtests is None):
				self.page.cbIVCurves.addItems(self.IVtests)

		self.page.pbModuleNew.setEnabled(   (self.mode == 'view') and     (self.info is None) )
		self.page.pbModuleEdit.setEnabled(  (self.mode == 'view') and not (self.info is None) )
		self.page.pbModuleSave.setEnabled(   self.mode in ['editing','creating'] )
		self.page.pbModuleCancel.setEnabled( self.mode in ['editing','creating'] )

		self.setMainSwitchingEnabled(         self.mode == 'view') 
		self.page.pbGoPCB.setEnabled(        (self.mode == 'view') and (self.page.sbPCBID.value() >= 0)        )
		self.page.pbGoSensor.setEnabled(     (self.mode == 'view') and (self.page.sbSensorID.value() >= 0)     )
		self.page.pbGoBaseplate.setEnabled(  (self.mode == 'view') and (self.page.sbBaseplateID.value() >= 0)  )
		self.page.pbGoKaptonStep.setEnabled( (self.mode == 'view') and (self.page.sbKaptonStep.value() >= 0) )
		self.page.pbGoSensorStep.setEnabled( (self.mode == 'view') and (self.page.sbSensorStep.value() >= 0) )
		self.page.pbGoPCBStep.setEnabled(    (self.mode == 'view') and (self.page.sbPCBStep.value() >= 0)    )
		self.page.sbModuleID.setEnabled(      self.mode == 'view')

		self.page.tabBinsRaw.setEnabled(    (self.mode == 'view') and not (self.info is None) )
		self.tb.setEnabled(                 (self.mode == 'view') and not (self.info is None) )
		self.fc.setEnabled(                 (self.mode == 'view') and not (self.info is None) )
		self.page.cbIVCurves.setEnabled(    (self.mode == 'view') and not (self.info is None) )

		self.page.dsbThickness.setReadOnly(  not (self.mode in ['editing','creating']) )
		self.page.sbBaseplateID.setReadOnly( not (self.mode in ['editing','creating']) )
		self.page.sbSensorID.setReadOnly(    not (self.mode in ['editing','creating']) )
		self.page.sbPCBID.setReadOnly(       not (self.mode in ['editing','creating']) )
		self.page.sbKaptonStep.setReadOnly(  not (self.mode in ['editing','creating']) )
		self.page.sbSensorStep.setReadOnly(  not (self.mode in ['editing','creating']) )
		self.page.sbPCBStep.setReadOnly(     not (self.mode in ['editing','creating']) )

	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if self.info is None:
			self.mode = 'creating'
			self.updateElements()
		else:
			pass

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if self.info is None:
			pass
		else:
			self.mode = 'editing'
			self.updateElements()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditig(self,*args,**kwargs):
		ID = self.page.sbModuleID.value()
		details = {
			'baseplate'  : self.page.sbBaseplateID.value(),
			'sensor'     : self.page.sbSensorID.value(),
			'PCB'        : self.page.sbPCBID.value(),
			'thickness'  : self.page.dsbThickness.value(),
			# 'kaptontype' : 
			'kaptonstep' : self.page.sbKaptonStep.value(),
			'sensorstep' : self.page.sbSensorStep.value(),
			'PCBstep'    : self.page.sbPCBStep.value(),
			}
		new = self.mode == 'creating'
		self.fm.changeModuleDetails(ID,details,new)
		self.mode = 'view'
		self.update_info()


	@enforce_mode('view')
	def updateIVData(self,index,*args,**kwargs):
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

	@enforce_mode('view')
	def updateIVPlot(self,*args,**kwargs):
		print("Update plot!")
		tab = self.page.tabBinsRaw.currentIndex()
		bins_asc  = self.page.ckPlotAsc.isChecked()
		bins_desc = self.page.ckPlotDesc.isChecked()
		bins_x = self.page.cbBinsXAxis.currentIndex()
		bins_y = self.page.cbBinsYAxis.currentIndex()
		raw_x = self.page.cbRawXAxis.currentIndex()
		raw_y = self.page.cbRawYAxis.currentIndex()

		if self.ivData is None:
			self.ax.clear()
			self.fc.draw()
			print("No data - clearing")

		elif tab == 0: # bins
			self.ax.clear()

			self.ax.set_xlabel(LABELS[bins_x])
			self.ax.set_ylabel(LABELS[bins_y])

			axdata = self.ivData[1][...,bins_x]
			aydata = self.ivData[1][...,bins_y]
			dxdata = self.ivData[2][...,bins_x]
			dydata = self.ivData[2][...,bins_y]

			if bins_asc:
				self.ax.plot(axdata*(MICRO if bins_x==2 and USE_MICROAMP else 1),aydata*(MICRO if bins_y==2 and USE_MICROAMP else 1),'r.',label='ascending')
			if bins_desc:
				self.ax.plot(dxdata*(MICRO if bins_x==2 and USE_MICROAMP else 1),dydata*(MICRO if bins_y==2 and USE_MICROAMP else 1),'b.',label='descending')
			if bins_asc and bins_desc:
				self.ax.legend()

			self.fc.draw()
			print("Plotting bins!")

		elif tab == 1: # raw
			self.ax.clear()
			self.ax.set_xlabel(LABELS[raw_x])
			self.ax.set_ylabel(LABELS[raw_y])
			xdata = self.ivData[0][...,raw_x]
			ydata = self.ivData[0][...,raw_y]
			self.ax.plot(xdata*(MICRO if raw_x==2 and USE_MICROAMP else 1),ydata*(MICRO if raw_y==2 and USE_MICROAMP else 1),'r.')
			self.fc.draw()
			print("Plotting raw!")

		else:
			self.ax.clear()
			self.fc.draw()
			print("Invalid tab - clearing")


	@enforce_mode('view')
	def goBaseplate(self,*args,**kwargs):
		ID = self.page.sbBaseplateID.value()
		if ID>=0:
			self.setUIPage('baseplates',ID=ID)
		else:
			return

	@enforce_mode('view')
	def goSensor(self,*args,**kwargs):
		ID = self.page.sbSensorID.value()
		if ID>=0:
			self.setUIPage('sensors',ID=ID)
		else:
			return

	@enforce_mode('view')
	def goPCB(self,*args,**kwargs):
		ID = self.page.sbPCBID.value()
		if ID>=0:
			self.setUIPage('PCBs',ID=ID)
		else:
			return

	@enforce_mode('view')
	def goKaptonStep(self,*args,**kwargs):
		print('go kapton')
		ID = self.page.sbKaptonStep.value()
		if ID>=0:
			self.setUIPage('kapton placement steps',ID=ID)
		else:
			return

	@enforce_mode('view')
	def goSensorStep(self,*args,**kwargs):
		print('go sensor')
		...

	@enforce_mode('view')
	def goPCBStep(self,*args,**kwargs):
		print('go PCB')
		...



	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is int):
				raise TypeError("Expected type <int> for ID; got <{}>".format(type(ID)))
			if ID < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbModuleID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))