from filemanager import fm, supplies, parts
from PyQt5 import QtCore
import time
import datetime
import os
import json

# - Loads a MODULE.  All wirebonding info will be stored in the corresp module object.

PAGE_NAME = "view_wirebonding"
DEBUG = False
SITE_SEP = ', '
NO_DATE = [2022,1,1]

INDEX_INSPECTION = {
	'yes':0,
	'pass':0,
	True:0,
	'no':1,
	'fail':1,
	False:1,
}


def separate_sites(sites_string):
	s = sites_string
	for char in SITE_SEP:
		s=s.replace(char, '\n')
	sites = [_ for _ in s.splitlines() if _]
	return sites

def site_format_check(sites_string):
	# Input should be a comma-separated list or a space-separated list (of numbers).
	if sites_string == "" or sites_string == "None":  return True
	for char in sites_string:
		if not (char.isdigit() or char==" " or char==","):
			return False
	return True

class func(object):
	def __init__(self,fm,userManager,page,setUIPage,setSwitchingEnabled):
		self.userManager = userManager
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.module = parts.module()
		self.module_exists = None
		self.batch_sylgard = supplies.batch_sylgard()
		self.batch_bond_wire = supplies.batch_bond_wire()
		self.batch_wedge = supplies.batch_wedge()
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

		auth_users = self.userManager.getAuthorizedUsers('wirebonding_back')
		self.index_users_wb = {auth_users[i]:i for i in range(len(auth_users))}
		auth_users = self.userManager.getAuthorizedUsers('wirebonding_front')
		self.index_users_wf = {auth_users[i]:i for i in range(len(auth_users))}
		auth_users = self.userManager.getAuthorizedUsers('encapsulation_back')
		self.index_users_eb = {auth_users[i]:i for i in range(len(auth_users))}
		auth_users = self.userManager.getAuthorizedUsers('encapsulation_front')
		self.index_users_ef = {auth_users[i]:i for i in range(len(auth_users))}
		auth_users = self.userManager.getAuthorizedUsers('test_bonds')
		self.index_users_tb = {auth_users[i]:i for i in range(len(auth_users))}
		auth_users = self.userManager.getAuthorizedUsers('final_inspection')
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

		self.page.pbAddPart.clicked.connect(self.finishSearch)
		self.page.pbCancelSearch.clicked.connect(self.cancelSearch)
		self.page.pbGoBatchSylgard.clicked.connect(self.goBatchSylgard)
		self.page.pbGoBatchBondWire.clicked.connect(self.goBatchBondWire)
		self.page.pbGoBatchWedge.clicked.connect(self.goBatchWedge)


	@enforce_mode(['view', 'editing'])
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.leID.text()
		else:
			self.page.leID.setText(ID)

		self.module_exists = False
		if getattr(self.module, 'ID', None) != None:
			self.module_exists = (ID == self.module.ID)

		# characteristics
		dates_to_set = [(self.module.back_bonds_date,  self.page.dWirebondingBack),
						(self.module.front_bonds_date, self.page.dWirebondingFront)]
		for st, dt in dates_to_set:
			if st is None:
				dt.setDate(QtCore.QDate(*NO_DATE))
			else:
				tm = datetime.datetime.strptime(st, "%Y-%m-%d")
				dat = QtCore.QDate(tm.year, tm.month, tm.day)
				dt.setDate(dat)

		# comments
		self.page.listComments.clear()
		for comment in self.module.wirebond_comments:
			self.page.listComments.addItem(comment)
		self.page.pteWriteComment.clear()

		# Not in DB, maybe ignore?
		self.page.listCommentsEncap.clear()
		for comment in self.module.encapsulation_comments:
			self.page.listCommentsEncap.addItem(comment)
		self.page.pteWriteCommentEncap.clear()


		# pre-wirebonding qualification
		self.page.cbPreinspection.setCurrentIndex(  INDEX_INSPECTION.get(self.module.pre_inspection  , -1))
		self.page.leBatchSylgard .setText(self.module.sylgard_batch   if self.module.sylgard_batch   != None else "")
		self.page.leBatchBondWire.setText(self.module.bond_wire_batch_num if self.module.bond_wire_batch_num != None else "")
		self.page.leBatchWedge   .setText(self.module.wedge_batch     if self.module.wedge_batch     != None else "")

		# Back wirebonding
		self.page.ckWirebondingBack.setChecked(       False if self.module.back_bonds          is None else self.module.back_bonds         )
		self.page.ckWirebondsInspectedBack.setChecked(False if self.module.back_bond_inspxn  is None else self.module.back_bond_inspxn )
		if not self.module.back_bonds_user in self.index_users_wb.keys() and not self.module.back_bonds_user is None:
			# Insertion user was deleted from user page...just add user to the dropdown
			self.index_users[self.module.back_bonds_user] = max(self.index_users_wb.values()) + 1
			self.page.cbWirebondingUserBack.addItem(self.module.back_bonds_user)
		self.page.cbWirebondingUserBack.setCurrentIndex(self.index_users_wb.get(self.module.back_bonds_user, -1))
		if not self.module.back_repair_user in self.index_users_wb.keys() and not self.module.back_repair_user is None:
			self.index_users[self.module.back_repair_user] = max(self.index_users_wb.values()) + 1
			self.page.cbWirebondsRepairedUserBack.addItem(self.module.back_repair_user)
		self.page.cbWirebondsRepairedUserBack.setCurrentIndex(self.index_users_wb.get(self.module.back_repair_user, -1))

		self.page.sbUnbondedChannelsBack.setValue(self.module.back_unbonded if self.module.back_unbonded else 0)

		# Back encapsulation
		self.page.ckEncapsulationBack.setChecked(False if self.module.back_encap    is None else self.module.back_encap)
		if not self.module.back_encap_user in self.index_users_eb.keys() and not self.module.back_encap_user is None:
			self.index_users[self.module.back_encap_user] = max(self.index_users_eb.values()) + 1
			self.page.cbEncapsulationUserBack.addItem(self.module.back_encap_user)
		self.page.cbEncapsulationUserBack.setCurrentIndex(self.index_users_eb.get(self.module.back_encap_user, -1))
		self.page.cbEncapsulationInspectionBack.setCurrentIndex(INDEX_INSPECTION.get(self.module.back_encap_inspxn,-1))
		times_to_set = [(self.module.back_encap_cure_start, self.page.dtCureStartBack),
						(self.module.back_encap_cure_stop,  self.page.dtCureStopBack),
						(self.module.front_encap_cure_start,self.page.dtCureStartFront),
						(self.module.front_encap_cure_stop, self.page.dtCureStopFront)]
		for st, dt in times_to_set:
			if st is None:
				dt.setDate(QtCore.QDate(*NO_DATE))
				dt.setTime(QtCore.QTime(0,0,0))
			else:
				tm = datetime.datetime.strptime(st, "%Y-%m-%d %H:%M:%S%z")
				localtime = tm.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
				dat = QtCore.QDate(localtime.year, localtime.month, localtime.day)
				tim = QtCore.QTime(localtime.hour, localtime.minute, localtime.second)
				dt.setDate(dat)
				dt.setTime(tim)

		# test bonds
		self.page.ckTestBonds.setChecked(False if self.module.is_test_bond_module is None else self.module.is_test_bond_module)
		if not self.module.bond_pull_user in self.index_users_tb.keys() and not self.module.bond_pull_user is None:
			self.index_users[self.module.bond_pull_user] = max(self.index_users_tb.values()) + 1
			self.page.cbTestBondsPulledUser.addItem(self.module.bond_pull_user)
		self.page.cbTestBondsPulledUser.setCurrentIndex(self.index_users_tb.get(self.module.bond_pull_user, -1))
		self.page.dsbBondPullAvg.setValue( -1 if self.module.bond_pull_avg is None else self.module.bond_pull_avg )
		self.page.dsbBondPullStd.setValue( -1 if self.module.bond_pull_stddev is None else self.module.bond_pull_stddev )

		# Front wirebonding
		self.page.ckWirebondingFront.setChecked(       False if self.module.front_bonds           is None else self.module.front_bonds)
		self.page.ckWirebondsInspectedFront.setChecked(False if self.module.front_bond_inspxn is None else self.module.front_bond_inspxn )
		self.page.pteUnbondedChannelsFront.setPlainText(        "" if self.module.front_unbonded is None \
		                                   else SITE_SEP.join([str(c) for c in self.module.front_unbonded]))
		if not self.module.front_bonds_user in self.index_users_wf.keys() and not self.module.front_bonds_user is None:
			self.index_users[self.module.front_bonds_user] = max(self.index_users_wf.values()) + 1
			self.page.cbWirebondingUserFront.addItem(self.module.front_bonds_user)
		self.page.cbWirebondingUserFront.setCurrentIndex(self.index_users_wf.get(self.module.front_bonds_user, -1))
		if not self.module.front_repair_user in self.index_users_wf.keys() and not self.module.front_repair_user is None:
			self.index_users[self.module.wirebons_repaired_user_front] = max(self.index_users_wf.values()) + 1
			self.page.cbWirebondsRepairedUserFront.addItem(self.module.front_repair_user)
		self.page.cbWirebondsRepairedUserFront.setCurrentIndex(self.index_users_wf.get(self.module.front_repair_user, -1))

		# Front encapsulation
		self.page.ckEncapsulationFront.setChecked(False if self.module.front_encap    is None else self.module.front_encap)
		if not self.module.front_encap_user in self.index_users_ef.keys() and not self.module.front_encap_user is None:
			self.index_users[self.module.front_encap_user] = max(self.index_users_ef.values()) + 1
			self.page.cbEncapsulationUserFront.addItem(self.module.front_encap_user)
		self.page.cbEncapsulationUserFront.setCurrentIndex(self.index_users_ef.get(self.module.front_encap_user, -1))
		self.page.cbEncapsulationInspectionFront.setCurrentIndex(INDEX_INSPECTION.get(self.module.front_encap_inspxn,-1))
		# NOTE:  Times covered above

		#CuringAgent wirebonding qualification
		if not self.module.final_inspxn_user in self.index_users_fi.keys() and not self.module.final_inspxn_user is None:
			self.index_users[self.module.final_inspxn_user] = max(self.index_users_fi.values()) + 1
			self.page.cbWirebondingFinalInspectionUser.addItem(self.module.final_inspxn_user)
		self.page.cbWirebondingFinalInspectionUser.setCurrentIndex(self.index_users_fi.get(self.module.final_inspxn_user, -1))
		self.page.cbWirebondingFinalInspectionOK.setCurrentIndex(INDEX_INSPECTION.get(self.module.final_inspxn_ok,-1))

		self.updateElements()


	@enforce_mode(['view','editing','searching'])
	def updateElements(self):
		module_exists   = self.module_exists

		mode_view      = self.mode == 'view'
		mode_editing   = self.mode == 'editing'
		mode_searching = self.mode == 'searching'

		self.setMainSwitchingEnabled(mode_view) 
		self.page.leID.setReadOnly(not mode_view)

		self.page.pbEdit  .setEnabled( mode_view )
		self.page.pbSave  .setEnabled( mode_editing   )
		self.page.pbCancel.setEnabled( mode_editing   )

		# characteristics
		self.page.dWirebondingBack.setReadOnly(  not mode_editing )
		self.page.dWirebondingFront.setReadOnly( not mode_editing )

		# comments
		self.page.pbDeleteComment.setEnabled(mode_editing)
		self.page.pbAddComment.setEnabled(   mode_editing)
		self.page.pteWriteComment.setEnabled(mode_editing)

		self.page.pbDeleteCommentEncap.setEnabled(mode_editing)
		self.page.pbAddCommentEncap.setEnabled(   mode_editing)
		self.page.pteWriteCommentEncap.setEnabled(mode_editing)

		# pre-wirebonding qualification
		self.page.cbPreinspection.setEnabled(     mode_editing )
		self.page.leBatchSylgard .setReadOnly(not mode_editing )
		self.page.leBatchBondWire.setReadOnly(not mode_editing )
		self.page.leBatchWedge   .setReadOnly(not mode_editing )

		# back wirebonding
		self.page.ckWirebondingBack.setEnabled(          mode_editing )
		self.page.ckWirebondsInspectedBack.setEnabled(   mode_editing )
		self.page.cbWirebondingUserBack.setEnabled(      mode_editing )
		self.page.cbWirebondsRepairedUserBack.setEnabled(mode_editing )
		self.page.sbUnbondedChannelsBack.setReadOnly(not mode_editing )

		# back encapsulation
		self.page.ckEncapsulationBack.setEnabled(           mode_editing )
		self.page.cbEncapsulationUserBack.setEnabled(       mode_editing )
		self.page.cbEncapsulationInspectionBack.setEnabled( mode_editing )
		self.page.dtCureStartBack.setReadOnly(          not mode_editing )
		self.page.dtCureStopBack.setReadOnly(           not mode_editing )
		self.page.pbCureStartNowBack.setEnabled(            mode_editing )
		self.page.pbCureStopNowBack.setEnabled(             mode_editing )

		# test bonds
		self.page.ckTestBonds.setEnabled(           mode_editing )
		self.page.cbTestBondsPulledUser.setEnabled( mode_editing )
		self.page.dsbBondPullAvg.setReadOnly(   not mode_editing )
		self.page.dsbBondPullStd.setReadOnly(   not mode_editing )

		# front wirebonding
		self.page.ckWirebondingFront.setEnabled(           mode_editing )
		self.page.ckWirebondsInspectedFront.setEnabled(    mode_editing )
		self.page.cbWirebondingUserFront.setEnabled(       mode_editing )
		self.page.cbWirebondsRepairedUserFront.setEnabled( mode_editing )
		self.page.pteWirebondingChannelsSkipFront.setReadOnly(not mode_editing)
		self.page.pteUnbondedChannelsFront.setReadOnly(not mode_editing )

		# front encapsulation
		self.page.ckEncapsulationFront.setEnabled(           mode_editing )
		self.page.cbEncapsulationUserFront.setEnabled(       mode_editing )
		self.page.cbEncapsulationInspectionFront.setEnabled( mode_editing )
		self.page.dtCureStartFront.setReadOnly(          not mode_editing )
		self.page.dtCureStopFront.setReadOnly(           not mode_editing )
		self.page.pbCureStartNowFront.setEnabled(            mode_editing )
		self.page.pbCureStopNowFront.setEnabled(             mode_editing )

		# wirebonding qualification
		self.page.cbWirebondingFinalInspectionUser.setEnabled( mode_editing )
		self.page.cbWirebondingFinalInspectionOK.setEnabled(   mode_editing )

		# search page:
		self.page.pbGoBatchSylgard.setEnabled( mode_editing or (mode_view and self.page.leBatchSylgard.text() != ""))
		self.page.pbGoBatchBondWire.setEnabled(mode_editing or (mode_view and self.page.leBatchBondWire.text() != ""))
		self.page.pbGoBatchWedge.setEnabled(   mode_editing or (mode_view and self.page.leBatchWedge.text() != ""))

		self.page.pbAddPart     .setEnabled(mode_searching)
		self.page.pbCancelSearch.setEnabled(mode_searching)

		# NEW:  Update pb's based on search result
		syl = self.page.leBatchSylgard.text()
		self.page.pbGoBatchSylgard.setText("select" if syl == "" else "go to")
		bnd = self.page.leBatchBondWire.text()
		self.page.pbGoBatchBondWire.setText("select" if bnd == "" else "go to")
		wdg = self.page.leBatchWedge.text()
		self.page.pbGoBatchWedge.setText("select" if wdg == "" else "go to")


	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		tmp_module = parts.module()
		tmp_ID = self.page.leID.text()
		tmp_exists = tmp_module.load(tmp_ID)
		if not tmp_exists:
			self.page.leStatus.setText("does not exist")
		else:
			self.page.leStatus.setText("editing")
			self.module = tmp_module
			self.mode = 'editing'
			self.update_info()

	@enforce_mode('editing')
	def cancelEditing(self,*args,**kwargs):
		self.page.leStatus.setText("")
		self.mode = 'view'
		self.update_info()

	@enforce_mode('editing')
	def saveEditing(self,*args,**kwargs):
		self.page.leStatus.setText("saved")
		# First, check text boxes for errors; do nothing if found
		self.page.leErrors.clear()
		pteList = {
				   "skip_front":self.page.pteWirebondingChannelsSkipFront,
				   "unbonded_front":self.page.pteUnbondedChannelsFront
				  }
		pteErrs = []
		for name, pte in pteList.items():
			if not site_format_check(pte.toPlainText()):
				pteErrs.append(name)
		# Check batch errors:  existence, emptiness, expiration
		tmp_sylgard = supplies.batch_sylgard()
		if not tmp_sylgard.load(self.page.leBatchSylgard.text()):
			pteErrs.append("Sylgard DNE")
		else:
			if tmp_sylgard.is_expired:  pteErrs.append("Sylgard expired")
			if tmp_sylgard.is_empty:    pteErrs.append("Sylgard empty")
		tmp_bond_wire = supplies.batch_bond_wire()
		if not tmp_bond_wire.load(self.page.leBatchBondWire.text()):
			pteErrs.append("Bond wire DNE")
		else:
			if tmp_bond_wire.is_expired:  pteErrs.append("Bond wire expired")
			if tmp_bond_wire.is_empty:    pteErrs.append("Bond wire empty")
		tmp_wedge = supplies.batch_wedge()
		if not tmp_wedge.load(self.page.leBatchWedge.text()):
			pteErrs.append("Wedge DNE")
		else:
			if tmp_wedge.is_expired:  pteErrs.append("Wedge expired")
			if tmp_wedge.is_empty:    pteErrs.append("Wedge empty")

		if len(pteErrs) > 0:
			self.page.leErrors.setText("Error:  {}".format(', '.join(pteErrs)))
			return


		# characteristics

		datew = self.page.dWirebondingBack.date().toPyDate()
		self.module.wirebonding_date_back  = str(datew)
		datew = self.page.dWirebondingFront.date().toPyDate()
		self.module.wirebonding_date_front = str(datew)

		# comments
		num_comments = self.page.listComments.count()
		self.module.wirebond_comments = [self.page.listComments.item(i).text() for i in range(num_comments)]

		# Commented for now
		num_comments_encap = self.page.listCommentsEncap.count()
		self.module.encapsulation_comments = [self.page.listCommentsEncap.item(i).text() for i in range(num_comments_encap)]

		# pre-wirebonding qualification
		self.module.pre_inspection  = str(self.page.cbPreinspection.currentText()  ) if str(self.page.cbPreinspection.currentText()  ) else None
		self.module.sylgard_batch = self.page.leBatchSylgard.text()  if self.page.leBatchSylgard.text()  != "" else None
		self.module.bond_wire_batch_num = self.page.leBatchBondWire.text() if self.page.leBatchBondWire.text() != "" else None
		self.module.wedge_batch = self.page.leBatchWedge.text()    if self.page.leBatchWedge.text()    != "" else None

		# back wirebonding
		self.module.back_bonds              = self.page.ckWirebondingBack.isChecked()
		self.module.back_bond_inspxn      = self.page.ckWirebondsInspectedBack.isChecked()
		self.module.back_bonds_user         = str(self.page.cbWirebondingUserBack.currentText()      ) if str(self.page.cbWirebondingUserBack.currentText()      ) else None
		self.module.back_repair_user  = str(self.page.cbWirebondsRepairedUserBack.currentText()) if str(self.page.cbWirebondsRepairedUserBack.currentText()) else None
		self.module.back_unbonded = self.page.sbUnbondedChannelsBack.value()

		# back encapsulation
		self.module.back_encap            = self.page.ckEncapsulationBack.isChecked()
		self.module.back_encap_user       = str(self.page.cbEncapsulationUserBack.currentText()             ) if str(self.page.cbEncapsulationUserBack.currentText()             ) else None
		self.module.back_encap_inspxn = str(self.page.cbEncapsulationInspectionBack.currentText()) if str(self.page.cbEncapsulationInspectionBack.currentText()) else None
		if self.page.dtCureStartBack.date().year() == NO_DATE[0]:
			self.module.back_encap_cure_start = None
		else:
			pydt = self.page.dtCureStartBack.dateTime().toPyDateTime().astimezone(datetime.timezone.utc)
			self.module.back_encap_cure_start = str(pydt)
		if self.page.dtCureStopBack.date().year() == NO_DATE[0]:
			self.module.back_encap_cure_stop = None
		else:
			pydt = self.page.dtCureStopBack.dateTime().toPyDateTime().astimezone(datetime.timezone.utc)
			self.module.back_encap_cure_stop = str(pydt)

		# test bonds
		self.module.is_test_bond_module             = self.page.ckTestBonds.isChecked()
		self.module.bond_pull_user = str(self.page.cbTestBondsPulledUser.currentText()      ) if str(self.page.cbTestBondsPulledUser.currentText()      ) else None
		self.module.bond_pull_avg = self.page.dsbBondPullAvg.value() if self.page.dsbBondPullAvg.value() >= 0 else None
		self.module.bond_pull_stddev = self.page.dsbBondPullStd.value() if self.page.dsbBondPullStd.value() >= 0 else None

		# front wirebonding
		self.module.front_bonds              = self.page.ckWirebondingFront.isChecked()
		self.module.front_bond_inspxn      = self.page.ckWirebondsInspectedFront.isChecked()
		self.module.front_bonds_user         = str(self.page.cbWirebondingUserFront.currentText()      ) if str(self.page.cbWirebondingUserFront.currentText()      ) else None
		self.module.front_repair_user  = str(self.page.cbWirebondsRepairedUserFront.currentText()) if str(self.page.cbWirebondsRepairedUserFront.currentText()) else None
		self.module.front_unbonded = separate_sites(str(self.page.pteUnbondedChannelsFront.toPlainText()       )) if self.page.pteUnbondedChannelsFront.toPlainText()        else None
		self.module.front_skip       = separate_sites(str(self.page.pteWirebondingChannelsSkipFront.toPlainText())) if self.page.pteWirebondingChannelsSkipFront.toPlainText() else None

		# front encapsulation
		self.module.front_encap            = self.page.ckEncapsulationFront.isChecked()
		self.module.front_encap_user       = str(self.page.cbEncapsulationUserFront.currentText()             ) if str(self.page.cbEncapsulationUserFront.currentText()             ) else None
		self.module.front_encap_inspxn = str(self.page.cbEncapsulationInspectionFront.currentText()) if str(self.page.cbEncapsulationInspectionFront.currentText()) else None
		pydt = self.page.dtCureStartFront.dateTime().toPyDateTime().astimezone(datetime.timezone.utc)
		self.module.front_encap_cure_start = str(pydt)
		pydt = self.page.dtCureStopFront.dateTime().toPyDateTime().astimezone(datetime.timezone.utc)
		self.module.front_encap_cure_stop = str(pydt)

		# wirebonding qualification
		self.module.final_inspxn_user = str(self.page.cbWirebondingFinalInspectionUser.currentText()     ) if str(self.page.cbWirebondingFinalInspectionUser.currentText()     ) else None
		self.module.final_inspxn_ok   = str(self.page.cbWirebondingFinalInspectionOK.currentText()) if str(self.page.cbWirebondingFinalInspectionOK.currentText()) else None

		self.module.save()
		self.mode = 'view'
		self.update_info()

		self.xmlModList.append(self.module.ID)


	@enforce_mode('editing')
	def loadBatchSylgard(self, *args, **kwargs):
		self.batch_sylgard.load(self.page.leBatchSylgard.text())

	@enforce_mode('editing')
	def loadBatchBondWire(self, *args, **kwargs):
		self.batch_bond_wire.load(self.page.leBatchBondWire.text())

	@enforce_mode('editing')
	def loadBatchWedge(self, *args, **kwargs):
		self.batch_wedge.load(self.page.leBatchWedge.text())


	def doSearch(self,*args,**kwargs):
		tmp_class = getattr(parts, self.search_part, None)
		if tmp_class is None:
			tmp_class = getattr(supplies, self.search_part)
			tmp_part = tmp_class()

		# Search local-only parts:  open part file
		part_file_name = os.sep.join([ fm.DATADIR, 'partlist', self.search_part+'s.json' ])
		with open(part_file_name, 'r') as opfl:
			part_list = json.load(opfl)

		for part_id, date in part_list.items():
			# If already added by DB query, skip:
			if len(self.page.lwPartList.findItems("{} {}".format(self.search_part, part_id), \
                                                  QtCore.Qt.MatchExactly)) > 0:
				continue
			self.page.lwPartList.addItem("{} {}".format(self.search_part, part_id))
			if self.search_part == 'batch_sylgard':
				self.loadBatchSylgard()
			elif self.search_part == 'batch_bond_wire':
				self.loadBatchBondWire()
			elif self.search_part == 'batch_wedge':
				self.loadBatchWedge()

		self.page.leSearchStatus.setText("Searched: "+self.search_part)
		self.mode = 'searching'
		self.updateElements()

	def finishSearch(self,*args,**kwargs):
		row = self.page.lwPartList.currentRow()
		if self.page.lwPartList.item(row) is None:
			return
		name = self.page.lwPartList.item(row).text().split()[1]
		if self.search_part == "batch_sylgard":
			le_to_fill = self.page.leBatchSylgard
		elif self.search_part == "batch_bond_wire":
			le_to_fill = self.page.leBatchBondWire
		elif self.search_part == "batch_wedge":
			le_to_fill = self.page.leBatchWedge
		le_to_fill.setText(name)

		self.page.lwPartList.clear()
		self.page.leSearchStatus.clear()
		self.mode = 'editing'
		if self.search_part == "batch_sylgard":
			self.loadBatchSylgard()
		elif self.search_part == "batch_bond_wire":
			self.loadBatchBondWire()
		elif self.search_part == "batch_wedge":
			self.loadBatchWedge()
		self.updateElements()

	def cancelSearch(self,*args,**kwargs):
		self.page.lwPartList.clear()
		self.page.leSearchStatus.clear()
		self.mode = 'editing'
		self.updateElements()


	def goBatchSylgard(self,*args,**kwargs):
		batch_sylgard = self.page.leBatchSylgard.text()
		if batch_sylgard != "":
			self.setUIPage('Supplies',batch_sylgard=batch_sylgard)
		else:
			self.mode = 'searching'
			self.search_part = 'batch_sylgard'
			self.doSearch()

	def goBatchBondWire(self,*args,**kwargs):
		batch_bond_wire = self.page.leBatchBondWire.text()
		if batch_bond_wire != "":
			self.setUIPage('Supplies',batch_bond_wire=batch_bond_wire)
		else:
			self.mode = 'searching'
			self.search_part = 'batch_bond_wire'
			self.doSearch()

	def goBatchWedge(self,*args,**kwargs):
		batch_wedge = self.page.leBatchWedge.text()
		if batch_wedge != "":
			self.setUIPage('Supplies',batch_wedge=batch_wedge)
		else:
			self.mode = 'searching'
			self.search_part = 'batch_wedge'
			self.doSearch()



	def xmlModified(self):
		return self.xmlModList

	def xmlModifiedReset(self):
		self.xmlModList = []


	@enforce_mode('editing')
	def cureStartNowBack(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStartBack.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStartBack.setTime(QtCore.QTime(*localtime[3:6]))

	@enforce_mode('editing')
	def cureStopNowBack(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStopBack.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStopBack.setTime(QtCore.QTime(*localtime[3:6]))

	@enforce_mode('editing')
	def cureStartNowFront(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStartFront.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStartFront.setTime(QtCore.QTime(*localtime[3:6]))

	@enforce_mode('editing')
	def cureStopNowFront(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStopFront.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStopFront.setTime(QtCore.QTime(*localtime[3:6]))


	@enforce_mode('editing')
	def deleteComment(self,*args,**kwargs):
		row = self.page.listComments.currentRow()
		if row >= 0:
			self.page.listComments.takeItem(row)

	@enforce_mode('editing')
	def addComment(self,*args,**kwargs):
		text = str(self.page.pteWriteComment.toPlainText())
		if text:
			self.page.listComments.addItem(text)
			self.page.pteWriteComment.clear()

	@enforce_mode('editing')
	def deleteCommentEncap(self,*args,**kwargs):
		row = self.page.listCommentsEncap.currentRow()
		if row >= 0:
			self.page.listCommentsEncap.takeItem(row)

	@enforce_mode('editing')
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
			self.page.sbID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
