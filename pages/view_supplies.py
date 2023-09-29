from PyQt5 import QtCore
from filemanager import supplies
import time

PAGE_NAME = "view_supplies"
#OBJECTTYPE = "sensor_step"
DEBUG = False

class simple_fsobj_vc(object):
	def __init__(self,
		fsobj,
		sbID,  # NOTE:  Now can be a le instead!
		dReceived,
		dExpires,
		ckIsEmpty,
		pbEditNew,
		pbSave,
		pbCancel,
		listComments,
		pteWriteComment,
		pbDeleteComment,
		pbAddComment,
		leCuring=None,
		ckNoExpiry=None
		):

		self.fsobj_exists    = None
		self.fsobj           = fsobj
		self.sbID            = sbID
		self.dReceived       = dReceived
		self.dExpires        = dExpires
		self.ckIsEmpty       = ckIsEmpty
		self.pbEditNew       = pbEditNew
		self.pbSave          = pbSave
		self.pbCancel        = pbCancel
		self.listComments    = listComments
		self.pteWriteComment = pteWriteComment
		self.pbDeleteComment = pbDeleteComment
		self.pbAddComment    = pbAddComment
		self.leCuring        = leCuring  # None if nonexistent
		self.ckNoExpiry      = ckNoExpiry

	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			if type(self.sbID).__name__ == 'QLineEdit':
				ID = self.sbID.text()
			else:
				ID = self.sbID.value()
		else:
			if type(self.sbID).__name__ == 'QLineEdit':
				self.sbID.setText(ID)
			else:
				self.sbID.setValue(ID)
		self.fsobj_exists = self.fsobj.load(ID)

		if self.fsobj_exists:
			self.pbEditNew.setText("edit")

			if self.dReceived != None:
				# Load date:
				ydm = self.fsobj.date_received.split('-')
				# Note:  QDate constructor format is ymd
				self.dReceived.setDate(QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1])))  #*self.fsobj.date_received))
				ydm = self.fsobj.date_expires.split('-')
				self.dExpires .setDate(QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1])))   #*self.fsobj.date_expires))

			self.ckIsEmpty.setChecked(self.fsobj.is_empty)
			if not self.ckNoExpiry is None:
				self.ckNoExpiry.setChecked(self.fsobj.no_expiry if not self.fsobj.no_expiry is None else False)

			if not self.leCuring is None:
				self.leCuring.setText(self.fsobj.curing_agent)

			self.listComments.clear()
			for comment in self.fsobj.comments:
				self.listComments.addItem(comment)
			self.pteWriteComment.clear()

		else:
			self.pbEditNew.setText("new")
			localtime = time.localtime()
			if self.dReceived != None:
				localtime = time.localtime()
				self.dReceived.setDate(QtCore.QDate(*localtime[0:3]))
				self.dExpires.setDate(QtCore.QDate(*localtime[0:3]))

			self.ckIsEmpty.setChecked(False)
			if not self.leCuring is None:
				self.leCuring.clear()

			self.listComments.clear()
			self.pteWriteComment.clear()

	def start_editing(self,*args,**kwargs):
		if self.sbID.text() == '':  return False
		if not self.fsobj_exists:
			if type(self.sbID).__name__ == 'QLineEdit':
				self.fsobj.new(self.sbID.text())
			else:
				self.fsobj.new(self.sbID.value())
			# if creating new part, auto-set date to current
			localtime = time.localtime()
			self.dReceived.setDate(QtCore.QDate(*localtime[0:3]))
			self.dExpires.setDate(QtCore.QDate(*localtime[0:3]))

		return True

	def cancel_editing(self,*args,**kwargs):
		self.update_info()

	def save_editing(self,*args,**kwargs):
		comments = []
		for i in range(self.listComments.count()):
			comments.append(self.listComments.item(i).text())
		self.fsobj.comments = comments
		
		if self.dReceived != None:
			dateR = self.dReceived.date()
			self.fsobj.date_received = "{}-{}-{}".format(dateR.month(), dateR.day(), dateR.year())
			dateE = self.dExpires.date()
			self.fsobj.date_expires  = "{}-{}-{}".format(dateE.month(), dateE.day(), dateE.year())
		if self.ckNoExpiry != None:
			self.fsobj.no_expiry = self.ckNoExpiry.isChecked()

		self.fsobj.is_empty = self.ckIsEmpty.isChecked()
		if not self.leCuring is None:
			if self.leCuring.text() != '':  self.fsobj.curing_agent = self.leCuring.text()
			else:  self.fsobj.curing_agent = None

		self.fsobj.save()
		self.update_info()

	def add_comment(self,*args,**kwargs):
		text = self.pteWriteComment.toPlainText()
		if text:
			self.listComments.addItem(text)
			self.pteWriteComment.clear()

	def delete_comment(self,*args,**kwargs):
		index = self.listComments.currentRow()
		if index >= 0:
			self.listComments.takeItem(index)

	def update_expiry(self,*args,**kwargs):
		self.fsobj.no_expiry = self.ckNoExpiry.isChecked()
		self.dExpires.setEnabled(not self.fsobj.no_expiry)


class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.batch_araldite = simple_fsobj_vc(
			supplies.batch_araldite(),
			self.page.leAralditeID,
			self.page.dAralditeReceived,
			self.page.dAralditeExpires,
			self.page.ckIsAralditeEmpty,
			self.page.pbAralditeEditNew,
			self.page.pbAralditeSave,
			self.page.pbAralditeCancel,
			self.page.listAralditeComments,
			self.page.pteAralditeWriteComment,
			self.page.pbAralditeDeleteComment,
			self.page.pbAralditeAddComment,
			)
		
		self.batch_wedge = simple_fsobj_vc(
			supplies.batch_wedge(),
			self.page.leWedgeID,
			self.page.dWedgeReceived,
			self.page.dWedgeExpires,
			self.page.ckIsWedgeEmpty,
			self.page.pbWedgeEditNew,
			self.page.pbWedgeSave,
			self.page.pbWedgeCancel,
			self.page.listWedgeComments,
			self.page.pteWedgeWriteComment,
			self.page.pbWedgeDeleteComment,
			self.page.pbWedgeAddComment,
			)

		self.batch_sylgard = simple_fsobj_vc(
			supplies.batch_sylgard(),
			self.page.leSylgardID,
			self.page.dSylgardReceived,
			self.page.dSylgardExpires,
			self.page.ckIsSylgardEmpty,
			self.page.pbSylgardEditNew,
			self.page.pbSylgardSave,
			self.page.pbSylgardCancel,
			self.page.listSylgardComments,
			self.page.pteSylgardWriteComment,
			self.page.pbSylgardDeleteComment,
			self.page.pbSylgardAddComment,
			self.page.leSylgardCuring,
			)

		self.batch_bond_wire = simple_fsobj_vc(
			supplies.batch_bond_wire(),
			self.page.leBondWireID,
			self.page.dBondWireReceived,
			self.page.dBondWireExpires,
			self.page.ckIsBondWireEmpty,
			self.page.pbBondWireEditNew,
			self.page.pbBondWireSave,
			self.page.pbBondWireCancel,
			self.page.listBondWireComments,
			self.page.pteBondWireWriteComment,
			self.page.pbBondWireDeleteComment,
			self.page.pbBondWireAddComment,
			)

		self.batch_tape_50 = simple_fsobj_vc(
			supplies.batch_tape_50(),
			self.page.leTape50ID,
			self.page.dTape50Received,
			self.page.dTape50Expires,
			self.page.ckIsTape50Empty,
			self.page.pbTape50EditNew,
			self.page.pbTape50Save,
			self.page.pbTape50Cancel,
			self.page.listTape50Comments,
			self.page.pteTape50WriteComment,
			self.page.pbTape50DeleteComment,
			self.page.pbTape50AddComment,
			ckNoExpiry=self.page.ckNoExpiry50,
			)

		self.batch_tape_120 = simple_fsobj_vc(
			supplies.batch_tape_120(),
			self.page.leTape120ID,
			self.page.dTape120Received,
			self.page.dTape120Expires,
			self.page.ckIsTape120Empty,
			self.page.pbTape120EditNew,
			self.page.pbTape120Save,
			self.page.pbTape120Cancel,
			self.page.listTape120Comments,
			self.page.pteTape120WriteComment,
			self.page.pbTape120DeleteComment,
			self.page.pbTape120AddComment,
			ckNoExpiry=self.page.ckNoExpiry120,
			)

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
		self.rig()
		self.mode = 'view'
		self.update_elements()
		self.update_info()
		print("{} setup completed".format(PAGE_NAME))

	@enforce_mode('setup')
	def rig(self):
		self.page.leAralditeID.textChanged.connect(self.update_info_batch_araldite)
		self.page.leWedgeID.textChanged.connect(self.update_info_batch_wedge)
		self.page.leSylgardID.textChanged.connect(self.update_info_batch_sylgard)
		self.page.leBondWireID.textChanged.connect(self.update_info_batch_bond_wire)
		self.page.leTape50ID.textChanged.connect(self.update_info_batch_tape_50)
		self.page.leTape120ID.textChanged.connect(self.update_info_batch_tape_120)

		self.page.pbAralditeEditNew.clicked.connect(self.start_editing_batch_araldite)
		self.page.pbWedgeEditNew.clicked.connect(self.start_editing_batch_wedge)
		self.page.pbSylgardEditNew.clicked.connect(self.start_editing_batch_sylgard)
		self.page.pbBondWireEditNew.clicked.connect(self.start_editing_batch_bond_wire)
		self.page.pbTape50EditNew.clicked.connect(self.start_editing_batch_tape_50)
		self.page.pbTape120EditNew.clicked.connect(self.start_editing_batch_tape_120)

		self.page.pbAralditeSave.clicked.connect(self.save_editing_batch_araldite)
		self.page.pbWedgeSave.clicked.connect(self.save_editing_batch_wedge)
		self.page.pbSylgardSave.clicked.connect(self.save_editing_batch_sylgard)
		self.page.pbBondWireSave.clicked.connect(self.save_editing_batch_bond_wire)
		self.page.pbTape50Save.clicked.connect(self.save_editing_batch_tape_50)
		self.page.pbTape120Save.clicked.connect(self.save_editing_batch_tape_120)
		
		self.page.pbAralditeCancel.clicked.connect(self.cancel_editing_batch_araldite)
		self.page.pbWedgeCancel.clicked.connect(self.cancel_editing_batch_wedge)
		self.page.pbSylgardCancel.clicked.connect(self.cancel_editing_batch_sylgard)
		self.page.pbBondWireCancel.clicked.connect(self.cancel_editing_batch_bond_wire)
		self.page.pbTape50Cancel.clicked.connect(self.cancel_editing_batch_tape_50)
		self.page.pbTape120Cancel.clicked.connect(self.cancel_editing_batch_tape_120)

		self.page.pbAralditeDeleteComment.clicked.connect(self.delete_comment_batch_araldite)
		self.page.pbWedgeDeleteComment.clicked.connect(self.delete_comment_batch_wedge)
		self.page.pbSylgardDeleteComment.clicked.connect(self.delete_comment_batch_sylgard)
		self.page.pbBondWireDeleteComment.clicked.connect(self.delete_comment_batch_bond_wire)
		self.page.pbTape50DeleteComment.clicked.connect(self.delete_comment_batch_tape_50)
		self.page.pbTape120DeleteComment.clicked.connect(self.delete_comment_batch_tape_120)

		self.page.pbAralditeAddComment.clicked.connect(self.add_comment_batch_araldite)
		self.page.pbWedgeAddComment.clicked.connect(self.add_comment_batch_wedge)
		self.page.pbSylgardAddComment.clicked.connect(self.add_comment_batch_sylgard)
		self.page.pbBondWireAddComment.clicked.connect(self.add_comment_batch_bond_wire)
		self.page.pbTape50AddComment.clicked.connect(self.add_comment_batch_tape_50)
		self.page.pbTape120AddComment.clicked.connect(self.add_comment_batch_tape_120)

		self.page.ckNoExpiry50.toggled.connect(self.update_expiry_50)
		self.page.ckNoExpiry120.toggled.connect(self.update_expiry_120)

	@enforce_mode(['view','editing_batch_wedge','editing_batch_sylgard','editing_batch_bond_wire',
                   'editing_batch_tape_50','editing_batch_tape_120'])
	def update_info_batch_araldite(self,ID=None,*args,**kwargs):
		self.batch_araldite.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_sylgard','editing_batch_bond_wire',
                   'editing_batch_tape_50','editing_batch_tape_120'])
	def update_info_batch_wedge(self,ID=None,*args,**kwargs):
		self.batch_wedge.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_wedge','editing_batch_bond_wire',
                   'editing_batch_tape_50','editing_batch_tape_120'])
	def update_info_batch_sylgard(self,ID=None,*args,**kwargs):
		self.batch_sylgard.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_wedge','editing_batch_sylgard',
                   'editing_batch_tape_50','editing_batch_tape_120'])
	def update_info_batch_bond_wire(self,ID=None,*args,**kwargs):
		self.batch_bond_wire.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_wedge','editing_batch_sylgard',
                   'editing_batch_bond_wire','editing_batch_tape_120'])
	def update_info_batch_tape_50(self,ID=None,*args,**kwargs):
		self.batch_tape_50.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_wedge','editing_batch_sylgard',
                   'editing_batch_bond_wire','editing_batch_tape_50'])
	def update_info_batch_tape_120(self,ID=None,*args,**kwargs):
		self.batch_tape_120.update_info(ID)

	def update_expiry_50(self,ID=None,*args,**kwargs):
		self.batch_tape_50.update_expiry()

	def update_expiry_120(self,ID=None,*args,**kwargs):
		self.batch_tape_120.update_expiry()


	@enforce_mode('view')
	def update_info(self,*args,**kwargs):
		self.update_info_batch_araldite()
		self.update_info_batch_wedge()
		self.update_info_batch_sylgard()
		self.update_info_batch_bond_wire()
		self.update_info_batch_tape_50()
		self.update_info_batch_tape_120()



	@enforce_mode(['view','editing_batch_araldite','editing_batch_wedge','editing_batch_sylgard','editing_batch_bond_wire',
                   'editing_batch_tape_50','editing_batch_tape_120'])
	def update_elements(self):
		mode_view                        = self.mode == 'view'
		mode_editing_batch_araldite      = self.mode == 'editing_batch_araldite'
		mode_editing_batch_wedge         = self.mode == 'editing_batch_wedge'
		mode_editing_batch_sylgard       = self.mode == 'editing_batch_sylgard'
		mode_editing_batch_bond_wire     = self.mode == 'editing_batch_bond_wire'
		mode_editing_batch_tape_50       = self.mode == 'editing_batch_tape_50'
		mode_editing_batch_tape_120      = self.mode == 'editing_batch_tape_120'
		self.setMainSwitchingEnabled(mode_view)

		self.page.leAralditeID.setEnabled(not mode_editing_batch_araldite)
		self.page.leWedgeID.setEnabled(not mode_editing_batch_wedge)
		self.page.leSylgardID.setEnabled(not mode_editing_batch_sylgard)
		self.page.leBondWireID.setEnabled(not mode_editing_batch_bond_wire)
		self.page.leTape50ID.setEnabled(not mode_editing_batch_tape_50)
		self.page.leTape120ID.setEnabled(not mode_editing_batch_tape_120)

		self.page.pbAralditeEditNew.setEnabled(mode_view)
		self.page.pbWedgeEditNew.setEnabled(mode_view)
		self.page.pbSylgardEditNew.setEnabled(mode_view)
		self.page.pbBondWireEditNew.setEnabled(mode_view)
		self.page.pbTape50EditNew.setEnabled(mode_view)
		self.page.pbTape120EditNew.setEnabled(mode_view)

		self.page.pbAralditeSave.setEnabled(mode_editing_batch_araldite)
		self.page.pbWedgeSave.setEnabled(mode_editing_batch_wedge)
		self.page.pbSylgardSave.setEnabled(mode_editing_batch_sylgard)
		self.page.pbBondWireSave.setEnabled(mode_editing_batch_bond_wire)
		self.page.pbTape50Save.setEnabled(mode_editing_batch_tape_50)
		self.page.pbTape120Save.setEnabled(mode_editing_batch_tape_120)

		self.page.pbAralditeCancel.setEnabled(mode_editing_batch_araldite)
		self.page.pbWedgeCancel.setEnabled(mode_editing_batch_wedge)
		self.page.pbSylgardCancel.setEnabled(mode_editing_batch_sylgard)
		self.page.pbBondWireCancel.setEnabled(mode_editing_batch_bond_wire)
		self.page.pbTape50Cancel.setEnabled(mode_editing_batch_tape_50)
		self.page.pbTape120Cancel.setEnabled(mode_editing_batch_tape_120)

		self.page.dAralditeReceived.setEnabled(mode_editing_batch_araldite)
		self.page.dWedgeReceived.setEnabled(mode_editing_batch_wedge)
		self.page.dSylgardReceived.setEnabled(mode_editing_batch_sylgard)
		self.page.dBondWireReceived.setEnabled(mode_editing_batch_bond_wire)
		self.page.dTape50Received.setEnabled(mode_editing_batch_tape_50)
		self.page.dTape120Received.setEnabled(mode_editing_batch_tape_120)

		self.page.dAralditeExpires.setEnabled(mode_editing_batch_araldite)
		self.page.dWedgeExpires.setEnabled(mode_editing_batch_wedge)
		self.page.dSylgardExpires.setEnabled(mode_editing_batch_sylgard)
		self.page.dBondWireExpires.setEnabled(mode_editing_batch_bond_wire)
		self.page.dTape50Expires.setEnabled(mode_editing_batch_tape_50 \
            and self.batch_tape_50.fsobj.no_expiry!=True)
		self.page.dTape120Expires.setEnabled(mode_editing_batch_tape_120 \
            and self.batch_tape_120.fsobj.no_expiry!=True)

		self.page.ckIsAralditeEmpty.setEnabled(mode_editing_batch_araldite)
		self.page.ckIsWedgeEmpty.setEnabled(mode_editing_batch_wedge)
		self.page.ckIsSylgardEmpty.setEnabled(mode_editing_batch_sylgard)
		self.page.ckIsBondWireEmpty.setEnabled(mode_editing_batch_bond_wire)
		self.page.ckIsTape50Empty.setEnabled(mode_editing_batch_tape_50)
		self.page.ckIsTape120Empty.setEnabled(mode_editing_batch_tape_120)

		self.page.leSylgardCuring.setEnabled(mode_editing_batch_sylgard)

		self.page.pbAralditeDeleteComment.setEnabled(mode_editing_batch_araldite)
		self.page.pbWedgeDeleteComment.setEnabled(mode_editing_batch_wedge)
		self.page.pbSylgardDeleteComment.setEnabled(mode_editing_batch_sylgard)
		self.page.pbBondWireDeleteComment.setEnabled(mode_editing_batch_bond_wire)
		self.page.pbTape50DeleteComment.setEnabled(mode_editing_batch_tape_50)
		self.page.pbTape120DeleteComment.setEnabled(mode_editing_batch_tape_120)

		self.page.pbAralditeAddComment.setEnabled(mode_editing_batch_araldite)
		self.page.pbWedgeAddComment.setEnabled(mode_editing_batch_wedge)
		self.page.pbSylgardAddComment.setEnabled(mode_editing_batch_sylgard)
		self.page.pbBondWireAddComment.setEnabled(mode_editing_batch_bond_wire)
		self.page.pbTape50AddComment.setEnabled(mode_editing_batch_tape_50)
		self.page.pbTape120AddComment.setEnabled(mode_editing_batch_tape_120)

		self.page.pteAralditeWriteComment.setEnabled(mode_editing_batch_araldite)
		self.page.pteWedgeWriteComment.setEnabled(mode_editing_batch_wedge)
		self.page.pteSylgardWriteComment.setEnabled(mode_editing_batch_sylgard)
		self.page.pteBondWireWriteComment.setEnabled(mode_editing_batch_bond_wire)
		self.page.pteTape50WriteComment.setEnabled(mode_editing_batch_tape_50)
		self.page.pteTape120WriteComment.setEnabled(mode_editing_batch_tape_120)

		self.page.ckNoExpiry50.setEnabled(mode_editing_batch_tape_50)
		self.page.ckNoExpiry120.setEnabled(mode_editing_batch_tape_120)


	@enforce_mode('view')
	def start_editing_batch_araldite(self,*args,**kwargs):
		if not self.batch_araldite.start_editing():  return
		self.mode = 'editing_batch_araldite'
		self.update_elements()

	@enforce_mode('editing_batch_araldite')
	def cancel_editing_batch_araldite(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.batch_araldite.update_info()

	@enforce_mode('editing_batch_araldite')
	def save_editing_batch_araldite(self,*args,**kwargs):
		self.batch_araldite.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_batch_araldite')
	def add_comment_batch_araldite(self,*args,**kwargs):
		self.batch_araldite.add_comment()

	@enforce_mode('editing_batch_araldite')
	def delete_comment_batch_araldite(self,*args,**kwargs):
		self.batch_araldite.delete_comment()

	
	@enforce_mode('view')
	def start_editing_batch_wedge(self,*args,**kwargs):
		if not self.batch_wedge.start_editing():  return
		self.mode = 'editing_batch_wedge'
		self.update_elements()

	@enforce_mode('editing_batch_wedge')
	def cancel_editing_batch_wedge(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.batch_wedge.update_info()

	@enforce_mode('editing_batch_wedge')
	def save_editing_batch_wedge(self,*args,**kwargs):
		self.batch_wedge.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_batch_wedge')
	def add_comment_batch_wedge(self,*args,**kwargs):
		self.batch_wedge.add_comment()

	@enforce_mode('editing_batch_wedge')
	def delete_comment_batch_wedge(self,*args,**kwargs):
		self.batch_wedge.delete_comment()
	

	@enforce_mode('view')
	def start_editing_batch_sylgard(self,*args,**kwargs):
		if not self.batch_sylgard.start_editing():  return
		self.mode = 'editing_batch_sylgard'
		self.update_elements()

	@enforce_mode('editing_batch_sylgard')
	def cancel_editing_batch_sylgard(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.batch_sylgard.update_info()

	@enforce_mode('editing_batch_sylgard')
	def save_editing_batch_sylgard(self,*args,**kwargs):
		self.batch_sylgard.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_batch_sylgard')
	def add_comment_batch_sylgard(self,*args,**kwargs):
		self.batch_sylgard.add_comment()

	@enforce_mode('editing_batch_sylgard')
	def delete_comment_batch_sylgard(self,*args,**kwargs):
		self.batch_sylgard.delete_comment()

	@enforce_mode('view')
	def start_editing_batch_bond_wire(self,*args,**kwargs):
		if not self.batch_bond_wire.start_editing():  return
		self.mode = 'editing_batch_bond_wire'
		self.update_elements()

	@enforce_mode('editing_batch_bond_wire')
	def cancel_editing_batch_bond_wire(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.batch_bond_wire.update_info()

	@enforce_mode('editing_batch_bond_wire')
	def save_editing_batch_bond_wire(self,*args,**kwargs):
		self.batch_bond_wire.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_batch_bond_wire')
	def add_comment_batch_bond_wire(self,*args,**kwargs):
		self.batch_bond_wire.add_comment()

	@enforce_mode('editing_batch_bond_wire')
	def delete_comment_batch_bond_wire(self,*args,**kwargs):
		self.batch_bond_wire.delete_comment()


	@enforce_mode('view')
	def start_editing_batch_tape_50(self,*args,**kwargs):
		if not self.batch_tape_50.start_editing():  return
		self.mode = 'editing_batch_tape_50'
		self.update_elements()

	@enforce_mode('editing_batch_tape_50')
	def cancel_editing_batch_tape_50(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.batch_tape_50.update_info()

	@enforce_mode('editing_batch_tape_50')
	def save_editing_batch_tape_50(self,*args,**kwargs):
		self.batch_tape_50.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_batch_tape_50')
	def add_comment_batch_tape_50(self,*args,**kwargs):
		self.batch_tape_50.add_comment()

	@enforce_mode('editing_batch_tape_50')
	def delete_comment_batch_tape_50(self,*args,**kwargs):
		self.batch_tape_50.delete_comment()


	@enforce_mode('view')
	def start_editing_batch_tape_120(self,*args,**kwargs):
		if not self.batch_tape_120.start_editing():  return
		self.mode = 'editing_batch_tape_120'
		self.update_elements()

	@enforce_mode('editing_batch_tape_120')
	def cancel_editing_batch_tape_120(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.batch_tape_120.update_info()

	@enforce_mode('editing_batch_tape_120')
	def save_editing_batch_tape_120(self,*args,**kwargs):
		self.batch_tape_120.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_batch_tape_120')
	def add_comment_batch_tape_120(self,*args,**kwargs):
		self.batch_tape_120.add_comment()

	@enforce_mode('editing_batch_tape_120')
	def delete_comment_batch_tape_120(self,*args,**kwargs):
		self.batch_tape_120.delete_comment()


	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		keys = kwargs.keys()

		if "batch_araldite" in keys:
			self.update_info_batch_araldite(kwargs['batch_araldite'])
		if "batch_wedge" in keys:
			self.update_info_batch_wedge(kwargs['batch_wedge'])
		if "batch_sylgard" in keys:
			self.update_info_batch_sylgard(kwargs['batch_sylgard'])
		if "batch_bond_wire" in keys:
			self.update_info_batch_bond_wire(kwargs['batch_bond_wire'])
		if "batch_tape_50" in keys:
			self.update_info_batch_tape_50(kwargs['batch_tape_50'])
		if "batch_tape_120" in keys:
			self.update_info_batch_tape_120(kwargs['batch_tape_120'])


	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
