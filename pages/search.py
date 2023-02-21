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
	'Baseplate':   'Baseplates',
	'Sensor':      'Sensors',
	'PCB':         'PCBs',
	'Protomodule': 'Protomodules',
	'Module':      'Modules',
}

PART_DICT = {
	'Baseplate':   fm.baseplate,
	'Sensor':      fm.sensor,
	'PCB':         fm.pcb,
	#'Protomodule': fm.protomodule,
	#'Module':      fm.module,
}

PART_NAME_DICT = {
	'Baseplate':  '{mat_type} Baseplate {channel_density} {geometry}',
	'Sensor':     '{sen_type} Si Sensor {channel_density} {geometry}',
	'PCB':        'PCB {channel_density} {geometry}',
	'Protomdule': '% {sen_type} ProtoModule {channel_density} {geometry}',
	'Module':     '% {sen_type} Si Module {channel_density} {geometry}'
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



class func(object):
	def __init__(self,fm,page,setUIPage,setSwitchingEnabled):
		self.page      = page
		self.setUIPage = setUIPage
		self.setMainSwitchingEnabled = setSwitchingEnabled

		self.mode = 'setup'


	def setup(self):
		self.rig()
		self.mode = 'view'
		print("{} setup completed".format(PAGE_NAME))

	def rig(self):
		self.page.pbSearch.clicked.connect(self.search)

		self.page.cbPartType.currentIndexChanged.connect( self.updateElements )
		self.page.ckUseDate.stateChanged.connect( self.updateElements )

		self.page.pbClearParams.clicked.connect( self.clearParams )

		self.page.pbClearResults.clicked.connect( self.clearResults )
		self.page.pbGoToPart.clicked.connect( self.goToPart )

		self.updateElements()

	def search(self, *args, **kwargs):  # WIP WIP WIP
		self.clearResults()

		search_dict = { self.page.cbInstitution:'location', self.page.cbShape:'geometry',
						self.page.cbMaterial:'mat_type', self.page.cbThickness:'sen_type',
						self.page.cbChannelDensity:'channel_density', self.page.cbPCBType:'pcb_type',
						self.page.cbAssmRow:'tray_row', self.page.cbAssmCol:'tray_col' }
		# Treat dCreated separately
		# Search criteria will be a dict:  'var_name':'value'
		search_criteria = {}
		for box, qty in search_dict.items():
			if box.isEnabled() and box.currentText() != '':
				search_criteria[qty] = box.currentText() if box.currentText() != "" else "%"
		search_date = self.page.ckUseDate.isChecked()
		if search_date:
			d_c = self.page.dCreated.date()
			d_created = "{}-{}-{}".format(d_c.month(), d_c.day(), d_c.year())

		"""
		# Now using DB_CURSOR:
		if fm.ENABLE_DB_COMMUNICATION:
			# In general:  Assemble sql query w/ items from search_dict
			part_type = self.page.cbPartType.currentText()
			# pt_template:  should be %_%_NAME_HD_% etc - % for anything not specified
			pt_template = PART_NAME_DICT[part_type].format(mat_type=search_criteria['mat_type'],
														   sen_type=search_criteria['sen_type'],
														   channel_density=search_criteria['channel_density'].
														   geometry=search_criteria['geometry'], )
			sql_query = "select kp.DISPLAY_NAME, p.*
from CMS_HGC_CORE_CONSTRUCT.PARTS p
inner join CMS_HGC_CORE_CONSTRUCT.KINDS_OF_PARTS kp
on p.KIND_OF_PART_ID = kp.KIND_OF_PART_ID
where kp.DISPLAY_NAME LIKE \'%{}%\'".format(pt_template)
			DB_CURSOR.execute(sql_query)
			columns = [col[0] for col in DB_CURSOR.description]
			DB_CURSOR.rowfactory = lambda *args: dict(zip(columns, args))
			data_part = DB_CURSOR.fetchone()
			if data_part is None:
				# Part not found
				print("SQL query found nothing")
		"""	

		
		part_type = self.page.cbPartType.currentText()
		if not part_type in PART_DICT.keys():  # disabled proto/modules
			print("WARNING: {}s are currently disabled".format(part_type))
			self.displayResults([])
			return

		part_temp = PART_DICT[part_type]()  # Constructs instance of searched-for class
		part_file_name = os.sep.join([ fm.DATADIR, 'partlist', part_type.lower()+'s.json' ])
		with open(part_file_name, 'r') as opfl:
			part_list = json.load(opfl)

		# Go through all parts in part_list, load each, and check qtys...
		found_parts = []
		for part_id, date in part_list.items():
			part_temp.load(part_id)
			found = True
			for qty, value in search_criteria.items():
				if str(getattr(part_temp, qty, None)) != value:  found = False
			if found:  found_parts.append("{} {}".format(part_type, part_id))
		

		self.displayResults(found_parts)


	
	def updateElements(self):
		# Update enabled/disabled elements
		# institution, geometry are always enabled (EXCEPT when assembly steps added)
		print("search, updateElements")
		part_type = self.page.cbPartType.currentText()
		self.page.cbInstitution   .setEnabled(part_type != '')
		self.page.cbShape         .setEnabled(part_type != '')
		self.page.cbMaterial      .setEnabled(part_type == 'Baseplate')
		self.page.cbThickness     .setEnabled(part_type == 'Sensor')
		self.page.cbChannelDensity.setEnabled(True)
		self.page.cbPCBType       .setEnabled(part_type == 'PCB')
		self.page.ckUseDate       .setEnabled(part_type == 'Protomodule' or part_type == 'Module')
		useDate = self.page.ckUseDate.isChecked()
		self.page.dCreated        .setReadOnly(not useDate or not (part_type == 'Protomodule' or part_type == 'Module'))
		self.page.cbAssmRow       .setEnabled(part_type == 'Protomodule' or part_type == 'Module')
		self.page.cbAssmCol       .setEnabled(part_type == 'Protomodule' or part_type == 'Module')

	def clearParams(self,*args,**kwargs):
		for wdgt in [self.page.cbInstituion,     self.page.cbShape,
					 self.page.cbMaterial,       self.page.cbThickness,
					 self.page.cbChannelDensity, self.page.cbPCBType,
					 self.page.cbAssmRow,        self.page.cbAssmCol
					]:
			wdgt.setCurrentIndex(0)

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


