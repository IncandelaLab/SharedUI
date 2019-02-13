from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg    as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

PAGE_NAME = "routine_iv"
OBJECTTYPE = "module"
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

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled


		self.routine_stage    = None
		self.routine_activity = None
		# many other internal variables


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

		self.act_fig = Figure()
		self.act_ax  = self.act_fig.add_subplot(111)
		self.act_fc  = FigureCanvas(self.act_fig)
		self.act_tb  = NavigationToolbar(self.act_fc,self.page)
		self.page.vlActive.addWidget(self.act_tb)
		self.page.vlActive.addWidget(self.act_fc)

	@enforce_mode('setup')
	def rig(self):
		...

	@enforce_mode('routine_setup')
	def update_info(self,ID=None,*args,**kwargs):
		...
		#self.updateElements(use_info=True)

	#@enforce_mode()



	@enforce_mode('routine_setup')
	def load_kwargs(self,kwargs):
		...

	@enforce_mode('routine_setup')
	def changed_to(self):
		...
