from filemanager import fm
from main_ui.mainwindow import Ui_MainWindow
from PyQt5 import QtGui as gui, QtCore as core, QtWidgets as wdgt
import sys
import time
import os

# FOR DATABASE UPLOADING:
from cmsdbldr_client import LoaderClient
import atexit  # Close ssh tunnel upon exiting the GUI


# Import page functionality classes
from pages.view_baseplate   import func as cls_func_view_baseplate
from pages.view_sensor      import func as cls_func_view_sensor
from pages.view_PCB         import func as cls_func_view_PCB
from pages.view_protomodule import func as cls_func_view_protomodule
from pages.view_module      import func as cls_func_view_module
from pages.search           import func as cls_func_search

from pages.view_kapton_step import func as cls_func_view_kapton_step
from pages.view_sensor_step import func as cls_func_view_sensor_step
from pages.view_pcb_step    import func as cls_func_view_pcb_step
from pages.view_wirebonding import func as cls_func_view_wirebonding

from pages.view_tooling     import func as cls_func_view_tooling
from pages.view_supplies    import func as cls_func_view_supplies

# from pages.routine_iv       import func as cls_func_routine_iv
from pages.view_shipment    import func as cls_func_shipment




# Set up page widgets
from pages_ui.view_baseplate import Ui_Form as form_view_baseplate
class widget_view_baseplate(wdgt.QWidget,form_view_baseplate):  #was gui.QWidget, etc
	def __init__(self,parent):
		super(widget_view_baseplate,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_sensor import Ui_Form as form_view_sensor
class widget_view_sensor(wdgt.QWidget,form_view_sensor):
	def __init__(self,parent):
		super(widget_view_sensor,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_PCB import Ui_Form as form_view_PCB
class widget_view_PCB(wdgt.QWidget,form_view_PCB):
	def __init__(self,parent):
		super(widget_view_PCB,self).__init__(parent)
		self.setupUi(self)


from pages_ui.view_protomodule import Ui_Form as form_view_protomodule
class widget_view_protomodule(wdgt.QWidget,form_view_protomodule):
	def __init__(self,parent):
		super(widget_view_protomodule,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_module import Ui_Form as form_view_module
class widget_view_module(wdgt.QWidget,form_view_module):
	def __init__(self,parent):
		super(widget_view_module,self).__init__(parent)
		self.setupUi(self)

# NEW:

from pages_ui.search import Ui_Form as form_search
class widget_search(wdgt.QWidget,form_search):
	def __init__(self,parent):
		super(widget_search,self).__init__(parent)
		self.setupUi(self)



from pages_ui.view_kapton_step import Ui_Form as form_view_kapton_step
class widget_view_kapton_step(wdgt.QWidget,form_view_kapton_step):
	def __init__(self,parent):
		super(widget_view_kapton_step,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_sensor_step import Ui_Form as form_view_sensor_step
class widget_view_sensor_step(wdgt.QWidget,form_view_sensor_step):
	def __init__(self,parent):
		super(widget_view_sensor_step,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_pcb_step import Ui_Form as form_view_pcb_step
class widget_view_pcb_step(wdgt.QWidget, form_view_pcb_step):
	def __init__(self,parent):
		super(widget_view_pcb_step,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_wirebonding import Ui_Form as form_view_wirebonding
class widget_view_wirebonding(wdgt.QWidget, form_view_wirebonding):
	def __init__(self,parent):
		super(widget_view_wirebonding,self).__init__(parent)
		self.setupUi(self)


from pages_ui.view_tooling import Ui_Form as form_view_tooling
class widget_view_tooling(wdgt.QWidget, form_view_tooling):
	def __init__(self,parent):
		super(widget_view_tooling,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_supplies import Ui_Form as form_view_supplies
class widget_view_supplies(wdgt.QWidget, form_view_supplies):
	def __init__(self,parent):
		super(widget_view_supplies,self).__init__(parent)
		self.setupUi(self)


# from pages_ui.routine_iv import Ui_Form as form_routine_iv
# class widget_routine_iv(wdgt.QWidget, form_routine_iv):
# 	def __init__(self,parent):
# 		super(widget_routine_iv,self).__init__(parent)
# 		self.setupUi(self)

from pages_ui.view_shipment import Ui_Form as form_shipment
class widget_shipment(wdgt.QWidget, form_shipment):
	def __init__(self,parent):
		super(widget_shipment,self).__init__(parent)
		self.setupUi(self)




# Dict of page IDs by name (as the name shows up in the page list widgets)
PAGE_IDS = {
	'search for parts'       : 0,
	'baseplates'             : 1,
	'sensors'                : 2,
	'PCBs'                   : 3,
	'protomodules'           : 4,
	'modules'                : 5,
	'tooling'                : 6,
	'supplies'               : 7,

	'kapton placement steps' : 8,
	'sensor placement steps' : 9,
	'PCB placement steps'    : 10,
	'wirebonding and encapsulating' : 11,

	'shipments'               :12, #WARNING:  Order has been switched
	# 'IV curve'               :11,
}


def id_generator():
	"""creates a generator for unique ID values"""
	next_id = 0
	while True:
		yield next_id
		next_id += 1


class mainDesigner(wdgt.QMainWindow,Ui_MainWindow):

	def __init__(self):
		super(mainDesigner,self).__init__(None)
		print("Setting up main UI ...")
		self.setupUi(self)
		print("Finished setting up main UI.")
		print("Initializing file manager...")
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
		self.setUIPage('baseplates')
		#self.setUIPage('search for parts')

		self.setWindowTitle("Module Assembly User Interface")
	
		self.timer_setup()

		# NEW:  Set up ssh tunnel for DB access!
		# First, request username:
		ldlg = UserDialog(self)
		loginResult = ldlg.exec_()
		while loginResult != 1:  # was if
			print("Username request cancelled!  Trying again...")
			loginResult = ldlg.exec_()
		print("Got username:  ",  ldlg.getUsername())
		username = ldlg.getUsername()
		os.system('ssh -f -N -M -S temp_socket -L 10131:itrac1609-v.cern.ch:10121 -L 10132:itrac1601-v.cern.ch:10121 {}@lxplus.cern.ch'.format(username))
		# Close upon exiting
		def close_ssh():
			os.system('ssh -S temp_socket -O exit lxplus.cern.ch')
		atexit.register(close_ssh)


	def setupPagesUI(self):
		self.page_search           = widget_search(None)           ; self.swPages.addWidget(self.page_search)

		self.page_view_baseplate   = widget_view_baseplate(None)   ; self.swPages.addWidget(self.page_view_baseplate)
		self.page_view_sensor      = widget_view_sensor(None)      ; self.swPages.addWidget(self.page_view_sensor)
		self.page_view_PCB         = widget_view_PCB(None)         ; self.swPages.addWidget(self.page_view_PCB)
		self.page_view_protomodule = widget_view_protomodule(None) ; self.swPages.addWidget(self.page_view_protomodule)
		self.page_view_module      = widget_view_module(None)      ; self.swPages.addWidget(self.page_view_module)
		self.page_view_tooling     = widget_view_tooling(None)     ; self.swPages.addWidget(self.page_view_tooling)
		self.page_view_supplies    = widget_view_supplies(None)    ; self.swPages.addWidget(self.page_view_supplies)	# NEW

		self.page_view_kapton_step = widget_view_kapton_step(None) ; self.swPages.addWidget(self.page_view_kapton_step)
		self.page_view_sensor_step = widget_view_sensor_step(None) ; self.swPages.addWidget(self.page_view_sensor_step)
		self.page_view_pcb_step    = widget_view_pcb_step(None)    ; self.swPages.addWidget(self.page_view_pcb_step)
		self.page_view_wirebonding = widget_view_wirebonding(None) ; self.swPages.addWidget(self.page_view_wirebonding)


		# self.page_routine_iv       = widget_routine_iv(None)       ; self.swPages.addWidget(self.page_routine_iv)
		self.page_shipment         = widget_shipment(None)         ; self.swPages.addWidget(self.page_shipment)


	def initPages(self):
		self.func_search           = cls_func_search(                fm, self.page_search          , self.setUIPage, self.setSwitchingEnabled)
		self.func_view_baseplate   = cls_func_view_baseplate(        fm, self.page_view_baseplate  , self.setUIPage, self.setSwitchingEnabled)
		self.func_view_sensor      = cls_func_view_sensor(           fm, self.page_view_sensor     , self.setUIPage, self.setSwitchingEnabled)
		self.func_view_PCB         = cls_func_view_PCB(              fm, self.page_view_PCB        , self.setUIPage, self.setSwitchingEnabled)
		self.func_view_protomodule = cls_func_view_protomodule(      fm, self.page_view_protomodule, self.setUIPage, self.setSwitchingEnabled)
		self.func_view_module      = cls_func_view_module(           fm, self.page_view_module     , self.setUIPage, self.setSwitchingEnabled)

		self.func_view_kapton_step = cls_func_view_kapton_step(      fm, self.page_view_kapton_step, self.setUIPage, self.setSwitchingEnabled)
		self.func_view_sensor_step = cls_func_view_sensor_step(      fm, self.page_view_sensor_step, self.setUIPage, self.setSwitchingEnabled)
		self.func_view_pcb_step    = cls_func_view_pcb_step(         fm, self.page_view_pcb_step   , self.setUIPage, self.setSwitchingEnabled)
		self.func_view_wirebonding = cls_func_view_wirebonding(      fm, self.page_view_wirebonding, self.setUIPage, self.setSwitchingEnabled)

		self.func_view_tooling     = cls_func_view_tooling(          fm, self.page_view_tooling    , self.setUIPage, self.setSwitchingEnabled)
		self.func_view_supplies    = cls_func_view_supplies(         fm, self.page_view_supplies   , self.setUIPage, self.setSwitchingEnabled)

		# self.func_routine_iv       = cls_func_routine_iv(            fm, self.page_routine_iv      , self.setUIPage, self.setSwitchingEnabled)
		self.func_shipment         = cls_func_shipment(              fm, self.page_shipment        , self.setUIPage, self.setSwitchingEnabled)

		# This list must be in the same order that the pages are in in the stackedWidget in the main UI file.
		# This is the same order as in the dict PAGE_IDS
		self.func_list = [
			self.func_search,
			self.func_view_baseplate,
			self.func_view_sensor,
			self.func_view_PCB,
			self.func_view_protomodule,
			self.func_view_module,
			self.func_view_tooling,
			self.func_view_supplies,

			self.func_view_kapton_step,
			self.func_view_sensor_step,
			self.func_view_pcb_step,
			self.func_view_wirebonding,

			self.func_shipment,  #WARNING:  Order has been switched.
			# self.func_routine_iv,
			]


	def rig(self):
		self.listInformation.itemActivated.connect(self.changeUIPage)
		self.listAssembly.itemActivated.connect(self.changeUIPage)
		self.listShippingAndReceiving.itemActivated.connect(self.changeUIPage)
		self.swPages.currentChanged.connect(self.pageChanged)

		# NEW, experimental
		self.pbUpload.clicked.connect(self.goUpload)


	def timer_setup(self):
		self.timer_id_gen = id_generator() # unique ID generator for timers
		self.timers = {} # dict of timers {ID:timer}

	def timer_add(self,interval=None,cxn=None,start=False):
		timer = core.QTimer(self)
		ID    = next(self.timer_id_gen)
		self.timers.update([ [ID, timer] ])

		if not (interval is None):
			self.timer_set_interval(ID,interval)

		if not (cxn is None):
			self.timer_connect(ID,cxn)

		if start:
			if interval is None:
				print("Warning: cannot start timer without interval")
			else:
				self.timer_start(ID)

		return ID

	def timer_remove(self,ID):
		if ID in self.timers.keys():
			timer = self.timers.pop(ID)
			timer.stop()
			timer.timeout.disconnect()
			del timer
		else:
			print("Warning: tried to remove nonexistent timer with ID {}".format(ID))

	def timer_start(self,ID):
		if ID in self.timers.keys():
			self.timers[ID].start()
		else:
			print("Warning: tried to start nonexistent timer with ID {}".format(ID))

	def timer_stop(self,ID):
		if ID in self.timers.keys():
			self.timers[ID].stop()
		else:
			print("Warning: tried to stop nonexistent timer with ID {}".format(ID))

	def timer_connect(self,ID,cxn):
		if ID in self.timers.keys():
			self.timers[ID].timeout.connect(cxn)
		else:
			print("Warning: tried to connect {} to nonexistent timer with ID {}".format(cxn,ID))

	def timer_disconnect(self,ID):
		if ID in self.timers.keys():
			self.timers[ID].timeout.disconnect()
		else:
			print("Warning: tried to disconnect nonexistent timer with ID {}".format(ID))

	def timer_set_interval(self,ID,interval_ms):
		if ID in self.timers.keys():
			self.timers[ID].setInterval(interval_ms)
		else:
			print("Warning: tried to set interval of nonexistent timer with ID {} to {}".format(ID, interval_ms))


	

	def pageChanged(self,*args,**kwargs):
		self.func_list[args[0]].changed_to()

	def changeUIPage(self,*args,**kwargs):
		self.setUIPage(args[0].text())

	def setUIPage(self, which_page, switch_to_page=True, **kwargs):
		if which_page in PAGE_IDS.keys():

			if self.func_list[PAGE_IDS[which_page]].mode == 'setup':
				print("page {} not yet setup; doing setup".format(which_page))
				self.func_list[PAGE_IDS[which_page]].setup()

			if switch_to_page:
				self.swPages.setCurrentIndex(PAGE_IDS[which_page])
				# self.func_list[PAGE_IDS[which_page]].changed_to() # notify page function that page has been changed to

			if len(kwargs) > 0:
				self.func_list[PAGE_IDS[which_page]].load_kwargs(kwargs)
		else:
			print("Page <{}> not supported yet. Tried to load with kwargs {}".format(which_page,kwargs))

	def setSwitchingEnabled(self,enabled):
		self.listInformation.setEnabled(enabled)
		self.listAssembly.setEnabled(enabled)
		self.listShippingAndReceiving.setEnabled(enabled)


	# New, sort of experimental
	def goUpload(self,*args,**kwargs):
		# Create a popup box requesting username/password, plus a "cancel" button.
		# If username+password given, submit.
		# BUT:  How can username/password be fed to loader?

		# NEW:
		# Find directory w/ a certain date, and upload ALL files in it.

		# OUTDATED:
		# FIRST:  Check to see whether there's any modified XML files
		xmlStepList = [self.func_view_baseplate, self.func_view_sensor, self.func_view_PCB, self.func_view_sensor_step]
		xmlFilesModified = 0
		for step in xmlStepList:
			xmlModList = step.xmlModified()
			if len(xmlModList) != 0:  xmlFilesModified += 1

		if xmlFilesModified == 0:
			print("ALL CHANGES HAVE ALREADY BEEN SAVED")
			return
				

		print("DISPLAYING POP-UP")
		ldlg = LoginDialog(self)
		loginResult = ldlg.exec_()
		if loginResult.isCancelled():
			print("Upload cancelled!")
		elif loginResult == wdgt.QDialog.Accepted:
			print("Upload successful!")
			# MAYBE:  New popup box here!
			# WARNING:  Might be difficult to pass obj info to save to LoginDialog...
			
			for step in xmlStepList:
				step.xmlModifiedReset()

		else:
			print("Upload unsuccessful!")


# Class for requesting GUI username at start (for ssh tunnel)
class UserDialog(wdgt.QDialog):
	def __init__(self, *args, **kwargs):
		super(UserDialog, self).__init__(*args, **kwargs)

		self.setWindowTitle("SSH tunnel:  username required")
		
		self.textName = wdgt.QLineEdit(self)
		self.buttonLogin = wdgt.QPushButton('Connect', self)
		self.buttonCancel = wdgt.QPushButton('Cancel', self)
		self.buttonLogin.clicked.connect(self.handleLogin)
		self.buttonCancel.clicked.connect(self.handleCancel)
		layout = wdgt.QVBoxLayout(self)
		layout.addWidget(self.textName)
		layout.addWidget(self.buttonLogin)
		layout.addWidget(self.buttonCancel)

		self.cancelled = False

	def handleLogin(self):
		self.username = self.textName.text()
		print("Got username {}".format(self.username))
		
		if self.username != "":
			self.accept()
		else:
			self.reject()

	def handleCancel(self):
		print("Login canceled")
		self.username = None
		self.cancelled = True
		self.reject()

	def isCancelled(self):
		return self.cancelled

	def getUsername(self):
		return self.username


# Class for DB upload login
class LoginDialog(wdgt.QDialog):

	def __init__(self, *args, **kwargs):
		super(LoginDialog, self).__init__(*args, **kwargs)

		self.setWindowTitle("Provide DB login credentials")
		
		self.textName = wdgt.QLineEdit(self)
		self.textPass = wdgt.QLineEdit(self)
		self.buttonLogin = wdgt.QPushButton('Login', self)
		self.buttonCancel = wdgt.QPushButton('Cancel', self)
		self.buttonLogin.clicked.connect(self.handleLogin)
		self.buttonCancel.clicked.connect(self.handleCancel)
		layout = wdgt.QVBoxLayout(self)
		layout.addWidget(self.textName)
		layout.addWidget(self.textPass)
		layout.addWidget(self.buttonLogin)
		layout.addWidget(self.buttonCancel)

		self.cancelled = False

	def handleLogin(self):
		username = self.textName.text()
		password = self.textPass.text()
		print("Got username {}, password {}".format(username, password))
		print("TEMP:  May need to authenticate in terminal")

		# PERFORM ATTEMPTED UPLOAD
		# If all good, then:
		#for f in :
		#	lc = LoaderClient(["--url", "https://cmsdca.cern.ch/hgc_loader/hgc/int2r", "--login", "--verbose", f])
		#	load_status = lc.run()

		#if load_status == 0:
		#	self.accept()

		#self.accept()
		# Otherwise...
		# self.reject()

	def handleCancel(self):
		print("Login canceled")
		self.cancelled = True
		self.reject()

	def isCancelled(self):
		return self.cancelled



if __name__ == '__main__':
	app = wdgt.QApplication(sys.argv)
	m=mainDesigner()
	m.resize(1366,768)
	m.show()
	sys.exit(app.exec_())
