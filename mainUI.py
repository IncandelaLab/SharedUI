from filemanager import fm
from main_ui.mainwindow import Ui_MainWindow
from PyQt5 import QtGui as gui, QtCore as core, QtWidgets as wdgt
import sys
import time
import os

# FOR DATABASE COMMUNICATION:
from cmsdbldr_client import LoaderClient
import atexit  # Close ssh tunnel upon exiting the GUI
import glob

# For uploading XML files in background
import threading
import subprocess


# Import page functionality classes
from pages.view_users       import func as cls_func_view_users
from pages.view_baseplate   import func as cls_func_view_baseplate
from pages.view_sensor      import func as cls_func_view_sensor
from pages.view_PCB         import func as cls_func_view_PCB
from pages.view_protomodule import func as cls_func_view_protomodule
from pages.view_module      import func as cls_func_view_module
from pages.search           import func as cls_func_search

#from pages.view_kapton_step import func as cls_func_view_kapton_step
from pages.view_sensor_step import func as cls_func_view_sensor_step
from pages.view_sensor_post import func as cls_func_view_sensor_post
from pages.view_pcb_step    import func as cls_func_view_pcb_step
from pages.view_pcb_post    import func as cls_func_view_pcb_post
from pages.view_wirebonding import func as cls_func_view_wirebonding
from pages.view_plots       import func as cls_func_view_plots

from pages.view_tooling     import func as cls_func_view_tooling
from pages.view_supplies    import func as cls_func_view_supplies




# Set up page widgets
from pages_ui.view_users import Ui_Form as form_view_users
class widget_view_users(wdgt.QWidget,form_view_users):
	def __init__(self,parent):
		super(widget_view_users,self).__init__(parent)
		self.setupUi(self)

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


from pages_ui.view_sensor_step import Ui_Form as form_view_sensor_step
class widget_view_sensor_step(wdgt.QWidget,form_view_sensor_step):
	def __init__(self,parent):
		super(widget_view_sensor_step,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_sensor_post import Ui_Form as form_view_sensor_post
class widget_view_sensor_post(wdgt.QWidget,form_view_sensor_post):
	def __init__(self,parent):
		super(widget_view_sensor_post,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_pcb_step import Ui_Form as form_view_pcb_step
class widget_view_pcb_step(wdgt.QWidget, form_view_pcb_step):
	def __init__(self,parent):
		super(widget_view_pcb_step,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_pcb_post import Ui_Form as form_view_pcb_post
class widget_view_pcb_post(wdgt.QWidget, form_view_pcb_post):
	def __init__(self,parent):
		super(widget_view_pcb_post,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_wirebonding import Ui_Form as form_view_wirebonding
class widget_view_wirebonding(wdgt.QWidget, form_view_wirebonding):
	def __init__(self,parent):
		super(widget_view_wirebonding,self).__init__(parent)
		self.setupUi(self)

from pages_ui.view_plots import Ui_Form as form_view_plots
class widget_view_plots(wdgt.QWidget, form_view_plots):
	def __init__(self,parent):
		super(widget_view_plots,self).__init__(parent)
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




# Dict of page IDs by name (as the name shows up in the page list widgets)
PAGE_IDS = {
	'Users'                  : 0,
	'Search for parts'       : 1,
	'Baseplates'             : 2,
	'Sensors'                : 3,
	'PCBs'                   : 4,
	#'Protomodules'           : 5,
	#'Modules'                : 6,
	'Tooling'                : 7,
	'Supplies'               : 8,

	#'1. Sensor - pre-assembly' : 9,
	#'2. Sensor - post-assembly': 10,
	#'3. PCB - pre-assembly'    : 11,
	#'4. PCB - post-assembly'    : 12,
	#'5. Wirebonding & encapsulating' : 13,
	#'6. Module testing' : 14,

}

# List of all pages where DB expects info to upload
UPLOAD_ENABLED_PAGES = [
	'Baseplates',  # In theory, should never have to upload these
	'Sensors',
	'PCBs',
	#'Protomodules',
	#'Modules',
	#'2. Sensor - post-assembly',
	#'4. PCB - post-assembly'
]


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

		self.setUIPage('Baseplates')
		print("Set UI page")

		self.setWindowTitle("Module Assembly User Interface")
	
		# NEW:  Set up ssh tunnel for DB access!
		# First, request username:
		ldlg = UserDialog(self)
		loginResult = ldlg.exec_()
		if loginResult != 1:
			print("Login cancelled")
			exit()
		#loginResult = 0
		#attempts = 0
		#while attempts < 3 and loginResult != 1:
		#	print("Login request: attempt {}".format(attempts))
		#	loginResult = ldlg.exec_()
		#	if loginResult == 1:  break
		#	attempts += 1
		self.username = ldlg.getUsername()
		print("Got username:  ",  ldlg.getUsername())
		os.system('ssh -f -N -M -S temp_socket -L 10131:itrac1609-v.cern.ch:10121 -L 10132:itrac1601-v.cern.ch:10121 {}@lxplus.cern.ch'.format(self.username))
		# Close upon exiting
		def close_ssh():
			print("Closing ssh connection")
			os.system('ssh -S temp_socket -O exit lxplus.cern.ch')
			print("Closed ssh connection")
		atexit.register(close_ssh)

		# After tunnel established, :
		fm.connectOracle()

		# NEW:  If not already present, create new ssh key for user
		# Enables scp without password prompt every time
		"""
		ssh_dir = os.path.expanduser('~/.ssh/hgcal_gui')
		if not os.path.isfile(ssh_dir+'/id_rsa_'.format(self.username)):
			# generate new ssh key at ~/.ssh/hgcal_gui/id_rsa_USERNAME
			print("NOTE:  Existing ssh key for DB loader not found.  Generating new ssh key (mandatory)...")
			if not os.path.exists(ssh_dir):
				os.mkdir(ssh_dir)
			keygen_result = subprocess.run(['ssh-keygen', '-f', ssh_dir+'/id_rsa_'+self.username, '-t', 'rsa', '-N', '\'\''])
			if keygen_result.returncode != 0:
				print("ERROR:  Problem occurred during ssh-keygen: status {}".format(keygen_result.returncode))
				print(keygen_result.stderr)
				exit()
			copy_result = subprocess.run(['ssh-copy-id', '-i', ssh_dir+'/id_rsa_'+self.username, self.username+'@dbloader-hgcal.cern.ch'])
			if copy_result.returncode != 0:
				print("ERROR:  Problem occurred during ssh-copy-id: status {}".format(copy_result.returncode))
				print(copy_result.stderr)
				exit()
		else:
			print("Existing ssh key found at {}/id_rsa_{}".format(ssh_dir, self.username))
		"""


	def setupPagesUI(self):
		self.page_view_users       = widget_view_users(None)       ; self.swPages.addWidget(self.page_view_users)

		self.page_search           = widget_search(None)           ; self.swPages.addWidget(self.page_search)
		self.page_view_baseplate   = widget_view_baseplate(None)   ; self.swPages.addWidget(self.page_view_baseplate)
		self.page_view_sensor      = widget_view_sensor(None)      ; self.swPages.addWidget(self.page_view_sensor)
		self.page_view_PCB         = widget_view_PCB(None)         ; self.swPages.addWidget(self.page_view_PCB)
		#self.page_view_protomodule = widget_view_protomodule(None) ; self.swPages.addWidget(self.page_view_protomodule)
		#self.page_view_module      = widget_view_module(None)      ; self.swPages.addWidget(self.page_view_module)
		self.page_view_tooling     = widget_view_tooling(None)     ; self.swPages.addWidget(self.page_view_tooling)
		self.page_view_supplies    = widget_view_supplies(None)    ; self.swPages.addWidget(self.page_view_supplies)	# NEW

		#self.page_view_sensor_step = widget_view_sensor_step(None) ; self.swPages.addWidget(self.page_view_sensor_step)
		#self.page_view_sensor_post = widget_view_sensor_post(None) ; self.swPages.addWidget(self.page_view_sensor_post)
		#self.page_view_pcb_step    = widget_view_pcb_step(None)    ; self.swPages.addWidget(self.page_view_pcb_step)
		#self.page_view_pcb_post    = widget_view_pcb_post(None)    ; self.swPages.addWidget(self.page_view_pcb_post)
		#self.page_view_wirebonding = widget_view_wirebonding(None) ; self.swPages.addWidget(self.page_view_wirebonding)
		#self.page_view_plots       = widget_view_plots(None)       ; self.swPages.addWidget(self.page_view_plots)



	def initPages(self):
		self.func_view_users       = cls_func_view_users(            fm, self.page_view_users      , self.setUIPage, self.setSwitchingEnabled)

		self.func_search           = cls_func_search(                fm, self.page_search          , self.setUIPage, self.setSwitchingEnabled)
		self.func_view_baseplate   = cls_func_view_baseplate(        fm, self.page_view_baseplate  , self.setUIPage, self.setSwitchingEnabled)
		self.func_view_sensor      = cls_func_view_sensor(           fm, self.page_view_sensor     , self.setUIPage, self.setSwitchingEnabled)
		self.func_view_PCB         = cls_func_view_PCB(              fm, self.page_view_PCB        , self.setUIPage, self.setSwitchingEnabled)
		#self.func_view_protomodule = cls_func_view_protomodule(      fm, self.page_view_protomodule, self.setUIPage, self.setSwitchingEnabled)
		#self.func_view_module      = cls_func_view_module(           fm, self.page_view_module     , self.setUIPage, self.setSwitchingEnabled)

		#self.func_view_sensor_step = cls_func_view_sensor_step(      fm, self.page_view_sensor_step, self.setUIPage, self.setSwitchingEnabled)
		#self.func_view_sensor_post = cls_func_view_sensor_post(      fm, self.page_view_sensor_post, self.setUIPage, self.setSwitchingEnabled)
		#self.func_view_pcb_step    = cls_func_view_pcb_step(         fm, self.page_view_pcb_step   , self.setUIPage, self.setSwitchingEnabled)
		#self.func_view_pcb_post    = cls_func_view_pcb_post(         fm, self.page_view_pcb_post   , self.setUIPage, self.setSwitchingEnabled)
		#self.func_view_wirebonding = cls_func_view_wirebonding(      fm, self.page_view_wirebonding, self.setUIPage, self.setSwitchingEnabled)
		#self.func_view_plots       = cls_func_view_plots(            fm, self.page_view_plots,       self.setUIPage, self.setSwitchingEnabled)

		self.func_view_tooling     = cls_func_view_tooling(          fm, self.page_view_tooling    , self.setUIPage, self.setSwitchingEnabled)
		self.func_view_supplies    = cls_func_view_supplies(         fm, self.page_view_supplies   , self.setUIPage, self.setSwitchingEnabled)


		# This list must be in the same order that the pages are in in the stackedWidget in the main UI file.
		# This is the same order as in the dict PAGE_IDS
		self.func_list = [
			self.func_view_users,

			self.func_search,
			self.func_view_baseplate,
			self.func_view_sensor,
			self.func_view_PCB,
			None, #self.func_view_protomodule,
			None, #self.func_view_module,
			self.func_view_tooling,
			self.func_view_supplies,

			None, #self.func_view_sensor_step,
			None, #self.func_view_sensor_post,
			None, #self.func_view_pcb_step,
			None, #self.func_view_pcb_post,
			None, #self.func_view_wirebonding,
			None, #self.func_view_plots,
			]


	def rig(self):
		self.listUsers.itemActivated.connect(self.changeUIPage)
		self.listInformation.itemActivated.connect(self.changeUIPage)
		self.listAssembly.itemActivated.connect(self.changeUIPage)
		#self.listShippingAndReceiving.itemActivated.connect(self.changeUIPage)
		self.swPages.currentChanged.connect(self.pageChanged)

		self.pbUploadObject.clicked.connect(self.goUploadObject)
		self.pbUploadDate.clicked.connect(self.goUploadDate)

	

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

			# NEW:  Enable/disable uploading accordingly.
			enableUploading = which_page in UPLOAD_ENABLED_PAGES
			self.pbUploadObject.setEnabled(enableUploading)
			#self.pbUploadDate.setEnabled(  enableUploading)
			#self.dUpload.setEnabled(       enableUploading)
			self.leStatus.setText("")
			self.leStatus.setEnabled(      enableUploading)

		else:
			print("Page <{}> not supported yet. Tried to load with kwargs {}".format(which_page,kwargs))

	def setSwitchingEnabled(self,enabled):
		self.listUsers.setEnabled(enabled)
		self.listInformation.setEnabled(enabled)
		self.listAssembly.setEnabled(enabled)
		#self.listShippingAndReceiving.setEnabled(enabled)


	# New, sort of experimental
	def goUploadObject(self,*args,**kwargs):
		# Create a popup box requesting username/password, plus a "cancel" button.
		# If username+password given, submit.
		# BUT:  How can username/password be fed to loader?

		# NEW:
		# Find directory w/ a certain date, and upload ALL files in it.

		# OUTDATED:
		# FIRST:  Check to see whether there's any modified XML files

		currentPage = self.func_list[self.swPages.currentIndex()]
		upload_files = currentPage.filesToUpload()
		print("Preparing to upload files for single object:", upload_files)
		"""
		# New method:  Zip all files together and scp
		for f in upload_files:
			os.system('zip tempzip.zip {}'.format(f))
		success = os.system('scp tempzip.zip phmaster@dbloader-hgcal.cern.ch:/home/dbspool/spool/hgc/int2r')
		#os.remove('tempzip.zip')
		
		if success==0:
			print("Upload successful")
			self.leStatus.setText("Success!")
		else:
			print("Upload failed!")
			self.leStatus.setText("Error during upload!")
		"""


		# Now upload files in separate thread - will need to wait if multiple files, loader can only handle 1
		x = threading.Thread(target=self.uploadFilesAndSleep, args=(upload_files,))
		x.start()
		print("Starting upload.  Will continue in background.")


		"""
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
		"""
	
	def uploadFilesAndSleep(self, flist):
		if len(flist)==0: return

		#lc = LoaderClient()
		success = True
		for f in flist:
			# Note:  .bash_history does NOT store commands run w/ subprocess
			#upload_status = lc.run(iargs=["--login", "--url", "https://cmsdca.cern.ch/hgc_loader/hgc/int2r", f, "--verbose"])
			scpcmd = "scp {} {}@dbloader-hgcal.cern.ch:/home/dbspool/spool/hgc/int2r".format(f, self.username)
			print("Scping...")
			result = os.system(scpcmd)
			print("scp'ed...")
			success = success and result == 0
			#success = (upload_status == 200) and success
			if result != 0:
				print("File transfer:  possible error!  Return code {}".format(result.returncode))

			if f != flist[-1]:  # if not final:
				# Wait 20s before uploading the next file
				# (If cond files are uploaded before the base file is read into the DB,
				# the DB won't be able to find the part and will throw and error)
				# 20s is a conservative estimate for the worst-case upload duration
				# (It's also really obnoxious w/ multiple passwords and must change ASAP)
				print("Waiting 20s before uploading dependent file...")
				print("Note:  You must reenter your password again after the wait.")
				print("This will hopefully change in future versions.")
				time.sleep(20)
		if success:
			self.leStatus.setText("Success!")
		else:
			self.leStatus.setText("Upload failed!")

		print("Finished uploading files.  See GUI status bar for result.")
	

	def goUploadDate(self):
		lDate = self.dUpload.date()
		dateStr = "{}-{}-{}".format(lDate.year(), lDate.month(), lDate.day())
		filemanager_dir = os.sep.join([os.getcwd(), 'filemanager_data'])
		part_files = glob.glob(filemanager_dir + "/*/{}/*upload*".format(dateStr))
		step_files = glob.glob(filemanager_dir + "/steps/*/*upload*".format(dateStr))
		print("Preparing to upload multiple object files:", part_files + step_files)
		lc = LoaderClient()
		success = True
		# NOTE:  Writing all errors to upload_errors.log
		sys.stdout = open('upload_errors.log', 'w+')
		for f in part_files + step_files:
			print("UPLOADING", f)
			# removed "--login" arg
			upload_status = lc.run(iargs=["--url", "https://cmsdca.cern.ch/hgc_loader/hgc/int2r", f, "--verbose"])
			success = (upload_status == 200) and success
		sys.stdout.close()
		if success:
			self.leStatus.setText("Success!")
		else:
			self.leStatus.setText("Error during upload!")


# Class for requesting GUI username at start (for ssh tunnel)
class UserDialog(wdgt.QDialog):
	def __init__(self, *args, **kwargs):
		super(UserDialog, self).__init__(*args, **kwargs)
		print("Initializing request box")

		self.setWindowTitle("SSH tunnel:  username required")
		
		self.textName = wdgt.QLineEdit(self)
		#self.passName = wdgt.QLineEdit(self)
		#passName.setEchoMode(gui.QLineEdit.Password) # conceal password
		self.buttonLogin = wdgt.QPushButton('Connect', self)
		self.buttonCancel = wdgt.QPushButton('Cancel', self)
		self.buttonLogin.clicked.connect(self.handleLogin)
		self.buttonCancel.clicked.connect(self.handleCancel)
		layout = wdgt.QVBoxLayout(self)
		layout.addWidget(self.textName)
		#layout.addWidget(self.passName)
		layout.addWidget(self.buttonLogin)
		layout.addWidget(self.buttonCancel)

		self.cancelled = False
		print("Initialized request box")

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
