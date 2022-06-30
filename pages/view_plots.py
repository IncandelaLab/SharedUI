from filemanager import fm
from PyQt5 import QtCore
import time
import os
import shutil

# NEW, experimental
from PyQt5.QtWidgets import QFileDialog, QWidget


PAGE_NAME = "view_plots"
DEBUG = False
SITE_SEP = ', '
NO_DATE = [2022,1,1]


def separate_sites(sites_string):
	s = sites_string
	for char in SITE_SEP:
		s=s.replace(char, '\n')
	sites = [_ for _ in s.splitlines() if _]
	return sites


# EXPERIMENTAL

class Filewindow(QWidget):
	def __init__(self):
		super(Filewindow, self).__init__()

	def getfile(self,*args,**kwargs):
		fname, fmt = QFileDialog.getOpenFileName(self, 'Open file', '~',"(*.jpg *.png *.xml)")
		print("File dialog:  got file", fname)
		return fname


class simple_fsobj_pt(object):  # from tools
	def __init__(self,
		fsobj_pt,
		leID,
		leStatus,
		pbLoad,
		pbEdit,
		pbSave,
		pbCancel,
		pbGo,
		listFiles,
		pbDeleteFiles,
		pbAddFiles,
		pbDeleteComment,
		listComments,
		pteWriteComment,
		pbAddComment
		):

		self.fsobj_pt = fsobj_pt
		self.leID = leID
		self.leStatus = leStatus
		self.pbLoad = pbLoad
		self.pbEdit = pbEdit
		self.pbSave = pbSave
		self.pbCancel = pbCancel
		self.pbGo = pbGo
		self.listFiles = listFiles
		self.pbDeleteFiles = pbDeleteFiles
		self.pbAddFiles = pbAddFiles
		self.pbDeleteComment = pbDeleteComment
		self.listComments = listComments
		self.pteWriteComment = pteWriteComment
		self.pbAddComment = pbAddComment

	def update_info(self,ID=None,do_load=True,*args,**kwargs):
		if ID is None:
			ID = self.leID.text()
		else:
			self.leID.setText(ID)
		if do_load:
			self.part_exists = self.fsobj_pt.load(ID)
		else:
			self.part_exists = False
		
		self.part_exists = (ID == self.fsobj_pt.ID)

		# comments
		self.listComments.clear()
		for comment in self.fsobj_pt.comments:
			self.listComments.addItem(comment)
		self.pteWriteComment.clear()


		self.listFiles.clear()
		for f in self.fsobj_pt.test_files:
			name = os.path.split(f)[1]
			self.listFiles.addItem(name)


	def load_part(self,*args,**kwargs):
		if self.leID.text == "":
			self.leStatus.setText("input an ID")
			return
		# Check whether part exists:
		tmp_ID = self.leID.text()
		tmp_exists = self.fsobj_pt.load(tmp_ID)
		if not tmp_exists:  # DNE; good to create
			self.leStatus.setText("part DNE")
			self.update_info(do_load=False)
			self.fsobj_pt.clear()
		else:
			self.leStatus.setText("part exists")
			self.update_info()

	def start_editing(self,*args,**kwargs):
		tmp_ID = self.leID.text()
		tmp_exists = self.fsobj_pt.load(tmp_ID)
		if not tmp_exists:
			self.leStatus.setText("does not exist")
			self.fsobj_pt.clear()

	def cancel_editing(self,*args,**kwargs):
		self.update_info()

	def save_editing(self,*args,**kwargs):
		# comments
		self.fsobj_pt.comments = []
		for i in range(self.listComments.count()):
			self.fsobj_pt.comments.append(str(self.listComments.item(i).text()))

		self.fsobj_pt.test_files = []
		for i in range(self.listFiles.count()):
			self.fsobj_pt.test_files.append(str(self.listFiles.item(i).text()))

		self.fsobj_pt.save()
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

	def add_file(self,f):
		fdir, fname = self.fsobj_pt.get_filedir_filename()
		# Create a copy of the file in the module storage directory
		tmp_filename = os.path.split(f)[1]
		new_filepath = fdir + '/' + tmp_filename
		shutil.copyfile(f, new_filepath)
		# From here on, the file is ONLY referred to by its name, not the full path!
		self.fsobj_pt.test_files.append(tmp_filename)
		self.fsobj_pt.save()
		self.update_info()

	def delete_file(self,row):
		fname = self.listFiles.item(row).text()
		fdir, fname_ = self.fsobj_pt.get_filedir_filename()
		self.listFiles.takeItem(row)
		os.remove(fdir + '/' + fname)  # remove file and save immediately (cancelling is hard to implement otherwise)
		self.fsobj_pt.test_files.remove(fname)
		self.fsobj_pt.save()
		self.update_info()




class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.pcb_obj = simple_fsobj_pt(
			fm.pcb(),
			self.page.leIDPCB,
			self.page.leStatusPCB,
			self.page.pbLoadPCB,
			self.page.pbEditPCB,
			self.page.pbSavePCB,
			self.page.pbCancelPCB,
			self.page.pbGoPCB,
			self.page.listFilesPCB,
			self.page.pbDeleteFilesPCB,
			self.page.pbAddFilesPCB,
			self.page.pbDeleteCommentPCB,
			self.page.listCommentsPCB,
			self.page.pteWriteCommentPCB,
			self.page.pbAddCommentPCB
			)
		self.module_obj = simple_fsobj_pt(
			fm.module(),
			self.page.leIDMod,
			self.page.leStatusMod,
			self.page.pbLoadMod,
			self.page.pbEditMod,
			self.page.pbSaveMod,
			self.page.pbCancelMod,
			self.page.pbGoMod,
			self.page.listFilesMod,
			self.page.pbDeleteFilesMod,
			self.page.pbAddFilesMod,
			self.page.pbDeleteCommentMod,
			self.page.listCommentsMod,
			self.page.pteWriteCommentMod,
			self.page.pbAddCommentMod
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
		print("{} setup completed".format(PAGE_NAME))
		self.update_info()
		self.updateElements()

	@enforce_mode('setup')
	def rig(self):
		self.page.pbLoadPCB.clicked.connect(self.loadPartPCB)
		self.page.pbEditPCB.clicked.connect(self.startEditingPCB)
		self.page.pbSavePCB.clicked.connect(self.saveEditingPCB)
		self.page.pbCancelPCB.clicked.connect(self.cancelEditingPCB)
		self.page.pbGoPCB.clicked.connect(self.goPCB)
		self.page.pbDeleteCommentPCB.clicked.connect(self.deleteCommentPCB)
		self.page.pbAddCommentPCB.clicked.connect(self.addCommentPCB)

		self.fwnd_pcb = Filewindow()
		self.page.pbAddFilesPCB.clicked.connect(self.getFilePCB)
		self.page.pbDeleteFilesPCB.clicked.connect(self.deleteFilePCB)

		self.page.pbLoadMod.clicked.connect(self.loadPartMod)
		self.page.pbEditMod.clicked.connect(self.startEditingMod)
		self.page.pbSaveMod.clicked.connect(self.saveEditingMod)
		self.page.pbCancelMod.clicked.connect(self.cancelEditingMod)
		self.page.pbGoMod.clicked.connect(self.goMod)
		self.page.pbDeleteCommentMod.clicked.connect(self.deleteCommentMod)
		self.page.pbAddCommentMod.clicked.connect(self.addCommentMod)

		self.fwnd_mod = Filewindow()
		self.page.pbAddFilesMod.clicked.connect(self.getFileMod)
		self.page.pbDeleteFilesMod.clicked.connect(self.deleteFileMod)


	@enforce_mode(['view', 'editing_pcb', 'editing_mod'])
	def update_info_pcb(self,ID=None,do_load=True,*args,**kwargs):
		self.pcb_obj.update_info(ID)
		#self.updateElements()

	@enforce_mode(['view', 'editing_pcb', 'editing_mod'])
	def update_info_module(self,ID=None,do_load=True,*args,**kwargs):
		self.module_obj.update_info(ID)
		#self.updateElements()

	@enforce_mode('view')
	def update_info(self,*args,**kwargs):
		self.update_info_pcb()
		self.update_info_module()


	@enforce_mode(['view','editing_pcb', 'editing_mod'])
	def updateElements(self):
		if self.mode == "editing_pcb":
			self.page.leStatusPCB.setText(self.mode)
			self.page.leStatusMod.clear()
		if self.mode == "editing_mod":
			self.page.leStatusPCB.clear()
			self.page.leStatusMod.setText(self.mode)

		pcb_exists    = self.pcb_obj.part_exists
		module_exists = self.module_obj.part_exists

		mode_view        = self.mode == 'view'
		mode_editing_pcb = self.mode == 'editing_pcb'
		mode_editing_mod = self.mode == 'editing_mod'

		self.setMainSwitchingEnabled(mode_view) 
		self.page.leIDPCB.setReadOnly(not mode_view)
		self.page.leIDMod.setReadOnly(not mode_view)

		self.page.pbLoadPCB.setEnabled(mode_view)
		self.page.pbLoadMod.setEnabled(mode_view)

		self.page.pbEditPCB  .setEnabled(mode_view and pcb_exists)
		self.page.pbEditMod  .setEnabled(mode_view and module_exists)
		self.page.pbSavePCB  .setEnabled(mode_editing_pcb)
		self.page.pbSaveMod  .setEnabled(mode_editing_mod)
		self.page.pbCancelPCB.setEnabled(mode_editing_pcb)
		self.page.pbCancelMod.setEnabled(mode_editing_mod)

		# comments
		self.page.pbDeleteCommentPCB.setEnabled(mode_editing_pcb)
		self.page.pbDeleteCommentMod.setEnabled(mode_editing_mod)
		self.page.pbAddCommentPCB   .setEnabled(mode_editing_pcb)
		self.page.pbAddCommentMod   .setEnabled(mode_editing_mod)
		self.page.pteWriteCommentPCB.setEnabled(mode_editing_pcb)
		self.page.pteWriteCommentMod.setEnabled(mode_editing_mod)

		self.page.pbAddFilesPCB   .setEnabled(mode_editing_pcb)
		self.page.pbAddFilesMod   .setEnabled(mode_editing_mod)
		self.page.pbDeleteFilesPCB.setEnabled(mode_editing_pcb)
		self.page.pbDeleteFilesMod.setEnabled(mode_editing_mod)


	# NEW:
	@enforce_mode('view')
	def loadPartPCB(self,*args,**kwargs):
		self.pcb_obj.load_part()
		self.updateElements()

	@enforce_mode('view')
	def loadPartMod(self,*args,**kwargs):
		self.module_obj.load_part()
		self.updateElements()

	@enforce_mode('view')
	def startEditingPCB(self,*args,**kwargs):
		self.pcb_obj.start_editing()
		self.mode = 'editing_pcb'
		self.updateElements()

	@enforce_mode('view')
	def startEditingMod(self,*args,**kwargs):
		self.module_obj.start_editing()
		self.mode = 'editing_mod'
		self.updateElements()

	@enforce_mode('editing_pcb')
	def cancelEditingPCB(self,*args,**kwargs):
		self.mode = 'view'
		self.pcb_obj.cancel_editing()
		self.updateElements()

	@enforce_mode('editing_mod')
	def cancelEditingMod(self,*args,**kwargs):
		self.mode = 'view'
		self.module_obj.cancel_editing()
		self.updateElements()



	@enforce_mode('editing_pcb')
	def saveEditingPCB(self,*args,**kwargs):
		self.mode = 'view'
		self.pcb_obj.save_editing()
		self.updateElements()

	@enforce_mode('editing_mod')
	def saveEditingMod(self,*args,**kwargs):
		self.mode = 'view'
		self.module_obj.save_editing()
		self.updateElements()

	@enforce_mode('editing_pcb')
	def deleteCommentPCB(self,*args,**kwargs):
		self.pcb_obj.delete_comment()

	@enforce_mode('editing_mod')
	def deleteCommentMod(self,*args,**kwargs):
		self.module_obj.delete_comment()

	@enforce_mode('editing_pcb')
	def addCommentPCB(self,*args,**kwargs):
		self.pcb_obj.add_comment()

	@enforce_mode('editing_mod')
	def addCommentMod(self,*args,**kwargs):
		self.module_obj.add_comment()

	@enforce_mode('view')
	def goPCB(self,*args,**kwargs):
		ID = self.page.lePCB.text()
		if ID != "":
			self.setUIPage('PCBs',ID=ID)

	@enforce_mode('view')
	def goMod(self,*args,**kwargs):
		ID = self.page.leMod.text()
		if ID != "":
			self.setUIPage('Modules',ID=ID)


	@enforce_mode('editing_pcb')
	def getFilePCB(self,*args,**kwargs):
		f = self.fwnd_pcb.getfile()
		if f:
			self.pcb_obj.add_file(f)
			self.updateElements()

	@enforce_mode('editing_mod')
	def getFileMod(self,*args,**kwargs):
		f = self.fwnd_mod.getfile()
		if f:
			self.module_obj.add_file(f)
			self.updateElements()


	@enforce_mode('editing_pcb')
	def deleteFilePCB(self,*args,**kwargs):
		row = self.page.listFilesPCB.currentRow()
		if row >= 0:
			self.pcb_obj.delete_file(row)

	@enforce_mode('editing_mod')
	def deleteFileMod(self,*args,**kwargs):
		row = self.page.listFilesMod.currentRow()
		if row >= 0:
			self.module_obj.delete_file(row)


	def filesToUpload(self):
		# Return a list of all files to upload to DB
		if self.module is None:
			return []
		else:
			return self.module.filesToUpload()


	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is str):
				raise TypeError("Expected type <str> for ID; got <{}>".format(type(ID)))
			#if ID < 0:
			#	raise ValueError("ID cannot be negative")
			self.page.leID.setText(ID)
			self.loadPart()

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
