import json
import time
import glob
import os
import sys

from PyQt5 import QtCore
import datetime
#NEW for xml file generation:
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import parse
from xml.etree.ElementTree import tostring
from xml.etree.ElementTree import fromstring
import csv

# Possible improvement:
import jinja2

#import rhapi_nolock as rh
# For DB requests:
import cx_Oracle
from xml.dom import minidom



# NEW
INSTITUTION_DICT = {  # For loading from/to LOCATION_ID XML tag
	1780: "FNAL",
	1781: "UMN",
	1782: "UCSB",
	1783: "CERN",
	1481: "UCSB",  # Technically "UCSB HEP", but prob no significant difference
	1482: "UMN",
	1483: "CERN",
	1484: "HEPHY",
	3800: "HPK",
	2180: "FNAL",
	1400: "UCSB",
	1420: "CERN",
	1440: "HEPHY",
	1460: "UMN",
}




###############################################
###############  assembly steps  ##############
###############################################


"""
class fsobj_step(fsobj_db):
	# Note:  fsobj_db is currently minimalistic, only really contains cond header
	# Could very feasibly remove at this point?

	# Goals:
	# Init arr of 6 protomodules
	# Upon load:
	# - sql query for protomod IDs matching step name
	# - Download all into local protomodules
	# GUI:
	# - Access all step-specific info via attrs that get info from child protomods
	# Upon save:
	# - define getDataSet() for each protomod - return dict
	# - Use above to build all cond, etc dicts
	# Upload:  Keep manual for now
	# - Upload assembly files for STEP ONLY - avoid 6 scp's if possible

	OBJECTNAME = "sensor step"
	FILEDIR    = os.sep.join(['steps','sensor','{date}'])
	FILENAME   = 'sensor_assembly_{ID:0>5}.xml'

	def __init__(self):
		# protomods start None, get filled only once they're known to exist
		self.protomodules = [None for i in range(6)]

	def load(self, ID):
		# ID is [asmbly_institution]_[number], defined by UI

		# First, check local:
		if ID == "" or ID == -1 or ID == None:
			self.clear()
			return False

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		data = None
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
		if str(ID) in data.keys():
			print("      FOUND in partlistfile, can quick load")
			dt = data[str(ID)]
			super(fsobj_part, self).load(ID)

		else:
			if not ENABLE_DB_COMMUNICATION:
				print("**TEMPORARY:  Object not found, and downloading disabled for testing!**")
					return False

			# Use DB_CURSOR and self.SQL_REQUEST to find XML files
			# Data from part table
			print("Requesting part data")
			DB_CURSOR.execute(self.sql_request_part(ID))

		sql_request = "s"s"select pa.SNSR_STEP, p.SERIAL_NUMBER
from CMS_HGC_HGCAL_COND.HGC_PRTO_MOD_ASMBLY pa
inner join CMS_HGC_CORE_CONSTRUCT.PARTS p
on p.PART_ID = ds.PART_ID
where pa.SNSR_STEP=\'{}\'"s"s".format(ID)
		DB_CURSOR.execute()




	# COND_TABLE varies, defined in each class
	# Table names:  CMS_HGC_HGCAL_COND.x
	# baseplates:  SI_MODULE_BASEPLATE
	# sensors:     SI_MODULE_SENSOR
	# PCBs:        FLATNS_PBC_ROCS_DATA
	# protomods:   HGC_PRTO_MOD_ASMBLY_COND
	# mods:        HGC_MOD_ASMBLY_COND



	COND_TABLE = None  # Table containing cond info, varies from obj to obj
	XML_PART_TEMPLATE = None  # Dict describing structure of part upload XML file
	XML_COND_TEMPLATE = None  # ............................ cond upload XML file

	PART_PROPERTIES = [
		# Read-only:
		"display_name",  # only entry from KINDS_OF_PARTS table
		# NOTE:  -> kind_of_part in XML
		"part_id",
		"record_insertion_user",
		"kind_of_part_id",  # NOTE:  Not used
		"manufacturer_id",  # -> manufacturer in XML, not always necessary
		"barcode",  # CANNOT upload this, breaks the xml
		"serial_number"
		# Read/write:
		"location",  # NOTE:  Not location_id
		"production_date",
		"batch_number",

		# local storage only (not in DB)
		"institution_location", # location at institution

		# NOTE:  All other vars in PARTS are ignored by the GUI.
		# Will be downloaded into json, but not used/uploaded.
		#"is_record_deleted",
		#"record_insertion_time",
		#"version",
		#"name_label",
		#"installed_date",
		#"removed_date",
		#"installed_by_user",
		#"removed_by_user",
		#"extension_table_name",
		#"record_lastupdate_time",
		#"record_lastupdate_user",
		#"comment_description"
	]
	
	COND_PROPERTIES = []
	LOCAL_PROPERTIES = []

	XML_PART_TEMPLATE = {"PARTS":{"PART":{  # same for all parts
		"KIND_OF_PART":"kind_of_part",
		"RECORD_INSERTION_USER":"record_insertion_user",
		"SERIAL_NUMBER":"ID",
		"COMMENT_DESCRIPTION":"comment_description",
		"LOCATION":"location",
		"MANUFACTURER":"manufacturer"  # Usually not used
	}}}
	# XML_COND_TEMPLATE is separate for each part

	def __init__(self):
		self.PROPERTIES = self.PART_PROPERTIES + self.COND_PROPERTIES \
						  + self.LOCAL_PROPERTIES
		super(fsobj_part, self).__init__()


	def sql_request_part(self, ID):
		#return "select * from PARTS p where p.SERIAL_NUMBER={}".format(self.ID)
		# old - also want to get KIND_OF_PART name for geometry info
		return "s"s"select kp.DISPLAY_NAME, p.*
from CMS_HGC_CORE_CONSTRUCT.PARTS p
inner join CMS_HGC_CORE_CONSTRUCT.KINDS_OF_PARTS kp
on p.KIND_OF_PART_ID = kp.KIND_OF_PART_ID
where p.SERIAL_NUMBER=\'{}\'
"s"s".format(ID)

	def sql_request_cond(self, ID):
		# SQL command:  Given a part SERIAL_NUMBER, select the entire corresponding row from COND_TABLE
		return "s"s"select p.SERIAL_NUMBER, fd.*
from CMS_HGC_CORE_COND.COND_DATA_SETS ds
inner join CMS_HGC_HGCAL_COND.{} fd
on fd.CONDITION_DATA_SET_ID = ds.CONDITION_DATA_SET_ID
inner join CMS_HGC_CORE_CONSTRUCT.PARTS p
on p.PART_ID = ds.PART_ID
where p.SERIAL_NUMBER=\'{}\'"s"s".format(self.COND_TABLE, ID)


	def save(self):
		# This one handles the json files
		super(fsobj_part, self).save()

		# NEXT, write the upload files!
		# There's two:  One for Build_UCSB_ProtoModules_00.xml, one for ProtoModules_BuildCond_00.xml (part and cond).
		# Defined in XML_PART_TEMPLATE, XML_COND_TEMPLATE
		filedir, filename = self.get_filedir_filename()
		fname_build = filename.replace('.xml', '_build_upload.xml')
		fname_cond  = filename.replace('.xml', '_cond_upload.xml')
		# Build file:
		xml_tree = self.generate_xml(self.XML_PART_TEMPLATE)
		root = xml_tree.getroot()
		xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')  #tostring imported from xml.etree.ElementTree
		xmlstr = xmlstr.replace("version=\"1.0\" ", "version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"")
		with open(filedir+'/'+fname_build, 'w') as f:
			f.write(xmlstr)
		# Cond file:
		if self.XML_COND_TEMPLATE:
			xml_tree = self.generate_xml(self.XML_COND_TEMPLATE)
			root = xml_tree.getroot()
			xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')
			xmlstr = xmlstr.replace("version=\"1.0\" ", "version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"")
			with open(filedir+'/'+fname_cond, 'w') as f:
				f.write(xmlstr)
	
		# NEXT:  Upload to DB!
		# Create new process (user should not wait for this):
		# upload base file first
		# wait n seconds
		# upload cond file second
		


	# Revamped
	def load(self, ID, on_property_missing = "warn"):
		if ID == "" or ID == -1 or ID == None:
			self.clear()
			return False

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		data = None
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
		if str(ID) in data.keys():
			print("      FOUND in partlistfile, can quick load")
			dt = data[str(ID)]
			super(fsobj_part, self).load(ID)

		else:
			if not ENABLE_DB_COMMUNICATION:
				print("**TEMPORARY:  Object not found, and downloading disabled for testing!**")
					return False

			# Use DB_CURSOR and self.SQL_REQUEST to find XML files
			# Data from part table
			print("Requesting part data")
			DB_CURSOR.execute(self.sql_request_part(ID))
			# Reformat
			columns = [col[0] for col in DB_CURSOR.description]
			DB_CURSOR.rowfactory = lambda *args: dict(zip(columns, args))
			data_part = DB_CURSOR.fetchone()
			if data_part is None:
				# Part not found
				print("SQL query found nothing")
				return False

			# Data from cond table
			print("Requesting cond data")
			print("QUERY:")
			print(self.sql_request_cond(ID))
			DB_CURSOR.execute(self.sql_request_cond(ID))
			# Reformat
			columns = [col[0] for col in DB_CURSOR.description]
			DB_CURSOR.rowfactory = lambda *args: dict(zip(columns, args))
			data_cond = DB_CURSOR.fetchone()
			# data_* is now a dict:  {"SERIAL_NUMBER":"xyz", "THICKNESS":"0.01", ...}

			# Load all data into self.
			# DB col names are [local var name].upper()
			print("Downloaded part data:")
			print(data_part)
			print("Downloaded cond data:")
			print(data_cond)

			def fill_self(data_x):
				for colname, var in data_x.items():
					# NOTE:  datetime objs cannot be stored as json, or simply sent to xml...so stringify
					if type(var) == datetime.datetime:
						dstring = "{}-{}-{} {:02d}:{:02d}:{:02d}".format(var.year, var.month, var.day, var.hour, var.minute, var.second)
						setattr(self, colname.lower(), dstring)
					elif type(var) == datetime.date:
						dstring = "{}-{}-{}".format(var.year, var.month, var.day)
						setattr(self, colname.lower(), dstring)
					else:
						setattr(self, colname.lower(), var)
			fill_self(data_part)
			fill_self(data_cond)

			# Data is now in python obj.  Ensure save:
			self.ID = ID
			self.save()

		#self.ID = ID
		return True




class step_sensor(fsobj_step):
	OBJECTNAME = "sensor step"
	FILEDIR    = os.sep.join(['steps','sensor','{date}'])
	FILENAME   = 'sensor_assembly_step_{ID:0>5}.json'
	PROPERTIES = [
		'user_performed', # name of user who performed step
		'institution',
		'location', # New--instituition where step was performed

		'run_start',  # New--unix time @ start of run
		'run_stop',  # New--unix time @ end of run
		'cure_start',
		'cure_stop',

		# Note:  Semiconductors types are stored in the sensor objects

		'cure_temperature', # Average temperature during curing (centigrade)
		'cure_humidity',    # Average humidity during curing (percent)

		'tools',        # list of pickup (sensor) tool IDs, ordered by pickup tool location
		'sensors',      # list of sensor      IDs, ordered by component tray position
		'baseplates',   # list of baseplate   IDs, ordered by assembly tray position
		'protomodules', # list of protomodule IDs assigned to new protomodules, by assembly tray location

		'tray_component_sensor', # ID of component tray used
		'tray_assembly',         # ID of assembly  tray used
		'batch_araldite',        # ID of araldite batch used

		# TEMP:
		'kind_of_part_id',
		'kind_of_part',

		'check_tool_feet',

		'xml_data_file',
	]


	XML_UPLOAD_DICT = {"PARTS":{"PART":{
		"KIND_OF_PART":"kind_of_part",
		"SERIAL_NUMBER":"ID",
		"COMMENT_DESCRIPTION":"comments_concat",
		"LOCATION":"location",
		"RECORD_INSERTION_USER":"insertion_user",
		"THICKNESS":"thickness",
		"FLATNESS":"flatness",
		"GRADE":"grade",
		"PREDEFINED_ATTRIBUTES":{
			"ATTRIBUTE":{
				"NAME":"AsmTrayPosn",
				"VALUE":"assem_tray_posn",
			}
		},
		#"COMMENTS":"comments_concat",
		"CHILDREN":{
			"PART":[{
				"KIND_OF_PART":"baseplate_type",
				"SERIAL_NUMBER":"baseplate",
				"PREDEFINED_ATTRIBUTES":{
					"ATTRIBUTE":{
						"NAME":"AsmTrayPosn",
						"VALUE":"assem_tray_posn",
					}
				}
			},
			{
				"KIND_OF_PART":"sensor_type",
				"SERIAL_NUMBER":"sensor",
				"PREDEFINED_ATTRIBUTES":{
					"NAME":"CmpTrayPosn",
					"VALUE":"comp_tray_posn",
				}
			}]
		}
	}}}


	# NOTE WARNING:  Commenting all WIP changes for now
	
	@property
	def temp_property(self):
		return None
	@temp_property.setter
	def temp_property(self, value):
		pass

	@property
	def curing_time_hrs(self):
		if self.run_start is None or self.run_stop is None:
			return None
		start_time = list(time.localtime(self.run_start))
		stop_time  = list(time.localtime(self.run_stop ))
		telapsed = start_time.secsTo(stop_time) / (60.0**2)

	# New:  Convert time_t to correctly-formatted date string
	@property
	def run_start_xml(self):
		if self.run_start is None:
			return None
		localtime = list(time.localtime(self.run_start))
		qdate = QtCore.QDate(*localtime[0:3])
		qtime = QtCore.QTime(*localtime[3:6])
		datestr = "{}-{}-{} {}:{}:{}".format(qdate.year(), qdate.month(), qdate.day(), \
                                             qtime.hour(), qtime.minute(), qtime.second())
		return datestr

	@property
	def run_stop_xml(self):  # Turns out we need this too
		if self.run_stop is None:
			return None
		localtime = list(time.localtime(self.run_stop))
		qdate = QtCore.QDate(*localtime[0:3])
		qtime = QtCore.QTime(*localtime[3:6])
		datestr = "{}-{}-{} {}:{}:{}".format(qdate.year(), qdate.month(), qdate.day(), \
                                             qtime.hour(), qtime.minute(), qtime.second())
		return datestr

	@property
	def xml_location(self):
		return "{}, {}".format(self.institution, self.location)

	@property
	def xml_comment_data(self):
		return "Proto Module {} Assembly".format(self.ID)

	@property
	def assembly_tray_name(self):
		return 'ASSEMBLY_TRAY_{}_{}'.format(self.institution, self.tray_assembly)

	@property
	def comp_tray_name(self):
		return 'SENSOR_COMPONENT_TRAY_{}_{}'.format(self.institution, self.tray_component_sensor)

	@property
	def sensor_tool_names(self):
		names = []
		for i in range(6):
			tmp_tool = tool_sensor()
			if self.tools[i] is None:
				names.append(None)
			elif tmp_tool.load(self.tools[i], self.institution):
				names.append("SNSR_TOOL_{}_{}".format(self.institution, self.tools[i]))
			else:
				names.append(None)
		return names

	@property
	def assembly_rows(self):
		return [1, 2, 3, 1, 2, 3]

	@property
	def assembly_cols(self):
		return [1, 1, 1, 2, 2, 2]

	@property
	def snsr_x_offsts(self):
		offsts = []
		for i in range(6):
			tmp_proto = protomodule()
			if self.protomodules[i] is None:
				offsts.append(None)
			elif tmp_proto.load(self.protomodules[i]):
				offsts.append(tmp_proto.offset_translation_x)
			else:
				offsts.append(None)
		return offsts

	@property
	def snsr_y_offsts(self):
		offsts = []
		for i in range(6):
			tmp_proto = protomodule()
			if self.protomodules[i] is None:
				offsts.append(None)
			if tmp_proto.load(self.protomodules[i]):
				offsts.append(tmp_proto.offset_translation_y)
			else:
				offsts.append(None)
		return offsts

	@property
	def snsr_ang_offsts(self):
		offsts = []
		for i in range(6):
			tmp_proto = protomodule()
			if self.protomodules[i] is None:
				offsts.append(None)
			if tmp_proto.load(self.protomodules[i]):
				offsts.append(tmp_proto.offset_rotation)
			else:
				offsts.append(None)
		return offsts


	ASSM_TABLE = 'c4220'
	COND_TABLE = 'c4260'
	ASSM_TABLE_NAME = 'HGC_PRTO_MOD_ASMBLY'
	COND_TABLE_NAME = 'HGC_PRTO_MOD_ASMBLY_COND'
	ASSM_TABLE_DESC = 'HGC Eight Inch Proto Module Assembly'
	COND_TABLE_DESC = 'HGC Eight Inch Proto Module Curing Cond'
	RUN_TYPE        = 'HGC 8inch Proto Module Assembly'
	CMT_DESCR = 'Build 8inch proto modules'

	# Vars for tables - constants
	GLUE_TYPE = 'Araldite'
	SLVR_EPXY_TYPE = None

	# For assembly steps, XML_STRUCT_DICT is automatically defined in the class init().
	# Dicts for uploading:  XML_UPLOAD_DICT, XML_COND_DICT

	# See Build_UCSB_ProtoModules_00.xml for structure
	XML_UPLOAD_DICT = {
		'HEADER':{
			'TYPE':{
				'EXTENSION_TABLE_NAME':'ASSM_TABLE_NAME',
				'NAME':'ASSM_TABLE_DESC'
			},
			'RUN':{
				'RUN_NAME':'RUN_TYPE',
				'RUN_BEGIN_TIMESTAMP':'run_start_xml',  # Format:  2018-03-26 00:00:00
				'RUN_END_TIMESTAMP':'run_stop_xml',
				'INITIATED_BY_USER':'user_performed',
				'LOCATION':'location',
				'COMMENT_DESCRIPTION':'CMT_DESCR'
			}
		},
		'DATA_SET':'DATA_SET_DICT'  # SPECIAL CASE:  This will be filled during save(), in a special case
	}

	DATA_SET_DICT = {
		# Leave out ID--should be assigned by DB loader! (?)
		'COMMENT_DESCRIPTION':'xml_comment_data', # Property; involves serial
		'VERSION':'VNUM',
		'PART':{
			'KIND_OF_PART':'temp_property',  # TBD
			'SERIAL_NUMBER':'modules'
		},
		'COMMENTS':'comments_concat',
		'DATA':{
			'ASMBL_TRAY_NAME':		'assembly_tray_name',
			'PLT_SER_NUM':			'baseplates',
			'PLT_ASM_ROW':			'assembly_rows',
			'PLT_ASM_COL':			'assembly_cols',
			'COMP_TRAY_NAME':		'comp_tray_name',
			'SNSR_SER_NUM':			'sensors',
			'SNSR_CMP_ROW':			'assembly_rows',  # These should always be the same as above...right?
			'SNSR_CMP_COL':			'assembly_cols',
			'SNSR_X_OFFST':			'snsr_x_offsts',
			'SNSR_Y_OFFST':			'snsr_y_offsts',
			'SNSR_ANG_OFFST':		'snsr_ang_offsts',
			'PCKUP_TOOL_NAME':		'sensor_tool_names',  # note: list
			'GLUE_TYPE':			'GLUE_TYPE',
			'GLUE_BATCH_NUM':		'batch_araldite',
			'SLVR_EPXY_TYPE':		'SLVR_EPXY_TYPE',
			'SLVR_EPXY_BATCH_NUM':	'temp_property',
		}
	}

	@property
	def batch_TEMP(self):
		return None


	XML_COND_DICT = {'data':{'row':{  # WIP
		'HEADER':{
			'TYPE':{
				'EXTENSION_TABLE_NAME':'COND_TABLE_NAME',
				'NAME':'ASSM_TABLE_DESC'
			},
			'RUN':{
				'RUN_NAME':'RUN_TYPE',
				'RUN_BEGIN_TIMESTAMP':'run_start_xml',  # Format:  2018-03-26 00:00:00
				'RUN_END_TIMESTAMP':'run_stop_xml',
				'INITIATED_BY_USER':'user_performed',
				'LOCATION':'xml_location',
				'COMMENT_DESCRIPTION':'CMT_DESCR'
			}
		},
		'DATA_SET':'DATA_SET_COND_DICT'  # SPECIAL CASE:  This will be filled during save(), in a special case
	}}}

	DATA_SET_COND_DICT = {
		'COMMENT_DESCRIPTION':'xml_comment_data', # Property; involves serial
		'VERSION':'VNUM',
		'PART':{
			'KIND_OF_PART':'protomodule_type',  # TBD
			'SERIAL_NUMBER':'protomodules'
		},
		'DATA':{
			'CURING_TIME_HRS':'curing_time_hrs',
			'TIME_START':'run_start_xml',
			'TIME_STOP':'run_stop_xml',
			'TEMP_DEGC':'cure_temperature',
			'HUMIDITY_PRCNT':'cure_humidity'
		}
	}

	@property
	def protomodule_type(self):
		# Grab a protomod--can be in any posn
		if self.protomodules is None:  return None
		prt = None
		for i in range(6):
			if self.protomodules[i] != None:  prt = self.protomodules[i]
		if not prt:  return None
		tmp_prtomod = protomodule()
		tmp_prtomod.load(prt)
		return tmp_prtomod.kind_of_part



class step_pcb(fsobj_step):
	OBJECTNAME = "PCB step"
	FILEDIR = os.sep.join(['steps','pcb','{date}'])
	FILENAME = 'pcb_assembly_step_{ID:0>5}.json'
	PROPERTIES = [
		'user_performed', # name of user who performed step
		'institution',
		'location', #Institution where step was performed
		
		'run_start',  # unix time @ start of run
		'run_stop',   # unix time @ start of run
		
		'cure_start',       # unix time @ start of curing
		'cure_stop',        # unix time @ end of curing
		'cure_temperature', # Average temperature during curing (centigrade)
		'cure_humidity',    # Average humidity during curing (percent)

		'tools',        # list of pickup tool IDs, ordered by pickup tool location
		'pcbs',         # list of pcb         IDs, ordered by component tray location
		'protomodules', # list of protomodule IDs, ordered by assembly tray location
		'modules',      # list of module      IDs assigned to new modules, by assembly tray location

		'tray_component_pcb', # ID of component tray used
		'tray_assembly',      # ID of assembly  tray used
		'batch_araldite',     # ID of araldite batch used

		'check_tool_feet',

		'xml_data_file',
	]


	# NOTE WARNING:  Commenting all WIP changes for now

	
	@property
	def temp_property(self):
		return None
	@temp_property.setter
	def temp_property(self, value):
		pass

	@property
	def curing_time_hrs(self):
		if self.run_start is None or self.run_stop is None:
			return None
		start_time = list(time.localtime(self.run_start))
		stop_time  = list(time.localtime(self.run_stop ))
		telapsed = start_time.secsTo(stop_time) / (60.0**2)

	# New:  Convert time_t to correctly-formatted date string
	@property
	def run_start_xml(self):
		if self.run_start is None:
			return None
		localtime = list(time.localtime(self.run_start))
		qdate = QtCore.QDate(*localtime[0:3])
		qtime = QtCore.QTime(*localtime[3:6])
		datestr = "{}-{}-{} {}:{}:{}".format(qdate.year(), qdate.month(), qdate.day(), \
                                             qtime.hour(), qtime.minute(), qtime.second())
		return datestr

	@property
	def run_stop_xml(self):  # Turns out we need this too
		if self.run_stop is None:
			return None
		localtime = list(time.localtime(self.run_stop))
		qdate = QtCore.QDate(*localtime[0:3])
		qtime = QtCore.QTime(*localtime[3:6])
		datestr = "{}-{}-{} {}:{}:{}".format(qdate.year(), qdate.month(), qdate.day(), \
                                             qtime.hour(), qtime.minute(), qtime.second())
		return datestr

	@property
	def xml_location(self):
		return "{}, {}".format(self.institution, self.location)

	@property
	def xml_comment_data(self):
		return "Module {} Assembly".format(self.ID)

	@property
	def assembly_tray_name(self):
		return 'ASSEMBLY_TRAY_{}_{}'.format(self.institution, self.tray_assembly)

	@property
	def comp_tray_name(self):
		return 'PCB_COMPONENT_TRAY_{}_{}'.format(self.institution, self.tray_component_pcb)

	@property
	def pcb_tool_names(self):
		names = []
		for i in range(6):
			tmp_tool = tool_pcb()
			if self.tools[i] is None:
				names.append(None)
			elif tmp_tool.load(self.tools[i], self.institution):
				names.append("PCB_TOOL_{}_{}".format(self.institution, self.tools[i]))
			else:
				names.append(None)
		return names

	@property
	def assembly_rows(self):
		return [1, 2, 3, 1, 2, 3]

	@property
	def assembly_cols(self):
		return [1, 1, 1, 2, 2, 2]

	ASSM_TABLE = 'c4240'
	COND_TABLE = 'c4280'
	ASSM_TABLE_NAME = 'HGC_MOD_ASMBLY'
	COND_TABLE_NAME = 'HGC_MOD_ASMBLY_COND'
	ASSM_TABLE_DESC = 'HGC Six Inch Module Assembly'
	COND_TABLE_DESC = 'HGC Six Inch Module Curing Cond'
	RUN_TYPE        = 'HGC 8inch Module Assembly'
	CMT_DESCR = 'Build 8inch modules'

	# Vars for tables - constants
	GLUE_TYPE = 'Araldite'
	SLVR_EPXY_TYPE = None

	# List of new vars to add:  cond_id, kind_of_condition, cond_data_set_id, part_id, protomodule_id, 

	# For assembly steps, XML_STRUCT_DICT is automatically defined in the class init().
	# Dicts for uploading:  XML_UPLOAD_DICT, XML_COND_DICT

	# See Build_UCSB_ProtoModules_00.xml for structure
	XML_UPLOAD_DICT = {
		'HEADER':{
			'TYPE':{
				'EXTENSION_TABLE_NAME':'ASSM_TABLE_NAME',
				'NAME':'ASSM_TABLE_DESC'
			},
			'RUN':{
				'RUN_NAME':'RUN_TYPE',
				'RUN_BEGIN_TIMESTAMP':'run_start_xml',  # Format:  2018-03-26 00:00:00
				'RUN_END_TIMESTAMP':'run_stop_xml',
				'INITIATED_BY_USER':'user_performed',
				'LOCATION':'location',
				'COMMENT_DESCRIPTION':'CMT_DESCR'
			}
		},
		'DATA_SET':'DATA_SET_DICT'  # SPECIAL CASE:  This will be filled during save(), in a special case
	}

	DATA_SET_DICT = {
		# Leave out ID--should be assigned by DB loader! (?)
		'COMMENT_DESCRIPTION':'xml_comment_data', # Property; involves serial
		'VERSION':'VNUM',
		'PART':{
			'KIND_OF_PART':'temp_property',  # TBD
			'SERIAL_NUMBER':'modules'
		},
		'COMMENTS':'comments_concat',
		'DATA':{
			'ASMBL_TRAY_NAME':		'assembly_tray_name',
			'PRTMOD_SER_NUM':		'protomodules',
			'PRTMOD_ASM_ROW':		'assembly_rows',
			'PRTMOD_ASM_COL':		'assembly_cols',
			'COMP_TRAY_NAME':		'comp_tray_name',
			'PCB_SER_NUM':			'pcbs',
			'PCB_CMP_ROW':			'assembly_row',  # These should always be the same as above...right?
			'PCB_CMP_COL':			'assembly_col',
			'PCKUP_TOOL_NAME':		'pcb_tool_names',
			'GLUE_TYPE':			'GLUE_TYPE',
			'GLUE_BATCH_NUM':		'batch_araldite',
			'SLVR_EPXY_TYPE':		'SLVR_EPXY_TYPE',
			'SLVR_EPXY_BATCH_NUM':	'temp_property',
		}
	}

	@property
	def batch_TEMP(self):
		return None


	XML_COND_DICT = {'data':{'row':{  # WIP
		'HEADER':{
			'TYPE':{
				'EXTENSION_TABLE_NAME':'COND_TABLE_NAME',
				'NAME':'ASSM_TABLE_DESC'
			},
			'RUN':{
				'RUN_NAME':'RUN_TYPE',
				'RUN_BEGIN_TIMESTAMP':'run_start_xml',  # Format:  2018-03-26 00:00:00
				'RUN_END_TIMESTAMP':'run_stop_xml',
				'INITIATED_BY_USER':'user_performed',
				'LOCATION':'xml_location',
				'COMMENT_DESCRIPTION':'CMT_DESCR'
			}
		},
		'DATA_SET':'DATA_SET_COND_DICT'  # SPECIAL CASE:  This will be filled during save(), in a special case
	}}}

	DATA_SET_COND_DICT = {
		'COMMENT_DESCRIPTION':'xml_comment_data', # Property; involves serial
		'VERSION':'VNUM',
		'PART':{
			'KIND_OF_PART':'module_type',  # TBD
			'SERIAL_NUMBER':'modules'
		},
		'DATA':{
			'CURING_TIME_HRS':'curing_time_hrs',
			'TIME_START':'run_start_xml',
			'TIME_STOP':'run_stop_xml',
			'TEMP_DEGC':'cure_temperature',
			'HUMIDITY_PRCNT':'cure_humidity'
		}
	}


	@property
	def module_type(self):
		# Grab a mod--can be in any posn
		if self.modules is None:  return None
		mod = None
		for i in range(6):
			if self.modules[i] != None:  mod = self.modules[i]
		if not mod:  return None
		tmp_mod = module()
		tmp_mod.load(mod)
		return tmp_mod.kind_of_part
"""


