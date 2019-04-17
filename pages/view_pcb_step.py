PAGE_NAME = "view_pcb_step"
OBJECTTYPE = "PCB_step"
DEBUG = False

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.fm        = fm
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.info = None
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

	@enforce_mode('setup')
	def rig(self):
		self.page.sbPCBStepID.valueChanged.connect(self.update_info)
		self.page.pbGoModule1.clicked.connect(self.goModule1)
		self.page.pbGoModule2.clicked.connect(self.goModule2)
		self.page.pbGoModule3.clicked.connect(self.goModule3)
		self.page.pbGoModule4.clicked.connect(self.goModule4)
		self.page.pbGoModule5.clicked.connect(self.goModule5)
		self.page.pbGoModule6.clicked.connect(self.goModule6)

		self.page.pbPCBStepNew.clicked.connect(self.startCreating)
		self.page.pbPCBStepEdit.clicked.connect(self.startEditing)
		self.page.pbPCBStepSave.clicked.connect(self.saveEditig)
		self.page.pbPCBStepCancel.clicked.connect(self.cancelEditing)


	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:ID = self.page.sbPCBStepID.value()
		self.info = self.fm.loadObjectDetails(OBJECTTYPE,ID)
		self.updateElements(use_info = True)

	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		if use_info:
			if self.info is None:
				self.page.leWho         .setText("")
				self.page.leDate        .setText("")
				self.page.leTime        .setText("")
				self.page.leCureStart   .setText("")
				self.page.leCureStop    .setText("")
				self.page.leCureDuration.setText("")
				self.page.leCureTemp    .setText("")
				self.page.leCureHumidity.setText("")
				self.page.sbModule1.setValue(-1); self.page.sbModule1.clear()
				self.page.sbModule2.setValue(-1); self.page.sbModule2.clear()
				self.page.sbModule3.setValue(-1); self.page.sbModule3.clear()
				self.page.sbModule4.setValue(-1); self.page.sbModule4.clear()
				self.page.sbModule5.setValue(-1); self.page.sbModule5.clear()
				self.page.sbModule6.setValue(-1); self.page.sbModule6.clear()
				self.page.sbTool1.setValue(-1); self.page.sbTool1.clear()
				self.page.sbTool2.setValue(-1); self.page.sbTool2.clear()
				self.page.sbTool3.setValue(-1); self.page.sbTool3.clear()
				self.page.sbTool4.setValue(-1); self.page.sbTool4.clear()
				self.page.sbTool5.setValue(-1); self.page.sbTool5.clear()
				self.page.sbTool6.setValue(-1); self.page.sbTool6.clear()
				self.page.leAralditeBatch.setText("")

			else:
				self.page.leWho         .setText( self.info['who']           )
				self.page.leDate        .setText( self.info['date']          )
				self.page.leTime        .setText( self.info['time']          )
				self.page.leCureStart   .setText( self.info['cure_start']    )
				self.page.leCureStop    .setText( self.info['cure_stop']     )
				self.page.leCureDuration.setText( self.info['cure_duration'] )
				self.page.leCureTemp    .setText( self.info['cure_temp']     )
				self.page.leCureHumidity.setText( self.info['cure_hum']      )
				self.page.sbModule1.setValue(     self.info['module_1']      )
				self.page.sbModule2.setValue(     self.info['module_2']      )
				self.page.sbModule3.setValue(     self.info['module_3']      )
				self.page.sbModule4.setValue(     self.info['module_4']      )
				self.page.sbModule5.setValue(     self.info['module_5']      )
				self.page.sbModule6.setValue(     self.info['module_6']      )
				self.page.sbTool1.setValue(       self.info['tool_1']        )
				self.page.sbTool2.setValue(       self.info['tool_2']        )
				self.page.sbTool3.setValue(       self.info['tool_3']        )
				self.page.sbTool4.setValue(       self.info['tool_4']        )
				self.page.sbTool5.setValue(       self.info['tool_5']        )
				self.page.sbTool6.setValue(       self.info['tool_6']        )
				self.page.leAralditeBatch.setText(self.info['araldite_batch'])

				if self.info['module_1'] == -1: self.page.sbModule1.clear()
				if self.info['module_2'] == -1: self.page.sbModule2.clear()
				if self.info['module_3'] == -1: self.page.sbModule3.clear()
				if self.info['module_4'] == -1: self.page.sbModule4.clear()
				if self.info['module_5'] == -1: self.page.sbModule5.clear()
				if self.info['module_6'] == -1: self.page.sbModule6.clear()
				if self.info['tool_1'  ] == -1: self.page.sbTool1.clear()
				if self.info['tool_2'  ] == -1: self.page.sbTool2.clear()
				if self.info['tool_3'  ] == -1: self.page.sbTool3.clear()
				if self.info['tool_4'  ] == -1: self.page.sbTool4.clear()
				if self.info['tool_5'  ] == -1: self.page.sbTool5.clear()
				if self.info['tool_6'  ] == -1: self.page.sbTool6.clear()

		self.setMainSwitchingEnabled( self.mode == 'view' )
		self.page.sbPCBStepID.setEnabled( self.mode == 'view' )

		self.page.leWho.setReadOnly(          not (self.mode in ['editing','creating']) )
		self.page.leDate.setReadOnly(         not (self.mode in ['editing','creating']) )
		self.page.leTime.setReadOnly(         not (self.mode in ['editing','creating']) )
		self.page.leCureStart.setReadOnly(    not (self.mode in ['editing','creating']) )
		self.page.leCureStop.setReadOnly(     not (self.mode in ['editing','creating']) )
		self.page.leCureDuration.setReadOnly( not (self.mode in ['editing','creating']) )
		self.page.leCureTemp.setReadOnly(     not (self.mode in ['editing','creating']) )
		self.page.leCureHumidity.setReadOnly( not (self.mode in ['editing','creating']) )
		self.page.sbModule1.setReadOnly(      not (self.mode in ['editing','creating']) )
		self.page.sbModule2.setReadOnly(      not (self.mode in ['editing','creating']) )
		self.page.sbModule3.setReadOnly(      not (self.mode in ['editing','creating']) )
		self.page.sbModule4.setReadOnly(      not (self.mode in ['editing','creating']) )
		self.page.sbModule5.setReadOnly(      not (self.mode in ['editing','creating']) )
		self.page.sbModule6.setReadOnly(      not (self.mode in ['editing','creating']) )
		self.page.sbTool1.setReadOnly(        not (self.mode in ['editing','creating']) )
		self.page.sbTool2.setReadOnly(        not (self.mode in ['editing','creating']) )
		self.page.sbTool3.setReadOnly(        not (self.mode in ['editing','creating']) )
		self.page.sbTool4.setReadOnly(        not (self.mode in ['editing','creating']) )
		self.page.sbTool5.setReadOnly(        not (self.mode in ['editing','creating']) )
		self.page.sbTool6.setReadOnly(        not (self.mode in ['editing','creating']) )
		self.page.leAralditeBatch.setReadOnly(not (self.mode in ['editing','creating']) )

		self.page.pbGoModule1.setEnabled( self.mode == 'view' and self.page.sbModule1.value()>=0 )
		self.page.pbGoModule2.setEnabled( self.mode == 'view' and self.page.sbModule2.value()>=0 )
		self.page.pbGoModule3.setEnabled( self.mode == 'view' and self.page.sbModule3.value()>=0 )
		self.page.pbGoModule4.setEnabled( self.mode == 'view' and self.page.sbModule4.value()>=0 )
		self.page.pbGoModule5.setEnabled( self.mode == 'view' and self.page.sbModule5.value()>=0 )
		self.page.pbGoModule6.setEnabled( self.mode == 'view' and self.page.sbModule6.value()>=0 )

		self.page.pbPCBStepNew.setEnabled(    (self.mode == 'view') and     (self.info is None) )
		self.page.pbPCBStepEdit.setEnabled(   (self.mode == 'view') and not (self.info is None) )
		self.page.pbPCBStepSave.setEnabled(    self.mode in ['editing','creating'] )
		self.page.pbPCBStepCancel.setEnabled(  self.mode in ['editing','creating'] )


	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if self.info is None:
			self.mode = 'creating'
			self.updateElements()
		else:
			pass

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if self.info is None:
			pass
		else:
			self.mode = 'editing'
			self.updateElements()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditig(self,*args,**kwargs):
		ID = self.page.sbPCBStepID.value()
		details = {
			'ID'            : ID,
			'who'           : str(self.page.leWho.text()),
			'date'          : str(self.page.leDate.text()),
			'time'          : str(self.page.leTime.text()),
			'cure_start'    : str(self.page.leCureStart.text()),
			'cure_stop'     : str(self.page.leCureStop.text()),
			'cure_duration' : str(self.page.leCureDuration.text()),
			'cure_temp'     : str(self.page.leCureTemp.text()),
			'cure_hum'      : str(self.page.leCureHumidity.text()),
			'module_1'      : self.page.sbModule1.value(),
			'module_2'      : self.page.sbModule2.value(),
			'module_3'      : self.page.sbModule3.value(),
			'module_4'      : self.page.sbModule4.value(),
			'module_5'      : self.page.sbModule5.value(),
			'module_6'      : self.page.sbModule6.value(),
			'tool_1'        : self.page.sbTool1.value(),
			'tool_2'        : self.page.sbTool2.value(),
			'tool_3'        : self.page.sbTool3.value(),
			'tool_4'        : self.page.sbTool4.value(),
			'tool_5'        : self.page.sbTool5.value(),
			'tool_6'        : self.page.sbTool6.value(),
			'araldite_batch': str(self.page.leAralditeBatch.text()),
			}
		new = self.mode == 'creating'
		self.fm.changeObjectDetails(OBJECTTYPE,ID,details,new)
		self.mode = 'view'
		self.update_info()

	@enforce_mode('view')
	def goModule1(self,*args,**kwargs):
		ID = self.page.sbModule1.value()
		if ID >= 0:
			self.setUIPage('modules',ID=ID)
		else:
			return

	@enforce_mode('view')
	def goModule2(self,*args,**kwargs):
		ID = self.page.sbModule2.value()
		if ID >= 0:
			self.setUIPage('modules',ID=ID)
		else:
			return

	@enforce_mode('view')
	def goModule3(self,*args,**kwargs):
		ID = self.page.sbModule3.value()
		if ID >= 0:
			self.setUIPage('modules',ID=ID)
		else:
			return

	@enforce_mode('view')
	def goModule4(self,*args,**kwargs):
		ID = self.page.sbModule4.value()
		if ID >= 0:
			self.setUIPage('modules',ID=ID)
		else:
			return

	@enforce_mode('view')
	def goModule5(self,*args,**kwargs):
		ID = self.page.sbModule5.value()
		if ID >= 0:
			self.setUIPage('modules',ID=ID)
		else:
			return

	@enforce_mode('view')
	def goModule6(self,*args,**kwargs):
		ID = self.page.sbModule6.value()
		if ID >= 0:
			self.setUIPage('modules',ID=ID)
		else:
			return

	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is int):
				raise TypeError("Expected type <int> for ID; got <{}>".format(type(ID)))
			if ID < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbPCBStepID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
