PAGE_NAME = "view_tooling"
#OBJECTTYPE = "sensor_step"
DEBUG = False

INDEX_INSTITUTION = {
	'CERN':0,
	'FNAL':1,
	'UCSB':2,
	'UMN':3,
}

INSTITUTION_INDEX = {  # Can probably be replaced w/ list
	0:'CERN',
	1:'FNAL',
	2:'UCSB',
	3:'UMN',
}

class simple_fsobj_vc(object):
	def __init__(self,
		fsobj_tool,
		sbID,
		cbInstitution,  # New
		#dsbSize,
		leLocation,  # New
		pbEditNew,
		pbSave,
		pbCancel,
		listComments,
		pteWriteComment,
		pbDeleteComment,
		pbAddComment,
		):

		self.fsobj_exists    = None
		self.fsobj_tool      = fsobj_tool  # Renamed to clarify that obj is a fsobj_tool
		self.sbID            = sbID
		self.cbInstitution   = cbInstitution
		#self.dsbSize         = dsbSize
		self.leLocation      = leLocation
		self.pbEditNew       = pbEditNew
		self.pbSave          = pbSave
		self.pbCancel        = pbCancel
		self.listComments    = listComments
		self.pteWriteComment = pteWriteComment
		self.pbDeleteComment = pbDeleteComment
		self.pbAddComment    = pbAddComment

	def update_info(self,ID=None,institution=None,*args,**kwargs):
		print("Calling update_info() in tooling page")
		if ID is None:
			ID = self.sbID.value()
		else:
			self.sbID.setValue(ID)
		if institution is None:
			print("Insittution is none:  calling update_info and saving institution!")
			institution = self.cbInstitution.currentText()
		else:
			self.cbInstitution.setCurrentIndex(INDEX_INSTITUTION.get(institution, -1))

		print("Loading with institution ", institution)
		self.fsobj_exists = self.fsobj_tool.load(ID, institution)

		if self.fsobj_exists:
			self.pbEditNew.setText("edit")
			#if self.fsobj_tool.size is None:
			#	self.dsbSize.setValue(0)
			#	self.dsbSize.clear()
			#else:
			#	self.dsbSize.setValue(self.fsobj_tool.size)
			if self.fsobj_tool.location is None:
				self.leLocation.setText("")
			else:
				self.leLocation.setText(self.fsobj_tool.location)

			self.listComments.clear()
			for comment in self.fsobj_tool.comments:
				self.listComments.addItem(comment)
			self.pteWriteComment.clear()

		else:
			self.pbEditNew.setText("new")
			#self.dsbSize.setValue(0)
			self.leLocation.setText("")
			self.listComments.clear()
			self.pteWriteComment.clear()

	def start_editing(self,*args,**kwargs):
		if not self.fsobj_exists:
			print("Creating new tool @ start_editing: ", self.cbInstitution.currentText())
			self.fsobj_tool.new(self.sbID.value(), self.cbInstitution.currentText())

	def cancel_editing(self,*args,**kwargs):
		self.update_info()

	def save_editing(self,*args,**kwargs):
		print("SAVING TOOL")
		print("CURRENT INST IS", self.fsobj_tool.institution)
		comments = []
		for i in range(self.listComments.count()):
			comments.append(self.listComments.item(i).text())
		self.fsobj_tool.comments = comments
		#size = self.dsbSize.value()
		#if size == 0.0:
		#	size = None
		#self.fsobj_tool.size = size
		self.fsobj_tool.location = self.leLocation.text()  # New
		self.fsobj_tool.save()
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
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.tool_sensor = simple_fsobj_vc(
			self.fm.tool_sensor(),
			self.page.sbSensorToolID,
			self.page.cbSensorToolInstitution,
			#self.page.dsbSensorToolSize,
			self.page.leSensorToolLocation,
			self.page.pbSensorToolEditNew,
			self.page.pbSensorToolSave,
			self.page.pbSensorToolCancel,
			self.page.listSensorToolComments,
			self.page.pteSensorToolWriteComment,
			self.page.pbSensorToolDeleteComment,
			self.page.pbSensorToolAddComment,
			)

		self.tool_pcb = simple_fsobj_vc(
			self.fm.tool_pcb(),
			self.page.sbPcbToolID,
			self.page.cbPcbToolInstitution,
			#self.page.dsbPcbToolSize,
			self.page.lePcbToolLocation,
			self.page.pbPcbToolEditNew,
			self.page.pbPcbToolSave,
			self.page.pbPcbToolCancel,
			self.page.listPcbToolComments,
			self.page.ptePcbToolWriteComment,
			self.page.pbPcbToolDeleteComment,
			self.page.pbPcbToolAddComment,
			)

		self.tray_component_sensor = simple_fsobj_vc(
			self.fm.tray_component_sensor(),
			self.page.sbSensorTrayID,
			self.page.cbSensorTrayInstitution,
			#self.page.dsbSensorTraySize,
			self.page.leSensorTrayLocation,
			self.page.pbSensorTrayEditNew,
			self.page.pbSensorTraySave,
			self.page.pbSensorTrayCancel,
			self.page.listSensorTrayComments,
			self.page.pteSensorTrayWriteComment,
			self.page.pbSensorTrayDeleteComment,
			self.page.pbSensorTrayAddComment,
			)

		self.tray_component_pcb = simple_fsobj_vc(
			self.fm.tray_component_pcb(),
			self.page.sbPcbTrayID,
			self.page.cbPcbTrayInstitution,
			#self.page.dsbPcbTraySize,
			self.page.lePcbTrayLocation,
			self.page.pbPcbTrayEditNew,
			self.page.pbPcbTraySave,
			self.page.pbPcbTrayCancel,
			self.page.listPcbTrayComments,
			self.page.ptePcbTrayWriteComment,
			self.page.pbPcbTrayDeleteComment,
			self.page.pbPcbTrayAddComment,
			)

		self.tray_assembly = simple_fsobj_vc(
			self.fm.tray_assembly(),
			self.page.sbAssemblyTrayID,
			self.page.cbAssemblyTrayInstitution,
			#self.page.dsbAssemblyTraySize,
			self.page.leAssemblyTrayLocation,
			self.page.pbAssemblyTrayEditNew,
			self.page.pbAssemblyTraySave,
			self.page.pbAssemblyTrayCancel,
			self.page.listAssemblyTrayComments,
			self.page.pteAssemblyTrayWriteComment,
			self.page.pbAssemblyTrayDeleteComment,
			self.page.pbAssemblyTrayAddComment,
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
		self.page.sbSensorToolID  .valueChanged.connect(self.update_info_sensor_tool_ID  )
		self.page.sbPcbToolID     .valueChanged.connect(self.update_info_pcb_tool_ID     )
		self.page.sbSensorTrayID  .valueChanged.connect(self.update_info_sensor_tray_ID  )
		self.page.sbPcbTrayID     .valueChanged.connect(self.update_info_pcb_tray_ID     )
		self.page.sbAssemblyTrayID.valueChanged.connect(self.update_info_assembly_tray_ID)
		# New:
		self.page.cbSensorToolInstitution  .currentIndexChanged.connect(self.update_info_sensor_tool_inst  )
		self.page.cbPcbToolInstitution     .currentIndexChanged.connect(self.update_info_pcb_tool_inst     )
		self.page.cbSensorTrayInstitution  .currentIndexChanged.connect(self.update_info_sensor_tray_inst  )
		self.page.cbPcbTrayInstitution     .currentIndexChanged.connect(self.update_info_pcb_tray_inst     )
		self.page.cbAssemblyTrayInstitution.currentIndexChanged.connect(self.update_info_assembly_tray_inst)

		self.page.pbSensorToolEditNew  .clicked.connect(self.start_editing_sensor_tool  )
		self.page.pbPcbToolEditNew     .clicked.connect(self.start_editing_pcb_tool     )
		self.page.pbSensorTrayEditNew  .clicked.connect(self.start_editing_sensor_tray  )
		self.page.pbPcbTrayEditNew     .clicked.connect(self.start_editing_pcb_tray     )
		self.page.pbAssemblyTrayEditNew.clicked.connect(self.start_editing_assembly_tray)

		self.page.pbSensorToolSave  .clicked.connect(self.save_editing_sensor_tool  )
		self.page.pbPcbToolSave     .clicked.connect(self.save_editing_pcb_tool     )
		self.page.pbSensorTraySave  .clicked.connect(self.save_editing_sensor_tray  )
		self.page.pbPcbTraySave     .clicked.connect(self.save_editing_pcb_tray     )
		self.page.pbAssemblyTraySave.clicked.connect(self.save_editing_assembly_tray)
		
		self.page.pbSensorToolCancel  .clicked.connect(self.cancel_editing_sensor_tool  )
		self.page.pbPcbToolCancel     .clicked.connect(self.cancel_editing_pcb_tool     )
		self.page.pbSensorTrayCancel  .clicked.connect(self.cancel_editing_sensor_tray  )
		self.page.pbPcbTrayCancel     .clicked.connect(self.cancel_editing_pcb_tray     )
		self.page.pbAssemblyTrayCancel.clicked.connect(self.cancel_editing_assembly_tray)

		self.page.pbSensorToolDeleteComment  .clicked.connect(self.delete_comment_sensor_tool  )
		self.page.pbPcbToolDeleteComment     .clicked.connect(self.delete_comment_pcb_tool     )
		self.page.pbSensorTrayDeleteComment  .clicked.connect(self.delete_comment_sensor_tray  )
		self.page.pbPcbTrayDeleteComment     .clicked.connect(self.delete_comment_pcb_tray     )
		self.page.pbAssemblyTrayDeleteComment.clicked.connect(self.delete_comment_assembly_tray)

		self.page.pbSensorToolAddComment  .clicked.connect(self.add_comment_sensor_tool  )
		self.page.pbPcbToolAddComment     .clicked.connect(self.add_comment_pcb_tool     )
		self.page.pbSensorTrayAddComment  .clicked.connect(self.add_comment_sensor_tray  )
		self.page.pbPcbTrayAddComment     .clicked.connect(self.add_comment_pcb_tray     )
		self.page.pbAssemblyTrayAddComment.clicked.connect(self.add_comment_assembly_tray)



	@enforce_mode(['view','editing_pcb_tool','editing_sensor_tray','editing_pcb_tray','editing_assembly_tray'])
	def update_info_sensor_tool_ID(self,ID=None,*args,**kwargs):
		if ID is None:
			institution = None
		else:
			institution = self.page.cbSensorToolInstitution.currentText()
		self.tool_sensor.update_info(ID,institution)

	@enforce_mode(['view','editing_pcb_tool','editing_sensor_tray','editing_pcb_tray','editing_assembly_tray'])
	def update_info_sensor_tool_inst(self,institution=None,*args,**kwargs):
		ID = self.page.sbSensorToolID.value()
		# By default, this fn is handed the # of the combobox, not the text.  Fix that:
		institution = INSTITUTION_INDEX[institution]
		self.tool_sensor.update_info(ID,institution)

	@enforce_mode(['view','editing_sensor_tool','editing_sensor_tray','editing_pcb_tray','editing_assembly_tray'])
	def update_info_pcb_tool_ID(self,ID=None,*args,**kwargs):
		if ID is None:
			institution = None
		else:
			institution = self.page.cbPcbToolInstitution.currentText()
		self.tool_pcb.update_info(ID,institution)

	@enforce_mode(['view','editing_sensor_tool','editing_sensor_tray','editing_pcb_tray','editing_assembly_tray'])
	def update_info_pcb_tool_inst(self,institution=None,*args,**kwargs):
		ID = self.page.sbPcbToolID.value()
		institution = INSTITUTION_INDEX[institution]
		self.tool_pcb.update_info(ID,institution)

	@enforce_mode(['view','editing_sensor_tool','editing_pcb_tool','editing_pcb_tray','editing_assembly_tray'])
	def update_info_sensor_tray_ID(self,ID=None,*args,**kwargs):
		if ID is None:
			institution = None
		else:
			institution = self.page.cbSensorTrayInstitution.currentText()
		self.tray_component_sensor.update_info(ID,institution)

	@enforce_mode(['view','editing_sensor_tool','editing_pcb_tool','editing_pcb_tray','editing_assembly_tray'])
	def update_info_sensor_tray_inst(self,institution=None,*args,**kwargs):
		ID = self.page.sbSensorTrayID.value()
		institution = INSTITUTION_INDEX[institution]
		self.tray_component_sensor.update_info(ID,institution)

	@enforce_mode(['view','editing_sensor_tool','editing_pcb_tool','editing_sensor_tray','editing_assembly_tray'])
	def update_info_pcb_tray_ID(self,ID=None,*args,**kwargs):
		if ID is None:
			institution = None
		else:
			institution = self.page.cbPcbTrayInstitution.currentText()
		self.tray_component_pcb.update_info(ID,institution)

	@enforce_mode(['view','editing_sensor_tool','editing_pcb_tool','editing_sensor_tray','editing_assembly_tray'])
	def update_info_pcb_tray_inst(self,institution=None,*args,**kwargs):
		ID = self.page.sbPcbTrayID.value()
		institution = INSTITUTION_INDEX[institution]
		self.tray_component_pcb.update_info(ID,institution)

	@enforce_mode(['view','editing_sensor_tool','editing_pcb_tool','editing_sensor_tray','editing_pcb_tray'])
	def update_info_assembly_tray_ID(self,ID=None,*args,**kwargs):
		if ID is None:
			institution = None
		else:
			institution = self.page.cbAssemblyTrayInstitution.currentText()
		self.tray_assembly.update_info(ID,institution)

	@enforce_mode(['view','editing_sensor_tool','editing_pcb_tool','editing_sensor_tray','editing_pcb_tray'])
	def update_info_assembly_tray_inst(self,institution=None,*args,**kwargs):
		ID = self.page.sbAssemblyTrayID.value()
		institution = INSTITUTION_INDEX[institution]
		self.tray_assembly.update_info(ID,institution)

	@enforce_mode('view')
	def update_info(self,*args,**kwargs):
		self.update_info_sensor_tool_ID()
		self.update_info_pcb_tool_ID()
		self.update_info_sensor_tray_ID()
		self.update_info_pcb_tray_ID()
		self.update_info_assembly_tray_ID()



	@enforce_mode(['view','editing_sensor_tool','editing_pcb_tool','editing_sensor_tray','editing_pcb_tray','editing_assembly_tray'])
	def update_elements(self):
		mode_view                  = self.mode == 'view'
		mode_editing_sensor_tool   = self.mode == 'editing_sensor_tool'
		mode_editing_pcb_tool      = self.mode == 'editing_pcb_tool'
		mode_editing_sensor_tray   = self.mode == 'editing_sensor_tray'
		mode_editing_pcb_tray      = self.mode == 'editing_pcb_tray'
		mode_editing_assembly_tray = self.mode == 'editing_assembly_tray'

		self.setMainSwitchingEnabled(mode_view)

		self.page.sbSensorToolID  .setEnabled(not mode_editing_sensor_tool  )
		self.page.sbPcbToolID     .setEnabled(not mode_editing_pcb_tool     )
		self.page.sbSensorTrayID  .setEnabled(not mode_editing_sensor_tray  )
		self.page.sbPcbTrayID     .setEnabled(not mode_editing_pcb_tray     )
		self.page.sbAssemblyTrayID.setEnabled(not mode_editing_assembly_tray)
		# New
		self.page.cbSensorToolInstitution  .setEnabled(not mode_editing_sensor_tool  )
		self.page.cbPcbToolInstitution     .setEnabled(not mode_editing_pcb_tool     )
		self.page.cbSensorTrayInstitution  .setEnabled(not mode_editing_sensor_tray  )
		self.page.cbPcbTrayInstitution     .setEnabled(not mode_editing_pcb_tray     )
		self.page.cbAssemblyTrayInstitution.setEnabled(not mode_editing_assembly_tray)

		self.page.pbSensorToolEditNew  .setEnabled(mode_view)
		self.page.pbPcbToolEditNew     .setEnabled(mode_view)
		self.page.pbSensorTrayEditNew  .setEnabled(mode_view)
		self.page.pbPcbTrayEditNew     .setEnabled(mode_view)
		self.page.pbAssemblyTrayEditNew.setEnabled(mode_view)

		self.page.pbSensorToolSave  .setEnabled(mode_editing_sensor_tool  )
		self.page.pbPcbToolSave     .setEnabled(mode_editing_pcb_tool     )
		self.page.pbSensorTraySave  .setEnabled(mode_editing_sensor_tray  )
		self.page.pbPcbTraySave     .setEnabled(mode_editing_pcb_tray     )
		self.page.pbAssemblyTraySave.setEnabled(mode_editing_assembly_tray)

		self.page.pbSensorToolCancel  .setEnabled(mode_editing_sensor_tool  )
		self.page.pbPcbToolCancel     .setEnabled(mode_editing_pcb_tool     )
		self.page.pbSensorTrayCancel  .setEnabled(mode_editing_sensor_tray  )
		self.page.pbPcbTrayCancel     .setEnabled(mode_editing_pcb_tray     )
		self.page.pbAssemblyTrayCancel.setEnabled(mode_editing_assembly_tray)

		"""self.page.dsbSensorToolSize  .setEnabled(mode_editing_sensor_tool  )
		self.page.dsbPcbToolSize     .setEnabled(mode_editing_pcb_tool     )
		self.page.dsbSensorTraySize  .setEnabled(mode_editing_sensor_tray  )
		self.page.dsbPcbTraySize     .setEnabled(mode_editing_pcb_tray     )
		self.page.dsbAssemblyTraySize.setEnabled(mode_editing_assembly_tray)
		"""

		self.page.leSensorToolLocation  .setEnabled(mode_editing_sensor_tool  )  # New
		self.page.lePcbToolLocation     .setEnabled(mode_editing_pcb_tool     )
		self.page.leSensorTrayLocation  .setEnabled(mode_editing_sensor_tray  )
		self.page.lePcbTrayLocation     .setEnabled(mode_editing_pcb_tray     )
		self.page.leAssemblyTrayLocation.setEnabled(mode_editing_assembly_tray)

		self.page.pbSensorToolDeleteComment  .setEnabled(mode_editing_sensor_tool  )
		self.page.pbPcbToolDeleteComment     .setEnabled(mode_editing_pcb_tool     )
		self.page.pbSensorTrayDeleteComment  .setEnabled(mode_editing_sensor_tray  )
		self.page.pbPcbTrayDeleteComment     .setEnabled(mode_editing_pcb_tray     )
		self.page.pbAssemblyTrayDeleteComment.setEnabled(mode_editing_assembly_tray)

		self.page.pbSensorToolAddComment  .setEnabled(mode_editing_sensor_tool  )
		self.page.pbPcbToolAddComment     .setEnabled(mode_editing_pcb_tool     )
		self.page.pbSensorTrayAddComment  .setEnabled(mode_editing_sensor_tray  )
		self.page.pbPcbTrayAddComment     .setEnabled(mode_editing_pcb_tray     )
		self.page.pbAssemblyTrayAddComment.setEnabled(mode_editing_assembly_tray)

		self.page.pteSensorToolWriteComment  .setEnabled(mode_editing_sensor_tool  )
		self.page.ptePcbToolWriteComment     .setEnabled(mode_editing_pcb_tool     )
		self.page.pteSensorTrayWriteComment  .setEnabled(mode_editing_sensor_tray  )
		self.page.ptePcbTrayWriteComment     .setEnabled(mode_editing_pcb_tray     )
		self.page.pteAssemblyTrayWriteComment.setEnabled(mode_editing_assembly_tray)



	@enforce_mode('view')
	def start_editing_sensor_tool(self,*args,**kwargs):
		if self.page.cbSensorToolInstitution.currentText() == "":  return
		self.mode = 'editing_sensor_tool'
		self.tool_sensor.start_editing()
		self.update_elements()

	@enforce_mode('editing_sensor_tool')
	def cancel_editing_sensor_tool(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.tool_sensor.update_info()

	@enforce_mode('editing_sensor_tool')
	def save_editing_sensor_tool(self,*args,**kwargs):
		self.tool_sensor.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_sensor_tool')
	def add_comment_sensor_tool(self,*args,**kwargs):
		self.tool_sensor.add_comment()

	@enforce_mode('editing_sensor_tool')
	def delete_comment_sensor_tool(self,*args,**kwargs):
		self.tool_sensor.delete_comment()



	@enforce_mode('view')
	def start_editing_pcb_tool(self,*args,**kwargs):
		if self.page.cbPcbToolInstitution.currentText() == "":  return
		self.mode = 'editing_pcb_tool'
		self.tool_pcb.start_editing()
		self.update_elements()

	@enforce_mode('editing_pcb_tool')
	def cancel_editing_pcb_tool(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.tool_pcb.update_info()

	@enforce_mode('editing_pcb_tool')
	def save_editing_pcb_tool(self,*args,**kwargs):
		self.tool_pcb.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_pcb_tool')
	def add_comment_pcb_tool(self,*args,**kwargs):
		self.tool_pcb.add_comment()

	@enforce_mode('editing_pcb_tool')
	def delete_comment_pcb_tool(self,*args,**kwargs):
		self.tool_pcb.delete_comment()



	@enforce_mode('view')
	def start_editing_sensor_tray(self,*args,**kwargs):
		if self.page.cbSensorTrayInstitution.currentText() == "":  return
		self.mode = 'editing_sensor_tray'
		self.tray_component_sensor.start_editing()
		self.update_elements()

	@enforce_mode('editing_sensor_tray')
	def cancel_editing_sensor_tray(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.tray_component_sensor.update_info()

	@enforce_mode('editing_sensor_tray')
	def save_editing_sensor_tray(self,*args,**kwargs):
		self.tray_component_sensor.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_sensor_tray')
	def add_comment_sensor_tray(self,*args,**kwargs):
		self.tray_component_sensor.add_comment()

	@enforce_mode('editing_sensor_tray')
	def delete_comment_sensor_tray(self,*args,**kwargs):
		self.tray_component_sensor.delete_comment()



	@enforce_mode('view')
	def start_editing_pcb_tray(self,*args,**kwargs):
		if self.page.cbPcbTrayInstitution.currentText() == "":  return
		self.mode = 'editing_pcb_tray'
		self.tray_component_pcb.start_editing()
		self.update_elements()

	@enforce_mode('editing_pcb_tray')
	def cancel_editing_pcb_tray(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.tray_component_pcb.update_info()

	@enforce_mode('editing_pcb_tray')
	def save_editing_pcb_tray(self,*args,**kwargs):
		self.tray_component_pcb.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_pcb_tray')
	def add_comment_pcb_tray(self,*args,**kwargs):
		self.tray_component_pcb.add_comment()

	@enforce_mode('editing_pcb_tray')
	def delete_comment_pcb_tray(self,*args,**kwargs):
		self.tray_component_pcb.delete_comment()



	@enforce_mode('view')
	def start_editing_assembly_tray(self,*args,**kwargs):
		if self.page.cbAssemblyTrayInstitution.currentText() == "":  return
		self.mode = 'editing_assembly_tray'
		self.tray_assembly.start_editing()
		self.update_elements()

	@enforce_mode('editing_assembly_tray')
	def cancel_editing_assembly_tray(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.tray_assembly.update_info()

	@enforce_mode('editing_assembly_tray')
	def save_editing_assembly_tray(self,*args,**kwargs):
		self.tray_assembly.save_editing()
		self.mode='view'
		self.update_elements()

	@enforce_mode('editing_assembly_tray')
	def add_comment_assembly_tray(self,*args,**kwargs):
		self.tray_assembly.add_comment()

	@enforce_mode('editing_assembly_tray')
	def delete_comment_assembly_tray(self,*args,**kwargs):
		self.tray_assembly.delete_comment()




	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		keys = kwargs.keys()
		#print("LOADING KWARGS")
		#print(kwargs)
		if "tool_sensor" in keys:
			self.update_info_sensor_tool_ID(kwargs['tool_sensor'])
		if "tool_pcb" in keys:
			self.update_info_pcb_tool_ID(kwargs['tool_pcb'])
		if "tray_component_sensor" in keys:
			self.update_info_sensor_tray_ID(kwargs['tray_component_sensor'])
		if "tray_component_pcb" in keys:
			self.update_info_pcb_tray_ID(kwargs['tray_component_pcb'])
		if "tray_assembly" in keys:
			self.update_info_assembly_tray_ID(kwargs['tray_assembly'])

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
