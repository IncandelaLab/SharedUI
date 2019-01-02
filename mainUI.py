from filemanager import manager
from main_ui.mainwindow import Ui_MainWindow
from PyQt4 import QtGui as gui, QtCore as core
import sys
import time

# Import page functionality classes
from pages.view_module    import func as c_func_view_module
from pages.view_baseplate import func as c_func_view_baseplate
from pages.view_sensor    import func as c_func_view_sensor
from pages.view_PCB       import func as c_func_view_PCB

# Set up page widgets
from pages_ui.view_module import Ui_Form as form_view_module
class widget_view_module(gui.QWidget,form_view_module):
	def __init__(self,parent):
		super(widget_view_module,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_baseplate import Ui_Form as form_view_baseplate
class widget_view_baseplate(gui.QWidget,form_view_baseplate):
	def __init__(self,parent):
		super(widget_view_baseplate,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_sensor import Ui_Form as form_view_sensor
class widget_view_sensor(gui.QWidget,form_view_sensor):
	def __init__(self,parent):
		super(widget_view_sensor,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_PCB import Ui_Form as form_view_PCB
class widget_view_PCB(gui.QWidget,form_view_PCB):
	def __init__(self,parent):
		super(widget_view_PCB,self).__init__(parent)
		self.setupUi(self)

# Dict of page IDs by name (as the name shows up in the page list widgets)
PAGE_IDS = {
	'modules':0,
	'baseplates':1,
	'sensors':2,
	'PCBs':3,
	#'assembly steps':4,
}

TIMERINTERVAL = 50

class mainDesigner(gui.QMainWindow,Ui_MainWindow):

	def __init__(self):
		super(mainDesigner,self).__init__(None)
		print("Setting up main UI ...")
		self.setupUi(self)
		print("Finished setting up main UI.")
		print("Initializing file manager...")
		self.fm = manager.manager()
		print("Finished initializing file manager.")
		print("Setting up pages' UI...")
		self.setupPagesUI()
		print("Finished setting up pages' UI.")
		print("Initializing pages...")
		self.initPages()
		print("Finished initializing pages.")
		print("Rigging UI...")
		self.rig()
		print("Finished rigging UI.")
		self.setUIPage('modules')

		#self.start()

	def setupPagesUI(self):
		self.page_view_module    = widget_view_module(None)    ; self.swPages.addWidget(self.page_view_module)
		self.page_view_baseplate = widget_view_baseplate(None) ; self.swPages.addWidget(self.page_view_baseplate)
		self.page_view_sensor    = widget_view_sensor(None)    ; self.swPages.addWidget(self.page_view_sensor)
		self.page_view_PCB       = widget_view_PCB(None)       ; self.swPages.addWidget(self.page_view_PCB)


	# Timer is not used yet, as timer-driven pages (routines) have not been added yet.

	# def timer_event(self):
	# 	pass

	# def start(self):
	# 	self.setWindowTitle("Module Production User Interface")
	# 	self.timer = core.QTimer(self)               # Create timer object
	# 	self.timer.setInterval(TIMERINTERVAL)        # Set timer interval to global TIMERINTERVAL, defined at the top of this file
	# 	self.timer.timeout.connect(self.timer_event) # Connect timer to the timer_event function
	# 	self.timer.start()                           # Start the timer


	def initPages(self):
		self.func_view_module    = c_func_view_module(    self.fm, self.page_view_module   , self.setUIPage, )
		self.func_view_baseplate = c_func_view_baseplate( self.fm, self.page_view_baseplate, self.setUIPage, self.setSwitchingEnabled)
		self.func_view_sensor    = c_func_view_sensor(    self.fm, self.page_view_sensor   , self.setUIPage, )
		self.func_view_PCB       = c_func_view_PCB(       self.fm, self.page_view_PCB      , self.setUIPage, )

		# This list must be in the same order that the pages are in in the stackedWidget in the main UI file.
		# This is the same order as in the dict PAGE_IDS
		self.func_list = [
			self.func_view_module,
			self.func_view_baseplate,
			self.func_view_sensor,
			self.func_view_PCB,
			]

	def pageChanged(self,*args,**kwargs):
		self.func_list[args[0]].changed_to()

	def changeUIPage(self,*args,**kwargs):
		self.setUIPage(args[0].text())

	def setUIPage(self,which_page,**kwargs):
		if which_page in PAGE_IDS.keys():

			if not self.func_list[PAGE_IDS[which_page]].is_setup:
				print("page {} not yet setup; doing setup".format(which_page))
				self.func_list[PAGE_IDS[which_page]].setup()

			self.swPages.setCurrentIndex(PAGE_IDS[which_page])
			if len(kwargs) > 0:
				self.func_list[PAGE_IDS[which_page]].load_kwargs(kwargs)
		else:
			print("Page <{}> not supported yet".format(which_page))

	def setSwitchingEnabled(self,enabled):
		self.listInformation.setEnabled(enabled)
		self.listAssembly.setEnabled(enabled)
		self.listShippingAndReceiving.setEnabled(enabled)

	def rig(self):
		self.listInformation.itemActivated.connect(self.changeUIPage)
		self.listAssembly.itemActivated.connect(self.changeUIPage)
		self.listShippingAndReceiving.itemActivated.connect(self.changeUIPage)
		self.swPages.currentChanged.connect(self.pageChanged)

		# later: add forward/back keyboard shortcuts (along with history support)


if __name__ == '__main__':
	app = gui.QApplication(sys.argv)
	m=mainDesigner()
	m.show()
	sys.exit(app.exec_())
