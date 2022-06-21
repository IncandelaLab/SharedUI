from PyQt5 import QtCore

PAGE_NAME = "view_tooling"
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
		leCuring=None
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

			if not self.leCuring is None:
				self.leCuring.setText(self.fsobj.curing_agent)

			self.listComments.clear()
			for comment in self.fsobj.comments:
				self.listComments.addItem(comment)
			self.pteWriteComment.clear()

		else:
			self.pbEditNew.setText("new")
			if self.dReceived != None:
				self.dReceived.setDate(QtCore.QDate(2020,1,1))
				self.dExpires.setDate(QtCore.QDate(2020,1,1))

			self.ckIsEmpty.setChecked(False)
			if not self.leCuring is None:
				self.leCuring.clear()

			self.listComments.clear()
			self.pteWriteComment.clear()

	def start_editing(self,*args,**kwargs):
		if not self.fsobj_exists:
			if type(self.sbID).__name__ == 'QLineEdit':
				self.fsobj.new(self.sbID.text())
			else:
				self.fsobj.new(self.sbID.value())

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


class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		#self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.batch_araldite = simple_fsobj_vc(
			fm.batch_araldite(),
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
			fm.batch_wedge(),
			self.page.sbWedgeID,
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
			fm.batch_sylgard(),
			self.page.sbSylgardID,
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
			fm.batch_bond_wire(),
			self.page.sbBondWireID,
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
		self.page.sbWedgeID.valueChanged.connect(self.update_info_batch_wedge)
		self.page.sbSylgardID.valueChanged.connect(self.update_info_batch_sylgard)
		self.page.sbBondWireID.valueChanged.connect(self.update_info_batch_bond_wire)

		self.page.pbAralditeEditNew.clicked.connect(self.start_editing_batch_araldite)
		self.page.pbWedgeEditNew.clicked.connect(self.start_editing_batch_wedge)
		self.page.pbSylgardEditNew.clicked.connect(self.start_editing_batch_sylgard)
		self.page.pbBondWireEditNew.clicked.connect(self.start_editing_batch_bond_wire)

		self.page.pbAralditeSave.clicked.connect(self.save_editing_batch_araldite)
		self.page.pbWedgeSave.clicked.connect(self.save_editing_batch_wedge)
		self.page.pbSylgardSave.clicked.connect(self.save_editing_batch_sylgard)
		self.page.pbBondWireSave.clicked.connect(self.save_editing_batch_bond_wire)
		
		self.page.pbAralditeCancel.clicked.connect(self.cancel_editing_batch_araldite)
		self.page.pbWedgeCancel.clicked.connect(self.cancel_editing_batch_wedge)
		self.page.pbSylgardCancel.clicked.connect(self.cancel_editing_batch_sylgard)
		self.page.pbBondWireCancel.clicked.connect(self.cancel_editing_batch_bond_wire)

		self.page.pbAralditeDeleteComment.clicked.connect(self.delete_comment_batch_araldite)
		self.page.pbWedgeDeleteComment.clicked.connect(self.delete_comment_batch_wedge)
		self.page.pbSylgardDeleteComment.clicked.connect(self.delete_comment_batch_sylgard)
		self.page.pbBondWireDeleteComment.clicked.connect(self.delete_comment_batch_bond_wire)

		self.page.pbAralditeAddComment.clicked.connect(self.add_comment_batch_araldite)
		self.page.pbWedgeAddComment.clicked.connect(self.add_comment_batch_wedge)
		self.page.pbSylgardAddComment.clicked.connect(self.add_comment_batch_sylgard)
		self.page.pbBondWireAddComment.clicked.connect(self.add_comment_batch_bond_wire)



	@enforce_mode(['view','editing_batch_wedge','editing_batch_sylgard','editing_batch_bond_wire'])
	def update_info_batch_araldite(self,ID=None,*args,**kwargs):
		self.batch_araldite.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_sylgard','editing_batch_bond_wire'])
	def update_info_batch_wedge(self,ID=None,*args,**kwargs):
		self.batch_wedge.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_wedge','editing_batch_bond_wire'])
	def update_info_batch_sylgard(self,ID=None,*args,**kwargs):
		self.batch_sylgard.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_wedge','editing_batch_sylgard'])
	def update_info_batch_bond_wire(self,ID=None,*args,**kwargs):
		self.batch_bond_wire.update_info(ID)

	
	@enforce_mode('view')
	def update_info(self,*args,**kwargs):
		self.update_info_batch_araldite()
		self.update_info_batch_wedge()
		self.update_info_batch_sylgard()
		self.update_info_batch_bond_wire()



	@enforce_mode(['view','editing_batch_araldite','editing_batch_wedge','editing_batch_sylgard','editing_batch_bond_wire'])
	def update_elements(self):
		mode_view                        = self.mode == 'view'
		mode_editing_batch_araldite      = self.mode == 'editing_batch_araldite'
		mode_editing_batch_wedge         = self.mode == 'editing_batch_wedge'
		mode_editing_batch_sylgard       = self.mode == 'editing_batch_sylgard'
		mode_editing_batch_bond_wire     = self.mode == 'editing_batch_bond_wire'

		self.setMainSwitchingEnabled(mode_view)

		self.page.leAralditeID.setEnabled(not mode_editing_batch_araldite)
		self.page.sbWedgeID.setEnabled(not mode_editing_batch_wedge)
		self.page.sbSylgardID.setEnabled(not mode_editing_batch_sylgard)
		self.page.sbBondWireID.setEnabled(not mode_editing_batch_bond_wire)

		self.page.pbAralditeEditNew.setEnabled(mode_view)
		self.page.pbWedgeEditNew.setEnabled(mode_view)
		self.page.pbSylgardEditNew.setEnabled(mode_view)
		self.page.pbBondWireEditNew.setEnabled(mode_view)

		self.page.pbAralditeSave.setEnabled(mode_editing_batch_araldite)
		self.page.pbWedgeSave.setEnabled(mode_editing_batch_wedge)
		self.page.pbSylgardSave.setEnabled(mode_editing_batch_sylgard)
		self.page.pbBondWireSave.setEnabled(mode_editing_batch_bond_wire)

		self.page.pbAralditeCancel.setEnabled(mode_editing_batch_araldite)
		self.page.pbWedgeCancel.setEnabled(mode_editing_batch_wedge)
		self.page.pbSylgardCancel.setEnabled(mode_editing_batch_sylgard)
		self.page.pbBondWireCancel.setEnabled(mode_editing_batch_bond_wire)

		self.page.dAralditeReceived.setEnabled(mode_editing_batch_araldite)
		self.page.dWedgeReceived.setEnabled(mode_editing_batch_wedge)
		self.page.dSylgardReceived.setEnabled(mode_editing_batch_sylgard)
		self.page.dBondWireReceived.setEnabled(mode_editing_batch_bond_wire)

		self.page.dAralditeExpires.setEnabled(mode_editing_batch_araldite)
		self.page.dWedgeExpires.setEnabled(mode_editing_batch_wedge)
		self.page.dSylgardExpires.setEnabled(mode_editing_batch_sylgard)
		self.page.dBondWireExpires.setEnabled(mode_editing_batch_bond_wire)

		self.page.ckIsAralditeEmpty.setEnabled(mode_editing_batch_araldite)
		self.page.ckIsWedgeEmpty.setEnabled(mode_editing_batch_wedge)
		self.page.ckIsSylgardEmpty.setEnabled(mode_editing_batch_sylgard)
		self.page.ckIsBondWireEmpty.setEnabled(mode_editing_batch_bond_wire)

		self.page.leSylgardCuring.setEnabled(mode_editing_batch_sylgard)

		self.page.pbAralditeDeleteComment.setEnabled(mode_editing_batch_araldite)
		self.page.pbWedgeDeleteComment.setEnabled(mode_editing_batch_wedge)
		self.page.pbSylgardDeleteComment.setEnabled(mode_editing_batch_sylgard)
		self.page.pbBondWireDeleteComment.setEnabled(mode_editing_batch_bond_wire)

		self.page.pbAralditeAddComment.setEnabled(mode_editing_batch_araldite)
		self.page.pbWedgeAddComment.setEnabled(mode_editing_batch_wedge)
		self.page.pbSylgardAddComment.setEnabled(mode_editing_batch_sylgard)
		self.page.pbBondWireAddComment.setEnabled(mode_editing_batch_bond_wire)

		self.page.pteAralditeWriteComment.setEnabled(mode_editing_batch_araldite)
		self.page.pteWedgeWriteComment.setEnabled(mode_editing_batch_wedge)
		self.page.pteSylgardWriteComment.setEnabled(mode_editing_batch_sylgard)
		self.page.pteBondWireWriteComment.setEnabled(mode_editing_batch_bond_wire)



	@enforce_mode('view')
	def start_editing_batch_araldite(self,*args,**kwargs):
		self.mode = 'editing_batch_araldite'
		self.batch_araldite.start_editing()
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
		self.mode = 'editing_batch_wedge'
		self.batch_wedge.start_editing()
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
		self.mode = 'editing_batch_sylgard'
		self.batch_sylgard.start_editing()
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
		self.mode = 'editing_batch_bond_wire'
		self.batch_bond_wire.start_editing()
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

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
