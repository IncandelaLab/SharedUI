from PyQt5 import QtCore
import time
import datetime
from filemanager import fm

PAGE_NAME = "view_shipment"
DEBUG = False

#NEW, WIP

PAGE_NAME_DICT = {
	'baseplate':   'baseplates',
	'sensor':      'sensors',
	'pcb':         'PCBs',
	'protomodule': 'protomodules',
	'module':      'modules',
}

#assorted useful vars

STATUS_NO_ISSUES = "valid (no issues)"
STATUS_ISSUES    = "invalid (issues present)"

I_DATE_CONFLICT = "date sent must be earlier than date received"
I_PART_DNE = "part(s) do not exist: {}"  #'PCB 10', etc
I_PART_DUP = "part(s) have duplicates: {}"
I_SENDER_DNE = "sender name is empty"
I_RECEIVER_DNE = "receiver name is empty"
I_FEDEX_DNE = "FedEx ID is empty"

INDEX_SEND_RECV = {
	'sending':0,
	'receiving':1,
}

"""INDEX_PART_TYPES = {
	'Module':fm.module(),
	'Baseplate':fm.baseplate(),
	'Sensor':fm.sensor(),
	'PCB':fm.pcb(),
	'Protomodule':fm.protomodule(),
}"""


class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.shipment = fm.shipment()
		self.shipment_exists = None

		self.mode = 'setup'

		self.partsToRemove = []  #NEW:  Store list of items that were deleted from the shipment
		# Necessary--the items' shipmentlists can't be updated until save() is called, but they're not stored anywhere else!


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
		self.page.sbShipmentID.valueChanged.connect(self.update_info)

		self.page.pbShipmentNew.clicked.connect(self.startCreating)
		self.page.pbShipmentEdit.clicked.connect(self.startEditing)
		self.page.pbShipmentSave.clicked.connect(self.saveEditing)
		self.page.pbShipmentCancel.clicked.connect(self.cancelEditing)

		self.page.pbSentNow.clicked.connect(self.setShipmentSentNow)
		self.page.pbReceivedNow.clicked.connect(self.setShipmentReceivedNow)

		self.page.pbAddPart.clicked.connect(self.addPart)
		self.page.pbDeleteSelected.clicked.connect(self.deleteSelected)
		self.page.pbGoToSelected.clicked.connect(self.goToSelected)


	@enforce_mode('view')
	def update_info(self,ID=None,*args,**kwargs):
		if ID is None:
			ID = self.page.sbShipmentID.value()
		else:
			self.page.sbShipmentID.setValue(ID)

		self.shipment_exists = self.shipment.load(ID)

		#Added for loops in updateInfo
		if self.shipment.modules is None:       self.shipment.modules      = []
		if self.shipment.baseplates is None:    self.shipment.baseplates   = []
		if self.shipment.sensors is None:       self.shipment.sensors      = []
		if self.shipment.pcbs is None:          self.shipment.pcbs         = []
		if self.shipment.protomodules is None:  self.shipment.protomodules = []

		#Fill displayed part list w/ part information
		self.page.lwPartList.clear()
		#NOTE:  WARNING:  Currently causes an error, bc modules aren't immediately stored.
		for module in self.shipment.modules:  #'module' is a STRING
			self.page.lwPartList.addItem("module " + str(module))
		for baseplate in self.shipment.baseplates:
			self.page.lwPartList.addItem("baseplate " + str(baseplate))
		for sensor in self.shipment.sensors:
			self.page.lwPartList.addItem("sensor " + str(sensor))
		for pcb in self.shipment.pcbs:
			self.page.lwPartList.addItem("pcb " + str(pcb))
		for protomodule in self.shipment.protomodules:
			self.page.lwPartList.addItem("protomodule " + str(protomodule))

		if not self.shipment.sendOrReceive is None:
			self.page.cbShipmentType.setCurrentIndex(INDEX_SEND_RECV.get(self.shipment.sendOrReceive))
		self.page.leSender  .setText("" if self.shipment.sender   is None else self.shipment.sender)
		self.page.leReceiver.setText("" if self.shipment.receiver is None else self.shipment.receiver)
		self.page.leFedEx   .setText("" if self.shipment.fedex_id is None else self.shipment.fedex_id)
		if not self.shipment.date_sent is None:
			self.page.dSent.setDate(QtCore.QDate(*self.shipment.date_sent))
		if not self.shipment.date_received is None:
			self.page.dReceived.setDate(QtCore.QDate(*self.shipment.date_received))
		#self.page.cbPartType.setCurrentIndex() should only be used once

		self.updateElements()


	@enforce_mode(['view','editing','creating'])
	def updateElements(self,use_info=False):
		shipment_exists      = self.shipment_exists

		mode_view     = self.mode == 'view'
		mode_editing  = self.mode == 'editing'
		mode_creating = self.mode == 'creating'

		self.setMainSwitchingEnabled(mode_view)
		self.page.sbShipmentID.setEnabled(mode_view)
		
		self.page.pbShipmentNew.setEnabled(    mode_view and not shipment_exists  )
		self.page.pbShipmentEdit.setEnabled(   mode_view and     shipment_exists  )
		self.page.pbShipmentSave.setEnabled(   mode_editing or mode_creating )
		self.page.pbShipmentCancel.setEnabled( mode_editing or mode_creating )

		self.page.cbShipmentType.setEnabled(   mode_creating or mode_editing  )
		self.page.leSender.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.leReceiver.setReadOnly( not (mode_creating or mode_editing) )
		self.page.leFedEx.setReadOnly(    not (mode_creating or mode_editing) )

		self.page.dSent.setReadOnly(      not (mode_creating or mode_editing) )
		self.page.pbSentNow.setEnabled(        mode_creating or mode_editing  )
		self.page.dReceived.setReadOnly(  not (mode_creating or mode_editing) )
		self.page.pbReceivedNow.setEnabled(    mode_creating or mode_editing  )

		self.page.lwPartList.setEnabled(       mode_creating or mode_editing  )
		self.page.pbAddPart.setEnabled(        mode_creating or mode_editing  )
		self.page.cbPartType.setEnabled(       mode_creating or mode_editing  )
		#self.page.sbPartID.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.lePartID.setReadOnly(   not (mode_creating or mode_editing) )
		self.page.pbDeleteSelected.setEnabled( mode_creating or mode_editing  )
		

	#NEW
	@enforce_mode(['editing','creating'])
	def updateIssues(self,*args,**kwargs):
		issues = []
		objects = []
		
		dneObjects = []
		dupObjects = []

		for i in range(self.page.lwPartList.count()):
			#First, make sure the part exists.  Err if it doesn't.
			item = self.page.lwPartList.item(i)
			tmp = item.text().split()
			partType = tmp[0]
			partID = int(tmp[1])
			partTemp = None
			partExists = True
			if partType == "module":
				partTemp = fm.module()
				partExists = partTemp.load(partID)
			elif partType == "baseplate":
				partTemp = fm.baseplate()
				partExists = partTemp.load(partID)
			elif partType == "sensor":
				partTemp = fm.sensor()
				partExists = partTemp.load(partID)
			elif partType == "pcb":
				partTemp = fm.module()
				partExists = partTemp.load(partID)
			elif partType == "protomodule":
				partTemp = fm.module()
				partExists = partTemp.load(partID)
			if not partExists:
				dneObjects.append(partType + " " + str(partID))

			#Next, check for duplicate items.  Remove these quietly.
			firstOccurrence = True  #Do NOT remove the first occurence of an item--it's the original!
			for j in range(self.page.lwPartList.count()):
				itemj = self.page.lwPartList.item(j)
				if itemj.text() == item.text():
					if firstOccurrence:  firstOccurrence = False
					else:
						if itemj.text() not in dupObjects:
							dupObjects.append(itemj.text())
		if dneObjects:
			issues.append(I_PART_DNE.format(', '.join([str(_) for _ in dneObjects])))
		if dupObjects:
			issues.append(I_PART_DUP.format(', '.join([str(_) for _ in dupObjects])))


		#Check sender/receiver existence
		if self.page.leSender.text() == "":
			issues.append(I_SENDER_DNE)
		if self.page.leReceiver.text() == "":
			issues.append(I_RECEIVER_DNE)
		if self.page.leFedEx.text() == "":
			issues.append(I_FEDEX_DNE)

		#Check send/receive dates
		if self.page.dSent.date() > self.page.dReceived.date():
			issues.append(I_DATE_CONFLICT)

		#Check that all parts exist


		self.page.lwErrList.clear()
		for issue in issues:
			self.page.lwErrList.addItem(issue)

		if issues:
			self.page.leStatus.setText(STATUS_ISSUES)
			self.page.pbShipmentSave.setEnabled(False)
		else:
			self.page.leStatus.setText(STATUS_NO_ISSUES)
			self.page.pbShipmentSave.setEnabled(True)



	@enforce_mode('view')
	def startCreating(self,*args,**kwargs):
		if not self.shipment_exists:
			ID = self.page.sbShipmentID.value()
			self.mode = 'creating'
			self.shipment.new(ID)
			self.updateElements()
		else:
			pass

	@enforce_mode('view')
	def startEditing(self,*args,**kwargs):
		if self.shipment_exists:
			self.mode = 'editing'
			self.updateElements()

	@enforce_mode(['editing','creating'])
	def cancelEditing(self,*args,**kwargs):
		self.mode = 'view'
		self.update_info()

	@enforce_mode(['editing','creating'])
	def saveEditing(self,*args,**kwargs):

		self.shipment.sender        = str(self.page.leSender.text()  ) if str(self.page.leSender.text()  ) else None
		self.shipment.receiver      = str(self.page.leReceiver.text()) if str(self.page.leReceiver.text()) else None
		self.shipment.fedex_id      = str(self.page.leFedEx.text()   ) if str(self.page.leFedEx.text()   ) else None
		self.shipment.date_sent     = [*self.page.dSent.date().getDate()]
		self.shipment.date_received = [*self.page.dReceived.date().getDate()]
		self.shipment.sendOrReceive = self.page.cbShipmentType.currentText().replace(' parts','')


		self.shipment.modules      = [] #All info has already been loaded into lwPartList, so no worries about info loss
		self.shipment.baseplates   = []
		self.shipment.sensors      = []
		self.shipment.pcbs         = []
		self.shipment.protomodules = []

		#Now find all parts in this shipment and add ID to 'shipment' var.
		#NOTE:  All parts should exist.  If not, there's something wrong with updateIssues().
		for i in range(self.page.lwPartList.count()):
			#Strip out part name
			tmp = self.page.lwPartList.item(i).text().split()
			partType = tmp[0]
			partID = int(tmp[1])
			partTemp = None
			if partType == "module":
				self.shipment.modules.append(partID)
				partTemp = fm.module()
			elif partType == "baseplate":
				self.shipment.baseplates.append(partID)
				partTemp = fm.baseplate()
			elif partType == "sensor":
				self.shipment.sensors.append(partID)
				partTemp = fm.sensor()
			elif partType == "pcb":
				self.shipment.pcbs.append(partID)
				partTemp = fm.pcb()
			elif partType == "protomodule":
				self.shipment.protomodules.append(partID)
				partTemp = fm.protomodule()
			partTemp.load(partID)
			if partID not in partTemp.shipments:
				partTemp.shipments.append(self.shipment.ID)
			partTemp.save()

		for partName in self.partsToRemove:
			tmp = partName.split()
			partType = tmp[0]
			partID = int(tmp[1])
			partTemp = None
			if partType == "module":
				if partID in self.shipment.modules:       self.shipment.modules.remove(partID)
				partTemp = fm.module()
			elif partType == "baseplate":
				if partID in self.shipment.baseplates:    self.shipment.baseplates.remove(partID)
				partTemp = fm.baseplate()
			elif partType == "sensor":
				if partID in self.shipment.sensors:       self.shipment.sensors.remove(partID)
				partTemp = fm.sensor()
			elif partType == "pcb":
				if partID in self.shipment.pcbs:          self.shipment.pcbs.remove(partID)
				partTemp = fm.pcb()
			elif partType == "protomodule":
				if partID in self.shipment.protomodules:  self.shipment.protomodules.remove(partID)
				partTemp = fm.protomodule()
			if partID is None:
				print("ERROR:  Attempted to load a None part ID in view_shipment.")
			if not partTemp.load(partID):
				pass  #This WILL be called if someone accidentally adds a nonexistent part and then deletes it.  No action required.

			if self.shipment.ID in partTemp.shipments: print("Shipment present in item shiplist; removing")
			partTemp.shipments = [x for x in partTemp.shipments if x != self.shipment.ID]
			partTemp.save()

		self.shipment.add_part_to_list()
		self.shipment.save()
		self.mode = 'view'
		self.update_info()
		self.partsToRemove.clear()


	@enforce_mode(['editing','creating'])
	def setShipmentSentNow(self,*args,**kwargs):
		localtime = time.localtime()
		self.page.dSent.setDate(QtCore.QDate(*localtime[0:3]))
		self.updateIssues()


	@enforce_mode(['editing','creating'])
	def setShipmentReceivedNow(self,*args,**kwargs):
		localtime = time.localtime()
		self.page.dReceived.setDate(QtCore.QDate(*localtime[0:3]))
		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def addPart(self,*args,**kwargs):  #WIP:  Ensure no duplicates, possibly the multiple shipments thing
		#partID = self.page.sbPartID.value()
		partID = self.page.lePartID.text()
		partName = self.page.cbPartType.currentText() + " " + str(partID)
		if partName == '':  return

		self.page.lwPartList.addItem(partName)
		if partName in self.partsToRemove:  #Make sure not to remove it upon save!
			self.partsToRemove.remove(partName)

		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def deleteSelected(self,*args,**kwargs):

		row = self.page.lwPartList.currentRow()  #from view_baseplate example
		cname = self.page.lwPartList.currentItem().text()
		#check for duplicates.  If dups are present, don't append to partsToRemove--there's still a copy of the part in the lw!
		if len(self.page.lwPartList.findItems(cname, QtCore.Qt.MatchExactly)) == 1:
			self.partsToRemove.append(cname)
		if row>=0:
			self.page.lwPartList.takeItem(row)

		self.updateIssues()

	@enforce_mode(['editing','creating'])
	def goToSelected(self,*args,**kwargs):
		name = self.page.lwPartList.currentItem().text().split()
		partType = name[0]
		partID = name[1]
		pageName = PAGE_NAME_DICT[partType]
		self.setUIPage(pageName, ID=partID)

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

	@enforce_mode('view')
	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			ID = kwargs['ID']
			if not (type(ID) is str):
				raise TypeError("Expected type <str> for ID; got <{}>".format(type(ID)))
			if int(ID) < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbShipmentID.setValue(int(ID))

	@enforce_mode('view')
	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))
		self.update_info()
