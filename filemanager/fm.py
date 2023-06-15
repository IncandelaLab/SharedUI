import json
import time
import glob
import os
import sys

#NEW for xml file generation:
from PyQt5 import QtCore
import datetime
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import parse
from xml.etree.ElementTree import tostring
from xml.etree.ElementTree import fromstring
import csv

#import rhapi_nolock as rh
# For DB requests:
import cx_Oracle
from xml.dom import minidom

# IMPORTANT NOTE:  Setting this to false disables DB communication.  Purely for debugging.
ENABLE_DB_COMMUNICATION = False


BASEPLATE_MATERIALS_NO_KAPTON = ['pcb']

MAC_ID_RANGES = {

	"UCSB" : [10000,19999],
	"CMU"  : [20000,29999],
	"TTU"  : [30000,39999],
	"NTU"  : [40000,49999],
	"IHEP" : [50000,59999],
	"BARC" : [60000,69999],

}

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


CENTURY = '{:0>3}__'

CFG_FILE = 'cfg.json'
CWD = os.getcwd()
if not CWD.endswith('filemanager'):
	CWD = os.sep.join([CWD,'filemanager'])

def loadconfig(file=None):

	global DATADIR
	global MAC

	# NOTE:  Currently hardcoding the filemanager_data location, and ignoring the config information!
	DATADIR  = os.sep.join([os.getcwd(), 'filemanager_data'])  # data['datadir']

	# NEW for searching:  Need to store list of all searchable object IDs.  Easiest approach is to dump a list via json.
	partlistdir = os.sep.join([DATADIR, 'partlist'])
	if not os.path.exists(partlistdir):
		os.makedirs(partlistdir)

	# Class names MUST match actual class names or stuff will break
	# Note:  Only the first 6 are searchable at the moment; the rest are in case they're needed later.
	# (And because save() now calls add_part_to_list for all objects except tools)
	obj_list = ['baseplate', 'sensor', 'pcb', 'protomodule', 'module',
				'batch_araldite', 'batch_wedge', 'batch_sylgard',
				'batch_bond_wire',
				'tool_sensor', 'tool_pcb', 'tray_assembly', 'tray_component_sensor', 'tray_component_pcb',
				'step_sensor', 'step_pcb']  # step_kapton removed
	for part in obj_list:
		fname = os.sep.join([partlistdir, part+'s.json'])
		if not os.path.exists(fname):
			with open(fname, 'w') as opfl:
				# Dump an empty dict if nothing is found
				# NOTE:  Format of dictionary is {ID:creation-date-string, ...}
				json.dump({}, opfl)



# Set up DB_CURSOR object for SQL requests:

def connectOracle():
	global DB_CURSOR
	print("LOADING ORACLE LIBRARY")
	try:
		# Custom bash variable set up in .bashrc by install script
		lib_dir = os.environ.get("INSTANT_CLIENT_HOME")
		cx_Oracle.init_oracle_client(lib_dir=lib_dir)
	except Exception as err:
		print("FATAL ERROR:  Could not find Oracle InstantClient libraries.")
		print("$INSTANT_CLIENT_HOME is", os.environ.get("INSTANT_CLIENT_HOME"))
		print("$PATH is", os.environ.get("PATH"))
		print("Exiting")
		sys.exit(1)
	print("Found instant client")
	# Set up connection - takes ~1s, so do once
	# EVERY db request goes through the cursor
	# TODO:  Change this upon switching to production DB
	print("Connecting...")
	db_connection = cx_Oracle.connect(user="CMS_HGC_PRTTYPE_HGCAL_READER",
					password="HGCAL_Reader_2016",
					dsn="localhost:10132/int2r_lb.cern.ch",
					encoding="UTF-8",
					)
	DB_CURSOR = db_connection.cursor()
	print("Connected")

loadconfig()
# moved to mainUI: (must call after tunnel)
#connectOracle()


###############################################
############# UserManager class ###############
###############################################


class UserManager:

	def __init__(self, userFile):
		# json file to store user info
		self.userFile = 'filemanager_data/' + userFile + '.json'
		self.userList = []
		self.pageList = ['view_baseplate', 'view_sensor', 'view_pcb',
				    'view_protomodule', 'view_module',
					'view_sensor_step', #'view_sensor_post',
					'view_pcb_step', #'view_pcb_post',
					'wirebonding_back', 'wirebonding_front',
					'encapsulation_back', 'encapsulation_front',
					'test_bonds', 'final_inspection'
				   ]
		# if userFile already exists, load all users in it:
		if os.path.isfile(self.userFile):
			with open(self.userFile, 'r') as opfl:
				self.userList = json.load(opfl)
		self.updateUsers()

	def updateUsers(self):
		with open(self.userFile, 'w') as opfl:
			json.dump(self.userList, opfl)

	def addUser(self, username, permList, isAdmin=False):
		print("perm list:", len(permList))
		print("pageList:", len(self.pageList))
		assert len(permList) == len(self.pageList), "ERROR:  permissions list length does not equal page list length!"
		if isAdmin:
			permList = [True for p in self.pageList]
		userdict = {'username':username,
					'permissions':permList,
					'isAdmin':isAdmin,
				   }
		self.userList.append(userdict)
		self.updateUsers()

	def updateUser(self, username, permList, isAdmin=False):
		if not username in self.getAllUsers():
			print("WARNING:  Attempted to update nonexistent user {}!".format(username))
			return
		assert len(permList) == len(self.pageList), "ERROR:  permissions list length does not equal page list length!"
		if isAdmin:
			permList = [True for p in self.pageList]
		new_userdict = {'username':username,
						'permissions':permList,
						'isAdmin':isAdmin
					   }
		userindex = list(self.getAllUsers()).index(username)
		self.userList[userindex] = new_userdict
		self.updateUsers()

	def removeUser(self, username):
		if not username in self.getAllUsers():
			print("WARNING:  Attempted to delete nonexistent user {}!".format(username))
			return False
		else:
			userindex = list(self.getAllUsers()).index(username)
			del self.userList[userindex]
			self.updateUsers()
			return True

	def getAllUsers(self):
		return [user['username'] for user in self.userList]

	def getAuthorizedUsers(self, pagename):
		page_index = self.pageList.index(pagename)
		return [user['username'] for user in self.userList if user['permissions'][page_index]]

	def getAdminUsers(self):
		return [user['username'] for user in self.userList if user['isAdmin']]

	def isAdmin(self, username):
		if not username in self.getAllUsers():
			print("WARINING:  Attempted to call isAdmin on nonexistent user {}!".format(username))
			return False
		userindex = list(self.getAllUsers()).index(username)
		return self.userList[userindex]['isAdmin']

	def getUserPerms(self, username):
		if not username in self.getAllUsers():
			return None
		userindex = list(self.getAllUsers()).index(username)
		return self.userList[userindex]['permissions']


userManager = UserManager("userInfoFile")




###############################################
############## fsobj base class ###############
###############################################

class fsobj(object):
	PROPERTIES_COMMON = [
		]

	DEFAULTS = {
	}

	DEFAULTS_COMMON = {
		#'comments':[],
	}

	OBJECTNAME = "fsobj"

	# NEW:
	VARS_TO_RENAME = {  # store list of corrected variable names
		
	}

	OBJ_NAME_DICT = {  #store list of corrected object names
		'baseplate':'HGC Eight Inch Plate',  #COMPLICATION
	}

	# MAYBE:
	# First table is the basic table; second table is the cond info
	#CONDS_DICT = {'step_sensor': ['c4220', 'c4260'],
	#			  'step_pcb':    ['c4240', 'c4280']
	#			 }

	# NEW
	XML_STRUCT_DICT = None  # Should not use the base class!

	# True if assembly step (multiple DATA_SETs per output file), else False
	MULTIPART_CLASS = False

	def __init__(self):
		super(fsobj, self).__init__()
		self.clear() # sets attributes to None

	def __str__(self):
		return "<{} {}>".format(self.OBJECTNAME, self.ID)

	def get_filedir_filename(self, ID = None, dt = None):
		if ID is None:
			ID = self.ID
		if dt is None:
			# filedir now depends on date information, defined upon first save() and stored via add_part_to_list
			with open(self.partlistfile, 'r') as opfl:
				data = json.load(opfl)
				date = data[str(ID)]
		else:
			date = dt

		filedir = os.sep.join([ DATADIR, self.FILEDIR.format(ID=ID, date=date) ])
		filename = self.FILENAME.format(ID=ID)
		return filedir, filename


	# NEW:  For search page
	def add_part_to_list(self, ID=None, date=None):
		# NOTE:  Date must have format {m}-{d}-{y}
		# ID param is for tooling:  self.ID is NOT the key that must be saved!
		# Instead, "ID_institution" is used.
		# self.ID -> id_
		id_ = self.ID if ID is None else ID

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not id_ in data.keys():
				# Note creation date and pass it to the dict
				dcreated = time.localtime()
				if id_ == None:  print("ERROR:  id_ in add_part_to_list is None!!!")
				if date:
					dc = date
				else:
					dc = '{}-{}-{}'.format(dcreated.tm_mon, dcreated.tm_mday, dcreated.tm_year)
				data[str(id_)] = dc
		with open(self.partlistfile, 'w') as opfl:
			json.dump(data, opfl)


	# Utility for xml-based _load_...:  Take a string from an XML element and return a var w/ the correct type
	# "True" -> bool, 100 -> int, etc.
	def _convert_str(self, string):
		if not string:  return None
		if string.isdigit():
			return int(string)
		elif string.replace('.','',1).isdigit():
			return float(string)
		elif string == "True":  # direct bool conversion fails...
			return True
		elif string == "False":
			return False
		elif string == "None":
			return None
		else:
			return string


	def load(self, ID):
		print("Attempting to load", ID)
		if ID == -1:
			self.clear()
			return False

		# First, check partlistfile to confirm existence.
		# If not found in partlistfile, return false.
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			print("Keys:", data.keys())
			if not str(ID) in data.keys():
				self.clear()
				return False
		print("Found in partlistfile")

		filedir, filename = self.get_filedir_filename(ID)
		xml_file = os.sep.join([filedir, filename])

		if not os.path.exists(xml_file):
			self.clear()
			return False
		print("Found xml file", xml_file)

		with open(xml_file, 'r') as opfl:
			data = json.load(opfl)

		self.ID = ID
		data_keys = data.keys()
		PROPERTIES = self.PROPERTIES + self.PROPERTIES_COMMON
		DEFAULTS = {**self.DEFAULTS_COMMON, **getattr(self, 'DEFAULTS', {})}

		props_in_data = [prop in data_keys for prop in PROPERTIES]
		print("data_keys:", data_keys)
		print("Properties:", PROPERTIES)
		print("props in data", props_in_data)

		for i,prop in enumerate(PROPERTIES):
			prop_in_data = props_in_data[i]

			if prop_in_data:
				setattr(self, prop, data[prop])
			else:
				prop_default = DEFAULTS[prop] if prop in DEFAULTS.keys() else None

		return True



	def new(self, ID):
		# NOTE:  Should never be called on an existing object.
		# The only person you can blame for doing this is yourself.
		self.ID = ID
		PROPERTIES = self.PROPERTIES + self.PROPERTIES_COMMON
		DEFAULTS = {**self.DEFAULTS_COMMON, **getattr(self, 'DEFAULTS', {})}
		for prop in PROPERTIES:
			setattr(self, prop, DEFAULTS[prop] if prop in DEFAULTS.keys() else None)


	def clear(self):
		self.ID = None
		PROPERTIES = self.PROPERTIES + self.PROPERTIES_COMMON
		DEFAULTS   = {**self.DEFAULTS, **self.DEFAULTS_COMMON}
		for prop in PROPERTIES:
			setattr(self, prop, DEFAULTS.get(prop, None))
		# For clearing, we don't check or set defaults
		# All properties, including ID, are set to None
		# Attempts to use an object when it has been cleared are meant to produce errors


	def generate_xml(self, input_dict):
		# GenerateXML ElementTree from input_dictionary, and return the ElementTree.
		# Note:  does not save XML file!
		# Note:  input_dict is a list of all items contained by the ROOT.  ROOT is not included, but 
		#        is generated automatically.

		root = Element('ROOT')
		root.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
		tree = ElementTree(root)

		for item_name, item in input_dict.items():
			if item_name == "DATA_SET" and self.MULTIPART_CLASS:
				self.make_dataset_element(root, item)
			else:
				child = self.dict_to_element(item, item_name)
				root.append(child)
		return tree


	def make_dataset_element(self, parent, item):
		# NEW:  If DATA_SET encountered, need to write one DATA_SET for each *module assembled.
		num_parts = 0
		protomodules = getattr(self, 'protomodules', None)
		modules = getattr(self, 'modules', None)
		if protomodules:
			num_parts = sum([1 for p in protomodules if p])  # List with Nones if no protomodule
		elif modules:
			num_parts = sum([1 for p in modules if p])
		else:  print("WARNING:  Failed to find [proto]modules in make_dataset_element()!")
		dataset_dict = getattr(self, item, None)
		if not dataset_dict:  print("ERROR: failed to find {}.{} in make_dataset_element()!".format(self.__class__.__name__, item))
		for i in range(num_parts):
			# Create a DATA_SET for each part
			child = self.dict_to_element(dataset_dict, "DATA_SET", data_set_index=i)
			parent.append(child)


	def dict_to_element(self, input_dict, element_name, data_set_index=None):
		# Utility for save()
		# Reads a dictionary, and returns an XML element 'element_name' filled with the contents of the current object
		# structured according to that dictionary.
		# NOTE:  This must be able to work recursively.  I.e. if one of the objs in the input_dict is a dict,
		#    it reads *that* dictionary and creates an element for it, +appends it to current element.  Etc.

		# NEW:  Add special case for multi-item assembly steps.  Will always appear in DATA_SET dict.
		# If in DATA_SET, data_set_index will NOT be None.  If not None, and the requested item is a list, 
		# 	return element i instead of the usual list handling case.
		#print("dict_to_element: input_dict is", input_dict)

		parent = Element(element_name)
		
		for item_name, item in input_dict.items():
			# CHANGE FOR NEW XML SYSTEM:
			# item is a list (comments), dict (another XML layer), or string (var)
			# If string, use getattr()

			if item_name == "DATA_SET":
				print("DATA SET FOUND; this is WIP")
				self.make_dataset_element(parent, item)
			elif type(item) == dict:
				# Recursive case: Create an element from the child dictionary.
				# "Remember" whether currently in a DATA_SET
				child = self.dict_to_element(item, item_name, data_set_index=data_set_index)
				# Special case for PARTs:
				if item_name == "PART" and data_set_index is None:
					child.set('mode','auto')
				parent.append(child)
			elif type(item) == list:
				# Second recursive case:  for multiple parts, etc
				for it in item:
					# For each item, create elements recursively and append to parent
					ch = self.dict_to_element(it, item_name, data_set_index=data_set_index)
					if item_name == "PART":
						ch.set('mode', 'auto')
					parent.append(ch)
			elif type(getattr(self, item, None)) == list:
				# Base case 1:  List of comments.  Create an element for each one.
				# If currently in a DATA_SET, grab the ith element!
				if data_set_index != None:
					child = Element(item_name)
					child.text = str(getattr(self, item, None)[data_set_index])
					parent.append(child)
				elif getattr(self, item, None) == []:
					# If empty, need to add a placeholder so load() knows to add an empty list
					child = Element(item_name)
					child.text = '[]'
					parent.append(child)
				else:
					for comment in getattr(self, item, None):
						child = Element(item_name)
						child.text = str(comment)
						parent.append(child)
			else:
				# Base case 2:
				child = Element(item_name)
				child.text = str(getattr(self, item, None))  # item should be the var name!
				# Fill attrs that don't exist w/ None
				parent.append(child)

		return parent


	# NOT fully general--db-involving parts need more code to handle files-to-upload.
	def save(self):
		# NOTE:  Can't check item existence via filepath existence, bc filepath isn't known until after item creation!
		# Instead, go into partlist dict and check to see whether item exists:
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not str(self.ID) in data.keys():
				# Object does not exist, so can't get filedir from get_filedir_filename()...
				# ...until the date has been set via add_part_to_list.  Do that now.
				self.add_part_to_list()

		filedir, filename = self.get_filedir_filename()
		file = os.sep.join([filedir, filename])
		if not os.path.exists(filedir):
			os.makedirs(filedir)	

		with open(file, 'w') as opfl:
			json.dump(vars(self), opfl, indent=4)


	# Return a list of all files to be uploaded to the DB
	# (i.e. all files in the object's storage dir with "upload" in the filename)
	#def filesToUpload(self):
	#	fdir, fname = self.get_filedir_filename()
	#	# Grab all files in that directory
	#	print("Found files to upload:", glob.glob(fdir + "/*upload*"))
	#	return glob.glob(fdir + "/*upload*")

	# NEW:  All parts/assembly steps use this, bc can't write multiple XML tags w/ same name
	@property
	def comments_concat(self):
		cmts = ';;'.join(self.comments)
		# Impose len reqt of 4000 chars (for DB; actual limit unknown/TBD)
		if len(cmts) > 4000:
			print("WARNING:  Total combined comments length exceeds 4000 chars - excess chars truncated")
			cmts = cmts[:4000]
		return cmts



# CLASS FOR TOOLS:
# These need to be treated separately because they're saved based on ID+institution and not just institution
# Mostly identical to fsobj, but with institution added as a primary key.
# Must "act" as if it's saved w/ 2 primary keys, but actually there's only one.

class fsobj_tool(fsobj):

	#def add_part_to_list(self):
	#	super(fsobj_tool, self).add_part_to_list("{}_{}".format(self.ID, self.institution))

	def load(self, ID, institution):
		return super(fsobj_tool, self).load("{}_{}".format(ID, institution))

	def new(self, ID, institution):
		#self.institution = institution
		super(fsobj_tool, self).new("{}_{}".format(ID, institution))

	#def clear(self):
	#	self.institution = None
	#	super(fsobj_tool, self).clear()

	@property
	def institution(self):
		 return self.ID.split("_")[1]







###############################################
##################  tooling  ##################
###############################################

class tool_sensor(fsobj_tool):
	OBJECTNAME = "sensor tool"
	FILEDIR = os.sep.join(['tooling','tool_sensor'])
	FILENAME = 'tool_sensor_{ID}.json'
	PROPERTIES = [
		'location',
	]



	# NOTE:  This and below objects must be saved with save_tooling(), not save().


class tool_pcb(fsobj_tool):
	OBJECTNAME = "PCB tool"
	FILEDIR = os.sep.join(['tooling','tool_pcb'])
	FILENAME = 'tool_pcb_{ID}.json'
	PROPERTIES = [
		'location',
	]


class tray_assembly(fsobj_tool):
	OBJECTNAME = "assembly tray"
	FILEDIR = os.sep.join(['tooling','tray_assembly'])
	FILENAME = 'tray_assembly_{ID}.json'
	PROPERTIES = [
		'location',
	]


class tray_component_sensor(fsobj_tool):
	OBJECTNAME = "sensor tray"
	FILEDIR = os.sep.join(['tooling','tray_component_sensor'])
	FILENAME = 'tray_component_sensor_{ID}.json'
	PROPERTIES = [
		'location',
	]


class tray_component_pcb(fsobj_tool):
	OBJECTNAME = "pcb tray"
	FILEDIR = os.sep.join(['tooling','tray_component_pcb'])
	FILENAME = 'tray_component_pcb_{ID}.json'
	PROPERTIES = [
		'location',
	]



########################################################
###### PARENT CLASS FOR PARTS AND ASSEMBLY STEPS #######
########################################################

# NOTE:  ID can be saved as either an int OR a string.

class fsobj_db(fsobj):
	# Key vars and utilities:
	XML_CONSTS = []  # List of vars loaded, but not edited, by GUI

	VNUM = 1   # Param in conditions XML

	COND_HEADER_DICT = {
		'TYPE':{
			'EXTENSION_TABLE_NAME':'COND_TABLE_NAME',
			'NAME':'TABLE_DESC',
		},
		'RUN':{
			'RUN_NAME':'RUN_TYPE',
			'RUN_BEGIN_TIMESTAMP':'run_begin_timestamp_',  # Format:  2018-03-26 00:00:00
			'RUN_END_TIMESTAMP':'run_end_timestamp_',
			'INITIATED_BY_USER':'initiated_by_user',
			'LOCATION':'location',
			'COMMENT_DESCRIPTION':'comment_description',
		}
	}

	# Member functions:

	def __init__(self):
		super(fsobj_db, self).__init__()
		# NO LONGER NECESSARY (via json):
		# Add all other vars to XML_STRUCT_DICT
		# (so they will be saved accordingly)
		#if self.XML_STRUCT_DICT is None:
		#	self.XML_STRUCT_DICT = {'data':{'row':{} } }
		#for var in self.PROPERTIES + self.PROPERTIES_COMMON:
		#	if var not in self.XML_CONSTS:  self.XML_STRUCT_DICT['data']['row'][var] = var

	# Universal properties:

	@property
	def institution_id(self):
		# INSTITUTION_DICT maps ID -> name#
		if self.institution == None:
			return None
		for instID, instname in INSTITUTION_DICT.items():
			if self.institution == instname:
				return instID
		print("WARNING:  institution ID for {} not found in INSTITUTION_DICT".format(self.institution))
		return None
	@institution_id.setter
	def institution_id(self, value):
		if value is None:
			self.institution = None
		elif not value in INSTITUTION_DICT.keys():
			print("WARNING:  institution_id:  Found invalid location ID {}".format(value))
			self.institution = None
		else:
			self.institution = INSTITUTION_DICT[value]

	# Auto-set:  if value downloaded, leave unchanged.  Otherwise, set to now.
	@property
	def run_begin_timestamp_(self):
		# Auto-formatted: {}-{}-{} {}:{}:{}.{}
		return str(datetime.datetime.now()) if self.run_begin_timestamp is None else self.run_begin_timestamp

	@property
	def run_end_timestamp_(self):
		return str(datetime.datetime.now()) if self.run_end_timestamp is None else self.run_end_timestamp




### PARENT CLASS FOR PARTS


class fsobj_part(fsobj_db):
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
		"record_insertion_user",  # read-only, likely not used
		"kind_of_part_id",  # NOTE:  Not used
		"manufacturer_id",  # -> manufacturer in XML, not always necessary
		"barcode",  # CANNOT upload this, breaks the xml
		"serial_number"
		# Read/write:
		#"location", # replaced
		#"location_name",  # NOTE:  Actually institution
		"production_date",
		"batch_number",
		"record_lastupdate_user",  # NOTE:  Using this in GUI

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
		#"comment_description"
	]
	
	COND_HEADER_PROPERTIES = [
		"run_name",
		"run_begin_timestamp",
		"run_end_timestamp",
		"initiated_by_user",
		"location_name",
		"comment_description"
	]

	COND_PROPERTIES = []
	LOCAL_PROPERTIES = []

	XML_PART_TEMPLATE = {"PARTS":{"PART":{  # same for all parts
		"KIND_OF_PART":"kind_of_part",
		"RECORD_INSERTION_USER":"record_insertion_user",
		"SERIAL_NUMBER":"ID",
		"BARCODE":"barcode",
		"COMMENT_DESCRIPTION":"comment_description",
		"LOCATION":"location_name",
		"MANUFACTURER":"manufacturer"  # Usually not used
	}}}
	# XML_COND_TEMPLATE is separate for each part

	def __init__(self):
		self.PROPERTIES = self.PART_PROPERTIES + self.COND_PROPERTIES \
						  + self.COND_HEADER_PROPERTIES + self.LOCAL_PROPERTIES
		super(fsobj_part, self).__init__()


	def sql_request_part(self, ID):
		#return "select * from PARTS p where p.SERIAL_NUMBER={}".format(self.ID)
		# old - also want to get KIND_OF_PART name for geometry info
		return """select kp.DISPLAY_NAME, p.*
from CMS_HGC_CORE_CONSTRUCT.PARTS p
inner join CMS_HGC_CORE_CONSTRUCT.KINDS_OF_PARTS kp
on p.KIND_OF_PART_ID = kp.KIND_OF_PART_ID
where p.SERIAL_NUMBER=\'{}\'
""".format(ID)

	def sql_request_cond(self, ID):
		# SQL command:  Given a part SERIAL_NUMBER, select the entire corresponding row from COND_TABLE
		# NOTE:  LOCATION_NAME is new, since PART only stores ID number
		return """select p.SERIAL_NUMBER, fd.*, lo.LOCATION_NAME
from CMS_HGC_CORE_COND.COND_DATA_SETS ds
inner join CMS_HGC_HGCAL_COND.{} fd
on fd.CONDITION_DATA_SET_ID = ds.CONDITION_DATA_SET_ID
inner join CMS_HGC_CORE_CONSTRUCT.PARTS p
on p.PART_ID = ds.PART_ID
inner join CMS_HGC_CORE_MANAGEMNT.LOCATIONS lo
on p.LOCATION_ID = lo.LOCATION_ID
where p.SERIAL_NUMBER=\'{}\'""".format(self.COND_TABLE, ID)


	def save(self):
		# This one handles the json files
		super(fsobj_part, self).save()

		# NEXT, write the upload files!
		# There's two:  One for Build_UCSB_ProtoModules_00.xml, one for ProtoModules_BuildCond_00.xml (part and cond).
		# Defined in XML_PART_TEMPLATE, XML_COND_TEMPLATE
		filedir, filename = self.get_filedir_filename()
		fname_build = filename.replace('.json', '_build_upload.xml')
		fname_cond  = filename.replace('.json', '_cond_upload.xml')
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

	# Now just inheriting
	def filesToUpload(self):
		print("Finding files:")
		if self.ID == "" or self.ID is None:  return []
		print("filesToUpload: Getting filedir filename")
		filedir, filename = self.get_filedir_filename()
		print("Got filedir filename")
		fname_build = filename.replace('.json', '_build_upload.xml')
		fname_cond  = filename.replace('.json', '_cond_upload.xml')
		print("Found", [os.path.join(filedir, fname_build), os.path.join(filedir, fname_cond)])
		return [os.path.join(filedir, fname_build), os.path.join(filedir, fname_cond)]
		


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
				# sometimes, no cond dataset will be uploaded.  If so:
				if not data_x:  return
				for colname, var in data_x.items():
					# NOTE:  datetime objs cannot be stored as json, or simply sent to xml...so stringify
					if type(var) == datetime.datetime:
						dstring = "{}-{}-{} {:02d}:{:02d}:{:02d}".format(var.year, var.month, var.day, var.hour, var.minute, var.second)
						setattr(self, colname.lower(), dstring)
					elif type(var) == datetime.date:
						dstring = "{}-{}-{}".format(var.year, var.month, var.day)
						setattr(self, colname.lower(), dstring)
					elif type(var) == str:
						st = self._convert_str(var)
						setattr(self, colname.lower(), st)
					else:
						setattr(self, colname.lower(), var)
			fill_self(data_part)
			fill_self(data_cond)

			# Data is now in python obj.  Ensure save:
			self.ID = ID
			self.save()

		#self.ID = ID
		return True




#class fsobj_assembly(fsobj):
#	#@property
#	#def sql_request(self):
#	#	return "select * from PARTS p where p.SERIAL_NUMBER={}".format(self.ID)






###############################################
#####  components, protomodules, modules  #####
###############################################

class baseplate(fsobj_part):
	OBJECTNAME = "baseplate"
	FILEDIR = os.sep.join(['baseplates','{date}'])
	FILENAME = "baseplate_{ID}.json"

	# Note:  serial_number == self.ID
	COND_TABLE_NAME = 'SI_MODULE_BASEPLATE'

	COND_PROPERTIES = [
		# Read/write from cond:
		"thickness",
		"flatness",
		"grade",
		"comments",	
	]

	LOCAL_PROPERTIES = [
		# Locally-saved, not part of DB:
		"institution_location",  # location at institution
		"protomodule",  # TBD
		"module",
	]

	# Derived properties:
	# material (from display_name)
	# geometry
	# channel density

	DEFAULTS = {
		"size":     '8', # This should not be changed!
		"display_name": "None Baseplate None None"
	}


	XML_COND_TEMPLATE = {
		"HEADER":fsobj_db.COND_HEADER_DICT,
		"DATA_SET":{
			"COMMENT_DESCRIPTION":"comment_description",
			"VERSION":"VNUM",
			"PART":{
				"SERIAL_NUMBER":"ID",
				"KIND_OF_PART":"kind_of_part",
			},
			"DATA":{
				"FLATNESS":"flatness",
				"THICKNESS":"thickness",
				"GRADE":"grade",
				"MATERIAL":"mat_type",
				"COMMENTS":"comments",
			}
		}
	}

	# for HEADER_DICT
	COND_TABLE = "SI_MODULE_BASEPLATE"
	TABLE_DESC = "Si Module Baseplate Test Data"

	# List of vars that should NOT be edited in the GUI and are only loaded from DB
	# (And some info would be redundant w/ other constants, eg KIND_OF_PART and self.size)
	XML_CONSTS = [
		'size',
	]


	@property
	def kind_of_part(self):
		return self.display_name
		#"{} Baseplate {} {}".format(self.material, self.channel_density, self.shape)

	@property
	def mat_type(self):
		return self.display_name.split()[0]
	@mat_type.setter  # eventually, these will not be used
	def mat_type(self, value):
		# Cannot replace bc of case w/ multiple Nones
		# split, then change and recombine
		splt = self.display_name.split(" ")
		splt[0] = str(value)
		self.display_name = " ".join(splt)

	@property
	def channel_density(self):
		if self.display_name is None:  return None
		return self.display_name.split()[2]
	@channel_density.setter
	def channel_density(self, value):
		splt = self.display_name.split(" ")
		splt[2] = str(value)
		self.display_name = " ".join(splt)

	@property
	def geometry(self):
		if self.display_name is None:  return None
		return self.display_name.split()[3]
	@geometry.setter
	def geometry(self, value):
		splt = self.display_name.split(" ")
		splt[3] = str(value)
		self.display_name = " ".join(splt)

	def ready_step_sensor(self, step_sensor = None, max_flatness = None):
		# POSSIBLE:  Query DB to check for sensors?
		# unless this is already done via goto/etc...
		if self.step_sensor and self.step_sensor != step_sensor:
			return False, "already assigned to protomodule {}".format(self.protomodule)
		return True, ""


class sensor(fsobj_part):
	OBJECTNAME = "sensor"
	FILEDIR = os.sep.join(['sensors','{date}'])
	FILENAME = "sensor_{ID}.json"

	COND_TABLE_NAME = "FLATNS_SENSOR_DATA"

	# Note:  serial_number == self.ID
	COND_PROPERTIES = [
		# Read/write from cond:
		"tested_by",
		"test_date",
		"status",
		"test_file_name",
		"thickness",
		"flatness",
		"grade",
		"comments",	
		"visual_inspection"
	]

	LOCAL_PROPERTIES = [
		# Locally-saved, not part of DB:
		"location",  # location at institution
		"protomodule",  # TBD
		"module",
	]

	# Derived properties:
	# material (from display_name)
	# geometry
	# channel density

	DEFAULTS = {
		"size":     '8', # This should not be changed!
		"display_name": "None Si Sensor None None"
	}

	XML_COND_TEMPLATE = {
		"HEADER":fsobj_db.COND_HEADER_DICT,
		"DATA_SET":{
			"COMMENT_DESCRIPTION":"comment_description",
			"VERSION":"VNUM",
			"PART":{
				"SERIAL_NUMBER":"ID",
				"KIND_OF_PART":"kind_of_part",
			},
			"DATA":{
				"TESTED_BY":"tested_by",
				"TEST_DATE":"test_date_",
				"STATUS":"status",
				"TEST_FILE_NAME":"test_file_name",
				"FLATNESS":"flatness",
				"THICKNESS":"thickness",
				"GRADE":"grade",
				"COMMENTS":"comments",
				"VISUAL_INSPECTION":"visual_inspection",
			}
		}
	}
	# Note:  properties w/ _ at the end of the filename are auto-filled
	# e.x. test_date:  If not null (if downloaded value), leave unchanged.
	# If null, set to current date.

	# for HEADER_DICT
	COND_TABLE = "FLATNS_SENSOR_DATA"
	TABLE_DESC = "HGC Sensor Flatness Data"


	# List of vars that should NOT be edited in the GUI and are only loaded from DB
	# (And some info would be redundant w/ other constants, eg KIND_OF_PART and self.size)
	XML_CONSTS = [
		'size',
	]


	@property
	def kind_of_part(self):
		return self.display_name

	@property
	def sen_type(self):
		return self.display_name.split()[0]
	@sen_type.setter  # eventually, these will not be used
	def sen_type(self, value):
		# Cannot replace bc of case w/ multiple Nones
		# split, then change and recombine
		print("SEN_TYPE SETTER")
		splt = self.display_name.split(" ")
		splt[0] = str(value)
		self.display_name = " ".join(splt)

	@property
	def channel_density(self):
		if self.display_name is None:  return None
		return self.display_name.split()[3]
	@channel_density.setter
	def channel_density(self, value):
		splt = self.display_name.split(" ")
		splt[3] = str(value)
		self.display_name = " ".join(splt)

	@property
	def geometry(self):
		if self.display_name is None:  return None
		return self.display_name.split()[4]
	@geometry.setter
	def geometry(self, value):
		splt = self.display_name.split(" ")
		splt[4] = str(value)
		self.display_name = " ".join(splt)


	@property  # Note: not a measured value
	def thickness(self):
		return float(self.type.split('um')[0])/1000
	@thickness.setter
	def thickness(self, value):
		pass

	@property
	def test_date_(self):
		return str(datetime.datetime.now()) if self.test_date is None else self.test_date

	# Should not be passing any of these params yet
	def ready_step_sensor(self, step_sensor = None, max_flatness = None):
		if self.step_sensor and self.step_sensor != step_sensor:
			return False, "already assigned to protomodule {}".format(self.protomodule)

		# Kapton qualification checks:
		errstr = ""
		checks = [
			self.inspection == "pass",
		]
		#if self.kapton_flatness is None:
		if self.flatness is None:
			errstr+=" flatness doesn't exist."
			checks.append(False)
		elif not (max_flatness is None):
			if max_flatness<self.flatness:
				errstr+="kapton flatness "+str(self.flatness)+" exceeds max "+str(max_flatness)+"."
				checks.append(False)

		if not all(checks):
			return False, "sensor qualification failed or incomplete. "+errstr
		else:
			return True, ""



class pcb(fsobj_part):
	OBJECTNAME = "PCB"
	FILEDIR = os.sep.join(['pcbs','{date}'])
	FILENAME = "pcb_{ID}.json"

	COND_TABLE_NAME = "FLATNS_PCB_ROCS_DATA"

	# Note:  serial_number == self.ID
	COND_PROPERTIES = [
		# Read/write from cond:
		"tested_by",
		"test_date",
		"status",
		"thickness",
		"flatness",
		"grade",
		"comments",	
		"test_file_name",
	]

	LOCAL_PROPERTIES = [
		# Locally-saved, not part of DB:
		"location",  # location at institution
		"protomodule",  # TBD
		"module",
	]

	# Derived properties:
	# material (from display_name)
	# geometry
	# channel density

	DEFAULTS = {
		"size":     '8', # This should not be changed!
		"display_name": "PCB None None"
	}


	XML_COND_TEMPLATE = {
		"HEADER":fsobj_db.COND_HEADER_DICT,
		"DATA_SET":{
			"COMMENT_DESCRIPTION":"comment_description",
			"VERSION":"VNUM",
			"PART":{
				"SERIAL_NUMBER":"ID",
				"KIND_OF_PART":"kind_of_part",
			},
			"DATA":{
				"TESTED_BY":"tested_by",
				"TEST_DATE":"test_date_",
				"STATUS":"status",
				"FLATNESS":"flatness",
				"THICKNESS":"thickness",
				"GRADE":"grade",
				"TEST_FILE_NAME":"test_file_name",
				"COMMENTS":"comments",
			}
		}
	}

	# for HEADER_DICT
	COND_TABLE = "FLATNS_PCB_ROCS_DATA"
	TABLE_DESC = "Flatness PCB ROCs Mounted"

	# List of vars that should NOT be edited in the GUI and are only loaded from DB
	# (And some info would be redundant w/ other constants, eg KIND_OF_PART and self.size)
	XML_CONSTS = [
		'size',
	]


	@property
	def kind_of_part(self):
		return self.display_name

	# no mat_type
	@property
	def channel_density(self):
		if self.display_name is None:  return None
		return self.display_name.split()[1]
	@channel_density.setter
	def channel_density(self, value):
		splt = self.display_name.split(" ")
		splt[1] = str(value)
		self.display_name = " ".join(splt)

	@property
	def geometry(self):
		if self.display_name is None:  return None
		return self.display_name.split()[2]
	@geometry.setter
	def geometry(self, value):
		splt = self.display_name.split(" ")
		splt[2] = str(value)
		self.display_name = " ".join(splt)

	@property
	def test_date_(self):
		return str(datetime.datetime.now()) if self.test_date is None else self.test_date

	def ready_step_pcb(self, step_pcb = None):
		if self.step_pcb and self.step_pcb != step_pcb:
			return False, "already assigned to module {}".format(self.module)
		return True, ""


class protomodule(fsobj_part):
	OBJECTNAME = "protomodule"
	FILEDIR = os.sep.join(['protomodules','{date}'])
	FILENAME = 'protomodule_{ID}.json'

	# Note:  serial_number == self.ID
	COND_PROPERTIES = [
		# Read/write from cond:
		"asmbl_tray_name",
		"plt_ser_num",
		"plt_asm_row",
		"plt_asm_col",
		"plt_fltnes_mm",
		"plt_thknes_mm",
		"comp_tray_name",
		"snsr_ser_num",
		"snsr_cmp_row",
		"snsr_cmp_col",
		"snsr_x_offst",
		"snsr_y_offst",
		"snsr_ang_offset",
		"snsr_tool_name",
		"snsr_tool_ht_set",
		"snsr_tool_ht_chk",
		"glue_type",
		"glue_batch_num",
		"slvr_epxy_type",
		"slvr_epxy_batch_num",
		"plt_grade",
		"snsr_tool_feet_chk",
		"snsr_step"
	]

	LOCAL_PROPERTIES = [
		# Locally-saved, not part of DB:
		"location",  # location at institution
		#"protomodule",  # TBD
		"module",
	]

	# Derived properties:
	# material (from display_name)
	# geometry
	# channel density

	DEFAULTS = {
		"size":     '8', # This should not be changed!
		"display_name": "None None Si ProtoModule None None"
	}


	XML_COND_TEMPLATE = {
		"HEADER":fsobj_db.COND_HEADER_DICT,
		"DATA_SET":{
			"COMMENT_DESCRIPTION":"comment_description",
			"VERSION":"VNUM",
			"PART":{
				"SERIAL_NUMBER":"ID",
				"KIND_OF_PART":"kind_of_part",
			},
			"DATA":{
				"ASMBL_TRAY_NAME":"asmbl_tray_name",
				"PLT_SER_NUM":"plt_ser_num",
				"PLT_ASM_ROW":"plt_asm_row",
				"PLT_ASM_COL":"plt_asm_col",
				"PLT_FLTNS_MM":"plt_fltns_mm",
				"PLT_CHKNES_MM":"plt_thknes_mm",
				"COMP_TRAY_NAME":"comp_tray_name",
				"SNSR_SER_NUM":"snsr_ser_num",
				"SNSR_COMP_ROW":"snsr_cmp_row",
				"SNSR_X_OFFST":"snsr_x_offst",
				"SNSR_T_OFFST":"snsr_y_offst",
				"SNSR_ANG_OFFSET":"snsr_ang_offset",
				"SNSR_TOOL_NAME":"snsr_tool_name",
				"SNSR_TOOL_HT_SET":"snsr_tool_ht_set",
				"SNSR_TOOL_HT_CHK":"snsr_tool_ht_chk",
				"GLUE_TYPE":"glue_type",
				"GLUE_BATCH_NUM":"glue_batch_num",
				"SLVR_EPXY_TYPE":"slvr_epxy_type",
				"SLVR_EPXY_BATCH_NUM":"slvr_epxy_batch_num",
				"PLT_GRADE":"plt_grade",
				"SNSR_TOOL_FEET_CHK":"snsr_tool_feet_chk",
				"SNSR_STEP":"snsr_step"

			}
		}
	}

	# for HEADER_DICT
	COND_TABLE = "HGC_PRTO_MOD_ASMBLY"
	TABLE_DESC = "HGC Six Inch Proto Module Assembly"

	# List of vars that should NOT be edited in the GUI and are only loaded from DB
	# (And some info would be redundant w/ other constants, eg KIND_OF_PART and self.size)
	XML_CONSTS = [
		'size',
	]


	# Note:  auto-complete this if part is created from baseplate/sensor/etc
	@property
	def kind_of_part(self):
		return self.display_name
		#"{} Baseplate {} {}".format(self.material, self.channel_density, self.shape)

	# TODO : name this, decide whether to auto-set or manually set type
	@property
	def calorimeter_type(self):
		# 'EM' if self.baseplate.material=='CuW' else 'HAD'	
		return self.display_name.split()[0]
	@calorimeter_type.setter  # eventually, these will not be used
	def calorimeter_type(self, value):
		# Cannot replace bc of case w/ multiple Nones
		# split, then change and recombine
		print("CALORIMETER_TYPE SETTER")
		splt = self.display_name.split(" ")
		splt[0] = str(value)
		self.display_name = " ".join(splt)

	@property
	def sen_type(self):
		return self.display_name.split()[1]
	@sen_type.setter  # eventually, these will not be used
	def sen_type(self, value):
		# Cannot replace bc of case w/ multiple Nones
		# split, then change and recombine
		print("SEN_TYPE SETTER")
		splt = self.display_name.split(" ")
		splt[1] = str(value)
		self.display_name = " ".join(splt)

	@property
	def channel_density(self):
		if self.display_name is None:  return None
		return self.display_name.split()[4]
	@channel_density.setter
	def channel_density(self, value):
		splt = self.display_name.split(" ")
		splt[4] = str(value)
		self.display_name = " ".join(splt)

	@property
	def geometry(self):
		if self.display_name is None:  return None
		return self.display_name.split()[5]
	@geometry.setter
	def geometry(self, value):
		splt = self.display_name.split(" ")
		splt[5] = str(value)
		self.display_name = " ".join(splt)


	@property  # Note: not a measured value
	def thickness(self):
		return float(self.type.split('um')[1])/1000
	@thickness.setter
	def thickness(self, value):
		pass


	"""
	@property
	def assem_tray_pos(self):
		return 
		#return "TRPOSN_{}{}".format(self.tray_row, tray_col)

	@property
	def comp_tray_pos(self):
		return "CMPOSN_{}{}".format(self.tray_row, tray_col)

	@property
	def tray_posn(self):
		# If has a sensor step, grab the position of this sensor and return it here...
		if self.step_sensor is None:
			print("Warning:  assm_tray_posn:  no sensor step yet")
			return "None"
		temp_sensor_step = step_sensor()
		found = temp_sensor_step.load(self.step_sensor)
		if not found:
			print("ERROR in tray_posn:  protomodule has sensor step {}, but none found!".format(self.step_sensor))
			return "None"
		else:
			position = temp_sensor_step.sensors.index(self.ID)
			return position

	@property
	def tray_row(self):
		posn = self.tray_posn()
		if posn == "None":  return posn
		else:  return posn%2+1

	@property
	def tray_col(self):
		posn = self.tray_posn()
		if posn == "None": return posn
		else:  return posn//3+1
	
	@property
	def baseplate_type(self):
		if self.baseplate is None:
			print("In baseplate_type:  protomod has no baseplate!")
			return None
		temp_baseplate = baseplate()
		if not temp_baseplate.load(self.baseplate):
			print("ERROR:  failed to load baseplate {} in baseplate_type!".format(self.baseplate))
			return None
		return temp_baseplate.description

	@property
	def sensor_type(self):
		if self.sensor is None:
			print("In sensor_type:  protomod has no sensor!")
			return None
		temp_sensor = sensor()
		if not temp_sensor.load(self.sensor):
			print("ERROR:  failed to load sensor {} in sensor_type!".format(self.sensor))
			return None
		return temp_sensor.description

	@property
	def resolution(self):
		if self.sensor is None:
			print("ERROR in module resolution:  sensor is None!")
			return None
		temp_sensor = sensor()
		if not temp_sensor.load(self.sensor):
			print("ERROR:  Could not find child sensor {}!".format(self.sensor))
			return None
		return temp_sensor.resolution
	"""


	def ready_step_pcb(self, step_pcb = None):
		if self.step_pcb and self.step_pcb != step_pcb:
			return False, "already assigned to module {}".format(self.module)
		return True, ""

		



class module(fsobj_part):
	OBJECTNAME = "module"
	FILEDIR    = os.sep.join(['modules','{date}','module_{ID}'])
	FILENAME   = 'module_{ID}.json'

	# Note:  serial_number == self.ID
	COND_PROPERTIES = [
		# Read/write from cond:
		"asmbl_tray_name",
		"prto_ser_num",
		"prto_asm_row",
		"prto_asm_col",
		"comp_tray_name",
		"pcb_ser_num",
		"pcb_fltnes_mm",
		"pcb_thknes_mm",
		"pcb_cmp_row",
		"pcb_cmp_col",
		"pcb_tool_name",
		"pcb_tool_ht_set",
		"pcb_tool_ht_chk",
		"glue_type",
		"glue_batch_num",
		"pcb_tool_feet_chk",
		"mod_grade",
		"pcb_step",
		"pcb_plcment_x_offset",
		"pcb_plcment_y_offset",
		"pcb_plcment_ang_offset",
		"mod_thkns_mm",
		"mod_fltns_mm",

		# wirebonding:
		"bond_wire_batch_num",
		"pre_inspection",
		"sylgard_batch",
		"wedge_batch",
		"back_bonds",
		"back_bonds_date",
		"back_bonds_user",
		"back_unbonded",
		"back_bond_inspxn",
		"back_repair_user",
		"front_bonds",
		"front_bonds_date",
		"front_bonds_user",
		"front_skip",
		"front_unbonded",
		"front_bond_inspxn",
		"front_repair_user",
		"back_encap",
		"back_encap_user",
		"back_encap_cure_start",
		"back_encap_cure_stop",
		"back_encap_inspxn",
		"front_encap",
		"front_encap_user",
		"front_encap_cure_start",
		"front_encap_cure_stop",
		"front_encap_inspxn",
		"is_test_bond_module",
		"bond_iull_user",  # typo in DB.......
		"bond_pull_avg",
		"bond_pull_stddev",
		"final_inspxn_user",
		"final_inspxn_ok",
		"wirebond_comments"
	]

	LOCAL_PROPERTIES = [
		# Locally-saved, not part of DB:
		"location",  # location at institution
		#"protomodule",  # TBD
	]

	# Derived properties:
	# material (from display_name)
	# geometry
	# channel density

	DEFAULTS = {
		"size":     '8', # This should not be changed!
		"display_name": "None None Si ProtoModule None None"
	}


	XML_COND_TEMPLATE = {
		"HEADER":fsobj_db.COND_HEADER_DICT,
		"DATA_SET":{
			"COMMENT_DESCRIPTION":"comment_description",
			"VERSION":"VNUM",
			"PART":{
				"SERIAL_NUMBER":"ID",
				"KIND_OF_PART":"kind_of_part",
			},
			"DATA":{
				"ASMBL_TRAY_NAME":"asmbl_tray_name",
				"PRTO_SER_NUM":"prto_ser_num",
				"PRTO_ASM_ROW":"prto_asm_row",
				"PRTO_ASM_COL":"prto_asm_col",
				"COMP_TRAY_NAME":"comp_tray_name",
				"PCB_SER_NUM":"pcb_ser_num",
				"PCB_FLTNES_MM":"pcb_fltnes_mm",
				"PCB_THKNES_MM":"pcb_thknes_mm",
				"PCB_CMP_ROW":"pcb_cmp_row",
				"PCB_CMP_COL":"pcb_cmp_col",
				"PCB_TOOL_NAME":"pcb_tool_name",
				"PCB_TOOL_HT_SET":"pcb_tool_ht_set",
				"PCB_TOOL_HT_CHK":"pcb_tool_ht_chk",
				"GLUE_TYPE":"glue_type",
				"GLUE_BATCH_NUM":"glue_batch_num",
				"PCB_TOOL_FEET_CHK":"pcb_tool_feet_chk",
				"MOD_GRADE":"mod_grade",
				"PCB_STEP":"pcb_step",
				"PCB_PLCMENT_X_OFFST":"pcb_plcment_x_offst",
				"PCB_PLCMENT_Y_OFFST":"pcb_plcment_y_offst",
				"SNSR_ANG_OFFSET":"snsr_ang_offset",
				"MOD_FLTNS_MM":"mod_fltns_mm",
				"MOD_FLTNS_MM":"mod_fltns_mm"
			}
		}
	}

	# Wirebonding-specific:
	WIREBOND_TABLE_NAME = "HGC_MOD_WIREBOND_TEST"
	WIREBOND_HEADER_DICT = {
		'TYPE':{
			'EXTENSION_TABLE_NAME':'WIREBOND_TABLE_NAME',
			'NAME':'TABLE_DESC',
		},
		'RUN':{
			'RUN_NAME':'RUN_TYPE',
			'RUN_BEGIN_TIMESTAMP':'run_begin_timestamp_',  # Format:  2018-03-26 00:00:00
			'RUN_END_TIMESTAMP':'run_end_timestamp_',
			'INITIATED_BY_USER':'initiated_by_user',
			'LOCATION':'location',
			'COMMENT_DESCRIPTION':'comment_description',
		}
	}
	XML_WIREBOND_TEMPLATE = {
		"HEADER":fsobj_db.COND_HEADER_DICT,
		"DATA_SET":{
			"COMMENT_DESCRIPTION":"comment_description",
			"VERSION":"VNUM",
			"PART":{
				"SERIAL_NUMBER":"ID",
				"KIND_OF_PART":"kind_of_part",
			},
			"DATA":{
				"BOND_WIRE_BATCH_NUM":"bond_wire_batch_num",
				"PRE_INSPECTION":"pre_inspection",
				"SYLGARD_BATCH":"sylgard_batch",
				"WEDGE_BATCH":"wedge_batch",
				"BACK_BONDS":"back_bonds",
				"BACK_BONDS_DATE":"back_bonds_date",
				"BACK_BONDS_USER":"back_bonds_user",
				"BACK_UNBONDED":"back_unbonded",
				"BACK_BOND_INSPXN":"back_bond_inspxn",
				"BACK_REPAIR_USER":"back_repair_user",
				"FRONT_BONDS":"front_bonds",
				"FRONT_BONDS_DATE":"front_bonds_date",
				"FRONT_BONDS_USER":"front_bonds_user",
				"FRONT_SKIP":"front_skip",
				"FRONT_UNBONDED":"front_unbonded",
				"FRONT_BOND_INSPXN":"front_bond_inspxn",
				"FRONT_REPAIR_USER":"front_repair_user",
				"BACK_ENCAP":"back_encap",
				"BACK_ENCAP_USER":"back_encap_user",
				"BACK_ENCAP_CURE_START":"back_encap_cure_start",
				"BACK_ENCAP_CURE_STOP":"back_encap_cure_stop",
				"BACK_ENCAP_INSPXN":"back_encap_inspxn",
				"FRONT_ENCAP":"front_encap",
				"FRONT_ENCAP_USER":"front_encap_user",
				"FRONT_ENCAP_CURE_START":"front_encap_cure_start",
				"FRONT_ENCAP_CURE_STOP":"front_encap_cure_stop",
				"FRONT_ENCAP_INSPXN":"front_encap_inspxn",
				"IS_TEST_BOND_MODULE":"is_test_bond_module",
				"BOND_IULL_USER":"bond_iull_user",  # typo in DB.......
				"BOND_PULL_AVG":"bond_pull_avg",
				"BOND_PULL_STDDEV":"bond_pull_stddev",
				"FINAL_INSPXN_USER":"final_inspxn_user",
				"FINAL_INSPXN_OK":"final_inspxn_ok",
				"WIREBOND_COMMENTS":"wirebond_comments"

			}
		}
	}


	# for HEADER_DICT
	COND_TABLE = "HGC_MOD_ASMBLY"
	TABLE_DESC = "HGC Six Inch Module Assembly"

	# List of vars that should NOT be edited in the GUI and are only loaded from DB
	# (And some info would be redundant w/ other constants, eg KIND_OF_PART and self.size)
	XML_CONSTS = [
		'size',
	]


	# Properties are same as protomodule's
	# Note:  auto-complete this if part is created from baseplate/sensor/etc
	@property
	def kind_of_part(self):
		return self.display_name

	# TODO : name this, decide whether to auto-set or manually set type
	@property
	def calorimeter_type(self):
		# 'EM' if self.baseplate.material=='CuW' else 'HAD'	
		return self.display_name.split()[0]
	@calorimeter_type.setter  # eventually, these will not be used
	def calorimeter_type(self, value):
		# Cannot replace bc of case w/ multiple Nones
		# split, then change and recombine
		print("CALORIMETER_TYPE SETTER")
		splt = self.display_name.split(" ")
		splt[0] = str(value)
		self.display_name = " ".join(splt)

	@property
	def sen_type(self):
		return self.display_name.split()[1]
	@sen_type.setter  # eventually, these will not be used
	def sen_type(self, value):
		# Cannot replace bc of case w/ multiple Nones
		# split, then change and recombine
		print("SEN_TYPE SETTER")
		splt = self.display_name.split(" ")
		splt[1] = str(value)
		self.display_name = " ".join(splt)

	@property
	def channel_density(self):
		if self.display_name is None:  return None
		return self.display_name.split()[4]
	@channel_density.setter
	def channel_density(self, value):
		splt = self.display_name.split(" ")
		splt[4] = str(value)
		self.display_name = " ".join(splt)

	@property
	def geometry(self):
		if self.display_name is None:  return None
		return self.display_name.split()[5]
	@geometry.setter
	def geometry(self, value):
		splt = self.display_name.split(" ")
		splt[5] = str(value)
		self.display_name = " ".join(splt)


	@property  # Note: not a measured value
	def thickness(self):
		return float(self.type.split('um')[1])/1000
	@thickness.setter
	def thickness(self, value):
		pass


	"""
	# TEMPORARY:  NOTE:  Must fix this...
	@property
	def wirebonding_completed(self):
		return self.wirebonding_back and \
		       self.wirebonds_inspected_back and \
		       self.wirebonding_front and \
		       self.wirebonds_inspected_front and \
		       self.encapsulation_inspection_back and \
               self.encapsulation_inspection_front and \
		       self.wirebonding_final_inspection_ok == 'pass'

	@property
	def assem_tray_pos(self):
		return "TRPOSN_{}{}".format(self.tray_posn%2+1, tray_posn//3+1)

	@property
	def comp_tray_pos(self):
		return "CMPOSN_{}{}".format(self.tray_posn%2+1, tray_posn//3+1)
	

	@property
	def tray_posn(self):
		# If has a pcb step, grab the position of this PCB and return it here...
		if self.step_pcb is None:
			print("assm_tray_posn:  no sensor step yet")
			return "None"
		temp_pcb_step = step_pcb()
		found = temp_pcb_step.load(self.step_pcb)
		if not found:
			print("ERROR in tray_posn:  module {} has PCB step {}, but none found!".format(self.ID, self.step_pcb))
			return "None"
		else:
			position = temp_sensor_step.sensors.index(self.ID)
			return position

	@property
	def tray_row(self):
		posn = self.tray_posn()
		if posn == "None":  return posn
		else:  return posn%2+1

	@property
	def tray_col(self):
		posn = self.tray_posn()
		if posn == "None": return posn
		else:  return posn//3+1
	"""

	# NEW:  Need to add an additional file/etc to handle wirebonding

	def save(self):
		# This one handles the json files
		super(module, self).save()

		# Additionally:  Write wirebonding XML file
		filedir, filename = self.get_filedir_filename()
		fname_wirebond = filename.replace('.json', '_wirebonding_upload.xml')

		xml_tree = self.generate_xml(self.XML_WIREBOND_TEMPLATE)
		root = xml_tree.getroot()
		xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')  #tostring imported from xml.etree.ElementTree
		xmlstr = xmlstr.replace("version=\"1.0\" ", "version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"")
		with open(filedir+'/'+fname_wirebond, 'w') as f:
			f.write(xmlstr)


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


###############################################
##################  supplies  #################
###############################################

class fsobj_supply(fsobj):
	def is_expired(self):
		if self.date_expires is None or self.date_received is None:
			return False
		ydm = tmp_sylgard.date_expires.split('-')
		expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))
		return QtCore.QDate.currentDate() > expires

	PROPERTIES = [
		'date_received',
		'date_expires',
		'is_empty',
	]

	XML_STRUCT_DICT = {'BATCH':{
		'ID':'ID',
		'RECEIVE_DATE':'date_received',
		'EXPIRE_DATE':'date_expires',
		'IS_EMPTY':'is_empty',
		'COMMENTS':'comments'
	}}

class batch_araldite(fsobj_supply):
	OBJECTNAME = "araldite batch"
	FILEDIR = os.sep.join(['supplies','batch_araldite','{date}'])
	FILENAME = 'batch_araldite_{ID:0>5}.xml'
	# Dates should have the format "{}-{}-{} {}:{}:{}".  NOT a property; the UI pages handle the loading.

class batch_wedge(fsobj_supply):
	OBJECTNAME = "wedge batch"
	FILEDIR = os.sep.join(['supplies','batch_wedge','{date}'])
	FILENAME = 'batch_wedge_{ID:0>5}.xml'


class batch_sylgard(fsobj_supply):  # was sylgar_thick
	OBJECTNAME = "sylgard batch"
	FILEDIR = os.sep.join(['supplies','batch_sylgard','{date}'])
	FILENAME = 'batch_sylgard_{ID:0>5}.xml'
	PROPERTIES = [
		'date_received',
		'date_expires',
		'is_empty',
		'curing_agent',
	]



class batch_bond_wire(fsobj_supply):
	OBJECTNAME = "bond wire batch"
	FILEDIR = os.sep.join(['supplies','batch_bond_wire','{date}'])
	FILENAME = 'batch_bond_wire_{ID:0>5}.xml'





if __name__ == '__main__':
	# test features without UI here
	"""
	test_pcb_tool = tool_sensor()
	test_pcb_tool.new("tool1", "UCSB")
	test_pcb_tool.location="place"
	test_pcb_tool.save()
	test_pcb_tool.clear()
	if test_pcb_tool.load("tool1", "UCSB"):
		print("Loaded tool")
	else:
		print("FAILED to load tool")
	print("Final tool location:", test_pcb_tool.location)
	print("TOOL TESTS COMPLETE.\n")

	test_arl = batch_araldite()
	test_arl.new("batch1")
	test_arl.is_empty = True
	test_arl.save()
	test_arl.clear()
	if test_arl.load("batch1"):
		print("Loaded batch")
	else:
		print("FAILED to load batch")
	print("Final batch status:", test_arl.is_empty)
	"""

	"""test_plt = baseplate()
	test_plt.load("plt1")
	test_plt.location = "place"
	test_plt.save()
	test_plt.clear()
	if test_plt.load("plt1"):
		print("Loaded plate")
		print(vars(test_plt))
	else:
		print("FAILED to load plate")
	print("Final plate location:", test_plt.location)
	

	# Now test DB retrieval
	test_plt = baseplate()
	test_plt.clear()
	if test_plt.load("TEST_PRELIM_MODULE_PHMASTER_3"):
		print("location:", test_plt.location)
		print("grade:", test_plt.grade)
		print("material:", test_plt.mat_type)
		print("type:", test_plt.display_name)
		print("geo:", test_plt.geometry)
		test_plt.save()
	else:
		print("LOAD FROM DB FAILED")
	

	# Now test DB uploading


	# Now test sensor, PCB

	print("\n\nSENSOR\n")
	test_plt = sensor()
	test_plt.clear()
	if test_plt.load("TEST_PRELIM_SENSOR_PHMASTER_1"):
		print("location:", test_plt.location)
		print("grade:", test_plt.grade)
		print("sensor type:", test_plt.sen_type)
		print("type:", test_plt.display_name)
		print("geo:", test_plt.geometry)
		test_plt.save()
	else:
		print("LOAD FROM DB FAILED")
	"""
	print("\n\nPCB\n")
	test_plt = pcb()
	test_plt.clear()
	if test_plt.load("TEST_PRELIM_PCB_PHMASTER_4"):
		print("location:", test_plt.location_name)
		print("grade:", test_plt.grade)
		print("type:", test_plt.display_name)
		print("geo:", test_plt.geometry)
		print("Comments:", test_plt.comments)
		test_plt.save()
	else:
		print("LOAD FROM DB FAILED")
	test_plt.clear()
	test_plt.new("pltname")
	print("New comments:", test_plt.comments)


	# Now test proto/module
	# ERR:  Can't test this or assembly steps until after successful DB upload...
	# esp since mod needs wirebond xml testing
	"""
	print("\n\nPROTOMODULE\n")
	test_plt = protomodule()
	test_plt.clear()
	if test_plt.load("TEST_PRELIM_SENSOR_PHMASTER_1"):
		print("location:", test_plt.location)
		print("grade:", test_plt.grade)
		print("sensor type:", test_plt.sen_type)
		print("type:", test_plt.display_name)
		print("geo:", test_plt.geometry)
		test_plt.save()
	else:
		print("LOAD FROM DB FAILED")

	print("\n\nMODULE\n")
	test_plt = pcb()
	test_plt.clear()
	if test_plt.load("TEST_PRELIM_PCB_PHMASTER_4"):
		print("location:", test_plt.location)
		print("grade:", test_plt.grade)
		print("type:", test_plt.display_name)
		print("geo:", test_plt.geometry)
		test_plt.save()
	else:
		print("LOAD FROM DB FAILED")
	"""



