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
		self.page.pbSearch.clicked.connect(self.search)

		self.page.cbPartType.currentIndexChanged.connect( self.updateElements )
		self.page.ckUseDate.stateChanged.connect( self.updateElements )

		self.page.pbClearParams.clicked.connect( self.clearParams )

		self.page.pbClearResults.clicked.connect( self.clearResults )
		self.page.pbGoToPart.clicked.connect( self.goToPart )

		self.updateElements()

	def search(self, *args, **kwargs):  # WIP WIP WIP
		self.clearResults()

		search_dict = { self.page.cbInstitution:'location_name', self.page.cbShape:'geometry',
						self.page.cbMaterial:'mat_type', self.page.cbThickness:'sen_type',
						self.page.cbChannelDensity:'channel_density', #self.page.cbPCBType:'pcb_type',
						self.page.cbAssmRow:'tray_row', self.page.cbAssmCol:'tray_col' }
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

		part_type = self.page.cbPartType.currentText()
		if not part_type in PART_DICT.keys():  # disabled proto/modules
			print("WARNING: {}s are currently disabled".format(part_type))
			self.displayResults([], [])
			return
		part_temp = PART_DICT[part_type]()  # Constructs instance of searched-for class
		# Search for locally-stored parts:
		part_file_name = os.sep.join([ fm.DATADIR, 'partlist', part_type.lower()+'s.json' ])
		with open(part_file_name, 'r') as opfl:
			part_list = json.load(opfl)
		# Go through all parts in part_list, load each, and check search criteria...

		found_local_parts = {}
		for part_id, date in part_list.items():
			print("Checking part for match:", part_id)
			part_temp.load(part_id)
			found = True
			for qty, value in search_criteria.items():
				if value == '%':  continue  # "wildcard" option, ignore this
				if str(getattr(part_temp, qty, None)) != value:
					print("Mismatch:", qty, str(getattr(part_temp, qty, None)), value)
					found = False
			if found:  found_local_parts[part_id] = part_temp.display_name

		# Search for parts in DB:
		found_remote_parts = {}  # serial:type
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
			sql_query = """select p.SERIAL_NUMBER, kp.DISPLAY_NAME
from CMS_HGC_CORE_CONSTRUCT.PARTS p
inner join CMS_HGC_CORE_CONSTRUCT.KINDS_OF_PARTS kp
on p.KIND_OF_PART_ID = kp.KIND_OF_PART_ID
inner join CMS_HGC_CORE_MANAGEMNT.LOCATIONS l
on p.LOCATION_ID = l.LOCATION_ID
where kp.DISPLAY_NAME like \'{}\'
and l.LOCATION_NAME like \'{}\'""".format(pt_query, search_criteria['location_name']) + pt_filter

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

		# If both in local and remote DB, remove from local list:
		for rp in found_remote_parts.keys():
			if rp in found_local_parts.keys():
				found_local_parts.pop(rp)

		self.displayResults(found_local_parts, found_remote_parts)


	
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
		#self.page.cbPCBType       .setEnabled(part_type == 'PCB')
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
		self.page.lwTypeList.clear()
		self.page.leStatus.setText("")

	def displayResults(self, localList, remoteList):
		# result list is [ [serial, type], ... ]
		if localList=={} and remoteList=={}:
			self.page.leStatus.setText("No results found")
			return

		for serial, typ in localList.items(): # serial: type
			self.page.lwPartList.addItem(serial+" (not uploaded to DB)")
			self.page.lwTypeList.addItem(typ)
		for serial, typ in remoteList.items():
			self.page.lwPartList.addItem(serial)
			self.page.lwTypeList.addItem(typ)
		self.page.leStatus.setText("Results found!")

	def goToPart(self,*args,**kwargs):
		if not self.page.lwPartList.currentItem():  return
		name = self.page.lwPartList.currentItem().text().replace(" (not uploaded to DB)", "") #.text().split()
		# find corresponding part type
		typ = self.page.lwTypeList.item(self.page.lwPartList.currentRow()).text()
		for pttype in PAGE_NAME_DICT:
			# note:  "module" in "protomodule", but module is last -> self-correcting.
			print(pttype.lower(), typ.lower())
			if pttype.lower() in typ.lower():
				pageName = PAGE_NAME_DICT[pttype]

		self.setUIPage(pageName, ID=name)


	def load_kwargs(self,kwargs):
		if 'ID' in kwargs.keys():
			print("Warning:  attempted to pass search page an ID (there's probably a bug somewhere)")

	def changed_to(self):
		print("changed to {}".format(PAGE_NAME))


