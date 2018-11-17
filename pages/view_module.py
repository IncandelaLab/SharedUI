from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg    as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

USE_MICROAMP = True
MICRO = 1e6

LBL_TIME = 'time (seconds)'
LBL_VOLTAGE = 'voltage (volts)'
LBL_CURRENT = 'current ({})'.format('microamps' if USE_MICROAMP else 'amps')
LBL_VSOURCE = 'sourced voltage (volts)'
LABELS = [LBL_TIME,LBL_VOLTAGE,LBL_CURRENT,LBL_VSOURCE]

nstr = lambda v:'' if v is None else str(v)

class func(object):

	def __init__(self,fm,page,setUIPage):
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage

		self.ivModuleID = None
		self.ivDataName = None
		self.ivData     = None

		self.setupFigures()
		self.rig()
		self.update_info()

	def setupFigures(self):
		self.fig = Figure()
		self.ax  = self.fig.add_subplot(111)
		self.fc  = FigureCanvas(self.fig)
		self.tb  = NavigationToolbar(self.fc,self.page)
		self.page.vlPlotIV.addWidget(self.tb)
		self.page.vlPlotIV.addWidget(self.fc)

	def rig(self):
		self.page.sbModuleID.valueChanged.connect(self.update_info)
		self.page.pbGoBaseplate.clicked.connect(self.goBaseplate)
		self.page.pbGoSensor.clicked.connect(self.goSensor)
		self.page.pbGoPCB.clicked.connect(self.goPCB)

		self.page.cbIVCurves.currentIndexChanged.connect(self.updateIVData)
		self.page.ckPlotAsc.stateChanged.connect(self.updateIVPlot)
		self.page.ckPlotDesc.stateChanged.connect(self.updateIVPlot)
		self.page.cbBinsXAxis.currentIndexChanged.connect(self.updateIVPlot)
		self.page.cbBinsYAxis.currentIndexChanged.connect(self.updateIVPlot)
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
			self.page.leBaseplateID.setText( nstr(info['baseplate']) )
			self.page.leSensorID.setText(    nstr(info['sensor']   ) )
			self.page.lePCBID.setText(       nstr(info['PCB']      ) )
			self.page.leThickness.setText(   nstr(info['thickness']) )

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

	def changed_to(self):
		print("changed to view_module")