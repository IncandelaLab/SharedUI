from filemanager import fm
from PyQt5 import QtCore
import time

# GENERAL FORMAT FOR PAGE:
# - Loads MODULE.  All wirebonding info will be stored in the corresp module object??
#    - Wirebonding is inextricably linked to one module, so I think this is okay...
# - ...

PAGE_NAME = "view_wirebonding"
DEBUG = False
SITE_SEP = ', '
NO_DATE = [2020,1,1]

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

INDEX_INSTITUTION = {
	'CERN':0,
	'FNAL':1,
	'UCSB':2,
	'UMN':3,
}


def separate_sites(sites_string):
	s = sites_string
	for char in SITE_SEP:
		s=s.replace(char, '\n')
	sites = [_ for _ in s.splitlines() if _]
	return sites

def site_format_check(sites_string):
	# Input should be a comma-separated list or a space-separated list (of numbers).
	for char in sites_string:
		if not (char.isdigit() or char==" " or char==","):
			return False
	return True

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.module = fm.module()
		self.module_exists = None
		self.mode = 'setup'

		# NEW
		self.xmlModList = []


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
		#self.page.sbID.valueChanged.connect(self.update_info)
		self.page.leID.textChanged.connect(self.update_info)

		self.page.pbEdit.clicked.connect(self.startEditing)
		self.page.pbSave.clicked.connect(self.saveEditing)
		self.page.pbCancel.clicked.connect(self.cancelEditing)


		self.page.pbCureStartNowBack.clicked.connect(self.cureStartNowBack)
		self.page.pbCureStopNowBack.clicked.connect( self.cureStopNowBack )
		self.page.pbCureStartNowFront.clicked.connect(self.cureStartNowFront)
		self.page.pbCureStopNowFront.clicked.connect( self.cureStopNowFront )

		self.page.pbDeleteComment.clicked.connect(self.deleteComment)
		self.page.pbAddComment.clicked.connect(self.addComment)

		self.page.pbDeleteCommentEncap.clicked.connect(self.deleteCommentEncap)
		self.page.pbAddCommentEncap.clicked.connect(self.addCommentEncap)

		auth_users = fm.userManager.getAuthorizedUsers('wirebonding_back')
		self.index_users_wb = {auth_users[i]:i for i in range(len(auth_users))}
		auth_users = fm.userManager.getAuthorizedUsers('wirebonding_front')
		self.index_users_wf = {auth_users[i]:i for i in range(len(auth_users))}
		auth_users = fm.userManager.getAuthorizedUsers('encapsulation_back')
		self.index_users_eb = {auth_users[i]:i for i in range(len(auth_users))}
		auth_users = fm.userManager.getAuthorizedUsers('encapsulation_front')
		self.index_users_ef = {auth_users[i]:i for i in range(len(auth_users))}
		auth_users = fm.userManager.getAuthorizedUsers('test_bonds')
		self.index_users_tb = {auth_users[i]:i for i in range(len(auth_users))}
		auth_users = fm.userManager.getAuthorizedUsers('final_inspection')
		self.index_users_fi = {auth_users[i]:i for i in range(len(auth_users))}

		for user in self.index_users_wb.keys():
			self.page.cbWirebondingUserBack.addItem(user)
			self.page.cbWirebondsRepairedUserBack.addItem(user)
		for user in self.index_users_wf.keys():
			self.page.cbWirebondingUserFront.addItem(user)
			self.page.cbWirebondsRepairedUserFront.addItem(user)
		for user in self.index_users_eb.keys():
			self.page.cbEncapsulationUserBack.addItem(user)
		for user in self.index_users_ef.keys():
			self.page.cbEncapsulationUserFront.addItem(user)
		for user in self.index_users_tb.keys():
			self.page.cbTestBondsPulledUser.addItem(user)
		for user in self.index_users_fi.keys():
			self.page.cbWirebondingFinalInspectionUser.addItem(user)



	@enforce_mode(['view', 'editing', 'creating'])
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.leID.text()
		else:
			self.page.leID.setText(ID)
		print("module ID is", ID)

		#self.module_exists = self.module.load(ID)
		self.module_exists = False
		print("obj mod id", self.module.ID)
		if getattr(self.module, 'ID', None) != None:
			self.module_exists = (ID == self.module.ID)

		# shipments and location
		#self.page.leInsertUser.setText("" if self.module.insertion_user is None else self.module.insertion_user)
		#self.page.leLocation.setText("" if self.module.location is None else self.module.location)

		# characteristics
		#self.page.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(self.module.institution, -1))
		if not self.module.wirebonding_date_back is None:
			date = self.module.wirebonding_date_back.split('-') # m d y format
			self.page.dWirebondingBack.setDate(QtCore.QDate(int(date[2]), int(date[0]), int(date[1]))) # y m d
		if not self.module.wirebonding_date_front is None:
			date = self.module.wirebonding_date_front.split('-') # m d y format
			self.page.dWirebondingFront.setDate(QtCore.QDate(int(date[2]), int(date[0]), int(date[1]))) # y m d

		# comments
		self.page.listComments.clear()
		for comment in self.module.wirebonding_comments:
			self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		self.page.listCommentsEncap.clear()
		for comment in self.module.encapsulation_comments:
			self.page.listCommentsEncap.addItem(comment)
		self.page.pteWriteCommentEncap.clear()


		# pre-wirebonding qualification
		self.page.cbPreinspection.setCurrentIndex(  INDEX_INSPECTION.get(self.module.preinspection  , -1))
		self.page.sbBatchSylgard .setValue(self.module.wirebonding_sylgard if self.module.wirebonding_sylgard != None else -1)
		self.page.sbBatchBondWire.setValue(self.module.wirebonding_bond_wire if self.module.wirebonding_bond_wire != None else -1)
		self.page.sbBatchWedge   .setValue(self.module.wirebonding_wedge if self.module.wirebonding_wedge != None else -1)

		# Back wirebonding
		self.page.ckWirebondingBack.setChecked(       False if self.module.wirebonding_back          is None else self.module.wirebonding_back         )
		self.page.ckWirebondsInspectedBack.setChecked(False if self.module.wirebonds_inspected_back  is None else self.module.wirebonds_inspected_back )
		#self.page.ckWirebondsRepairedBack.setChecked( False if self.module.wirebonds_repaired_back   is None else self.module.wirebonds_repaired_back  )
		#self.page.leWirebondingUserBack.setText(      "" if self.module.wirebonding_user_back         is None else self.module.wirebonding_user_back        )
		#self.page.leWirebondsRepairedUserBack.setText("" if self.module.wirebonds_repaired_user_back  is None else self.module.wirebonds_repaired_user_back )
		if not self.module.wirebonding_user_back in self.index_users_wb.keys() and not self.module.wirebonding_user_back is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.module.wirebonding_user_back] = max(self.index_users_wb.values()) + 1
			self.page.cbWirebondingUserBack.addItem(self.module.wirebonding_user_back)
		self.page.cbWirebondingUserBack.setCurrentIndex(self.index_users_wb.get(self.module.wirebonding_user_back, -1))
		if not self.module.wirebonds_repaired_user_back in self.index_users_wb.keys() and not self.module.wirebonds_repaired_user_back is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.module.wirebonds_repaired_user_back] = max(self.index_users_wb.values()) + 1
			self.page.cbWirebondsRepairedUserBack.addItem(self.module.wirebonds_repaired_user_back)
		self.page.cbWirebondsRepairedUserBack.setCurrentIndex(self.index_users_wb.get(self.module.wirebonds_repaired_user_back, -1))

		print("JOINING:", self.module.wirebonding_unbonded_channels_back)
		self.page.pteUnbondedChannelsBack.setPlainText(        "" if self.module.wirebonding_unbonded_channels_back          is None else SITE_SEP.join([str(c) for c in self.module.wirebonding_unbonded_channels_back]         ))
		#self.page.pteWirebondsDamagedBack.setPlainText(     "" if self.module.wirebonds_damaged_back       is None else SITE_SEP.join(self.module.wirebonds_damaged_back      ))
		#self.page.pteWirebondsRepairedListBack.setPlainText("" if self.module.wirebonds_repaired_list_back is None else SITE_SEP.join(self.module.wirebonds_repaired_list_back))

		# Back encapsulation
		self.page.ckEncapsulationBack.setChecked(False if self.module.encapsulation_back    is None else self.module.encapsulation_back)
		#self.page.leEncapsulationUserBack.setText("" if self.module.encapsulation_user_back is None else self.module.encapsulation_user_back)
		if not self.module.encapsulation_user_back in self.index_users_eb.keys() and not self.module.encapsulation_user_back is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.module.encapsulation_user_back] = max(self.index_users_eb.values()) + 1
			self.page.cbEncapsulationUserBack.addItem(self.module.encapsulation_user_back)
		self.page.cbEncapsulationUserBack.setCurrentIndex(self.index_users_eb.get(self.module.encapsulation_user_back, -1))
		self.page.cbEncapsulationInspectionBack.setCurrentIndex(INDEX_INSPECTION.get(self.module.encapsulation_inspection_back,-1))
		if self.module.encapsulation_cure_start_back is None:
			self.page.dtCureStartBack.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStartBack.setTime(QtCore.QTime(0,0,0))
		else:
			localtime = list(time.localtime(self.module.encapsulation_cure_start_back))
			self.page.dtCureStartBack.setDate(QtCore.QDate(*localtime[0:3]))
			self.page.dtCureStartBack.setTime(QtCore.QTime(*localtime[3:6]))

		if self.module.encapsulation_cure_stop_back is None:
			self.page.dtCureStopBack.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStopBack.setTime(QtCore.QTime(0,0,0))
		else:
			localtime = list(time.localtime(self.module.encapsulation_cure_stop_back))
			self.page.dtCureStopBack.setDate(QtCore.QDate(*localtime[0:3]))
			self.page.dtCureStopBack.setTime(QtCore.QTime(*localtime[3:6]))

		# test bonds
		self.page.ckTestBonds.setChecked(         False if self.module.test_bonds           is None else self.module.test_bonds          )
		#self.page.ckTestBondsPulled.setChecked(   False if self.module.test_bonds_pulled    is None else self.module.test_bonds_pulled   )
		#self.page.leTestBondsPulledUser.setText(  "" if self.module.test_bonds_pulled_user   is None else self.module.test_bonds_pulled_user  )
		if not self.module.test_bonds_pulled_user in self.index_users_tb.keys() and not self.module.test_bonds_pulled_user is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.module.test_bonds_pulled_user] = max(self.index_users_tb.values()) + 1
			self.page.cbTestBondsPulledUser.addItem(self.module.test_bonds_pulled_user)
		self.page.cbTestBondsPulledUser.setCurrentIndex(self.index_users_tb.get(self.module.test_bonds_pulled_user, -1))
		#self.page.cbTestBondsPulledOK.setCurrentIndex(  INDEX_INSPECTION.get(self.module.test_bonds_pulled_ok  , -1))
		self.page.dsbBondPullAvg.setValue( -1 if self.module.test_bonds_pull_avg is None else self.module.test_bonds_pull_avg )
		self.page.dsbBondPullStd.setValue( -1 if self.module.test_bonds_pull_std is None else self.module.test_bonds_pull_std )

		# Front wirebonding
		self.page.ckWirebondingFront.setChecked(       False if self.module.wirebonding_front           is None else self.module.wirebonding_front         )
		self.page.ckWirebondsInspectedFront.setChecked(False if self.module.wirebonds_inspected_front   is None else self.module.wirebonds_inspected_front )
		#self.page.ckWirebondsRepairedFront.setChecked( False if self.module.wirebonds_repaired_front    is None else self.module.wirebonds_repaired_front  )
		#self.page.leWirebondingUserFront.setText(      "" if self.module.wirebonding_user_front         is None else self.module.wirebonding_user_front        )
		#self.page.leWirebondsRepairedUserFront.setText("" if self.module.wirebonds_repaired_user_front  is None else self.module.wirebonds_repaired_user_front )
		#self.page.pteWirebondingChannelsSkipFront.setPlainText( "" if self.module.wirebonding_skip_channels_front    is None else SITE_SEP.join(self.module.wirebonding_skip_channels_front   ))
		self.page.pteUnbondedChannelsFront.setPlainText(        "" if self.module.wirebonding_unbonded_channels_front is None else SITE_SEP.join([str(c) for c in self.module.wirebonding_unbonded_channels_front]))
		if not self.module.wirebonding_user_front in self.index_users_wf.keys() and not self.module.wirebonding_user_front is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.module.wirebonding_user_front] = max(self.index_users_wf.values()) + 1
			self.page.cbWirebondingUserFront.addItem(self.module.wirebonding_user_front)
		self.page.cbWirebondingUserFront.setCurrentIndex(self.index_users_wf.get(self.module.wirebonding_user_front, -1))
		if not self.module.wirebonds_repaired_user_front in self.index_users_wf.keys() and not self.module.wirebonds_repaired_user_front is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.module.wirebons_repaired_user_front] = max(self.index_users_wf.values()) + 1
			self.page.cbWirebondsRepairedUserFront.addItem(self.module.wirebonds_repaired_user_front)
		self.page.cbWirebondsRepairedUserFront.setCurrentIndex(self.index_users_wf.get(self.module.wirebonds_repaired_user_front, -1))

		#self.page.pteWirebondsDamagedFront.setPlainText(     "" if self.module.wirebonds_damaged_front       is None else SITE_SEP.join(self.module.wirebonds_damaged_front      ))
		#self.page.pteWirebondsRepairedListFront.setPlainText("" if self.module.wirebonds_repaired_list_front is None else SITE_SEP.join(self.module.wirebonds_repaired_list_front))

		#self.page.ckShieldLayerBonds.setChecked(False if self.module.wirebonding_shield is None else self.module.wirebonding_shield)
		#self.page.ckGuardLayerBonds.setChecked( False if self.module.wirebonding_guard  is None else self.module.wirebonding_guard )


		# Front encapsulation
		self.page.ckEncapsulationFront.setChecked(False if self.module.encapsulation_front    is None else self.module.encapsulation_front)
		#self.page.leEncapsulationUserFront.setText("" if self.module.encapsulation_user_front is None else self.module.encapsulation_user_front)
		if not self.module.encapsulation_user_front in self.index_users_ef.keys() and not self.module.encapsulation_user_front is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.module.encapsulation_user_front] = max(self.index_users_ef.values()) + 1
			self.page.cbEncapsulationUserFront.addItem(self.module.encapsulation_user_front)
		self.page.cbEncapsulationUserFront.setCurrentIndex(self.index_users_ef.get(self.module.encapsulation_user_front, -1))
		self.page.cbEncapsulationInspectionFront.setCurrentIndex(INDEX_INSPECTION.get(self.module.encapsulation_inspection_front,-1))
		if self.module.encapsulation_cure_start_front is None:
			self.page.dtCureStartFront.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStartFront.setTime(QtCore.QTime(0,0,0))
		else:
			localtime = list(time.localtime(self.module.encapsulation_cure_start_front))
			self.page.dtCureStartFront.setDate(QtCore.QDate(*localtime[0:3]))
			self.page.dtCureStartFront.setTime(QtCore.QTime(*localtime[3:6]))

		if self.module.encapsulation_cure_stop_front is None:
			self.page.dtCureStopFront.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStopFront.setTime(QtCore.QTime(0,0,0))
		else:
			localtime = list(time.localtime(self.module.encapsulation_cure_stop_front))
			self.page.dtCureStopFront.setDate(QtCore.QDate(*localtime[0:3]))
			self.page.dtCureStopFront.setTime(QtCore.QTime(*localtime[3:6]))


		# wirebonding qualification
		#self.page.ckWirebondingFinalInspection.setChecked(False if self.module.wirebonding_final_inspection is None else self.module.wirebonding_final_inspection)
		#self.page.leWirebondingFinalInspectionUser.setText("" if self.module.wirebonding_final_inspection_user is None else self.module.wirebonding_final_inspection_user)
		if not self.module.wirebonding_final_inspection_user in self.index_users_fi.keys() and not self.module.wirebonding_final_inspection_user is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.module.wirebonding_final_inspection_user] = max(self.index_users_fi.values()) + 1
			self.page.cbWirebondingFinalInspectionUser.addItem(self.module.wirebonding_final_inspection_user)
		self.page.cbWirebondingFinalInspectionUser.setCurrentIndex(self.index_users_fi.get(self.module.wirebonding_final_inspection_user, -1))
		self.page.cbWirebondingFinalInspectionOK.setCurrentIndex(INDEX_INSPECTION.get(self.module.wirebonding_final_inspection_ok,-1))

		self.updateElements()


	@enforce_mode(['view','editing','creating'])
	def updateElements(self):
		module_exists   = self.module_exists

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'

		self.setMainSwitchingEnabled(mode_view) 
		self.page.leID.setReadOnly(not mode_view)

		self.page.pbEdit  .setEnabled( mode_view )  # and     module_exists )
		self.page.pbSave  .setEnabled( mode_creating or mode_editing   )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing   )

		# characteristics
		#self.page.leInsertUser.setReadOnly( not (mode_creating or mode_editing) )
		#self.page.leLocation.setReadOnly(   not (mode_creating or mode_editing) )
		#self.page.cbInstitution.setEnabled(      mode_creating or mode_editing  )
		self.page.dWirebonding.setReadOnly(  not (mode_creating or mode_editing) )

		# comments
		self.page.pbDeleteComment.setEnabled(mode_creating or mode_editing)
		self.page.pbAddComment.setEnabled(   mode_creating or mode_editing)
		self.page.pteWriteComment.setEnabled(mode_creating or mode_editing)

		self.page.pbDeleteCommentEncap.setEnabled(mode_creating or mode_editing)
		self.page.pbAddCommentEncap.setEnabled(   mode_creating or mode_editing)
		self.page.pteWriteCommentEncap.setEnabled(mode_creating or mode_editing)

		# pre-wirebonding qualification
		self.page.cbPreinspection.setEnabled(   mode_creating or mode_editing )
		self.page.sbBatchSylgard .setReadOnly(not (mode_creating or mode_editing) )
		self.page.sbBatchBondWire.setReadOnly(not (mode_creating or mode_editing) )
		self.page.sbBatchWedge   .setReadOnly(not (mode_creating or mode_editing) )

		# back wirebonding
		self.page.ckWirebondingBack.setEnabled(        mode_creating or mode_editing )
		self.page.ckWirebondsInspectedBack.setEnabled( mode_creating or mode_editing )
		#self.page.ckWirebondsRepairedBack.setEnabled(  mode_creating or mode_editing )
		#self.page.leWirebondingUserBack.setReadOnly(        not (mode_creating or mode_editing) )
		#self.page.leWirebondsRepairedUserBack.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.cbWirebondingUserBack.setEnabled(      mode_creating or mode_editing )
		self.page.cbWirebondsRepairedUserBack.setEnabled(mode_creating or mode_editing )
		self.page.pteUnbondedChannelsBack.setReadOnly(         not (mode_creating or mode_editing) )
		#self.page.pteWirebondsDamagedBack.setReadOnly(      not (mode_creating or mode_editing) )
		#self.page.pteWirebondsRepairedListBack.setReadOnly( not (mode_creating or mode_editing) )

		# back encapsulation
		self.page.ckEncapsulationBack.setEnabled( mode_creating or mode_editing )
		#self.page.leEncapsulationUserBack.setReadOnly( not (mode_creating or mode_editing) )
		self.page.cbEncapsulationUserBack.setEnabled(       mode_creating or mode_editing )
		self.page.cbEncapsulationInspectionBack.setEnabled( mode_creating or mode_editing )
		self.page.dtCureStartBack.setReadOnly( not (mode_creating or mode_editing) )
		self.page.dtCureStopBack.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.pbCureStartNowBack.setEnabled( mode_creating or mode_editing )
		self.page.pbCureStopNowBack.setEnabled(  mode_creating or mode_editing )

		# test bonds
		self.page.ckTestBonds.setEnabled(          mode_creating or mode_editing )
		#self.page.ckTestBondsPulled.setEnabled(    mode_creating or mode_editing )
		#self.page.leTestBondsPulledUser.setReadOnly(    not (mode_creating or mode_editing) )
		self.page.cbTestBondsPulledUser.setEnabled(mode_creating or mode_editing )
		#self.page.cbTestBondsPulledOK.setEnabled(   mode_creating or mode_editing )
		self.page.dsbBondPullAvg.setReadOnly(           not (mode_creating or mode_editing) )
		self.page.dsbBondPullStd.setReadOnly(           not (mode_creating or mode_editing) )

		# front wirebonding
		self.page.ckWirebondingFront.setEnabled(        mode_creating or mode_editing )
		self.page.ckWirebondsInspectedFront.setEnabled( mode_creating or mode_editing )
		#self.page.ckWirebondsRepairedFront.setEnabled(  mode_creating or mode_editing )
		#self.page.leWirebondingUserFront.setReadOnly(        not (mode_creating or mode_editing) )
		#self.page.leWirebondsRepairedUserFront.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.cbWirebondingUserFront.setEnabled(       mode_creating or mode_editing )
		self.page.cbWirebondsRepairedUserFront.setEnabled( mode_creating or mode_editing )
		self.page.pteUnbondedChannelsFront.setReadOnly(         not (mode_creating or mode_editing) )
		#self.page.pteWirebondsDamagedFront.setReadOnly(      not (mode_creating or mode_editing) )
		#self.page.pteWirebondsRepairedListFront.setReadOnly( not (mode_creating or mode_editing) )

		# front encapsulation
		self.page.ckEncapsulationFront.setEnabled( mode_creating or mode_editing )
		#self.page.leEncapsulationUserFront.setReadOnly( not (mode_creating or mode_editing) )
		self.page.cbEncapsulationUserFront.setEnabled( mode_creating or mode_editing )
		self.page.cbEncapsulationInspectionFront.setEnabled( mode_creating or mode_editing )
		self.page.dtCureStartFront.setReadOnly( not (mode_creating or mode_editing) )
		self.page.dtCureStopFront.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.pbCureStartNowFront.setEnabled( mode_creating or mode_editing )
		self.page.pbCureStopNowFront.setEnabled(  mode_creating or mode_editing )

		# wirebonding qualification
		#self.page.ckWirebondingFinalInspection.setEnabled( mode_creating or mode_editing )
		#self.page.leWirebondingFinalInspectionUser.setReadOnly( not (mode_creating or mode_editing) )
		self.page.cbWirebondingFinalInspectionUser.setEnabled( mode_creating or mode_editing )
		self.page.cbWirebondingFinalInspectionOK.setEnabled( mode_creating or mode_editing )



	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		print("ERROR:  This is outdated and should not be used.")
		if not self.module_exists:
			ID = self.page.sbID.value()
			self.mode = 'creating'
			self.module.new(ID)
			self.updateElements()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_module = fm.module()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_module.load(tmp_ID)
		if not tmp_exists:
			self.page.leStatus.setText("does not exist")
		else:
			self.module = tmp_module
			self.mode = 'editing'
			self.update_info()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):
		# First, check text boxes for errors; do nothing if found
		self.page.leErrors.clear()
		pteList = {"unbonded_back":self.page.pteUnbondedChannelsBack,
				   # "damaged_back":self.page.pteWirebondsDamagedBack,
				   # "repaired_back":self.page.pteWirebondsRepairedListBack,
				   "skip_front":self.page.pteWirebondingChannelsSkipFront,
				   "unbonded_front":self.page.pteUnbondedChannelsFront
				   # "damaged_front":self.page.pteWirebondsDamagedFront,
				   # "repaired_front":self.page.pteWirebondsRepairedListFront
				  }
		pteErrs = []
		for name, pte in pteList.items():
			if not site_format_check(pte.toPlainText()):
				pteErrs.append(name)
		# Check batch errors:  existence, emptiness, expiration
		"""
		if self.module.wirebonding_sylgard is None:
			pteErrs.append("Sylgard missing")
		if self.module.wirebonding_bond_wire is None:
			pteErrs.append("Bond wire missing")
		if self.module.wirebonding_wedge is None:
			pteErrs.append("Wedge missing")
		"""
		tmp_sylgard = fm.batch_sylgard()
		if not tmp_sylgard.load(self.page.sbBatchSylgard.value()):
			pteErrs.append("Sylgard DNE")
		else:
			if not (tmp_sylgard.date_expires) is None:
				ydm = tmp_sylgard.date_expires.split('-')
				expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))
				if QtCore.QDate.currentDate() > expires:  pteErrs.append("Sylgard expired")
			if tmp_sylgard.is_empty:  pteErrs.append("Sylgard empty")
		tmp_bond_wire = fm.batch_bond_wire()
		if not tmp_bond_wire.load(self.page.sbBatchBondWire.value()):
			pteErrs.append("Bond wire DNE")
		else:
			if not (tmp_bond_wire.date_expires) is None:
				ydm = tmp_bond_wire.date_expires.split('-')
				expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))
				if QtCore.QDate.currentDate() > expires:  pteErrs.append("Bond wire expired")
			if tmp_bond_wire.is_empty:  pteErrs.append("Bond wire empty")
		tmp_wedge = fm.batch_wedge()
		if not tmp_wedge.load(self.page.sbBatchWedge.value()):
			pteErrs.append("Wedge DNE")
		else:
			if not (tmp_wedge.date_expires) is None:
				ydm = tmp_wedge.date_expires.split('-')
				expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))
				if QtCore.QDate.currentDate() > expires:  pteErrs.append("Wedge expired")
			if tmp_wedge.is_empty:  pteErrs.append("Wedge empty")

		if len(pteErrs) > 0:
			self.page.leErrors.setText("Error:  {}".format(', '.join(pteErrs)))
			return

		# NEW:  Check to ensure all steps are completed, set in module page if done
		self.module.wirebonding_completed = self.page.ckWirebondingBack.isChecked() and self.page.ckWirebondsInspectedBack.isChecked() and \
                                            self.page.ckWirebondingFront.isChecked() and self.page.ckWirebondsInspectedFront.isChecked() and \
                                            self.page.ckEncapsulationBack.isChecked() and self.page.cbEncapsulationInspectionBack.currentText() != '' and \
                                            self.page.ckEncapsulationFront.isChecked() and self.page.cbEncapsulationInspectionFront.currentText() != '' and \
                                            self.page.cbFinalInspectionOK.currentText() != ''
                                            

		# characteristics

		#self.module.insertion_user = str(self.page.leInsertUser.text()   ) if str(self.page.leInsertUser.text())         else None
		#self.module.location    = str(self.page.leLocation.text()        ) if str(self.page.leLocation.text())           else None
		#self.module.institution = str(self.page.cbInstitution.currentText()) if str(self.page.cbInstitution.currentText()) else None
		datew = self.page.dWirebondingBack.date()
		self.module.wirebonding_date_back  = "{}-{}-{}".format(datew.month(), datew.day(), datew.year())
		datew = self.page.dWirebondingFront.date()
		self.module.wirebonding_date_front = "{}-{}-{}".format(datew.month(), datew.day(), datew.year())

		# comments
		num_comments = self.page.listComments.count()
		self.module.wirebonding_comments = []
		for i in range(num_comments):
			self.module.wirebonding_comments.append(str(self.page.listComments.item(i).text()))

		num_comments_encap = self.page.listCommentsEncap.count()
		self.module.encapsulation_comments = []
		for i in range(num_comments_encap):
			self.module.encapsulation_comments.append(str(self.page.listCommentsEncap.item(i).text()))

		# pre-wirebonding qualification
		self.module.preinspection        = str(self.page.cbPreinspection.currentText()  ) if str(self.page.cbPreinspection.currentText()  ) else None
		self.module.wirebonding_sylgard   = self.page.sbBatchSylgard.value()  if self.page.sbBatchSylgard.value() >= 0  else None
		self.module.wirebonding_bond_wire = self.page.sbBatchBondWire.value() if self.page.sbBatchBondWire.value() >= 0 else None
		self.module.wirebonding_wedge     = self.page.sbBatchWedge.value()    if self.page.sbBatchWedge.value() >= 0    else None

		# back wirebonding
		self.module.wirebonding_back              = self.page.ckWirebondingBack.isChecked()
		self.module.wirebonds_inspected_back      = self.page.ckWirebondsInspectedBack.isChecked()
		#self.module.wirebonds_repaired_back       = self.page.ckWirebondsRepairedBack.isChecked()
		self.module.wirebonding_user_back         = str(self.page.cbWirebondingUserBack.currentText()      ) if str(self.page.cbWirebondingUserBack.currentText()      ) else None
		self.module.wirebonds_repaired_user_back  = str(self.page.cbWirebondsRepairedUserBack.currentText()) if str(self.page.cbWirebondsRepairedUserBack.currentText()) else None
		self.module.wirebonding_unbonded_channels_back = separate_sites(str(self.page.pteUnbondedChannelsBack.toPlainText()        )) if str(self.page.pteUnbondedChannelsBack.toPlainText()        ) else None
		#self.module.wirebonds_damaged_back          = separate_sites(str(self.page.pteWirebondsDamagedBack.toPlainText()     )) if str(self.page.pteWirebondsDamagedBack.toPlainText()     ) else None
		#self.module.wirebonds_repaired_list_back    = separate_sites(str(self.page.pteWirebondsRepairedListBack.toPlainText())) if str(self.page.pteWirebondsRepairedListBack.toPlainText()) else None

		# back encapsulation
		self.module.encapsulation_back            = self.page.ckEncapsulationBack.isChecked()
		self.module.encapsulation_user_back       = str(self.page.cbEncapsulationUserBack.currentText()             ) if str(self.page.cbEncapsulationUserBack.currentText()             ) else None
		self.module.encapsulation_inspection_back = str(self.page.cbEncapsulationInspectionBack.currentText()) if str(self.page.cbEncapsulationInspectionBack.currentText()) else None
		if self.page.dtCureStartBack.date().year() == NO_DATE[0]:
			self.module.encapsulation_cure_start_back = None
		else:
			self.module.encapsulation_cure_start_back = self.page.dtCureStartBack.dateTime().toTime_t()
		if self.page.dtCureStopBack.date().year() == NO_DATE[0]:
			self.module.encapsulation_cure_stop_back = None
		else:
			self.module.encapsulation_cure_stop_back = self.page.dtCureStopBack.dateTime().toTime_t()

		# test bonds
		self.module.test_bonds             = self.page.ckTestBonds.isChecked()
		#self.module.test_bonds_pulled      = self.page.ckTestBondsPulled.isChecked()
		self.module.test_bonds_pulled_user = str(self.page.cbTestBondsPulledUser.currentText()      ) if str(self.page.cbTestBondsPulledUser.currentText()      ) else None
		#self.module.test_bonds_pulled_ok   = str(self.page.cbTestBondsPulledOK.currentText() ) if str(self.page.cbTestBondsPulledOK.currentText() ) else None
		self.module.test_bond_pull_avg = self.page.dsbBondPullAvg.value() if self.page.dsbBondPullAvg.value() >= 0 else None
		self.module.test_bond_pull_std = self.page.dsbBondPullStd.value() if self.page.dsbBondPullStd.value() >= 0 else None

		# front wirebonding
		self.module.wirebonding_front              = self.page.ckWirebondingFront.isChecked()
		self.module.wirebonds_inspected_front      = self.page.ckWirebondsInspectedFront.isChecked()
		#self.module.wirebonds_repaired_front       = self.page.ckWirebondsRepairedFront.isChecked()
		self.module.wirebonding_user_front         = str(self.page.cbWirebondingUserFront.currentText()      ) if str(self.page.cbWirebondingUserFront.currentText()      ) else None
		self.module.wirebonds_repaired_user_front  = str(self.page.cbWirebondsRepairedUserFront.currentText()) if str(self.page.cbWirebondsRepairedUserFront.currentText()) else None
		self.module.wirebonding_unbonded_channels_front = separate_sites(str(self.page.pteUnbondedChannelsFront.toPlainText()        )) if str(self.page.pteUnbondedChannelsFront.toPlainText() ) else None
		#self.module.wirebonds_damaged_front          = separate_sites(str(self.page.pteWirebondsDamagedFront.toPlainText()     ))   if str(self.page.pteWirebondsDamagedFront.toPlainText()     ) else None
		#self.module.wirebonds_repaired_list_front    = separate_sites(str(self.page.pteWirebondsRepairedListFront.toPlainText()))   if str(self.page.pteWirebondsRepairedListFront.toPlainText()) else None
		self.module.wirebonds_skip_channels_front    = separate_sites(str(self.page.pteWirebondingChannelsSkipFront.toPlainText())) if str(self.page.pteWirebondingChannelsSkipFront.toPlainText()) else None

		# front encapsulation
		self.module.encapsulation_front            = self.page.ckEncapsulationFront.isChecked()
		self.module.encapsulation_user_front       = str(self.page.cbEncapsulationUserFront.currentText()             ) if str(self.page.cbEncapsulationUserFront.currentText()             ) else None
		self.module.encapsulation_inspection_front = str(self.page.cbEncapsulationInspectionFront.currentText()) if str(self.page.cbEncapsulationInspectionFront.currentText()) else None
		#if self.page.dtCureStartFront.date().year() == NO_DATE[0]:
		#	self.module.encapsulation_cure_start_front = None
		#else:
		self.module.encapsulation_cure_start_front = self.page.dtCureStartFront.dateTime().toTime_t()
		#if self.page.dtCureStopFront.date().year() == NO_DATE[0]:
		#	self.module.encapsulation_cure_stop_front = None
		#else:
		self.module.encapsulation_cure_stop_front = self.page.dtCureStopFront.dateTime().toTime_t()

		# wirebonding qualification
		#self.module.wirebonding_final_inspection      = self.page.ckWirebondingFinalInspection.isChecked()
		self.module.wirebonding_final_inspection_user = str(self.page.cbWirebondingFinalInspectionUser.currentText()     ) if str(self.page.cbWirebondingFinalInspectionUser.currentText()     ) else None
		self.module.wirebonding_final_inspection_ok   = str(self.page.cbWirebondingFinalInspectionOK.currentText()) if str(self.page.cbWirebondingFinalInspectionOK.currentText()) else None


		self.module.save()
		self.mode = 'view'
		self.update_info()

		self.xmlModList.append(self.module.ID)



	def xmlModified(self):
		return self.xmlModList

	def xmlModifiedReset(self):
		self.xmlModList = []


	@enforce_mode(['editing','creating'])
	def cureStartNowBack(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStartBack.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStartBack.setTime(QtCore.QTime(*localtime[3:6]))

	@enforce_mode(['editing','creating'])
	def cureStopNowBack(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStopBack.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStopBack.setTime(QtCore.QTime(*localtime[3:6]))

	@enforce_mode(['editing','creating'])
	def cureStartNowFront(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStartFront.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStartFront.setTime(QtCore.QTime(*localtime[3:6]))

	@enforce_mode(['editing','creating'])
	def cureStopNowFront(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStopFront.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStopFront.setTime(QtCore.QTime(*localtime[3:6]))


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

	@enforce_mode(['editing','creating'])
	def deleteCommentEncap(self,*args,**kwargs):
		row = self.page.listCommentsEncap.currentRow()
		if row >= 0:
			self.page.listCommentsEncap.takeItem(row)

	@enforce_mode(['editing','creating'])
	def addCommentEncap(self,*args,**kwargs):
		text = str(self.page.pteWriteCommentEncap.toPlainText())
		if text:
			self.page.listCommentsEncap.addItem(text)
			self.page.pteWriteCommentEncap.clear()


	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is str):
				raise TypeError("Expected type <str> for ID; got <{}>".format(type(ID)))
			#if ID < 0:
			#	raise ValueError("ID cannot be negative")
			self.page.sbID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
