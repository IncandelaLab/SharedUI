from PyQt5 import QtCore
import time
import datetime
import os
import json
from filemanager import fm

PAGE_NAME = "search"
DEBUG = False

#NEW, WIP

PAGE_NAME_DICT = {
	'baseplate':   'baseplates',
	'sensor':      'sensors',
	'pcb':         'PCBs',
	'protomodule': 'protomodules',
	'module':      'modules',
	#'shipment':    'shipments',
}

PART_DICT = {
	'baseplate':   fm.baseplate,
	'sensor':      fm.sensor,
	'pcb':         fm.pcb,
	'protomodule': fm.protomodule,
	'module':      fm.module,
	#'shipment':    fm.shipment,
}

INDEX_INSTITUTION = {
	'':0,
	'CERN':1,
	'FNAL':2,
	'UCSB':3,
	'UMN':4,
	'HEPHY':5,
	'HPK':6,
}

INDEX_SHAPE = {
	'':0,
	'full':1,
	'half':2,
	'five':3,
	'three':4,
	'semi':5,
	'semi(-)':6,
	'choptwo':7,
}

INDEX_MATERIAL = {
	'':0,
	'CuW':1,
	'PCB':2,
}

INDEX_TYPE = {
	'':0,
	'120 um':1,
	'200 um':2,
	'300 um':3,
}

INDEX_TYPE = {
	'':0,
	'HGCROCV1':1,
	'HGCROCV2':2,
	'HGCROCV3':3,
	'SKIROCV1':4,
	'SKIROCV2':5,
	'SKIROCV3':6,
	'HGCROC dummy':7,
}

INDEX_CHANNEL = {
	'':0,
	'HD':1,
	'LD':2,
}



#assorted useful vars

STATUS_NO_ISSUES = "valid (no issues)"
STATUS_ISSUES    = "invalid (issues present)"

I_DATE_CONFLICT = "date sent must be earlier than date received"
I_PART_DNE = "part(s) do not exist: {}"  #'PCB 10', etc
I_PART_DUP = "part(s) have duplicates: {}"
I_SENDER_DNE = "sender name is empty"
I_RECEIVER_DNE = "receiver name is empty"


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

		self.mode = 'setup'

	# This fn is so search page can access the part lists of the other relevant pages...
	# outdated
	#def setPageList(self, pageList):
	#	self.pageList = pageList


	def setup(self):
		self.rig()
		self.mode = 'view'
		print("{} setup completed".format(PAGE_NAME))
		#self.update_info()

	def rig(self):
		"""
		self.page.pbSearchInstitution.clicked.connect(self.searchInstitution)
		self.page.pbSearchRecDate.clicked.connect(    self.searchRecDate)
		self.page.pbSearchBType.clicked.connect(      self.searchBType)
		self.page.pbSearchSType.clicked.connect(      self.searchSType)
		self.page.pbSearchPType.clicked.connect(      self.searchPType)
		"""
		self.page.pbSearch.clicked.connect(self.search)

		self.page.cbPartType.currentIndexChanged.connect( self.updateElements )
		self.page.ckUseDate.stateChanged.connect( self.updateElements )

		self.page.pbClearResults.clicked.connect(     self.clearResults)
		self.page.pbGoToPart.clicked.connect(         self.goToPart)

		self.page.lwPartList.setEnabled(True)
		self.updateElements()

	def search(self, *args, **kwargs):
		self.clearResults()
		part_type = self.page.cbPartType.currentText()
		part_temp = PART_DICT[part_type]()  # Constructs instance of searched-for class
		part_file_name = os.sep.join([ fm.DATADIR, 'partlist', part_type+'s.json' ])
		with open(part_file_name, 'r') as opfl:
			part_list = json.load(opfl)

		search_dict = { self.page.cbInstitution:'institution', self.page.cbShape:'shape',
						self.page.cbMaterial:'material', self.page.cbThickness:'type',
						self.page.cbChannelDensity:'resolution_type', self.page.cbPCBType:'type' }
		# Treat dCreated separately
		# Search criteria will be a dict:  'var_name':'value'
		search_criteria = {}
		for box, qty in search_dict.items():
			if box.isEnabled() and box.currentText != '':
				search_criteria[qty] = box.currentText()
		search_date = self.page.ckUseDate.isChecked()
		if search_date:
			d_c = self.page.dCreated.date()
			d_created = "{}-{}-{}".format(d_c.month(), d_c.day(), d_c.year())

		# Go through all parts in part_list, load each, and check qtys...
		found_parts = []
		for part_id, date in part_list.items():
			part_temp.load(part_id, query_db=False)
			found = True
			for qty, value in search_criteria.items():
				if getattr(part_temp, qty, None) != value:  found = False
			if found:  found_parts.append("{} {}".format(part_type, part_id))

		self.displayResults(found_parts)

		"""
		print("Searching for parts")
		# Go into the partlist.  Saved format is "name":"date created"
		# For each part, load it and check for the corresp attribute
		# - BUT do not load from DB!  load(query_db=False)
		partname = self.page.cbPartType.currentText()
		filename = os.sep.join([ fm.DATADIR, 'partlist', partname+'s.json' ])
		with open(filename, 'r') as opfl:
			part_list = json.load(opfl)

		found_parts = []

		# Check whether each part matches the search criteria
		for identifier in part_list:
			part = partclass()
			assert part.load(identifier)
			# Check all search criteria:
			for prop in {'institution':'cbInstitution', 'geometry':'cbShape', ''}
				if x.currentText() == loaded_part_text:
					found_parts.append(identifier)
		"""

	"""
	def searchInstitution(self,*args,**kwargs):
		print("Searching for institution...")
		self.clearResults()

		search_institution = self.page.cbInstitution.currentText()
		# A file for each searchable part type currently exists at fm.DATADIR/partlist/.
		# ...formatted as a list of ID numbers.  Load it w/ json.load() to retrieve...
		found_parts = []

		for partname, partclass in PART_DICT.items():
			if partname == 'shipment':  continue

			filename = os.sep.join([ fm.DATADIR, 'partlist', partname+'s.json' ])
			with open(filename, 'r') as opfl:
				part_list = json.load(opfl)

			# Check whether each part matches the search criteria
			for identifier in part_list:
				part = partclass()  # I am PRETTY sure this works
				assert part.load(identifier)
				if part.institution == search_institution:
					found_parts.append("{} {}".format(partname, identifier))

		self.displayResults(found_parts)


	def searchRecDate(self,*args,**kwargs):
		self.clearResults()
		search_date = [*self.page.dReceived.date().getDate()]
		print("Searching rec date!")
		found_parts = []

		for partname, partclass in PART_DICT.items():
			if partname != 'shipment':  continue

			filename = os.sep.join([ fm.DATADIR, 'partlist', partname+'s.json' ])
			with open(filename, 'r') as opfl:
				part_list = json.load(opfl)
			print("Found parts: ", part_list)
			# Check whether each part matches the search criteria
			for identifier in part_list:
				part = partclass()  # I am PRETTY sure this works
				assert part.load(identifier)
				print(part.date_received)
				print(search_date)
				if part.date_received == search_date:
					found_parts.append("{} {}".format(partname, identifier))

		self.displayResults(found_parts)

	def searchBType(self,*args,**kwargs):
		self.clearResults()
		search_btype = self.page.cbBType.currentText()
		
		found_parts = []

		for partname, partclass in PART_DICT.items():
			if partname != 'baseplate':  continue

			filename = os.sep.join([ fm.DATADIR, 'partlist', partname+'s.json' ])
			with open(filename, 'r') as opfl:
				part_list = json.load(opfl)

			# Check whether each part matches the search criteria
			for identifier in part_list:
				part = partclass()  # I am PRETTY sure this works
				assert part.load(identifier)
				if part.material == search_btype:
					found_parts.append("{} {}".format(partname, identifier))

		self.displayResults(found_parts)

	def searchSType(self,*args,**kwargs):
		self.clearResults()
		search_stype = self.page.cbSType.currentText()
		
		found_parts = []

		for partname, partclass in PART_DICT.items():
			if partname != 'sensor':  continue

			filename = os.sep.join([ fm.DATADIR, 'partlist', partname+'s.json' ])
			with open(filename, 'r') as opfl:
				part_list = json.load(opfl)

			# Check whether each part matches the search criteria
			for identifier in part_list:
				part = partclass()  # I am PRETTY sure this works
				assert part.load(identifier)
				if part.type == search_stype:
					found_parts.append("{} {}".format(partname, identifier))

		self.displayResults(found_parts)
	
	def searchPType(self,*args,**kwargs):
		self.clearResults()
		search_ptype = self.page.cbPType.currentText()
		
		found_parts = []

		for partname, partclass in PART_DICT.items():
			if partname != 'shipment':  continue

			filename = os.sep.join([ fm.DATADIR, 'partlist', partname+'s.json' ])
			with open(filename, 'r') as opfl:
				part_list = json.load(opfl)

			# Check whether each part matches the search criteria
			for identifier in part_list:
				part = partclass()  # I am PRETTY sure this works
				assert part.load(identifier)
				if part.type == search_ptype:
					found_parts.append("{} {}".format(partname, identifier))
		
		self.displayResults(found_parts)
	"""
	
	def updateElements(self):
		# Update enabled/disabled elements
		# institution, geometry are always enabled (EXCEPT when assembly steps added)
		part_type = self.page.cbPartType.currentText()
		self.page.cbInstitution   .setEnabled(part_type != '')
		self.page.cbShape         .setEnabled(part_type != '')
		self.page.cbMaterial      .setEnabled(part_type == 'baseplate')
		self.page.cbThickness     .setEnabled(part_type == 'sensor')
		self.page.cbChannelDensity.setEnabled(part_type == 'sensor')
		self.page.cbPCBType       .setEnabled(part_type == 'PCB')
		self.page.ckUseDate       .setEnabled(part_type != 'protomodule' and part_type != 'module')
		useDate = self.page.ckUseDate.isChecked()
		self.page.dCreated        .setReadOnly(not useDate or (part_type != 'protomodule' and part_type != 'module'))


	def clearResults(self,*args,**kwargs):
		# empty lwPartList
		self.page.lwPartList.clear()
		self.page.leStatus.setText("")

	def displayResults(self, displayList):
		if displayList == []:
			self.page.leStatus.setText("No results found")
			return

		for part in displayList:
			self.page.lwPartList.addItem(part)
		self.page.leStatus.setText("Results found!")

	def goToPart(self,*args,**kwargs):
		#print("CURRENTLY WIP; NEED TO IMPLEMENT THIS NEXT")
		name = self.page.lwPartList.currentItem().text().split()
		partType = name[0]
		partID = name[1]
		pageName = PAGE_NAME_DICT[partType]

		self.setUIPage(pageName, ID=partID)


	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			print("Warning:  attempted to pass search page an ID (there's probably a bug somewhere)")
			"""ID = kwargs['ID']
			if not (type(ID) is str):
				raise TypeError("Expected type <str> for ID; got <{}>".format(type(ID)))
			if int(ID) < 0:
				raise ValueError("ID cannot be negative")
			self.page.sbShipmentID.setValue(int(ID))"""

	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))


