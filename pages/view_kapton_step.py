from PyQt5 import QtCore
import time
import datetime

NO_DATE = [2000,1,1]

PAGE_NAME = "view_kapton_step"
OBJECTTYPE = "kapton_step"
DEBUG = False

STATUS_NO_ISSUES = "valid (no issues)"
STATUS_ISSUES    = "invalid (issues present)"

# tooling and supplies
I_TRAY_COMPONENT_DNE = "sensor component tray does not exist or is not selected"
I_TRAY_ASSEMBLY_DNE  = "assembly tray does not exist or is not selected"
I_BATCH_ARALDITE_DNE     = "araldite batch does not exist or is not selected"
I_BATCH_ARALDITE_EXPIRED = "araldite batch has expired"

# baseplates
I_BASEPLATE_NOT_READY  = "baseplate(s) in position(s) {} is not ready for kapton application. reason: {}"

# kapton inspection
I_KAPTON_INSPECTION_NOT_DONE = "kapton inspection not done for position(s) {}"
I_KAPTON_INSPECTION_ON_EMPTY = "kapton inspection checked for empty position(s) {}"

# rows / positions
I_NO_PARTS_SELECTED = "no parts have been selected"
I_ROWS_INCOMPLETE   = "positions {} are partially filled"
I_TOOL_SENSOR_DNE      = "sensor tool(s) in position(s) {} do not exist"
I_BASEPLATE_DNE        = "baseplate(s) in position(s) {} do not exist"
I_TOOL_SENSOR_DUPLICATE = "same sensor tool is selected on multiple positions: {}"
I_BASEPLATE_DUPLICATE   = "same baseplate is selected on multiple positions: {}"

# compatibility
I_SIZE_MISMATCH = "size mismatch between some selected objects"
I_SIZE_MISMATCH_6 = "* list of 6-inch objects selected: {}"
I_SIZE_MISMATCH_8 = "* list of 8-inch objects selected: {}"

# location
I_LOCATION = "some selected objects are not at this location: {}"

class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.tools_sensor = [fm.tool_sensor() for _ in range(6)]
		self.baseplates   = [fm.baseplate()   for _ in range(6)]
		self.tray_component_sensor = fm.tray_component_sensor()
		self.tray_assembly         = fm.tray_assembly()
		self.batch_araldite        = fm.batch_araldite()

		self.step_kapton = fm.step_kapton()
		self.step_kapton_exists = None

		self.MAC = fm.MAC

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
		self.sb_tools = [
			self.page.sbTool1,
			self.page.sbTool2,
			self.page.sbTool3,
			self.page.sbTool4,
			self.page.sbTool5,
			self.page.sbTool6,
		]
		self.pb_go_tools = [
			self.page.pbGoTool1,
			self.page.pbGoTool2,
			self.page.pbGoTool3,
			self.page.pbGoTool4,
			self.page.pbGoTool5,
			self.page.pbGoTool6,
		]

		self.sb_baseplates = [
			self.page.sbBaseplate1,
			self.page.sbBaseplate2,
			self.page.sbBaseplate3,
			self.page.sbBaseplate4,
			self.page.sbBaseplate5,
			self.page.sbBaseplate6,
		]
		self.pb_go_baseplates = [
			self.page.pbGoBaseplate1,
			self.page.pbGoBaseplate2,
			self.page.pbGoBaseplate3,
			self.page.pbGoBaseplate4,
			self.page.pbGoBaseplate5,
			self.page.pbGoBaseplate6,
		]
		self.ck_kaptons_inspected = [
			self.page.ckKaptonInspected1,
			self.page.ckKaptonInspected2,
			self.page.ckKaptonInspected3,
			self.page.ckKaptonInspected4,
			self.page.ckKaptonInspected5,
			self.page.ckKaptonInspected6,
			]

		for i in range(6):
			self.pb_go_tools[i].clicked.connect(self.goTool)
			self.pb_go_baseplates[i].clicked.connect(self.goBaseplate)

			self.sb_tools[i].editingFinished.connect(             self.loadToolSensor )
			self.sb_baseplates[i].editingFinished.connect(        self.loadBaseplate  )
			self.ck_kaptons_inspected[i].clicked.connect( self.updateIssues   )

		self.page.sbTrayComponent.editingFinished.connect( self.loadTrayComponentSensor )
		self.page.sbTrayAssembly.editingFinished.connect(  self.loadTrayAssembly        )
		self.page.sbBatchAraldite.editingFinished.connect( self.loadBatchAraldite       )

		self.page.sbID.valueChanged.connect(self.update_info)

		self.page.pbNew.clicked.connect(    self.startCreating )
		self.page.pbEdit.clicked.connect(   self.startEditing  )
		self.page.pbSave.clicked.connect(   self.saveEditing   )
		self.page.pbCancel.clicked.connect( self.cancelEditing )

		self.page.pbGoBatchAraldite.clicked.connect( self.goBatchAraldite )
		self.page.pbGoTrayAssembly.clicked.connect(  self.goTrayAssembly  )
		self.page.pbGoTrayComponent.clicked.connect( self.goTrayComponent )

		self.page.pbDatePerformedNow.clicked.connect( self.setDatePerformedNow )
		self.page.pbCureStartNow.clicked.connect(     self.setCureStartNow     )
		self.page.pbCureStopNow.clicked.connect(      self.setCureStopNow      )

	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbID.value()
		else:
			self.page.sbID.setValue(ID)

		self.step_kapton_exists = self.step_kapton.load(ID)

		self.page.listIssues.clear()
		self.page.leStatus.clear()

		if self.step_kapton_exists:
			self.page.leUserPerformed.setText(self.step_kapton.user_performed)

			date_performed = self.step_kapton.date_performed
			if not (date_performed is None):
				self.page.dPerformed.setDate(QtCore.QDate(*self.step_kapton.date_performed))
			else:
				self.page.dPerformed.setDate(QtCore.QDate(*NO_DATE))

			cure_start = self.step_kapton.cure_start
			cure_stop  = self.step_kapton.cure_stop
			if cure_start is None:
				self.page.dtCureStart.setDate(QtCore.QDate(*NO_DATE))
				self.page.dtCureStart.setTime(QtCore.QTime(0,0,0))
			else:
				localtime = list(time.localtime(cure_start))
				self.page.dtCureStart.setDate(QtCore.QDate(*localtime[0:3]))
				self.page.dtCureStart.setTime(QtCore.QTime(*localtime[3:6]))

			if cure_stop is None:
				self.page.dtCureStop.setDate(QtCore.QDate(*NO_DATE))
				self.page.dtCureStop.setTime(QtCore.QTime(0,0,0))
			else:
				localtime = list(time.localtime(cure_stop))
				self.page.dtCureStop.setDate(QtCore.QDate(*localtime[0:3]))
				self.page.dtCureStop.setTime(QtCore.QTime(*localtime[3:6]))

			self.page.leCureDuration.setText(str(int(self.step_kapton.cure_duration)) if not (self.step_kapton.cure_duration is None) else "")
			self.page.leCureTemperature.setText(self.step_kapton.cure_temperature)
			self.page.leCureHumidity.setText(self.step_kapton.cure_humidity)

			self.page.sbBatchAraldite.setValue(self.step_kapton.batch_araldite if not (self.step_kapton.batch_araldite is None) else -1)
			self.page.sbTrayAssembly.setValue( self.step_kapton.tray_assembly  if not (self.step_kapton.tray_assembly  is None) else -1)
			self.page.sbTrayComponent.setValue(self.step_kapton.tray_component_sensor if not (self.step_kapton.tray_component_sensor is None) else -1)

			if not (self.step_kapton.tools is None):
				for i in range(6):
					self.sb_tools[i].setValue(self.step_kapton.tools[i] if not (self.step_kapton.tools[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_tools[i].setValue(-1)

			if not (self.step_kapton.baseplates is None):
				for i in range(6):
					self.sb_baseplates[i].setValue(self.step_kapton.baseplates[i] if not (self.step_kapton.baseplates[i] is None) else -1)
			else:
				for i in range(6):
					self.sb_baseplates[i].setValue(-1)

			if not (self.step_kapton.kaptons_inspected is None):
				for i in range(6):
					self.ck_kaptons_inspected[i].setChecked(False if self.step_kapton.kaptons_inspected[i] is None else self.step_kapton.kaptons_inspected[i])
			else:
				for i in range(6):
					self.ck_kaptons_inspected[i].setChecked(False)

		else:
			self.page.leUserPerformed.setText("")
			self.page.dPerformed.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStart.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStart.setTime(QtCore.QTime(0,0,0))
			self.page.dtCureStop.setDate(QtCore.QDate(*NO_DATE))
			self.page.dtCureStop.setTime(QtCore.QTime(0,0,0))
			self.page.leCureDuration.setText("")
			self.page.leCureTemperature.setText("")
			self.page.leCureHumidity.setText("")
			self.page.sbBatchAraldite.setValue(-1)
			self.page.sbTrayComponent.setValue(-1)
			self.page.sbTrayAssembly.setValue(-1)
			for i in range(6):
				self.sb_tools[i].setValue(-1)
				self.sb_baseplates[i].setValue(-1)
				self.ck_kaptons_inspected[i].setChecked(False)

		for i in range(6):
			if self.sb_tools[i].value() == -1:self.sb_tools[i].clear()
			if self.sb_baseplates[i].value() == -1:self.sb_baseplates[i].clear()

		if self.page.sbBatchAraldite.value() == -1:self.page.sbBatchAraldite.clear()
		if self.page.sbTrayComponent.value() == -1:self.page.sbTrayComponent.clear()
		if self.page.sbTrayAssembly.value() == -1:self.page.sbTrayAssembly.clear()

		self.updateElements()

	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'
		tools_exist      = [_.value()>=0 for _ in self.sb_tools     ]
		baseplates_exist = [_.value()>=0 for _ in self.sb_baseplates]
		step_kapton_exists = self.step_kapton_exists

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbID.setEnabled(mode_view)

		self.page.pbDatePerformedNow.setEnabled(mode_creating or mode_editing)
		self.page.pbCureStartNow    .setEnabled(mode_creating or mode_editing)
		self.page.pbCureStopNow     .setEnabled(mode_creating or mode_editing)

		self.page.leUserPerformed  .setReadOnly(mode_view)
		self.page.dPerformed       .setReadOnly(mode_view)
		self.page.dtCureStart      .setReadOnly(mode_view)
		self.page.dtCureStop       .setReadOnly(mode_view)
		self.page.leCureTemperature.setReadOnly(mode_view)
		self.page.leCureHumidity   .setReadOnly(mode_view)
		self.page.sbTrayComponent  .setReadOnly(mode_view)
		self.page.sbTrayAssembly   .setReadOnly(mode_view)
		self.page.sbBatchAraldite  .setReadOnly(mode_view)

		self.page.pbGoTrayComponent.setEnabled(mode_view and self.page.sbTrayComponent.value() >= 0)
		self.page.pbGoTrayAssembly .setEnabled(mode_view and self.page.sbTrayAssembly .value() >= 0)
		self.page.pbGoBatchAraldite.setEnabled(mode_view and self.page.sbBatchAraldite.value() >= 0)

		for i in range(6):
			self.sb_tools[i].setReadOnly(mode_view)
			self.sb_baseplates[i].setReadOnly(mode_view)
			self.pb_go_tools[i].setEnabled(     mode_view and tools_exist[i]     )
			self.pb_go_baseplates[i].setEnabled(mode_view and baseplates_exist[i])
			self.ck_kaptons_inspected[i].setEnabled(mode_creating or mode_editing)

		self.page.pbNew.setEnabled(    mode_view and not step_kapton_exists )
		self.page.pbEdit.setEnabled(   mode_view and     step_kapton_exists )
		self.page.pbSave.setEnabled(   mode_creating or mode_editing        )
		self.page.pbCancel.setEnabled( mode_creating or mode_editing        )

		#NEW:  May resolve the num_kapton issue...should at least init num_kaptons to 0.
		#baseplates = []
		#print("Initializing num_kaptons")
		for i in range(6):
			if self.baseplates[i].num_kaptons == None:
				#print("Baseplate "+str(i)+" was None")
				self.baseplates[i].num_kaptons = 0
			#initializes only...maybe this will work.
			#The below was commented until recently...
			self.baseplates.append(self.sb_baseplates[i].value() if self.sb_baseplates[i].value() >= 0 else None)
			if not self.baseplates[i] == None:
				which_kapton_layer = None
				if (self.baseplates[i].step_kapton is None) or (self.baseplates[i].step_kapton == self.ID):
					which_kapton_layer = 1
					#print("kapton layer 1...")
				elif (baseplates[i].step_kapton_2 is None) or (self.baseplates[i].step_kapton_2 == self.ID):
					which_kapton_layer = 2
					#print("kapton layer 2...")
				num_kaptons = 0
				if not self.baseplates[i].step_kapton   is None: num_kaptons += 1
				if not self.baseplates[i].step_kapton_2 is None: num_kaptons += 1
				self.baseplates[i].num_kaptons = num_kaptons



	@enforce_mode(['editing','creating'])
	def loadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tools_sensor[i].load(self.sb_tools[i].value()     )
			self.baseplates[i].load(  self.sb_baseplates[i].value())
		self.tray_component_sensor.load(self.page.sbTrayComponent.value())
		self.tray_assembly.load(        self.page.sbTrayAssembly.value() )
		self.batch_araldite.load(       self.page.sbBatchAraldite.value())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def unloadAllObjects(self,*args,**kwargs):
		for i in range(6):
			self.tools_sensor[i].clear()
			self.baseplates[i].clear()
		self.tray_component_sensor.clear()
		self.tray_assembly.clear()
		self.batch_araldite.clear()
		
	@enforce_mode(['editing','creating'])
	def loadToolSensor(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.tools_sensor[which].load(self.sb_tools[which].value())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadBaseplate(self, *args, **kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		self.baseplates[which].load(self.sb_baseplates[which].value())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadTrayComponentSensor(self, *args, **kwargs):
		print("LOADING TRAY COMPONENT SENSOR")
		print("value = "+str(self.page.sbTrayComponent.value()))
		self.tray_component_sensor.load(self.page.sbTrayComponent.value())
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadTrayAssembly(self, *args, **kwargs):
		print("Loading tray assembly")
		self.tray_assembly.load(self.page.sbTrayAssembly.value() )
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def loadBatchAraldite(self, *args, **kwargs):
		self.batch_araldite.load(self.page.sbBatchAraldite.value())
		self.updateIssues()


	@enforce_mode(['editing','creating'])
	def updateIssues(self,*args,**kwargs):
		issues = []
		objects = []

		print("Calling updateIssues")

		# tooling and supplies
		#NOT WORKING:
		if self.tray_component_sensor.ID is None:
			print("tray comp ID is None")
			issues.append(I_TRAY_COMPONENT_DNE)
		else:
			objects.append(self.tray_component_sensor)

		if self.tray_assembly.ID is None:
			issues.append(I_TRAY_ASSEMBLY_DNE)
		else:
			objects.append(self.tray_assembly)

		if self.batch_araldite.ID is None:
			issues.append(I_BATCH_ARALDITE_DNE)
		else:
			objects.append(self.batch_araldite)
			if not (self.batch_araldite.date_expires is None):
				expires = datetime.date(*self.batch_araldite.date_expires)
				today = datetime.date(*time.localtime()[:3])
				if today > expires:
					issues.append(I_BATCH_ARALDITE_EXPIRED)
		

		# rows
		sensor_tools_selected = [_.value()     for _ in self.sb_tools            ]
		baseplates_selected   = [_.value()     for _ in self.sb_baseplates       ]
		kaptons_inspected     = [_.isChecked() for _ in self.ck_kaptons_inspected]

		sensor_tool_duplicates = [_ for _ in range(6) if sensor_tools_selected[_] >= 0 and sensor_tools_selected.count(sensor_tools_selected[_])>1]
		baseplate_duplicates   = [_ for _ in range(6) if baseplates_selected[_]   >= 0 and baseplates_selected.count(  baseplates_selected[_]  )>1]

		if sensor_tool_duplicates:
			issues.append(I_TOOL_SENSOR_DUPLICATE.format(', '.join([str(_+1) for _ in sensor_tool_duplicates])))
		if baseplate_duplicates:
			issues.append(I_BASEPLATE_DUPLICATE.format(', '.join([str(_+1) for _ in baseplate_duplicates])))

		rows_empty = []
		rows_full = []
		rows_incomplete = []
		rows_kapton_inspection_on_empty = []
		rows_kapton_inspection_not_done = []
		rows_baseplate_dne = []
		rows_tool_sensor_dne = []

		for i in range(6):
			num_parts = 0

			if sensor_tools_selected[i] >= 0:
				num_parts += 1
				objects.append(self.tools_sensor[i])
				if self.tools_sensor[i].ID is None:
					rows_tool_sensor_dne.append(i)

			if baseplates_selected[i] >= 0:
				num_parts += 1
				objects.append(self.baseplates[i])
				if self.baseplates[i].ID is None:
					rows_baseplate_dne.append(i)
				else:
					#NOTE:  Max flatness is 250 um.  I think.
					print("calling ready_step "+str(i)+", num_k is "+str(self.baseplates[i].num_kaptons))
					ready, reason = self.baseplates[i].ready_step_kapton(self.page.sbID.value(), .250)
					if not ready:
						issues.append(I_BASEPLATE_NOT_READY.format(i,reason))

			if num_parts == 0:
				rows_empty.append(i)
				if kaptons_inspected[i]:
					rows_kapton_inspection_on_empty.append(i)

			elif num_parts == 2:
				rows_full.append(i)
				if not kaptons_inspected[i]:
					rows_kapton_inspection_not_done.append(i)
			else:
				rows_incomplete.append(i)

		if not (len(rows_full) or len(rows_incomplete)):
			issues.append(I_NO_PARTS_SELECTED)

		if rows_incomplete:
			issues.append(I_ROWS_INCOMPLETE.format(', '.join(map(str,rows_incomplete))))

		if rows_kapton_inspection_on_empty:
			issues.append(I_KAPTON_INSPECTION_ON_EMPTY.format(', '.join([str(_+1) for _ in rows_kapton_inspection_on_empty])))
		if rows_kapton_inspection_not_done:
			issues.append(I_KAPTON_INSPECTION_NOT_DONE.format(', '.join([str(_+1) for _ in rows_kapton_inspection_not_done])))

		if rows_baseplate_dne:
			issues.append(I_BASEPLATE_DNE.format(', '.join([str(_+1) for _ in rows_baseplate_dne])))
		if rows_tool_sensor_dne:
			issues.append(I_TOOL_SENSOR_DNE.format(', '.join([str(_+1) for _ in rows_tool_sensor_dne])))


		objects_6in = []
		objects_8in = []
		objects_not_here = []

		for obj in objects:

			size = getattr(obj, "size", None)
			if size in [6.0, 6, '6']:
				objects_6in.append(obj)
			if size in [8.0, 8, '8']:
				objects_8in.append(obj)

			location = getattr(obj, "location", None)
			if not (location in [None, self.MAC]):
				objects_not_here.append(obj)

		if len(objects_6in) and len(objects_8in):
			issues.append(I_SIZE_MISMATCH)
			issues.append(I_SIZE_MISMATCH_6.format(', '.join([str(_) for _ in objects_6in])))
			issues.append(I_SIZE_MISMATCH_8.format(', '.join([str(_) for _ in objects_8in])))

		if objects_not_here:
			issues.append(I_LOCATION.format([str(_) for _ in objects_not_here]))


		self.page.listIssues.clear()
		for issue in issues:
			self.page.listIssues.addItem(issue)

		if issues:
			self.page.leStatus.setText(STATUS_ISSUES)
			self.page.pbSave.setEnabled(False)

		else:
			self.page.leStatus.setText(STATUS_NO_ISSUES)
			self.page.pbSave.setEnabled(True)


	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if not self.step_kapton_exists:
			ID = self.page.sbID.value()
			self.mode = 'creating'
			self.step_kapton.new(ID)
			self.updateElements()
			self.loadAllObjects()

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if self.step_kapton_exists:
			self.mode = 'editing'
			self.updateElements()
			self.loadAllObjects()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):

		self.step_kapton.user_performed = str( self.page.leUserPerformed.text() )

		if self.page.dPerformed.date().year() == NO_DATE[0]:
			self.step_kapton.date_performed = None
		else:
			self.step_kapton.date_performed = [*self.page.dPerformed.date().getDate()]

		if self.page.dtCureStart.date().year() == NO_DATE[0]:
			self.step_kapton.cure_start = None
		else:
			self.step_kapton.cure_start = self.page.dtCureStart.dateTime().toTime_t()

		if self.page.dtCureStop.date().year() == NO_DATE[0]:
			self.step_kapton.cure_stop = None
		else:
			self.step_kapton.cure_stop  = self.page.dtCureStop.dateTime().toTime_t()

		self.step_kapton.cure_humidity    = str(self.page.leCureHumidity.text())
		self.step_kapton.cure_temperature = str(self.page.leCureTemperature.text())

		tools = []
		baseplates = []
		kaptons_inspected = []
		for i in range(6):
			tools.append(self.sb_tools[i].value() if self.sb_tools[i].value() >= 0 else None)
			baseplates.append(self.sb_baseplates[i].value() if self.sb_baseplates[i].value() >= 0 else None)
			kaptons_inspected.append(self.ck_kaptons_inspected[i].isChecked() if self.sb_baseplates[i].value() >= 0 else None)
		self.step_kapton.tools = tools
		self.step_kapton.baseplates = baseplates
		self.step_kapton.kaptons_inspected = kaptons_inspected

		self.step_kapton.tray_component_sensor = self.page.sbTrayComponent.value() if self.page.sbTrayComponent.value() >= 0 else None
		self.step_kapton.tray_assembly         = self.page.sbTrayAssembly.value()  if self.page.sbTrayAssembly.value()  >= 0 else None
		self.step_kapton.batch_araldite        = self.page.sbBatchAraldite.value() if self.page.sbBatchAraldite.value() >= 0 else None

		print("Saving kapton step")
		self.step_kapton.save()
		self.unloadAllObjects()
		self.mode = 'view'
		self.update_info()

	def goTool(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1 # last character of sender name is integer 1 through 6; subtract one for zero index
		tool = self.sb_tools[which].value()
		self.setUIPage('tooling',tool_sensor=tool)

	def goBaseplate(self,*args,**kwargs):
		sender_name = str(self.page.sender().objectName())
		which = int(sender_name[-1]) - 1
		baseplate = self.sb_baseplates[which].value()
		self.setUIPage('baseplates',ID=baseplate)

	def goBatchAraldite(self,*args,**kwargs):
		batch_araldite = self.page.sbBatchAraldite.value()
		self.setUIPage('supplies',batch_araldite=batch_araldite)

	def goTrayComponent(self,*args,**kwargs):
		tray_component_sensor = self.page.sbTrayComponent.value()
		self.setUIPage('tooling',tray_component_sensor=tray_component_sensor)

	def goTrayAssembly(self,*args,**kwargs):
		tray_assembly = self.page.sbTrayAssembly.value()
		self.setUIPage('tooling',tray_assembly=tray_assembly)

	def setDatePerformedNow(self, *args, **kwargs):
		self.page.dPerformed.setDate(QtCore.QDate(*time.localtime()[:3]))

	def setCureStartNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStart.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStart.setTime(QtCore.QTime(*localtime[3:6]))

	def setCureStopNow(self, *args, **kwargs):
		localtime = time.localtime()
		self.page.dtCureStop.setDate(QtCore.QDate(*localtime[0:3]))
		self.page.dtCureStop.setTime(QtCore.QTime(*localtime[3:6]))

	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is int):
				raise TypeError("Expected type <int> for ID; got <{}>".format(type(ID)))
			if ID < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbID.setValue(ID)

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
