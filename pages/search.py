from PyQt5 import QtCore
from PyQt5.QtWidgets import QComboBox, QCheckBox
import time
import datetime
import os
import json
from filemanager import fm, parts, tools, supplies

PAGE_NAME = "search"
DEBUG = False

#NEW, WIP

PAGE_NAME_DICT = {
	'Baseplate':   'Baseplates',
	'Sensor':      'Sensors',
	'PCB':         'PCBs',
	'Protomodule': 'Protomodules',
	'Module':      'Modules',
	'Tool':        'Tooling',
	'Supply':      'Supplies'
}

PART_DICT = {
	'Baseplate':   parts.baseplate,
	'Sensor':      parts.sensor,
	'PCB':         parts.pcb,
	'Protomodule': parts.protomodule,
	'Module':      parts.module
}

TOOL_SUPPLY_DICT = {
    # tools
	'Sensor tool'           : tools.tool_sensor,
	'PCB tool'              : tools.tool_pcb,
	'Assembly tray'         : tools.tray_assembly,
	'Sensor component tray' : tools.tray_component_sensor,
	'PCB component tray'    : tools.tray_component_pcb,
	# supplies
	'Araldite batch'        : supplies.batch_araldite,
	'Wedge batch'           : supplies.batch_wedge,
	'Sylgard batch'         : supplies.batch_sylgard,
	'Bond wire batch'       : supplies.batch_bond_wire,
	'Transfer tape 50um'    : supplies.batch_tape_50,
	'Transfer tape 125um'   : supplies.batch_tape_120
}

TOOL_SUPPLY_OBJNAME_CLSNAME = {}

PART_NAME_DICT = {
	'Baseplate':  '{mat_type} Baseplate {channel_density} {geometry}',
	'Sensor':     '{sen_type} Si Sensor {channel_density} {geometry}',
	'PCB':        'PCB {channel_density} {geometry}',
	'Protomodule': '% {sen_type} ProtoModule {channel_density} {geometry}',
	'Module':     '% {sen_type} Si Module {channel_density} {geometry}'
}

# Need to filter out all part types other than the ones used in the GUI.
# Ex want "120um Si Sensor HD Full" and NOT "300um LD Si Sensor Wafer"
PART_NAME_FILTER = {
	'Baseplate': '',
	# Easy, no filter needed
	'Sensor': """\nand regexp_like(kp.DISPLAY_NAME, \'.* .* Sensor (HD|LD) .*\')
and not kp.DISPLAY_NAME like \'%Halfmoon%\'""",
	# include: 120um Si Sensor HD Full
	# exclude: 120um Si Sensor HD Halfmoon-B
	# exclude: 300um LD Si Sensor Wafer
	# exclude: HPK Six Inch 256 Sensor Guard Ring
	#          % % Sensor [HD][LD] %
	#    NOT REGEXP '%Halfmoon%'
	'PCB': '\nand regexp_like(kp.DISPLAY_NAME, \'PCB (HD|LD)\')',
	# exclude:  PCB/Kapton Baseplate ..., PCB baseplate...
	'Protomodule': '',
	# No filter needed
	'Module': '',
	# No filter needed
}

INDEX_INSTITUTION = {
	'':0,
	'CERN':1,
	'FNAL':2,
	'UCSB':3,
	'UMN':4,
	'HEPHY':5,
	'HPK':6,
	'CMU':7,
	'TTU':8,
	'IHEP':9,
	'TIFR':10,
	'NTU':11,
	'FSU':12
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
		# search for parts
		self.page.pbSearch.clicked.connect(self.search)

		self.page.cbPartType.currentIndexChanged.connect( self.updateElements )
		self.page.ckUseDate.stateChanged.connect( self.updateElements )

		self.page.pbClearParams.clicked.connect( self.clearParams )

		self.page.pbClearResults.clicked.connect( self.clearResults )
		self.page.pbGoToPart.clicked.connect( self.goToPart )

		# search for tools and supplies
		self.page.pbSearch_2.clicked.connect(self.search_tool_supply)
		self.page.cbToolSupplyType.currentIndexChanged.connect( self.updateElements )
		self.page.cbEmpty.currentIndexChanged.connect( self.updateElements )
		self.page.cbExpired.currentIndexChanged.connect( self.updateElements )

		self.page.pbClearParams_2.clicked.connect( self.clearParams_tool_supply )

		self.page.pbClearResults_2.clicked.connect( self.clearResults_tool_supply )
		self.page.pbGoToToolSupply.clicked.connect( self.goToToolSupply )
		self.updateElements()

	def search(self, *args, **kwargs):  # WIP WIP WIP
		self.clearResults()

		part_type = self.page.cbPartType.currentText()
		if not part_type in PART_DICT.keys():
			print("WARNING: {}s are currently disabled".format(part_type))
			self.displayResults([], [])
			return
		part_temp = PART_DICT[part_type]()  # Constructs instance of searched-for class

		search_dict = { self.page.cbInstitution:'location', self.page.cbShape:'geometry',
						self.page.cbMaterial:'material', self.page.cbThickness:'sen_type',
						self.page.cbChannelDensity:'channel_density',
						self.page.cbAssmRow:"asm_row",
						self.page.cbAssmCol:"asm_col",
					  }

		# Treat dCreated separately
		# Search criteria will be a dict:  'var_name':'value'
		search_criteria = {}
		for box, qty in search_dict.items():
			if box.isEnabled(): # and box.currentText() != '':
				search_criteria[qty] = box.currentText() if box.currentText() != "" else "%"
		#search_date = self.page.ckUseDate.isChecked()
		#if search_date: # to implement
		#	d_c = self.page.dCreated.date()
		#	d_created = "{}-{}-{}".format(d_c.month(), d_c.day(), d_c.year())

		# Search for locally-stored parts:
		part_file_name = os.sep.join([ fm.DATADIR, 'partlist', part_type.lower()+'s.json' ])
		with open(part_file_name, 'r') as opfl:
			part_list = json.load(opfl)
		# Go through all parts in part_list, load each, and check search criteria...

		found_local_parts = {}
		for part_id, date in part_list.items():
			part_temp.load(part_id)
			found = True
			for qty, value in search_criteria.items():
				if value == '%':  continue  # "wildcard" option, ignore this
				if str(getattr(part_temp, qty, None)) != value:
					found = False
			if found:  found_local_parts[part_id] = part_temp.kind_of_part

		# Search for parts in DB:
		found_remote_parts = {}  # serial:type
		"""
		if fm.ENABLE_DB_COMMUNICATION:
			# In general:  Assemble sql query w/ items from search_dict
			# pt_template:  should be %_%_NAME_HD_% etc - % is a wildcard for anything not specified
			print("search_criteria is:\n", search_criteria)
			pt_template = PART_NAME_DICT[part_type]
			pt_query = pt_template.format(**search_criteria)
			pt_filter = PART_NAME_FILTER[part_type]
			#						mat_type=search_criteria['mat_type'],
			#						      sen_type=search_criteria['sen_type'],
			#						      channel_density=search_criteria['channel_density'],
			#						      geometry=search_criteria['geometry'], )
			sql_query = "*"*"select p.SERIAL_NUMBER, kp.DISPLAY_NAME
from CMS_HGC_CORE_CONSTRUCT.PARTS p
inner join CMS_HGC_CORE_CONSTRUCT.KINDS_OF_PARTS kp
on p.KIND_OF_PART_ID = kp.KIND_OF_PART_ID
inner join CMS_HGC_CORE_MANAGEMNT.LOCATIONS l
on p.LOCATION_ID = l.LOCATION_ID
where kp.DISPLAY_NAME like \'{}\'
and l.LOCATION_NAME like \'{}\'"*"*".format(pt_query, search_criteria['location_name']) + pt_filter

			print("Executing query:\n", sql_query)
			fm.DB_CURSOR.execute(sql_query)
			columns = [col[0] for col in fm.DB_CURSOR.description]
			fm.DB_CURSOR.rowfactory = lambda *args: dict(zip(columns, args))
			data_part = fm.DB_CURSOR.fetchall()#fetchone()
			print("Query results:\n", data_part)
			if data_part is None:
				# Part not found
				print("SQL query found nothing")
			# results:   [{'SERIAL_NUMBER': 'serial'}, ...]
			for el in data_part:
				found_remote_parts[el['SERIAL_NUMBER']] = el['DISPLAY_NAME']
		"""

		# If both in local and remote DB, remove from local list:
		for rp in found_remote_parts.keys():
			if rp in found_local_parts.keys():
				found_local_parts.pop(rp)

		self.displayResults(found_local_parts, found_remote_parts)

	def search_tool_supply(self, *args, **kwargs):
		self.clearResults_tool_supply()

		tool_supply_type = self.page.cbToolSupplyType.currentText()
		tool_supply_temp = TOOL_SUPPLY_DICT[tool_supply_type]()
		
		search_dict = {
			self.page.cbInstitutionTool : 'institution',
			self.page.cbEmpty           : 'is_empty',
			self.page.cbExpired         : 'is_expired'
		}
    
		search_criteria = {}
		for wdgt, qty in search_dict.items():
			if wdgt.isEnabled():
				# if isinstance(wdgt, QComboBox):
				search_criteria[qty] = wdgt.currentText() if wdgt.currentText() != "" else "%"
				# elif isinstance(wdgt, QCheckBox):
				# 	search_criteria[qty] = wdgt.isChecked()
		# Search for tools and supplies:
		tool_supply_name = tool_supply_temp.__class__.__name__
		part_file_name = os.sep.join([ fm.DATADIR, 'partlist', tool_supply_name+'s.json' ])
		with open(part_file_name, 'r') as opfl:
			tool_supply_list = json.load(opfl)

		# Go through all parts in part_list, load each, and check search criteria...
		found_tool_supply = {}
		for tool_supply_id, date in tool_supply_list.items():
			if 'batch' in tool_supply_name:  # supply
				tool_supply_temp.load(tool_supply_id)
				TOOL_SUPPLY_OBJNAME_CLSNAME[tool_supply_temp.OBJECTNAME] = tool_supply_name
				found = True
				for qty, value in search_criteria.items():
					if value == '%':  continue  # "wildcard" option, ignore this
					value = False if 'not' in value else True
					if getattr(tool_supply_temp, qty, None) != value:
						found = False
				if found:  found_tool_supply[tool_supply_id] = tool_supply_temp.OBJECTNAME + ': expires after ' + tool_supply_temp.date_expires
			else:  # tool
				found = True
				tool_ID = tool_supply_id.split('_')[0]
				tool_institute = tool_supply_id.split('_')[1]
				if tool_institute != search_criteria['institution']:
					found = False
				if found:
					tool_supply_temp.load(tool_ID,tool_institute)
					TOOL_SUPPLY_OBJNAME_CLSNAME[tool_supply_temp.OBJECTNAME] = tool_supply_name
					# load comments in the info box
					coment_str = ''
					for i, cmt in enumerate(tool_supply_temp.comments):
						coment_str += cmt
						if i != len(tool_supply_temp.comments)-1: coment_str += ', '
					found_tool_supply[tool_supply_id] = tool_supply_temp.OBJECTNAME + ': ' + coment_str
	
		self.displayResults_tool_supply(found_tool_supply)
    
    
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
		self.page.ckUseDate       .setEnabled(part_type == 'Protomodule' or part_type == 'Module')
		useDate = self.page.ckUseDate.isChecked()
		self.page.dCreated        .setReadOnly(not (part_type == 'Protomodule' or part_type == 'Module'))
		self.page.cbAssmRow       .setEnabled(part_type == 'Protomodule' or part_type == 'Module')
		self.page.cbAssmCol       .setEnabled(part_type == 'Protomodule' or part_type == 'Module')

		tool_supply_name = self.page.cbToolSupplyType.currentText()
		if 'batch' in tool_supply_name or 'tape' in tool_supply_name:
			tool_supply_type = 'supply'
		else: tool_supply_type = 'tool'
		self.page.cbInstitutionTool   .setEnabled(tool_supply_type == 'tool')
		self.page.cbEmpty             .setEnabled(tool_supply_type == 'supply')
		self.page.cbExpired           .setEnabled(tool_supply_type == 'supply')

	def clearParams(self,*args,**kwargs):
		for wdgt in [self.page.cbInstitution,     self.page.cbShape,
					 self.page.cbMaterial,       self.page.cbThickness,
					 self.page.cbChannelDensity,
					 self.page.cbAssmRow,        self.page.cbAssmCol
					]:
			wdgt.setCurrentIndex(0)
		self.page.ckUseDate.setChecked(False)

	def clearParams_tool_supply(self,*args,**kwargs):
		for wdgt in [
			self.page.cbInstitutionTool,
			self.page.cbEmpty,
			self.page.cbExpired
			]:
			wdgt.setCurrentIndex(0)
		# self.page.cbInstitutionTool.setCurrentIndex(0)
		# self.page.cbEmpty.setCurrentIndex(0)
		# self.page.ckExpired.setCurrentIndex(0)

	def clearResults(self,*args,**kwargs):
		# empty lwPartList
		self.page.lwPartList.clear()
		self.page.lwTypeList.clear()
		self.page.leStatus.setText("")

	def clearResults_tool_supply(self,*args,**kwargs):
		# empty lwToolSupplyList
		self.page.lwToolSupplyList.clear()
		self.page.lwInfoList.clear()
		self.page.leStatusToolSupply.setText("")

	def displayResults(self, localList, remoteList):
		# result list is [ [serial, type], ... ]
		if localList=={} and remoteList=={}:
			self.page.leStatus.setText("No results found")
			return

		for serial, typ in localList.items(): # serial: type
			self.page.lwPartList.addItem(serial+" (not uploaded to DB)")
			# self.page.lwTypeList.addItem(typ)
		for serial, typ in remoteList.items():
			self.page.lwPartList.addItem(serial)
			# self.page.lwTypeList.addItem(typ)
		
  		# Sort search results
		self.page.lwPartList.sortItems()
		for row in range(self.page.lwPartList.count()):
			if self.page.lwPartList.item(row).text().find(" (not uploaded to DB)"):
				serial = self.page.lwPartList.item(row).text().split(" (not uploaded to DB)")[0]
				self.page.lwTypeList.addItem(localList[serial])
			else:
				serial = self.page.lwPartList.item(row).text()
				self.page.lwTypeList.addItem(remoteList[serial])
		self.page.leStatus.setText("Results found!")

	def displayResults_tool_supply(self, foundList):
		if foundList=={}:
			self.page.leStatusToolSupply.setText("No results found")
			return
		for serial, typ in foundList.items(): # serial: type
			self.page.lwToolSupplyList.addItem(serial)
		# Sort search results
		self.page.lwToolSupplyList.sortItems()
		for row in range(self.page.lwToolSupplyList.count()):
			serial = self.page.lwToolSupplyList.item(row).text()
			self.page.lwInfoList.addItem(foundList[serial])
		self.page.leStatusToolSupply.setText("Results found!")

	def goToPart(self,*args,**kwargs):
		if not self.page.lwPartList.currentItem():  return
		name = self.page.lwPartList.currentItem().text().replace(" (not uploaded to DB)", "") #.text().split()
		# find corresponding part type
		typ = self.page.lwTypeList.item(self.page.lwPartList.currentRow()).text()
		pageName = None
		for pttype in PAGE_NAME_DICT:
			# note:  "module" in "protomodule", but module is last -> self-correcting.
			#print(pttype.lower(), typ.lower())
			if pttype.lower() in typ.lower():
				pageName = PAGE_NAME_DICT[pttype]
				break
		self.setUIPage(pageName, ID=name)

	def goToToolSupply(self,*args,**kwargs):
		if not self.page.lwToolSupplyList.currentItem():  return
		name = self.page.lwToolSupplyList.currentItem().text()
		# find corresponding tool/supply type
		info = self.page.lwInfoList.item(self.page.lwToolSupplyList.currentRow()).text()
		pageName = None
		clsname = TOOL_SUPPLY_OBJNAME_CLSNAME[info.split(':')[0]]
		args_dict = {}
		if 'batch' in info:
			pageName = PAGE_NAME_DICT['Supply']
			args_dict[clsname] = name
		else:
			pageName = PAGE_NAME_DICT['Tool']
			args_dict[clsname] = int(name.split('_')[0])
			args_dict['institution'] = name.split('_')[1]
		self.setUIPage(pageName, **args_dict)
		

	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			print("Warning:  attempted to pass search page an ID (there's probably a bug somewhere)")

	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))


