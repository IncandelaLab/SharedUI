import json
import time
import glob
import os

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

import rhapi_nolock as rh
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

loadconfig()



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
                    #'view_wirebonding' -> each individual wirebonding step
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
			print("WARNING: called getUserPerms on {} (not a user)".format(username))
			return None
		userindex = list(self.getAllUsers()).index(username)
		return self.userList[userindex]['permissions']


userManager = UserManager("userInfoFile")




###############################################
############## fsobj base class ###############
###############################################

class fsobj(object):
	PROPERTIES_COMMON = [
		'comments',
		]

	DEFAULTS = {
	}

	DEFAULTS_COMMON = {
		'comments':[],
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

	# List of all class vars that are saved as a list--e.g. comments, parts, etc.
	# Will be handled differently from normal xml items
	ITEMLIST_LIST = ['comments']

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
	def add_part_to_list(self, date=None):
		# NOTE:  Date must have format {m}-{d}-{y}
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not self.ID in data.keys():
				# Note creation date and pass it to the dict
				dcreated = time.localtime()
				if self.ID == None:  print("ERROR:  self.ID in add_part_to_list is None!!!")
				if date:
					dc = date
				else:
					dc = '{}-{}-{}'.format(dcreated.tm_mon, dcreated.tm_mday, dcreated.tm_year)
				data[str(self.ID)] = dc
		with open(self.partlistfile, 'w') as opfl:
			json.dump(data, opfl)


	# Utility for _load_...:  Take a string from an XML element and return a var w/ the correct type
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


	# Utility used for load():  Set vars of obj using struct_dict, xml_tree
	# Recursively look through dict.  For each element found, assign XML value to corresponding var/property.
	# - If dict, recusive case.
	# - If list, create multiple elements w/ same tag.
	# - Else assign normally.
	def _load_from_dict(self, struct_dict, xml_tree):
		for item_name, item in struct_dict.items():
			# item_name = XML tag name, item = name of var/prop to assign
			# If dict, recursive case.
			if type(item) is dict:
				self._load_from_dict(item, xml_tree)
			# If list item, load all elements:
			elif item in self.ITEMLIST_LIST:
				itemdata = xml_tree.findall('.//'+item_name)  # List of all contents of matching tags
				# NOTE:  Items could be text or ints!  Convert accordingly.
				itemdata = [self._convert_str(it.text) for it in itemdata]
				if itemdata == []:
					setattr(self, item, None)
				elif itemdata == ['[]'] or itemdata == '[]':
					setattr(self, item, [])
				else:
					setattr(self, item, itemdata)  # Should be a list containing contents; just assign it to the var
			# if ordinary item, convert from str and assign
			else:
				itemdata = xml_tree.find('.//'+item_name)  # NOTE:  itemdata is an Element, not text!
				assert not itemdata is None, "ERROR:  Found None search result for {} in _load_from_dict(), {} {}".format(item_name, self.__class__.__name__, self.ID)
				idt = self._convert_str(itemdata.text)
				setattr(self, item, idt)


	def load(self, ID, on_property_missing = "warn"):
		if ID == -1:
			self.clear()
			return False

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not str(ID) in data.keys():
				self.clear()
				return False

		filedir, filename = self.get_filedir_filename(ID)
		xml_file = os.sep.join([filedir, filename])

		if not os.path.exists(xml_file):
			self.clear()
			return False

		xml_tree = parse(xml_file)
		self._load_from_dict(self.XML_STRUCT_DICT, xml_tree)

		self.ID = ID
		return True



	def new(self, ID):
		print("FSOBJ NEW")
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
			if item_name == "DATA_SET":
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

		parent = Element(element_name)
		
		for item_name, item in input_dict.items():
			# CHANGE FOR NEW XML SYSTEM:
			# item is a list (comments), dict (another XML layer), or string (var)
			# If string, use getattr()

			if item_name == "DATA_SET":
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


	# Should be fully general--all objects can use this if XML_STRUCT_DICT works.
	# Need separate implementation for tools?
	# NOTE:  Can pass new_struct_dict if multiple XML files must be saved for a part/assembly step.
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

		# Generate XML tree:
		struct_dict = self.XML_STRUCT_DICT

		xml_tree = self.generate_xml(struct_dict)

		# Save xml file:
		filedir, filename = self.get_filedir_filename()
		if not os.path.exists(filedir):
			os.makedirs(filedir)
		root = xml_tree.getroot()
		#tostring imported from xml.etree.ElementTree
		xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')
		with open(filedir+'/'+filename, 'w') as f:
			f.write(xmlstr)

	# Return a list of all files to be uploaded to the DB
	# (i.e. all files in the object's storage dir with "upload" in the filename)
	def filesToUpload(self):
		fdir, fname = self.get_filedir_filename()
		# Grab all files in that directory
		return glob.glob(fdir + "/*upload*")

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


class fsobj_tool(fsobj):

	# This is the same for all tools!
	XML_STRUCT_DICT = {'TOOL':{
		'ID':'ID',
		'INSTITUTION':'institution',
		'LOCATION':'location',
		'COMMENT':'comments'
	}}

	PROPERTIES = [
		'institution',
	]

	# NEW--used only for tooling parts.
	def get_filedir_filename(self, ID = None, institution = None):
		if ID is None:
			ID = self.ID
		if institution is None:
			institution = self.institution
		filedir  = os.sep.join([ DATADIR, self.FILEDIR.format(ID=ID, institution=institution, century = CENTURY.format(ID//100)) ])
		filename = self.FILENAME.format(ID=ID, institution=institution)
		return filedir, filename

	# For search page
	def add_part_to_list(self):
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not self.ID in data.keys():
				dcreated = time.localtime()
				assert self.ID!=None, "ERROR:  self.ID in add_part_to_list (tool) is None!"
				assert self.institution!=None, "ERROR:  self.institution in add_part_to_list (tool) is None!"
				# Key difference here:  Key is (ID, institution)
				data["{}_{}".format(self.ID, self.institution)] = '{}-{}-{}'.format(dcreated.tm_mon, dcreated.tm_mday, dcreated.tm_year)
		with open(self.partlistfile, 'w') as opfl:
			json.dump(data, opfl)


	def load(self, ID, institution, on_property_missing = "warn"):
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not "{}_{}".format(ID, institution) in data.keys():  # Key modification
				self.clear()
				return False

		if ID == -1:
			self.clear()
			return False
		if institution == None:
			self.clear()
			return False

		filedir, filename = self.get_filedir_filename(ID, institution)
		xml_file = os.sep.join([filedir, filename])

		if not os.path.exists(xml_file):
			self.clear()
			return False

		xml_tree = parse(xml_file)
		self._load_from_dict(self.XML_STRUCT_DICT, xml_tree)

		self.ID = ID
		return True


	def new(self, ID, institution):
		self.ID = ID
		self.institution = institution
		PROPERTIES = self.PROPERTIES + self.PROPERTIES_COMMON
		DEFAULTS = {**self.DEFAULTS_COMMON, **getattr(self, 'DEFAULTS', {})}
		for prop in PROPERTIES:
			setattr(self, prop, DEFAULTS[prop] if prop in DEFAULTS.keys() else None)
	

	def clear(self):
		self.ID = None
		self.institution = None
		PROPERTIES = self.PROPERTIES + self.PROPERTIES_COMMON
		DEFAULTS   = {**self.DEFAULTS, **self.DEFAULTS_COMMON}
		for prop in PROPERTIES:
			setattr(self, prop, DEFAULTS.get(prop, None))

########################################################
###### PARENT CLASS FOR PARTS AND ASSEMBLY STEPS #######
########################################################

# New:  .
# NOTE:  ID can be saved as either an int OR a string.

class fsobj_db(fsobj):
	# NOTE:  primary key ID can be an int (assembly) OR a string (part)
	# Vars storing names of tables to request XML files from
	ASSM_TABLE = None
	COND_TABLE = None

	# For base xml file
	XML_STRUCT_DICT = None
	# For creating xml upload file
	XML_UPLOAD_DICT = None
	# For conditions file (thickness or temp/etc)
	XML_COND_DICT = None
	# List of vars that are only loaded (NOT edited by GUI)
	XML_CONSTS = []
	
	# Also requires XML_STRUCT_DICT (for gui storage only),
	# ...XML_UPLOAD_DICT, XML_COND_DICT (BOTH for uploading, see child class definitions).
	# NOTE that the protomodule creation file is created by the protomodule class, and must be uploaded with these.

	# Generic header for all COND files
	COND_HEADER_DICT = {
		'TYPE':{
			'EXTENSION_TABLE_NAME':'COND_TABLE_NAME',
			'NAME':'TABLE_DESC',
		},
		'RUN':{
			'RUN_NAME':'RUN_TYPE',
			'RUN_BEGIN_TIMESTAMP':'run_start_xml',  # Format:  2018-03-26 00:00:00
			'RUN_END_TIMESTAMP':'run_stop_xml',
			'INITIATED_BY_USER':'user_performed',
			'LOCATION':'xml_location',
			'COMMENT_DESCRIPTION':'CMT_DESCR',
		}
	}



	def __init__(self):
		super(fsobj_db, self).__init__()
		# Add all other vars to XML_STRUCT_DICT
		# (so they will be saved accordingly)
		if self.XML_STRUCT_DICT is None:
			self.XML_STRUCT_DICT = {'data':{'row':{} } }
		for var in self.PROPERTIES + self.PROPERTIES_COMMON:
			if var not in self.XML_CONSTS:  self.XML_STRUCT_DICT['data']['row'][var] = var

	def save(self):
		# This one handles self.XML_STRUCT_DICT...
		super(fsobj_db, self).save()

		# NEXT, write the upload files!
		# There's two:  One for Build_UCSB_ProtoModules_00.xml, one for ProtoModules_BuildCond_00.xml (base and cond).
		# Defined in XML_UPLOAD_DICT, XML_COND_DICT
		filedir, filename = self.get_filedir_filename()
		fname_build = filename.replace('.xml', '_build_upload.xml')
		fname_cond  = filename.replace('.xml', '_cond_upload.xml')
		# Build file:
		xml_tree = self.generate_xml(self.XML_UPLOAD_DICT)
		root = xml_tree.getroot()
		xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')  #tostring imported from xml.etree.ElementTree
		xmlstr = xmlstr.replace("version=\"1.0\" ", "version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"")
		with open(filedir+'/'+fname_build, 'w') as f:
			f.write(xmlstr)
		# Cond file:
		xml_tree = self.generate_xml(self.XML_COND_DICT)
		root = xml_tree.getroot()
		xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')
		xmlstr = xmlstr.replace("version=\"1.0\" ", "version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"")
		with open(filedir+'/'+fname_cond, 'w') as f:
			f.write(xmlstr)



	def load(self, ID, on_property_missing = "warn"):
		if ID == "" or ID == -1 or ID == None:
			self.clear()
			return False

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if str(ID) in data.keys():
				dt = data[str(ID)]
			else:
				if not ENABLE_DB_COMMUNICATION:
					print("**TEMPORARY:  Object downloading disabled for testing!**")
					return False
				
				self.ID = ID
				search_conditions = {'ID':self.ID}  # Only condition needed
				# For each XML file/table needed, make a request:
				# Should automatically determine where file should be saved AND add part to list
				assm_request = self.request_XML(self.ASSM_TABLE, search_conditions)

				cond_request = self.request_XML(self.COND_TABLE, search_conditions, suffix="_cond")

				if assm_request != cond_request:  # One file is found, the other isn't:
					print("ERROR:  Only one of 2 requested files was found!")
					print("Base file found: ", assm_request)
					print("Cond file found: ", cond_request)
					self.clear()
					return False
				elif not (assm_request and cond_request):
					print("Object not found.  Returning false...")
					self.clear()
					return False
				# Otherwise, both files are found!  Load from both of them.
				print("Object found!")
				self.add_part_to_list()
				self.add_part_to_list()
				dcreated = time.localtime()
				dt = '{}-{}-{}'.format(dcreated.tm_mon, dcreated.tm_mday, dcreated.tm_year)
				
		filedir, filename = self.get_filedir_filename(ID)  #, date=dt)
		condname = filename.replace('.xml', '_cond.xml')
		xml_file      = os.sep.join([filedir, filename])

		assert os.path.exists(xml_file), "ERROR:  Step is present in partlistfile OR downloaded, but XML file {} does not exist!".format(xml_file)

		xml_tree = parse(xml_file)
		self._load_from_dict(self.XML_STRUCT_DICT, xml_tree)

		# NOTE:  Now saving cond file ONLY as an upload file.  Load all info from standard file.
		self.ID = ID
		return True

	
	# NEW: Must save to correct location!
	def request_XML(self, table_name, search_conditions, suffix=None):
		# NOTE NOTE NOTE:  Must save file in correct location AND add_part_to_list!
		# suffix is added to the end of the filename (will be _cond)
		if not ENABLE_DB_COMMUNICATION:
			return False

		if self.ID == None or self.ID == -1:
			print("WARNING:  Called request_XML() on uninitialized object; ignoring")
			return False

		#filedir, filename = self.get_filedir_filename(self.ID)
		#condname = filename.replace('.xml', '_cond.xml')

		sql_template = 'select * from hgc_int2r.{} p'
		sql_request = sql_template.format(table_name)
		sql_request = sql_request + ' where'
		# search_conditions is a dict:  {param_name:param_value}
		for param, value in search_conditions.items():
			sql_request = sql_request + ' p.{}={}'.format(param, value)

		try:
			api = rh.RhApi(url='https://cmsdca.cern.ch/hgc_rhapi', debug=True, sso='login')
			data = api.xml(sql_request, verbose=True)
		except rh.RhApiRowLimitError as e:
			print("ERROR in request_xml():  Could not download files from DB:")
			print(e)
			return False

		xml_str = minidom.parseString(data).toprettyxml(indent="    ")
		# Output is an empty XML file, header len 61
		# NOTE:  Should be a SINGLE XML result!
		if len(xml_str) < 62:
			print("WARNING in request_xml():  No files match the search criteria")
			return False
		# Store requested file
		xml_tree = fromstring(xml_str)
		ID = int(xml_tree.find('.//ID').text)
		date = xml_tree.find('.//TIME_START')
		# file date format = {}-{}-{}, mdy
		# XML date format = 26-MAR-18
		# https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
		dt = datetime.strptime(date, '%d-%b-%y')
		filedir, filename = self.get_filedir_filename(ID, date)

		if suffix:  filename = filename.replace('.xml', suffix+'.xml')

		with open(os.path.join([filedir, filename]), 'w') as f:
			f.write(xml_str)

		self.add_part_to_list(datetime.strftime('%m-%d-%Y'))

		return True

	# Universal properties

	@property
	def institution_id(self):
		# INSTITUTION_DICT maps ID -> name#
		for instID, instname in INSTITUTION_DICT.items():
			if self.institution == instname:  return instID
		print("ERROR:  location not found in INSTITUTION_DICT")
		return None
	@institution_id.setter
	def institution_id(self, value):
		if value is None:
			self.institution = None
		elif not value in INSTITUTION_DICT.keys():
			print("WARNING:  institution_id:  Found invalid location ID {}".format(value))
		else:
			self.institution = INSTITUTION_DICT[value]






###############################################
##################  tooling  ##################
###############################################

class tool_sensor(fsobj_tool):
	OBJECTNAME = "sensor tool"
	FILEDIR = os.sep.join(['tooling','tool_sensor'])
	FILENAME = 'tool_sensor_{institution}_{ID:0>5}.xml'
	PROPERTIES = [
		'location',
	]



	# NOTE:  This and below objects must be saved with save_tooling(), not save().


class tool_pcb(fsobj_tool):
	OBJECTNAME = "PCB tool"
	FILEDIR = os.sep.join(['tooling','tool_pcb'])
	FILENAME = 'tool_pcb_{institution}_{ID:0>5}.xml'
	PROPERTIES = [
		'location',
	]


class tray_assembly(fsobj_tool):
	OBJECTNAME = "assembly tray"
	FILEDIR = os.sep.join(['tooling','tray_assembly'])
	FILENAME = 'tray_assembly_{institution}_{ID:0>5}.xml'
	PROPERTIES = [
		'location',
	]


class tray_component_sensor(fsobj_tool):
	OBJECTNAME = "sensor tray"
	FILEDIR = os.sep.join(['tooling','tray_component_sensor'])
	FILENAME = 'tray_component_sensor_{institution}_{ID:0>5}.xml'
	PROPERTIES = [
		'location',
	]


class tray_component_pcb(fsobj_tool):
	OBJECTNAME = "pcb tray"
	FILEDIR = os.sep.join(['tooling','tray_component_pcb'])
	FILENAME = 'tray_component_pcb_{institution}_{ID:0>5}.xml'
	PROPERTIES = [
		'location',
	]



###############################################
#####  components, protomodules, modules  #####
###############################################

class baseplate(fsobj_db):
	OBJECTNAME = "baseplate"
	FILEDIR = os.sep.join(['baseplates','{date}'])
	FILENAME = "baseplate_{ID}.xml"

	PROPERTIES = [
		# location
		"institution",
		"location",  # physical location of part

		# characteristics (defined upon reception)
		"barcode",
		"material",     # physical material
		"size",         # hexagon width, numerical. 6 or 8 (integers) for 6-inch or 8-inch
		"shape",        # 

		# baseplate qualification 
		"flatness",
		"thickness",           # measure thickness of baseplate
		"grade",   # A, B, or C
		"channel_density", # NEW - needed for geometry information

		"check_edges_firm", # None if not checked yet; True if passed; False if failed
		"check_glue_spill", # None if not checked yet; True if passed; False if failed

		# sensor application
		"step_sensor", # which step_sensor used it
		"protomodule", # what protomodule (ID) it's a part of; None if not part of any

		# Associations to other objects
		"module", # what module (ID) it's a part of; None if not part of any

		# NEW to match XML script
		"insertion_user", # may not need this...

		# NEW:  Data to be read from base XML file
		# Will be given straight to the upload file, or held onto
		"id_number",
		"parent_ID",
		"description",
	]

	DEFAULTS = {
		"size":     '8', # This should not be changed!
	}


	"""XML_STRUCT_DICT = { "data":{"row":{
		"ID":"id_number",
		"PART_PARENT_ID":'parent_id',  #Don't care about this (not needed for upload)
		"KIND_OF_PART_ID":"kind_of_part_id",
		"KIND_OF_PART":"kind_of_part",
		"LOCATION_ID":"institution_id",
		"SERIAL_NUMBER":"ID",
		"DESCRIPTION":"description",
	}}}"""

	XML_UPLOAD_DICT = {"PARTS":{"PART":{
		"KIND_OF_PART":"kind_of_part",
		"RECORD_INSERTION_USER":"insertion_user",
		"SERIAL_NUMBER":"ID",
		"COMMENT_DESCRIPTION":"comments_concat",
		"LOCATION":"institution",
	}}}

	XML_COND_DICT = {
		"HEADER":self.COND_HEADER_DICT,
		"DATA_SET":{
			"COMMENT_DESCRIPTION":"inspection_comment",
			"VERSION":"VNUM",
			"PART":{
				"SERIAL_NUMBER":"ID",
				"KIND_OF_PART":"kind_of_part",
			}
			"DATA":{
				"FLATNESS":"flatness",
				"COMMENTS":"inspection_comment",
				"THICKNESS":"thickness",
				"GRADE":"grade",
			}
		}
	}

	# List of vars that should NOT be edited in the GUI and are only loaded from DB
	# (And some info would be redundant w/ other constants, eg KIND_OF_PART and self.size)
	XML_CONSTS = [
		'size',
	]

	# List of vars that are stored as lists.
	# Need to be treated separately @ loading from XML
	ITEMLIST_LIST = ['comments'] # 'corner_heights'


	@property
	def kind_of_part(self):
		return "{} Baseplate {}".format(self.material, self.shape)
	@kind_of_part.setter
	def kind_of_part(self, value):
		# Parse and read in the baseplate size
		if value is None or value == "None":
			self.material = None
			self.shape = None
		else:
			self.material = value.split()[0]
			self.shape = value.split()[2]


	def ready_step_sensor(self, step_sensor = None, max_flatness = None):
		if self.step_sensor and self.step_sensor != step_sensor:
			return False, "already assigned to protomodule {}".format(self.protomodule)
		return True, ""


class sensor(fsobj_db):
	OBJECTNAME = "sensor"
	FILEDIR = os.sep.join(['sensors','{date}'])
	FILENAME = "sensor_{ID}.xml"
	PROPERTIES = [
		# location
		"institution",
		"location",  # physical location of part

		# characteristics (defined upon reception)
		"barcode",
		"manufacturer",
		"type",         # NEW:  This is now chosen from a drop-down menu
		"size",         # 
		"channel_density",  # HD or LD
		"shape",        # 
		"grade",
		"flatness",     # 

		# sensor qualification
		"inspection", # None if not inspected yet; True if passed; False if failed

		# sensor step
		"step_sensor", # which step_sensor placed this sensor
		"protomodule", # which protomodule this sensor is a part of

		# associations to other objects
		"module", # which module this sensor is a part of

		# New to match Akshay's script
		"insertion_user",
		# NEW:  Data to be read from base XML file
		"id_number",
		"description",

	]

	DEFAULTS = {
		"size":    '8',  # DO NOT MODIFY
	}

	XML_STRUCT_DICT = { "data":{"row":{
		"KIND_OF_PART_ID":"kind_of_part_id",
		"KIND_OF_PART":"kind_of_part", #TBD:  Property
		"LOCATION_ID":"institution_id", # same...
		"MANUFACTURER":"manufacturer",
		"SERIAL_NUMBER":"ID",
		"DESCRIPTION":"description",  # Can probably leave this blank...
	}}}

	XML_UPLOAD_DICT = {"PARTS":{"PART":{
		"KIND_OF_PART":"kind_of_part",
		"RECORD_INSERTION_USER":"insertion_user",
		"SERIAL_NUMBER":"ID",
		"COMMENT_DESCRIPTION":"comments_concat",
		"LOCATION":"institution",
		# NEW:
		"THICKNESS":"thickness",
		"VISUAL_INSPECTION":"inspection",
		"GRADE":"grade",
		#"COMMENTS":"comments_concat",
		#"PREDEFINED_ATTRIBUTES":{  # Ignore this for now...
		#	"ATTRIBUTE":{
		#		"NAME":"HGC Silicon Sensor Type",
		#		"VALUE":"200DD",
		#	}
		#}
	}}}

	XML_CONSTS = [
		'size',
	]

	ITEMLIST_LIST = ['comments']

	@property
	def resolution(self):
		return self.channel_density
	@resolution.setter
	def resolution(self, value):
		self.channel_density = value

	@property
	def kind_of_part(self):
		return "{} Si Sensor {} {}".format(self.type, self.resolution, self.shape)
	@kind_of_part.setter
	def kind_of_part(self, value):
		# Parse and read in the baseplate size
		if value is None:
			self.type = None
			self.resolution = None
			self.shape = None
		else:
			self.type = value.split()[0]
			self.resolution = value.split()[2]
			self.shape = value.split()[3]

	@property
	def thickness(self):
		return float(self.type.split('um')[0])/1000



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



class pcb(fsobj_db):
	OBJECTNAME = "PCB"
	FILEDIR = os.sep.join(['pcbs','{date}'])
	FILENAME = "pcb_{ID}.xml"
	PROPERTIES = [
		# location
		"institution",
		"location",  # physical location of part

		# details / measurements / characteristics
		"insertion_user",
		"barcode", 
		"manufacturer", # 
		"type",         # 
		"resolution",   # NEW
		"num_rocs",     # NEW
		"size",         # 
		"channels",     # 
		"shape",        # 

		# pcb qualification
		"grade",
		"thickness",  # 
		"flatness",   # 
		
		# pcb step
		"step_pcb", # which step_pcb placed this pcb
		"module",   # which module this pcb is a part of

		# NEW:  Data to be read from base XML file
		"id_number",
		"kind_of_part_id",
		"kind_of_part",
		"description",

		"manufacturer",  # for output XML
		"version",
		"batch_number",

		"test_files",
	]

	DEFAULTS = {
		"size":     '8',
		"comment_description":  "TEST",
		"test_files":[],
	}

	XML_STRUCT_DICT = { "data":{"row":{
		"ID":"id_number",
		"KIND_OF_PART_ID":"kind_of_part_id",
		"KIND_OF_PART":"kind_of_part", #TBD:  Property
		"LOCATION_ID":"institution_id", # same...
		"MANUFACTURER":"manufacturer",
		"SERIAL_NUMBER":"ID",
		"VERSION":"version",
		"BATCH_NUMBER":"batch_number",
	}}}

	XML_UPLOAD_DICT = {"PARTS":{"PART":{
		"KIND_OF_PART":"kind_of_part",
		"RECORD_INSERTION_USER":"insertion_user",
		"SERIAL_NUMBER":"ID",
		"COMMENT_DESCRIPTION":"comments_concat",
		"LOCATION":"institution",
		"MANUFACTURER":"manufacturer",
		"FLATNESS":"flatness",
		"THICKNESS":"thickness",
		"GRADE":"grade",
		#"COMMENTS":"comments_concat",
	}}}

	DAQ_DATADIR = 'daq'

	XML_CONSTS = [
		#'ID',  # does NOT count
		'resolution_type',
	]

	ITEMLIST_LIST = ['comments', 'test_files']

	# WIP, go back and fix!
	
	@property
	def kind_of_part(self): # Determined entirely by size
		return "PCB/Kapton {} {}".format(self.resolution, self.shape)
	@kind_of_part.setter
	def kind_of_part(self, value):
		if value is None:
			self.resolution = None
			self.shape = None
		else:
			self.resolution = value.split()[1]
			self.shape = value.split()[2]

	def ready_step_pcb(self, step_pcb = None):
		if self.step_pcb and self.step_pcb != step_pcb:
			return False, "already assigned to module {}".format(self.module)
		return True, ""


class protomodule(fsobj_db):
	OBJECTNAME = "protomodule"
	FILEDIR = os.sep.join(['protomodules','{date}'])
	FILENAME = 'protomodule_{ID}.xml'
	PROPERTIES = [
		# location
		"institution",
		"location",  # physical location of part

		# characteristics - taken from child parts upon creation of protomodule
		"insertion_user",
		"thickness",   # sum of baseplate and sensor, plus glue gap
		"channels",    # from sensor
		"size",        # from baseplate or sensor (identical)
		"shape",       # from baseplate or sensor (identical)
		"grade",
		# initial location is also filled from child parts

		# sensor step - filled upon creation
		"step_sensor", # ID of sensor step
		"baseplate",   # ID of baseplate
		"sensor",      # ID of sensor

		# protomodule qualification
		"offset_translation_x", # translational offset of placement
		"offset_translation_y",
		"offset_rotation",    # rotation offset of placement
		"flatness",           # flatness of sensor surface after curing

		# pcb step
		"step_pcb", # ID of pcb step
		"module",   # ID of module

		# NEW:  Data to be read from base XML file
		"id_number",
		"part_parent_id",
		"kind_of_part_id",
		"kind_of_part",
		"comment_description",
	]

	DEFAULTS = {
		"size":     '8',
		"comment_description":"top layer: pcb",  # SUBJECT TO CHANGE
	}

	
	XML_STRUCT_DICT = { "data":{"row":{
		"ID":"id_number",
		"PART_PARENT_ID":"part_parent_id",
		"KIND_OF_PART_ID":"kind_of_part_id",
		"KIND_OF_PART":"kind_of_part",
		"LOCATION_ID":"institution_id",
		"SERIAL_NUMBER":"ID",
	}}}

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

	XML_CONSTS = [
		#'ID',  # does NOT count
		'resolution_type',
	]

	ITEMLIST_LIST = ['comments']

	@property
	def kind_of_part(self):
		if not self.sensor or not self.baseplate:  return None
		return '{} {} Si ProtoModule {} {}'.format('EM' if self.baseplate.material=='CuW' else 'HAD', 
                                                  self.sensor.type, self.sensor.resolution, self.shape)

	@kind_of_part.setter
	def kind_of_part(self, value):
		pass

	@property
	def assem_tray_pos(self):
		return "TRPOSN_{}{}".format(self.tray_row, tray_col)

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

	def ready_step_pcb(self, step_pcb = None):
		if self.step_pcb and self.step_pcb != step_pcb:
			return False, "already assigned to module {}".format(self.module)
		return True, ""

		



class module(fsobj_db):
	OBJECTNAME = "module"
	FILEDIR    = os.sep.join(['modules','{date}','module_{ID}'])
	FILENAME   = 'module_{ID}.xml'
	PROPERTIES = [
		# location
		"institution",
		"location",  # physical location of part

		# characteristics - taken from child parts upon creation of module
		"insertion_user",
		"thickness",   # sum of protomodule and sensor, plus glue gap
		"flatness",    # NEW
		"channels",    # from protomodule or pcb (identical)
		"size",        # from protomodule or pcb (identical)
		"shape",       # from protomodule or pcb (identical)
		"grade",
		# initial location is also filled from child parts
		"inspection",  # may want to get rid of this / move it to the assembly page

		# components and steps - filled upon creation
		"baseplate",     # 
		"sensor",        # 
		"protomodule",   # 
		"pcb",           # 
		"step_sensor",   # 
		"step_pcb",      # 

		# module qualification
		"preinspection",
		"offset_translation_x",
		"offset_translation_y",
		"offset_rotation",

		# wirebonding
		# NEW: NOTE:  This info is filled out using the wirebonding page exclusively!
		"wirebonding_comments",  # Comments from wirebonding page only
		"wirebonding_date_back",
		"wirebonding_date_front",

		"wirebonding_sylgard",
		"wirebonding_bond_wire",
		"wirebonding_wedge",

		# back wirebonding
		"wirebonding_back",                # has wirebonding been done
		"wirebonding_unbonded_channels_back", # list of sites that were not wirebonded
		"wirebonding_user_back",           # who performed wirebonding
		"wirebonds_inspected_back",     # whether inspection has happened
		"wirebonds_repaired_user_back", # who repaired bonds

		# front wirebonding
		"wirebonding_front",                # has wirebonding been done
		"wirebonding_skip_channels_front",  # list of channels to ignore
		"wirebonding_unbonded_channels_front", # list of sites that were not wirebonded
		"wirebonding_user_front",           # who performed wirebonding
		"wirebonds_inspected_front",     # whether inspection has happened
		"wirebonds_repaired_user_front", # who repaired bonds

		# back encapsulation
		"encapsulation_back",             # has encapsulation been done
		"encapsulation_user_back",        # who performed encapsulation
		"encapsulation_cure_start_back", # (unix) time at start of encapsulation
		"encapsulation_cure_stop_back",  # (unix) time at end of encapsulation
		"encapsulation_inspection_back", # None if not yet inspected; True if pased; False if failed

		# front encapsulation
		"encapsulation_front",             # has encapsulation been done
		"encapsulation_user_front",        # who performed encapsulation
		"encapsulation_cure_start_front", # (unix) time at start of encapsulation
		"encapsulation_cure_stop_front",  # (unix) time at end of encapsulation
		"encapsulation_inspection_front", # None if not yet inspected; True if pased; False if failed

		"encapsulation_comments",

		# test bonds
		"test_bonds",             # is this a module for which test bonds will be done?
		"test_bonds_pulled_user", # who pulled test bonds
		"test_bonds_pull_avg",    # average pull strength
		"test_bonds_pull_std",    # stddev of pull strength

		"wirebonding_final_inspection_user",
		"wirebonding_final_inspection_ok",


		# NEW:  Data to be read from base XML file
		"id_number",
		"part_parent_id",
		"description",

		"test_files",
	]
	
	PROPERTIES_DO_NOT_SAVE = [
	]

	DEFAULTS = {
		"wirebonding_comments":[],
		"encapsulation_comments":[],
		"size":    '8',
		"test_files":[],
	}

	ITEMLIST_LIST = ['comments', 'wirebonding_comments', 'encapsulation_comments', 'test_files',
		'wirebonding_unbonded_channels_front'
	]

	XML_STRUCT_DICT = { "data":{"row":{
		"ID":"id_number",
		"PART_PARENT_ID":"part_parent_id",
		"KIND_OF_PART_ID":"kind_of_part_id",
		"KIND_OF_PART":"kind_of_part",
		"LOCATION_ID":"institution_id",
		"SERIAL_NUMBER":"ID",
		"DESCRIPTION":"description",
	}}}

	XML_UPLOAD_DICT = {"PARTS":{"PART":{
		"KIND_OF_PART":"kind_of_part",
		"SERIAL_NUMBER":"ID",
		"COMMENT_DESCRIPTION":"comments_concat",
		"LOCATION":"location",
		"RECORD_INSERTION_USER":"insertion_user",
		"THICKNES":"thickness",
		"GRADE":"grade",
		"COMMENTS":"comments_concat",
		"PREDEFINED_ATTRIBUTES":{
			"ATTRIBUTE":{  # ignore for now per Umesh
				"NAME":"AsmTrayPosn",
				"VALUE":"assem_tray_posn",
			},
			"ATTRIBUTE":{
				"NAME":"WireBonded",
				"VALUE":"wirebonding_completed",
			}
		},
		"CHILDREN":{
			"PART":[{
				"KIND_OF_PART":"protomodule_type",
				"SERIAL_NUMBER":"protomodule",
				"PREDEFINED_ATTRIBUTES":{
					"ATTRIBUTE":{
						"NAME":"AsmTrayPosn",
						"VALUE":"assem_tray_posn",
					}
				}
			},
			{
				"KIND_OF_PART":"pcb_type",
				"SERIAL_NUMBER":"pcb",
				"PREDEFINED_ATTRIBUTES":{
					"ATTRIBUTE":{
						"NAME":"CmpTrayPosn",
						"VALUE":"comp_tray_posn",
					}
				}
			}]
		}
	}}}

	XML_CONSTS = [
		#'ID',  # does NOT count
		'resolution_type',
	]


	@property
	def kind_of_part(self):
		if not self.sensor or not self.baseplate:  return None
		return '{} {} Si Module {} {}'.format('EM' if self.baseplate.material=='CuW' else 'HAD', 
                                                   self.sensor.type, self.sensor.resolution, self.shape)
	@kind_of_part.setter
	def kind_of_part(self, value):
		print("TODO:  mod kind_of_part:  implement when DB enabled")

	@kind_of_part.setter
	def kind_of_part(self, value):
		# Parse and read in the baseplate size
		if value is None:
			return None
		else:
			print("PLACEHOLDER:  Need to handle case:  downloaded module w/o corresponding pcb/protomod")

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


	@property
	def protomodule_type(self):
		if self.protomodule is None:
			print("ERROR in protomodule_type:  protomodule is None!")
			return None
		temp_protomodule = protomodule()
		if not temp_protomodule.load(self.protomodule):
			print("ERROR in protomodule_type:  Could not find child protomodule {}!".format(self.protomodule))
			return None
		return temp_protomodule.kind_of_part

	@property
	def pcb_type(self):
		if self.pcb is None:
			print("ERROR in pcb_type:  pcb is None!")
			return None
		temp_pcb = pcb()
		if not temp_pcb.load(self.pcb):
			print("ERROR in pcb_type:  Could not find child PCB {}!".format(self.pcb))
			return None
		return temp_pcb.kind_of_part

	@property
	def resolution(self):
		if self.sensor is None:
			print("ERROR in module resolution:  sensor is None!")
			return None
		temp_sensor = sensor()
		if not temp_sensor.load(self.sensor):
			print("ERROR in module resolution:  Could not find child sensor {}!".format(self.sensor))
			return None
		return temp_sensor.resolution



###############################################
###############  assembly steps  ##############
###############################################

class step_sensor(fsobj_db):
	OBJECTNAME = "sensor step"
	FILEDIR    = os.sep.join(['steps','sensor','{date}'])
	FILENAME   = 'sensor_assembly_step_{ID:0>5}.xml'
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

	ITEMLIST_LIST = ['comments', 'tools', 'sensors', 'baseplates', 'protomodules']

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
	VNUM = 1

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



class step_pcb(fsobj_db):
	OBJECTNAME = "PCB step"
	FILEDIR = os.sep.join(['steps','pcb','{date}'])
	FILENAME = 'pcb_assembly_step_{ID:0>5}.xml'
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


	# PASTED RECENTLY, needs revision
	ITEMLIST_LIST = ['comments', 'tools', 'pcbs', 'protomodules', 'modules']

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
	VNUM = 1

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
	"""PROPERTIES = [
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
	}}"""
	# Dates should have the format "{}-{}-{} {}:{}:{}".  NOT a property; the UI pages handle the loading.

class batch_wedge(fsobj_supply):
	OBJECTNAME = "wedge batch"
	FILEDIR = os.sep.join(['supplies','batch_wedge','{date}'])
	FILENAME = 'batch_wedge_{ID:0>5}.xml'
	"""PROPERTIES = [
		'date_received',
		'date_expired',
		'is_empty',
	]
	XML_STRUCT_DICT = {'BATCH':{
		'ID':'ID',
		'RECEIVE_DATE':'date_received',
		'EXPIRE_DATE':'date_expires',
		'IS_EMPTY':'is_empty',
		'COMMENTS':'comments'
	}}"""

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
	XML_STRUCT_DICT = {'BATCH':{
		'ID':'ID',
		'RECEIVE_DATE':'date_received',
		'EXPIRE_DATE':'date_expires',
		'IS_EMPTY':'is_empty',
		'CURING_AGENT':'curing_agent',
		'COMMENTS':'comments'
	}}


class batch_bond_wire(fsobj_supply):
	OBJECTNAME = "bond wire batch"
	FILEDIR = os.sep.join(['supplies','batch_bond_wire','{date}'])
	FILENAME = 'batch_bond_wire_{ID:0>5}.xml'
	"""PROPERTIES = [
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
	}}"""






if __name__ == '__main__':
	# test features without UI here
	# currently unused
	...
