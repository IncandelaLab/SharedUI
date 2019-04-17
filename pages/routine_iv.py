from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg    as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

PAGE_NAME = "routine_iv"
OBJ_MODULE = "module"
DEBUG = False

I_UNIT = "uA" # 
I_MULT = 1e6  # convert amps to microamps

V_UNIT = "V"
V_MULT = 1.0

T_UNIT = "s"
T_MULT = 1.0

LABEL_I = "current ({})".format(I_UNIT)
LABEL_V = "bias voltage ({})".format(V_UNIT)
LABEL_T = "time ({})".format(T_UNIT)

MSG_MODULE_EXISTS_TRUE  = "Module exists"
MSG_MODULE_EXISTS_FALSE = "Module does not exist"
MSG_MODULE_READY_TRUE   = "Module ready for IV curve"
MSG_MODULE_READY_FALSE  = "Module not ready for IV curve"

PAGE_ID_MODULE = "modules"


class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.moduleInfo = None
		self.moduleIV   = None


		self.routine_stage    = None
		self.routine_activity = None
		# many other internal variables


		self.mode = 'setup'

		# routine_setup variables
		self.routine_setup_ready = None
		self.routine_setup_issues = {
			'keithley_no_port'   :None,
			'module_exists_false':None,
			'module_ready_false' :None,
		}
		self.routine_setup_issues_console = {
			'keithley_no_port'   :'No COM port selected for keithley',
			'module_exists_false':'Selected module with ID {} does not exist',
			'module_ready_false' :'Selected module with ID {} not ready for IV curve',
		}


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
		self.mode = 'routine_setup'
		print("{} setup completed".format(PAGE_NAME))
		self.update_info()

	def setupFigures(self):
		self.all_fig = Figure()
		self.all_ax  = self.all_fig.add_subplot(111)
		self.all_fc  = FigureCanvas(self.all_fig)
		self.all_tb  = NavigationToolbar(self.all_fc,self.page)
		self.page.vlAll.addWidget(self.all_tb)
		self.page.vlAll.addWidget(self.all_fc)
		self.all_fig.subplots_adjust(left=0.105,right=0.98,top=0.98,bottom=0.145)

		self.act_fig = Figure()
		self.act_ax  = self.act_fig.add_subplot(111)
		self.act_fc  = FigureCanvas(self.act_fig)
		self.act_tb  = NavigationToolbar(self.act_fc,self.page)
		self.page.vlActive.addWidget(self.act_tb)
		self.page.vlActive.addWidget(self.act_fc)
		self.act_fig.subplots_adjust(left=0.105,right=0.98,top=0.98,bottom=0.145)

	@enforce_mode('setup')
	def rig(self):
		self.page.sbModuleID.valueChanged.connect(self.updateModuleInfo)
		self.page.pbGoModule.clicked.connect(self.goModule)


	@enforce_mode('routine_setup')
	def updateModuleInfo(self,*args,**kwargs):
		moduleID = self.page.sbModuleID.value()
		self.moduleInfo, self.moduleIV = self.fm.loadObjectDetails(OBJ_MODULE,moduleID)
		self.updateElements(change='moduleID')


	@enforce_mode('routine_setup')
	def update_info(self,ID=None,*args,**kwargs):
		self.updateModuleInfo()
		self.updateElements('mode')
		



	@enforce_mode(['routine_setup','routine_perform'])
	def updateElements(self,change=None):
		if change is None:
			return
		
		if change == 'moduleID' or change == 'all':
			# :TODO:
			# based on module existence & status
			# update dict on setup issues
			# then call function that refreshes pteConsole
			if self.moduleInfo is None:
				self.page.leModuleExists.setText(MSG_MODULE_EXISTS_FALSE)
				self.page.leModuleReady.clear()
			else:
				self.page.leModuleExists.setText(MSG_MODULE_EXISTS_TRUE)
				self.page.leModuleReady.setText(MSG_MODULE_READY_FALSE if self.moduleInfo['PCB'] == -1 else MSG_MODULE_READY_TRUE)
				# :TODO:
				# When wirebonding and curing status is added: change this to check if the module is bonded, encapsulated, and cured

		if change == 'mode' or change == 'all':
			self.page.sbModuleID.setEnabled( self.mode == 'routine_setup' ) # :TODO: and no issues with routine_setup
			self.page.pbGoModule.setEnabled( self.mode == 'routine_setup' and self.page.sbModuleID.value() >= 0 )

			self.page.pbRefreshComPorts.setEnabled( self.mode == 'routine_setup' )
			self.page.cbKeithleyPort.setEnabled(    self.mode == 'routine_setup' )
			self.page.cbKeithleyBaud.setEnabled(    self.mode == 'routine_setup' )
			self.page.pbKeithleyQuery.setEnabled(   self.mode == 'routine_setup' )

			self.page.pbRoutineStart.setEnabled(   self.mode == 'routine_setup'   )
			self.page.pbRoutinePause.setEnabled(   self.mode == 'routine_perform' )
			self.page.pbRoutineResume.setEnabled(  self.mode == 'routine_perform' )
			self.page.pbRoutineDescend.setEnabled( self.mode == 'routine_perform' )
			self.page.pbRoutineEnd.setEnabled(     self.mode == 'routine_perform' )

			self.page.pteNotes.setEnabled( self.mode == 'routine_perform' )


	@enforce_mode('routine_setup')
	def goModule(self,*args,**kwargs):
		moduleID = self.page.sbModuleID.value()
		if moduleID >= 0:
			self.setUIPage(PAGE_ID_MODULE,ID=moduleID)

	@enforce_mode('routine_setup')
	def load_kwargs(self,kwargs):
		...

	@enforce_mode('routine_setup')
	def changed_to(self):
		self.updateModuleInfo() # module info may have changed, so we reload it and propagate consequences.
