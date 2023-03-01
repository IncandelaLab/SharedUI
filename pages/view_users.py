from PyQt5 import QtCore
import time
import datetime
from filemanager import fm

PAGE_NAME = "view_users"
DEBUG = False

#NEW, WIP


class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.currentUser = None

		self.mode = 'setup'

		self.usersToRemove = []  #NEW:  Store list of users that were deleted
		# MAYBE necessary--the userlists can't be updated until save() is called, but they're not stored anywhere else!


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

		self.page.pbAddUser.clicked.connect(self.addUser)
		self.page.pbDeleteSelected.clicked.connect(self.deleteSelected)
		self.page.pbEditSelected.clicked.connect(self.editSelected)
		self.page.pbSaveUser.clicked.connect(self.saveUser)
		self.page.pbCancel.clicked.connect(self.cancelEditing)

	@enforce_mode(['view', 'creating', 'editing'])
	def update_info(self,ID=None,*args,**kwargs):
		# Need to do:
		# - call this whenever a new user is selected+loaded
		# - Update all check boxes, username box, isAdmin
		# - Ensure userlist is up to date

		row = self.page.lwUsers.currentRow()
		print("ROW:", row)
		if row >= 0 and self.mode != 'view':
			self.currentUser = self.page.lwUsers.item(row).text()
			self.currentUser = self.currentUser.replace(' (admin)','')
		else:
			self.currentUser = None
		self.user_exists = self.currentUser != None
		print("CURRENT USER:", self.currentUser)
		print("pre username text:", self.currentUser if self.user_exists else "")

		self.page.lwUsers.clear()
		userlist = fm.userManager.getAllUsers()
		for user in userlist:
			if fm.userManager.isAdmin(user):
				self.page.lwUsers.addItem(user + " (admin)")
			else:
				self.page.lwUsers.addItem(user)

		print("Setting username text:", self.currentUser if self.user_exists else "")
		self.page.leUsername.setText(self.currentUser if self.user_exists else "")

		self.page.cbAdministrator.setChecked(False if not self.user_exists else fm.userManager.isAdmin(self.currentUser))
		userperms = fm.userManager.getUserPerms(self.currentUser)
		self.page.cbBaseplate  .setChecked(False if userperms is None else userperms[0])
		self.page.cbSensor     .setChecked(False if userperms is None else userperms[1])
		self.page.cbPcb        .setChecked(False if userperms is None else userperms[2])
		self.page.cbProtomodule.setChecked(False if userperms is None else userperms[3])
		self.page.cbModule     .setChecked(False if userperms is None else userperms[4])
		self.page.cbStepSensor .setChecked(False if userperms is None else userperms[5])
		self.page.cbStepPcb    .setChecked(False if userperms is None else userperms[6])
		self.page.cbBackWirebonding   .setChecked(False if userperms is None else userperms[7])
		self.page.cbFrontWirebonding  .setChecked(False if userperms is None else userperms[8])
		self.page.cbBackEncapsulation .setChecked(False if userperms is None else userperms[9])
		self.page.cbFrontEncapsulation.setChecked(False if userperms is None else userperms[10])
		self.page.cbTestBonds         .setChecked(False if userperms is None else userperms[11])
		self.page.cbFinalInspection   .setChecked(False if userperms is None else userperms[12])

		self.updateElements()


	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		user_exists      = self.user_exists

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'

		self.setMainSwitchingEnabled(mode_view)

		self.page.pbAddUser.setEnabled(mode_view)
		self.page.pbEditSelected.setEnabled(mode_view)
		self.page.pbDeleteSelected.setEnabled(mode_editing)
		self.page.pbSaveUser.setEnabled(mode_creating or mode_editing)
		self.page.pbCancel.setEnabled(mode_editing or mode_creating)

		self.page.leUsername.setReadOnly(not (mode_creating or mode_editing))
		self.page.cbAdministrator.setEnabled(mode_creating or mode_editing)
		self.page.cbBaseplate    .setEnabled(mode_creating or mode_editing)
		self.page.cbSensor       .setEnabled(mode_creating or mode_editing)
		self.page.cbPcb          .setEnabled(mode_creating or mode_editing)
		self.page.cbProtomodule  .setEnabled(mode_creating or mode_editing)
		self.page.cbModule       .setEnabled(mode_creating or mode_editing)
		self.page.cbStepSensor   .setEnabled(mode_creating or mode_editing)
		self.page.cbStepPcb      .setEnabled(mode_creating or mode_editing)
		self.page.cbBackEncapsulation .setEnabled(mode_creating or mode_editing)
		self.page.cbBackWirebonding   .setEnabled(mode_creating or mode_editing)
		self.page.cbFrontEncapsulation.setEnabled(mode_creating or mode_editing)
		self.page.cbFrontWirebonding  .setEnabled(mode_creating or mode_editing)
		self.page.cbTestBonds         .setEnabled(mode_creating or mode_editing)
		self.page.cbFinalInspection   .setEnabled(mode_creating or mode_editing)


	@enforce_mode('view')
	def addUser(self,*args,**kwargs):
		self.mode = 'creating'
		self.updateElements()

	@enforce_mode('view')
	def editSelected(self,*args,**kwargs):
		print("editSelected called")
		#if self.user_exists:
		self.mode = 'editing'
		self.update_info()
		#else:
		#	print("User does not exist; skipping")

	@enforce_mode(['editing'])  #,'creating'])
	def deleteSelected(self,*args,**kwargs):
		# NOTE:  Can only call this if currently editing a user
		fm.userManager.removeUser(self.page.leUsername.text())
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveUser(self,*args,**kwargs):
		username = self.page.leUsername.text()
		isAdmin = self.page.cbAdministrator.isChecked()
		if isAdmin:
			permissions = [True for i in range(13)]
		else:
			permissions = [
				self.page.cbBaseplate.isChecked(),
				self.page.cbSensor.isChecked(),
				self.page.cbPcb.isChecked(),
				self.page.cbProtomodule.isChecked(),
				self.page.cbModule.isChecked(),
				self.page.cbStepSensor.isChecked(),
				#self.page.cbStepSensor.isChecked(),  # post
				self.page.cbStepPcb.isChecked(),
				#self.page.cbStepPcb.isChecked(),  # post
				self.page.cbBackWirebonding.isChecked(),
				self.page.cbFrontWirebonding.isChecked(),
				self.page.cbBackEncapsulation.isChecked(),
				self.page.cbFrontEncapsulation.isChecked(),
				self.page.cbTestBonds.isChecked(),
				self.page.cbFinalInspection.isChecked()
			]
		if not self.user_exists:
			# Create new user
			fm.userManager.addUser(username, permissions, isAdmin=isAdmin)
		else:
			# Save changes to existing user
			fm.userManager.updateUser(username, permissions, isAdmin=isAdmin)

		self.mode = 'view'
		self.update_info()
		
	@enforce_mode(['editing', 'creating'])
	def cancelEditing(self,*args,**kwargs):
		# cancel editing, discard changes
		self.mode = 'view'
		self.update_info()


	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is str):
				raise TypeError("Expected type <str> for ID; got <{}>".format(type(ID)))
			if int(ID) < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbShipmentID.setValue(int(ID))

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
