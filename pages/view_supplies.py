from PyQt5 import QtCore

PAGE_NAME = "view_tooling"
#OBJECTTYPE = "sensor_step"
DEBUG = False

class simple_fsobj_vc(object):
	def __init__(self,
		fsobj,
		sbID,
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

	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.sbID.value()
		else:
			self.sbID.setValue(ID)
		self.fsobj_exists = self.fsobj.load(ID)

		if self.fsobj_exists:
			self.pbEditNew.setText("edit")

			self.dReceived.setDate(QtCore.QDate(*self.fsobj.date_received))
			self.dExpires.setDate(QtCore.QDate(*self.fsobj.date_expires))

			self.ckIsEmpty.setChecked(self.fsobj.is_empty)

			self.listComments.clear()
			for comment in self.fsobj.comments:
				self.listComments.addItem(comment)
			self.pteWriteComment.clear()

		else:
			self.pbEditNew.setText("new")

			self.dReceived.setDate(QtCore.QDate(2000,1,1))
			self.dExpires.setDate(QtCore.QDate(2000,1,1))

			self.ckIsEmpty.setChecked(False)

			self.listComments.clear()
			self.pteWriteComment.clear()

	def start_editing(self,*args,**kwargs):
		if not self.fsobj_exists:
			self.fsobj.new(self.sbID.value())

	def cancel_editing(self,*args,**kwargs):
		self.update_info()

	def save_editing(self,*args,**kwargs):
		comments = []
		for i in range(self.listComments.count()):
			comments.append(self.listComments.item(i).text())
		self.fsobj.comments = comments

		self.fsobj.date_received = self.dReceived.date().getDate()
		self.fsobj.date_expires  = self.dExpires.date().getDate()

		self.fsobj.is_empty = self.ckIsEmpty.isChecked()

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
			self.page.sbAralditeID,
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

		self.batch_loctite = simple_fsobj_vc(
			fm.batch_loctite(),
			self.page.sbLoctiteID,
			self.page.dLoctiteReceived,
			self.page.dLoctiteExpires,
			self.page.ckIsLoctiteEmpty,
			self.page.pbLoctiteEditNew,
			self.page.pbLoctiteSave,
			self.page.pbLoctiteCancel,
			self.page.listLoctiteComments,
			self.page.pteLoctiteWriteComment,
			self.page.pbLoctiteDeleteComment,
			self.page.pbLoctiteAddComment,
			)

		self.batch_sylgard_thick = simple_fsobj_vc(
			fm.batch_sylgard_thick(),
			self.page.sbSylgardThickID,
			self.page.dSylgardThickReceived,
			self.page.dSylgardThickExpires,
			self.page.ckIsSylgardThickEmpty,
			self.page.pbSylgardThickEditNew,
			self.page.pbSylgardThickSave,
			self.page.pbSylgardThickCancel,
			self.page.listSylgardThickComments,
			self.page.pteSylgardThickWriteComment,
			self.page.pbSylgardThickDeleteComment,
			self.page.pbSylgardThickAddComment,
			)

		self.batch_sylgard_thin = simple_fsobj_vc(
			fm.batch_sylgard_thin(),
			self.page.sbSylgardThinID,
			self.page.dSylgardThinReceived,
			self.page.dSylgardThinExpires,
			self.page.ckIsSylgardThinEmpty,
			self.page.pbSylgardThinEditNew,
			self.page.pbSylgardThinSave,
			self.page.pbSylgardThinCancel,
			self.page.listSylgardThinComments,
			self.page.pteSylgardThinWriteComment,
			self.page.pbSylgardThinDeleteComment,
			self.page.pbSylgardThinAddComment,
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
		self.page.sbAralditeID.valueChanged.connect(self.update_info_batch_araldite)
		self.page.sbLoctiteID.valueChanged.connect(self.update_info_batch_loctite)
		self.page.sbSylgardThickID.valueChanged.connect(self.update_info_batch_sylgard_thick)
		self.page.sbSylgardThinID.valueChanged.connect(self.update_info_batch_sylgard_thin)
		self.page.sbBondWireID.valueChanged.connect(self.update_info_batch_bond_wire)

		self.page.pbAralditeEditNew.clicked.connect(self.start_editing_batch_araldite)
		self.page.pbLoctiteEditNew.clicked.connect(self.start_editing_batch_loctite)
		self.page.pbSylgardThickEditNew.clicked.connect(self.start_editing_batch_sylgard_thick)
		self.page.pbSylgardThinEditNew.clicked.connect(self.start_editing_batch_sylgard_thin)
		self.page.pbBondWireEditNew.clicked.connect(self.start_editing_batch_bond_wire)

		self.page.pbAralditeSave.clicked.connect(self.save_editing_batch_araldite)
		self.page.pbLoctiteSave.clicked.connect(self.save_editing_batch_loctite)
		self.page.pbSylgardThickSave.clicked.connect(self.save_editing_batch_sylgard_thick)
		self.page.pbSylgardThinSave.clicked.connect(self.save_editing_batch_sylgard_thin)
		self.page.pbBondWireSave.clicked.connect(self.save_editing_batch_bond_wire)
		
		self.page.pbAralditeCancel.clicked.connect(self.cancel_editing_batch_araldite)
		self.page.pbLoctiteCancel.clicked.connect(self.cancel_editing_batch_loctite)
		self.page.pbSylgardThickCancel.clicked.connect(self.cancel_editing_batch_sylgard_thick)
		self.page.pbSylgardThinCancel.clicked.connect(self.cancel_editing_batch_sylgard_thin)
		self.page.pbBondWireCancel.clicked.connect(self.cancel_editing_batch_bond_wire)

		self.page.pbAralditeDeleteComment.clicked.connect(self.delete_comment_batch_araldite)
		self.page.pbLoctiteDeleteComment.clicked.connect(self.delete_comment_batch_loctite)
		self.page.pbSylgardThickDeleteComment.clicked.connect(self.delete_comment_batch_sylgard_thick)
		self.page.pbSylgardThinDeleteComment.clicked.connect(self.delete_comment_batch_sylgard_thin)
		self.page.pbBondWireDeleteComment.clicked.connect(self.delete_comment_batch_bond_wire)

		self.page.pbAralditeAddComment.clicked.connect(self.add_comment_batch_araldite)
		self.page.pbLoctiteAddComment.clicked.connect(self.add_comment_batch_loctite)
		self.page.pbSylgardThickAddComment.clicked.connect(self.add_comment_batch_sylgard_thick)
		self.page.pbSylgardThinAddComment.clicked.connect(self.add_comment_batch_sylgard_thin)
		self.page.pbBondWireAddComment.clicked.connect(self.add_comment_batch_bond_wire)



	@enforce_mode(['view','editing_batch_loctite','editing_batch_sylgard_thick','editing_batch_sylgard_thin','editing_batch_bond_wire'])
	def update_info_batch_araldite(self,ID=None,*args,**kwargs):
		self.batch_araldite.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_sylgard_thick','editing_batch_sylgard_thin','editing_batch_bond_wire'])
	def update_info_batch_loctite(self,ID=None,*args,**kwargs):
		self.batch_loctite.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_loctite','editing_batch_sylgard_thin','editing_batch_bond_wire'])
	def update_info_batch_sylgard_thick(self,ID=None,*args,**kwargs):
		self.batch_sylgard_thick.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_loctite','editing_batch_sylgard_thick','editing_batch_bond_wire'])
	def update_info_batch_sylgard_thin(self,ID=None,*args,**kwargs):
		self.batch_sylgard_thin.update_info(ID)

	@enforce_mode(['view','editing_batch_araldite','editing_batch_loctite','editing_batch_sylgard_thick','editing_batch_sylgard_thin'])
	def update_info_batch_bond_wire(self,ID=None,*args,**kwargs):
		self.batch_bond_wire.update_info(ID)

	
	@enforce_mode('view')
	def update_info(self,*args,**kwargs):
		self.update_info_batch_araldite()
		self.update_info_batch_loctite()
		self.update_info_batch_sylgard_thick()
		self.update_info_batch_sylgard_thin()
		self.update_info_batch_bond_wire()



	@enforce_mode(['view','editing_batch_araldite','editing_batch_loctite','editing_batch_sylgard_thick','editing_batch_sylgard_thin','editing_batch_bond_wire'])
	def update_elements(self):
		mode_view                        = self.mode == 'view'
		mode_editing_batch_araldite      = self.mode == 'editing_batch_araldite'
		mode_editing_batch_loctite       = self.mode == 'editing_batch_loctite'
		mode_editing_batch_sylgard_thick = self.mode == 'editing_batch_sylgard_thick'
		mode_editing_batch_sylgard_thin  = self.mode == 'editing_batch_sylgard_thin'
		mode_editing_batch_bond_wire     = self.mode == 'editing_batch_bond_wire'

		self.setMainSwitchingEnabled(mode_view)

		self.page.sbAralditeID.setEnabled(not mode_editing_batch_araldite)
		self.page.sbLoctiteID.setEnabled(not mode_editing_batch_loctite)
		self.page.sbSylgardThickID.setEnabled(not mode_editing_batch_sylgard_thick)
		self.page.sbSylgardThinID.setEnabled(not mode_editing_batch_sylgard_thin)
		self.page.sbBondWireID.setEnabled(not mode_editing_batch_bond_wire)

		self.page.pbAralditeEditNew.setEnabled(mode_view)
		self.page.pbLoctiteEditNew.setEnabled(mode_view)
		self.page.pbSylgardThickEditNew.setEnabled(mode_view)
		self.page.pbSylgardThinEditNew.setEnabled(mode_view)
		self.page.pbBondWireEditNew.setEnabled(mode_view)

		self.page.pbAralditeSave.setEnabled(mode_editing_batch_araldite)
		self.page.pbLoctiteSave.setEnabled(mode_editing_batch_loctite)
		self.page.pbSylgardThickSave.setEnabled(mode_editing_batch_sylgard_thick)
		self.page.pbSylgardThinSave.setEnabled(mode_editing_batch_sylgard_thin)
		self.page.pbBondWireSave.setEnabled(mode_editing_batch_bond_wire)

		self.page.pbAralditeCancel.setEnabled(mode_editing_batch_araldite)
		self.page.pbLoctiteCancel.setEnabled(mode_editing_batch_loctite)
		self.page.pbSylgardThickCancel.setEnabled(mode_editing_batch_sylgard_thick)
		self.page.pbSylgardThinCancel.setEnabled(mode_editing_batch_sylgard_thin)
		self.page.pbBondWireCancel.setEnabled(mode_editing_batch_bond_wire)

		self.page.dAralditeReceived.setEnabled(mode_editing_batch_araldite)
		self.page.dLoctiteReceived.setEnabled(mode_editing_batch_loctite)
		self.page.dSylgardThickReceived.setEnabled(mode_editing_batch_sylgard_thick)
		self.page.dSylgardThinReceived.setEnabled(mode_editing_batch_sylgard_thin)
		self.page.dBondWireReceived.setEnabled(mode_editing_batch_bond_wire)

		self.page.dAralditeExpires.setEnabled(mode_editing_batch_araldite)
		self.page.dLoctiteExpires.setEnabled(mode_editing_batch_loctite)
		self.page.dSylgardThickExpires.setEnabled(mode_editing_batch_sylgard_thick)
		self.page.dSylgardThinExpires.setEnabled(mode_editing_batch_sylgard_thin)
		self.page.dBondWireExpires.setEnabled(mode_editing_batch_bond_wire)

		self.page.ckIsAralditeEmpty.setEnabled(mode_editing_batch_araldite)
		self.page.ckIsLoctiteEmpty.setEnabled(mode_editing_batch_loctite)
		self.page.ckIsSylgardThickEmpty.setEnabled(mode_editing_batch_sylgard_thick)
		self.page.ckIsSylgardThinEmpty.setEnabled(mode_editing_batch_sylgard_thin)
		self.page.ckIsBondWireEmpty.setEnabled(mode_editing_batch_bond_wire)

		self.page.pbAralditeDeleteComment.setEnabled(mode_editing_batch_araldite)
		self.page.pbLoctiteDeleteComment.setEnabled(mode_editing_batch_loctite)
		self.page.pbSylgardThickDeleteComment.setEnabled(mode_editing_batch_sylgard_thick)
		self.page.pbSylgardThinDeleteComment.setEnabled(mode_editing_batch_sylgard_thin)
		self.page.pbBondWireDeleteComment.setEnabled(mode_editing_batch_bond_wire)

		self.page.pbAralditeAddComment.setEnabled(mode_editing_batch_araldite)
		self.page.pbLoctiteAddComment.setEnabled(mode_editing_batch_loctite)
		self.page.pbSylgardThickAddComment.setEnabled(mode_editing_batch_sylgard_thick)
		self.page.pbSylgardThinAddComment.setEnabled(mode_editing_batch_sylgard_thin)
		self.page.pbBondWireAddComment.setEnabled(mode_editing_batch_bond_wire)

		self.page.pteAralditeWriteComment.setEnabled(mode_editing_batch_araldite)
		self.page.pteLoctiteWriteComment.setEnabled(mode_editing_batch_loctite)
		self.page.pteSylgardThickWriteComment.setEnabled(mode_editing_batch_sylgard_thick)
		self.page.pteSylgardThinWriteComment.setEnabled(mode_editing_batch_sylgard_thin)
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
	def start_editing_batch_loctite(self,*args,**kwargs):
		self.mode = 'editing_batch_loctite'
		self.batch_loctite.start_editing()
		self.update_elements()

	@enforce_mode('editing_batch_loctite')
	def cancel_editing_batch_loctite(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.batch_loctite.update_info()

	@enforce_mode('editing_batch_loctite')
	def save_editing_batch_loctite(self,*args,**kwargs):
		self.batch_loctite.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_batch_loctite')
	def add_comment_batch_loctite(self,*args,**kwargs):
		self.batch_loctite.add_comment()

	@enforce_mode('editing_batch_loctite')
	def delete_comment_batch_loctite(self,*args,**kwargs):
		self.batch_loctite.delete_comment()


	@enforce_mode('view')
	def start_editing_batch_sylgard_thick(self,*args,**kwargs):
		self.mode = 'editing_batch_sylgard_thick'
		self.batch_sylgard_thick.start_editing()
		self.update_elements()

	@enforce_mode('editing_batch_sylgard_thick')
	def cancel_editing_batch_sylgard_thick(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.batch_sylgard_thick.update_info()

	@enforce_mode('editing_batch_sylgard_thick')
	def save_editing_batch_sylgard_thick(self,*args,**kwargs):
		self.batch_sylgard_thick.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_batch_sylgard_thick')
	def add_comment_batch_sylgard_thick(self,*args,**kwargs):
		self.batch_sylgard_thick.add_comment()

	@enforce_mode('editing_batch_sylgard_thick')
	def delete_comment_batch_sylgard_thick(self,*args,**kwargs):
		self.batch_sylgard_thick.delete_comment()


	@enforce_mode('view')
	def start_editing_batch_sylgard_thin(self,*args,**kwargs):
		self.mode = 'editing_batch_sylgard_thin'
		self.batch_sylgard_thin.start_editing()
		self.update_elements()

	@enforce_mode('editing_batch_sylgard_thin')
	def cancel_editing_batch_sylgard_thin(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.batch_sylgard_thin.update_info()

	@enforce_mode('editing_batch_sylgard_thin')
	def save_editing_batch_sylgard_thin(self,*args,**kwargs):
		self.batch_sylgard_thin.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_batch_sylgard_thin')
	def add_comment_batch_sylgard_thin(self,*args,**kwargs):
		self.batch_sylgard_thin.add_comment()

	@enforce_mode('editing_batch_sylgard_thin')
	def delete_comment_batch_sylgard_thin(self,*args,**kwargs):
		self.batch_sylgard_thin.delete_comment()


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
		if "batch_loctite" in keys:
			self.update_info_batch_loctite(kwargs['batch_loctite'])
		if "batch_sylgard_thick" in keys:
			self.update_info_batch_sylgard_thick(kwargs['batch_sylgard_thick'])
		if "batch_sylgard_thin" in keys:
			self.update_info_batch_sylgard_thin(kwargs['batch_sylgard_thin'])
		if "batch_bond_wire" in keys:
			self.update_info_batch_bond_wire(kwargs['batch_bond_wire'])

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
