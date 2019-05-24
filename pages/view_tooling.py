PAGE_NAME = "view_tooling"
#OBJECTTYPE = "sensor_step"
DEBUG = False

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.tool_sensor           = self.fm.tool_sensor()
		self.tool_pcb              = self.fm.tool_pcb()
		self.tray_component_sensor = self.fm.tray_component_sensor()
		self.tray_component_pcb    = self.fm.tray_component_pcb()
		self.tray_assembly         = self.fm.tray_assembly()

		self.mode = 'setup'

		self.tool_sensor_exists           = None
		self.tool_pcb_exists              = None
		self.tray_component_sensor_exists = None
		self.tray_component_pcb_exists    = None
		self.tray_assembly_exists         = None

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
		self.page.sbSensorToolID  .valueChanged.connect(self.update_info_sensor_tool  )
		self.page.sbPcbToolID     .valueChanged.connect(self.update_info_pcb_tool     )
		self.page.sbSensorTrayID  .valueChanged.connect(self.update_info_sensor_tray  )
		self.page.sbPcbTrayID     .valueChanged.connect(self.update_info_pcb_tray     )
		self.page.sbAssemblyTrayID.valueChanged.connect(self.update_info_assembly_tray)

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



	# change modes for these to any except relevant editing mode

	@enforce_mode(['view','editing_pcb_tool','editing_sensor_tray','editing_pcb_tray','editing_assembly_tray'])
	def update_info_sensor_tool(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbSensorToolID.value()
		else:
			self.page.sbSensorToolID.setValue(ID)
		self.tool_sensor_exists = self.tool_sensor.load(ID)

		if self.tool_sensor_exists:
			self.page.pbSensorToolEditNew.setText("edit")
			if self.tool_sensor.size is None:
				self.page.dsbSensorToolSize.setValue(0)
				self.page.dsbSensorToolSize.clear()
			else:
				self.page.dsbSensorToolSize.setValue(self.tool_sensor.size)
			self.page.listSensorToolComments.clear()
			for comment in self.tool_sensor.comments:
				self.page.listSensorToolComments.addItem(comment)
			self.page.pteSensorToolWriteComment.clear()

		else:
			self.page.pbSensorToolEditNew.setText("new")
			self.page.dsbSensorToolSize.setValue(0)
			self.page.dsbSensorToolSize.clear()
			self.page.listSensorToolComments.clear()
			self.page.pteSensorToolWriteComment.clear()

	@enforce_mode(['view','editing_sensor_tool','editing_sensor_tray','editing_pcb_tray','editing_assembly_tray'])
	def update_info_pcb_tool(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbPcbToolID.value()
		else:
			self.page.sbPcbToolID.setValue(ID)
		self.tool_pcb_exists = self.tool_pcb.load(ID)

		if self.tool_pcb_exists:
			self.page.pbPcbToolEditNew.setText("edit")
			if self.tool_pcb.size is None:
				self.page.dsbPcbToolSize.setValue(0)
				self.page.dsbPcbToolSize.clear()
			else:
				self.page.dsbPcbToolSize.setValue(self.tool_pcb.size)
			self.page.listPcbToolComments.clear()
			for comment in self.tool_pcb.comments:
				self.page.listPcbToolComments.addItem(comment)
			self.page.ptePcbToolWriteComment.clear()

		else:
			self.page.pbPcbToolEditNew.setText("new")
			self.page.dsbPcbToolSize.setValue(0)
			self.page.dsbPcbToolSize.clear()
			self.page.listPcbToolComments.clear()
			self.page.ptePcbToolWriteComment.clear()

	@enforce_mode(['view','editing_sensor_tool','editing_pcb_tool','editing_pcb_tray','editing_assembly_tray'])
	def update_info_sensor_tray(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbSensorTrayID.value()
		else:
			self.page.sbSensorTrayID.setValue(ID)
		self.tray_component_sensor_exists = self.tray_component_sensor.load(ID)

		if self.tray_component_sensor_exists:
			self.page.pbSensorTrayEditNew.setText("edit")
			if self.tray_component_sensor.size is None:
				self.page.dsbSensorTraySize.setValue(0)
				self.page.dsbSensorTraySize.clear()
			else:
				self.page.dsbSensorTraySize.setValue(self.tray_component_sensor.size)
			self.page.listSensorTrayComments.clear()
			for comment in self.tray_component_sensor.comments:
				self.page.listSensorTrayComments.addItem(comment)
			self.page.pteSensorTrayWriteComment.clear()

		else:
			self.page.pbSensorTrayEditNew.setText("new")
			self.page.dsbSensorTraySize.setValue(0)
			self.page.dsbSensorTraySize.clear()
			self.page.listSensorTrayComments.clear()
			self.page.pteSensorTrayWriteComment.clear()

	@enforce_mode(['view','editing_sensor_tool','editing_pcb_tool','editing_sensor_tray','editing_assembly_tray'])
	def update_info_pcb_tray(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbPcbTrayID.value()
		else:
			self.page.sbPcbTrayID.setValue(ID)
		self.tray_component_pcb_exists = self.tray_component_pcb.load(ID)

		if self.tray_component_pcb_exists:
			self.page.pbPcbTrayEditNew.setText("edit")
			if self.tray_component_pcb.size is None:
				self.page.dsbPcbTraySize.setValue(0)
				self.page.dsbPcbTraySize.clear()
			else:
				self.page.dsbPcbTraySize.setValue(self.tray_component_pcb.size)
			self.page.listPcbTrayComments.clear()
			for comment in self.tray_component_pcb.comments:
				self.page.listPcbTrayComments.addItem(comment)
			self.page.ptePcbTrayWriteComment.clear()

		else:
			self.page.pbPcbTrayEditNew.setText("new")
			self.page.dsbPcbTraySize.setValue(0)
			self.page.dsbPcbTraySize.clear()
			self.page.listPcbTrayComments.clear()
			self.page.ptePcbTrayWriteComment.clear()

	@enforce_mode(['view','editing_sensor_tool','editing_pcb_tool','editing_sensor_tray','editing_pcb_tray'])
	def update_info_assembly_tray(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbAssemblyTrayID.value()
		else:
			self.page.sbAssemblyTrayID.setValue(ID)
		self.tray_assembly_exists = self.tray_assembly.load(ID)

		if self.tray_assembly_exists:
			self.page.pbAssemblyTrayEditNew.setText("edit")
			if self.tray_assembly.size is None:
				self.page.dsbAssemblyTraySize.setValue(0)
				self.page.dsbAssemblyTraySize.clear()
			else:
				self.page.dsbAssemblyTraySize.setValue(self.tray_assembly.size)
			self.page.listAssemblyTrayComments.clear()
			for comment in self.tray_assembly.comments:
				self.page.listAssemblyTrayComments.addItem(comment)
			self.page.pteAssemblyTrayWriteComment.clear()

		else:
			self.page.pbAssemblyTrayEditNew.setText("new")
			self.page.dsbAssemblyTraySize.setValue(0)
			self.page.dsbAssemblyTraySize.clear()
			self.page.listAssemblyTrayComments.clear()
			self.page.pteAssemblyTrayWriteComment.clear()

	@enforce_mode('view')
	def update_info(self,*args,**kwargs):
		self.update_info_sensor_tool()
		self.update_info_pcb_tool()
		self.update_info_sensor_tray()
		self.update_info_pcb_tray()
		self.update_info_assembly_tray()



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

		self.page.dsbSensorToolSize  .setEnabled(mode_editing_sensor_tool  )
		self.page.dsbPcbToolSize     .setEnabled(mode_editing_pcb_tool     )
		self.page.dsbSensorTraySize  .setEnabled(mode_editing_sensor_tray  )
		self.page.dsbPcbTraySize     .setEnabled(mode_editing_pcb_tray     )
		self.page.dsbAssemblyTraySize.setEnabled(mode_editing_assembly_tray)

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
		self.mode = 'editing_sensor_tool'
		if not self.tool_sensor_exists:
			self.tool_sensor.new(self.page.sbSensorToolID.value())
		self.update_elements()

	@enforce_mode('editing_sensor_tool')
	def cancel_editing_sensor_tool(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.update_info_sensor_tool()

	@enforce_mode('editing_sensor_tool')
	def save_editing_sensor_tool(self,*args,**kwargs):
		comments = []
		for i in range(self.page.listSensorToolComments.count()):
			comments.append(self.page.listSensorToolComments.item(i).text())
		self.tool_sensor.comments = comments
		size = self.page.dsbSensorToolSize.value()
		if size == 0.0:
			size = None
		self.tool_sensor.size = size
		self.tool_sensor.save()
		self.mode='view'
		self.update_elements()
		self.update_info_sensor_tool()

	@enforce_mode('editing_sensor_tool')
	def add_comment_sensor_tool(self,*args,**kwargs):
		text = self.page.pteSensorToolWriteComment.toPlainText()
		if text:
			self.page.listSensorToolComments.addItem(text)
			self.page.pteSensorToolWriteComment.clear()

	@enforce_mode('editing_sensor_tool')
	def delete_comment_sensor_tool(self,*args,**kwargs):
		index = self.page.listSensorToolComments.currentRow()
		if index >= 0:
			self.page.listSensorToolComments.takeItem(index)



	@enforce_mode('view')
	def start_editing_pcb_tool(self,*args,**kwargs):
		self.mode = 'editing_pcb_tool'
		if not self.tool_pcb_exists:
			self.tool_pcb.new(self.page.sbPcbToolID.value())
		self.update_elements()

	@enforce_mode('editing_pcb_tool')
	def cancel_editing_pcb_tool(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.update_info_pcb_tool()

	@enforce_mode('editing_pcb_tool')
	def save_editing_pcb_tool(self,*args,**kwargs):
		comments = []
		for i in range(self.page.listPcbToolComments.count()):
			comments.append(self.page.listPcbToolComments.item(i).text())
		self.tool_pcb.comments = comments
		size = self.page.dsbPcbToolSize.value()
		if size == 0.0:
			size = None
		self.tool_pcb.size = size
		self.tool_pcb.save()
		self.mode='view'
		self.update_elements()
		self.update_info_pcb_tool()

	@enforce_mode('editing_pcb_tool')
	def add_comment_pcb_tool(self,*args,**kwargs):
		text = self.page.ptePcbToolWriteComment.toPlainText()
		if text:
			self.page.listPcbToolComments.addItem(text)
			self.page.ptePcbToolWriteComment.clear()

	@enforce_mode('editing_pcb_tool')
	def delete_comment_pcb_tool(self,*args,**kwargs):
		index = self.page.listPcbToolComments.currentRow()
		if index >= 0:
			self.page.listPcbToolComments.takeItem(index)



	@enforce_mode('view')
	def start_editing_sensor_tray(self,*args,**kwargs):
		self.mode = 'editing_sensor_tray'
		if not self.tray_component_sensor_exists:
			self.tray_component_sensor.new(self.page.sbSensorTrayID.value())
		self.update_elements()

	@enforce_mode('editing_sensor_tray')
	def cancel_editing_sensor_tray(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.update_info_sensor_tray()

	@enforce_mode('editing_sensor_tray')
	def save_editing_sensor_tray(self,*args,**kwargs):
		comments = []
		for i in range(self.page.listSensorTrayComments.count()):
			comments.append(self.page.listSensorTrayComments.item(i).text())
		self.tray_component_sensor.comments = comments
		size = self.page.dsbSensorTraySize.value()
		if size == 0.0:
			size = None
		self.tray_component_sensor.size = size
		self.tray_component_sensor.save()
		self.mode='view'
		self.update_elements()
		self.update_info_sensor_tray()

	@enforce_mode('editing_sensor_tray')
	def add_comment_sensor_tray(self,*args,**kwargs):
		text = self.page.pteSensorTrayWriteComment.toPlainText()
		if text:
			self.page.listSensorTrayComments.addItem(text)
			self.page.pteSensorTrayWriteComment.clear()

	@enforce_mode('editing_sensor_tray')
	def delete_comment_sensor_tray(self,*args,**kwargs):
		index = self.page.listSensorTrayComments.currentRow()
		if index >= 0:
			self.page.listSensorTrayComments.takeItem(index)



	@enforce_mode('view')
	def start_editing_pcb_tray(self,*args,**kwargs):
		self.mode = 'editing_pcb_tray'
		if not self.tray_component_pcb_exists:
			self.tray_component_pcb.new(self.page.sbPcbTrayID.value())
		self.update_elements()

	@enforce_mode('editing_pcb_tray')
	def cancel_editing_pcb_tray(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.update_info_pcb_tray()

	@enforce_mode('editing_pcb_tray')
	def save_editing_pcb_tray(self,*args,**kwargs):
		comments = []
		for i in range(self.page.listPcbTrayComments.count()):
			comments.append(self.page.listPcbTrayComments.item(i).text())
		self.tray_component_pcb.comments = comments
		size = self.page.dsbPcbTraySize.value()
		if size == 0.0:
			size = None
		self.tray_component_pcb.size = size
		self.tray_component_pcb.save()
		self.mode='view'
		self.update_elements()
		self.update_info_pcb_tray()

	@enforce_mode('editing_pcb_tray')
	def add_comment_pcb_tray(self,*args,**kwargs):
		text = self.page.ptePcbTrayWriteComment.toPlainText()
		if text:
			self.page.listPcbTrayComments.addItem(text)
			self.page.ptePcbTrayWriteComment.clear()

	@enforce_mode('editing_pcb_tray')
	def delete_comment_pcb_tray(self,*args,**kwargs):
		index = self.page.listPcbTrayComments.currentRow()
		if index >= 0:
			self.page.listPcbTrayComments.takeItem(index)



	@enforce_mode('view')
	def start_editing_assembly_tray(self,*args,**kwargs):
		self.mode = 'editing_assembly_tray'
		self.update_elements()

	@enforce_mode('editing_assembly_tray')
	def cancel_editing_assembly_tray(self,*args,**kwargs):
		self.mode='view'
		self.update_elements()
		self.update_info_assembly_tray()

	@enforce_mode('editing_assembly_tray')
	def save_editing_assembly_tray(self,*args,**kwargs):
		comments = []
		for i in range(self.page.listAssemblyTrayComments.count()):
			comments.append(self.page.listAssemblyTrayComments.item(i).text())
		self.tray_assembly.comments = comments
		size = self.page.dsbAssemblyTraySize.value()
		if size == 0.0:
			size = None
		self.tray_assembly.size = size
		self.tray_assembly.save()
		self.mode='view'
		self.update_elements()
		self.update_info_assembly_tray()

	@enforce_mode('editing_assembly_tray')
	def add_comment_assembly_tray(self,*args,**kwargs):
		text = self.page.pteAssemblyTrayWriteComment.toPlainText()
		if text:
			self.page.listAssemblyTrayComments.addItem(text)
			self.page.pteAssemblyTrayWriteComment.clear()

	@enforce_mode('editing_assembly_tray')
	def delete_comment_assembly_tray(self,*args,**kwargs):
		index = self.page.listAssemblyTrayComments.currentRow()
		if index >= 0:
			self.page.listAssemblyTrayComments.takeItem(index)




	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		keys = kwargs.keys()

		if 'sensor_tool' in keys:
			self.update_info_sensor_tool(kwargs['sensor_tool'])
		if "pcb_tool" in keys:
			self.update_info_pcb_tool(kwargs['pcb_tool'])
		if "sensor_tray" in keys:
			self.update_info_sensor_tray(kwargs['sensor_tray'])
		if "pcb_tray" in keys:
			self.update_info_pcb_tray(kwargs['pcb_tray'])
		if "assembly_tray" in keys:
			self.update_info_assembly_tray(kwargs['assembly_tray'])

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
