import os
import json
import numpy
import time
import subprocess
import glob

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
LOCATION_DICT = {  # For loading from LOCATION_ID XML tag
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
	if file is None:
		file = os.sep.join([CWD, CFG_FILE])
	
	with open(file, 'r') as opfl:
		data = json.load(opfl)

	global DATADIR
	global MAC

	# NOTE:  Currently hardcoding the filemanager_data location, and ignoring the config information!
	DATADIR  = os.sep.join([os.getcwd(), 'filemanager_data'])  # data['datadir']
	MAC      = data['MAC']
	ID_RANGE = MAC_ID_RANGES.get(MAC,[90000,99999])

	if not MAC in MAC_ID_RANGES.keys():
		print("Warning: MAC ({}) not in list of MAC names ({})".format(
			MAC,
			', '.join(MAC_ID_RANGES.keys())
			))

	# NEW for searching:  Need to store list of all searchable object IDs.  Easiest approach is to dump a list via json.
	print("CALLING LOADCONFIG")
	partlistdir = os.sep.join([DATADIR, 'partlist'])
	if not os.path.exists(partlistdir):
		os.makedirs(partlistdir)

	# Class names MUST match actual class names or stuff will break
	# Note:  Only the first 6 are searchable at the moment; the rest are in case they're needed later.
	# (And because save() now calls add_part_to_list for all objects except tools)
	obj_list = ['baseplate', 'sensor', 'pcb', 'protomodule', 'module', 'shipment',
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
					'view_sensor_step', 'view_pcb_step',
                    # NOTE:  'view_wirebonding' -> each individual wirebonding step
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
		if len(permList) != len(self.pageList):
			print("ERROR:  permissions list length does not equal page list length!")
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
			print("ERROR:  Attempted to update nonexistent user!")
			return
		if len(permList) != len(self.pageList):
			print("ERROR:  permissions list length does not equal page list length!")
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
			print("WARNING:  Attempting to delete nonexistent user")
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
			print("Warning: called isAdmin on {} (not a user)".format(username))
			return False
		userindex = list(self.getAllUsers()).index(username)
		return self.userList[userindex]['isAdmin']

	def getUserPerms(self, username):
		if not username in self.getAllUsers():
			print("Warning: called getUserPerms on {} (not a user)".format(username))
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

	# NEW:
	#PARTS_LIST = ['baseplate':, 'sensor', 'pcb', 'protomodule', 'module']
	# Similarly...
	# Must be a dict, since need to access different tables for each one!
	# First table is the basic table; second table is the cond info
	#CONDS_DICT = {'step_sensor': ['c4220', 'c4260'],
	#			  'step_pcb':    ['c4240', 'c4280']
	#			 }

	# NEW
	XML_STRUCT_DICT = None  # Should not use the base class!

	# List of all class vars that are saved as a list--e.g. comments, shipment parts, etc.
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
				#data.append(self.ID)
				# Now a dictionary:
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


	# NOW OUTDATED; see below for new version
	"""
	def save(self, objname = 'fsobj'):  #NOTE:  objname param is new
		# NOTE:  Can't check item existence via filepath existence, bc filepath isn't known until after item creation!
		# Instead, go into partlist dict and check to see whether item exists:
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not self.ID in data.keys():
				# Object does not exist, so can't get filedir from get_filedir_filename()
				# ...until the date has been set via add_part_to_list.  Do that now.
				self.add_part_to_list()				

		filedir, filename = self.get_filedir_filename(self.ID)
		file = os.sep.join([filedir, filename])
		if not os.path.exists(filedir):
			os.makedirs(filedir)


		# OLD, FOR JSON:
		with open(file, 'w') as opfl:
			if hasattr(self, 'PROPERTIES_DO_NOT_SAVE'):
				contents = vars(self)
				filtered_contents = {_:contents[_] for _ in contents.keys() if _ not in self.PROPERTIES_DO_NOT_SAVE}
				json.dump(filtered_contents, opfl, indent=4)
			else:
				json.dump(vars(self), opfl, indent=4)
		"""

	# USE XML_STRUCT_DICT to find vars in the XML tree and assign them to vars/properties
	# Changes:
	# - Don't need to worry about PROPERTIES_DO_NOT_SAVE; ignore them
	# - ...can basically ignorne the below, because the new method is radically different

	# Recursively look through dict.  For each element found, assign XML value to corresponding var/property.
	# - If dict, recusive case.
	# - If list, create multiple elements w/ same tag.
	# - Else assign normally.
	# Utility used for load():  Set vars of obj using struct_dict, xml_tree
	def _load_from_dict(self, struct_dict, xml_tree):
		#print("ITEMLIST LIST IS:")
		#print("    ", self.ITEMLIST_LIST)
		for item_name, item in struct_dict.items():
			# item_name = XML tag name, item = name of var/prop to assign
			if type(item) is dict:
				self._load_from_dict(item, xml_tree)
			# If item must be stored as a list in the class:
			elif item in self.ITEMLIST_LIST:  #len(xml_tree.findall(item_name)) > 1:  # If multiple items found:
				itemdata = xml_tree.findall('.//'+item_name)  # List of all contents of matching tags
				# NOTE:  Items could be text or ints!  Convert accordingly.
				itemdata = [self._convert_str(it.text) for it in itemdata]
				#print("_load_from_dict:  list item {} found!  Contents: {}".format(item, itemdata))
				if itemdata == []:
					setattr(self, item, None)
				elif itemdata == ['[]'] or itemdata == '[]':
					setattr(self, item, [])
				else:
					setattr(self, item, itemdata)  # Should be a list containing contents; just assign it to the var
			else:
				#print("_load_from_dict: ordinary XML item {} found!".format(item_name))
				itemdata = xml_tree.find('.//'+item_name)  # NOTE:  itemdata is an Element, not text!
				#print("Loaded item text is", itemdata.text, "; item is", item)
				if itemdata.text.isdigit():  # If int:
					idt = int(itemdata.text)
				elif itemdata.text.replace('.','',1).isdigit():  # If float:
					idt = float(itemdata.text)
				elif itemdata.text == 'True':  idt = True
				elif itemdata.text == 'False': idt = False
				elif itemdata.text == 'None':  idt = None
				else:  # If string
					idt = itemdata.text
				setattr(self, item, idt)

	# Utility:  Take a string from an XML element and return a var w/ the correct type
	# "True" -> bool, 100 -> int, etc.
	def _convert_str(self, string):
		if string.isdigit():
			return int(string)
		elif string.replace('.','',1).isdigit():
			return float(string)
		elif string == "True" or string == "False":
			return bool(string)
		elif string == "None":
			return None
		else:
			return string


	def load(self, ID, on_property_missing = "warn"):
		if ID == -1:
			self.clear()
			return False

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not str(ID) in data.keys():
				# FOR NOW:
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
		self.ID = ID
		PROPERTIES = self.PROPERTIES + self.PROPERTIES_COMMON
		DEFAULTS = {**self.DEFAULTS_COMMON, **getattr(self, 'DEFAULTS', {})}
		for prop in PROPERTIES:
			setattr(self, prop, DEFAULTS[prop] if prop in DEFAULTS.keys() else None)

		# REMOVED, moved to save().  Doesn't seem necessary?+interfered w/ cancelling steps
		"""
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not self.ID in data.keys():
				# Object does not exist, so can't get filedir from get_filedir_filename()
				# ...until the date has been set via add_part_to_list.  Do that now.
				self.add_part_to_list()
		"""

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
		# Generate XML ElementTree from input_dictionary, and return the ElementTree.
		# Note:  does not save XML file!
		# Note:  input_dict is a list of all items contained by the ROOT.  ROOT is not included, but 
		#        is generated automatically.

		root = Element('ROOT')
		root.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
		tree = ElementTree(root)
		print("CALLING generate_xml().  Full dict is:")
		print(input_dict)

		for item_name, item in input_dict.items():
			# Note:  Need to add a case if one of the items is a list.
			# For files where multiple DATA_SETs w/ the same name are needed.
			# ...problem:  Don't necessarily know how many DATA SETS in advance.
			# (Note:  Might not actually want this)
			"""
			if type(item) == list:
				print("  List found in generate_xml.  Calling dict to element...", item)
				for item_ in item:
					child = self.dict_to_element(item_, item_name)
					root.append(child)
			"""
			if item_name == "DATA_SET":
				# Special treatment.  First, find number of datasets to save, one for each module/protomodule:
				num_parts = 0
				protomodules = getattr(self, 'protomodules', None)
				modules = getattr(self, 'modules', None)
				if protomodules:
					num_parts = sum([1 for p in protomodules if p])  # List with Nones if no protomodule
				elif modules:
					num_parts = sum([1 for p in modules if p])
				else:  print("ERROR: failed to find protomodules, modules in generate_xml()!")
				dataset_dict = getattr(self, item, None)
				if not dataset_dict:  print("ERROR: failed to find dataset dict!")
				print("Creating DATA_SET_DICT, num parts is", num_parts)
				for i in range(num_parts):
					# Create a DATA_SET for each part
					child = self.dict_to_element(dataset_dict, item_name, data_set_index=i)
					root.append(child)
			else:
				print("  List not found in generate_xml.  Calling dict to element on...")
				print(item, item_name)
				child = self.dict_to_element(item, item_name)
				root.append(child)
		return tree


	def dict_to_element(self, input_dict, element_name, data_set_index=None):
		# Reads a dictionary, and returns an XML element 'element_name' filled with the contents of the current object
		# structured according to that dictionary.
		# NOTE:  This must be able to work recursively.  I.e. if one of the objs in the input_dict is a dict,
		#    it reads *that* dictionary and creates an element for it, +appends it to current element.  Etc.
		print("***dict_to_element:*** element {}, input dict is".format(element_name))
		print(input_dict, type(input_dict))
		print("data_set_index:", data_set_index)

		# NEW:  Add special case for multi-item assembly steps.  Will always appear in DATA_SET dict.
		# If in DATA_SET, data_set_index will NOT be None.  If not None, and a list is found, return element i instead of the usual list handling case.
		# ALT (since need to append all 6 DSs in special case:

		
		parent = Element(element_name)
		
		for item_name, item in input_dict.items():
			# CHANGE FOR NEW XML SYSTEM:
			# item is a list (comments), dict (another XML layer), or string (var)
			# If string, use getattr()
			print("    dict_to_element:  name, dict are:", item_name, item)


			if type(item) == dict:
				#print("  **Dict found.  Calling recursive case...")
				# Recursive case: Create an element from the child dictionary.
				# "Remember" whether currently in a DATA_SET
				child = self.dict_to_element(item, item_name, data_set_index=data_set_index)
				# Special case for PARTs:
				if item_name == "PART" and data_set_index is None:
					child.set('mode','auto')
				parent.append(child)
			elif type(item) == list:
				# Second recursive case:  for multiple parts, comments, etc
				print("    Found list of vals to store for", item_name, item)
				# "PART":[{part_dict_1}, {part_dict_2}]; both have to be labeled w/ "PART"
				for it in item:
					# For each item, create elements recursively and append to parent
					ch = self.dict_to_element(it, item_name, data_set_index=data_set_index)
					if item_name == "PART":
						ch.set('mode', 'auto')
					parent.append(ch)
			elif type(getattr(self, item, None)) == list:  #type(item) == list:
				# Base case 1:  List of comments.  Create an element for each one.
				print("    Found list: ", getattr(self, item, None))

				# If currently in a DATA_SET, need to treat differently!
				if data_set_index != None:
					#print("\nFOUND DATA_SET LIST!  Adding item i:", data_set_index, str(getattr(self, item, None)[data_set_index]), '\n')
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
				print("    INSERTING BASE ITEM", item_name, item)
				# Base case 2:
				child = Element(item_name)
				child.text = str(getattr(self, item, None))  # item should be the var name!
				# Fill attrs that don't exist w/ None
				# This SHOULD work with properties!
				print("    Creating element {} with contents {}".format(item_name, child.text))
				parent.append(child)

		return parent


	# NEWLY REWORKED
	# Should be fully general--all objects can use this if XML_STRUCT_DICT works.
	# Need separate implementation for tools?
	# NOTE:  Can pass new_struct_dict if multiple XML files must be saved for a part/assembly step.
	def save(self):  #save_xml(self, xml_tree):
		#if new_struct_dict is None and not new_fname is None:
		#	print("ERROR IN SAVE():  Got a new struct dict, but not a corresponding filename!")

		# NOTE:  Can't check item existence via filepath existence, bc filepath isn't known until after item creation!
		# Instead, go into partlist dict and check to see whether item exists:
		print("Calling fsobj save")
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not str(self.ID) in data.keys():  # Note:  str(self.ID) saved in add_part_to_list
				# Object does not exist, so can't get filedir from get_filedir_filename()
				# ...until the date has been set via add_part_to_list.  Do that now.
				self.add_part_to_list()
		# Now redundant
		#filedir, filename = self.get_filedir_filename(self.ID)
		#file = os.sep.join([filedir, filename])
		#if not os.path.exists(filedir):
		#	os.makedirs(filedir)

		# Generate XML tree:
		struct_dict = self.XML_STRUCT_DICT

		xml_tree = self.generate_xml(struct_dict)  #self.XML_STRUCT_DICT)

		# Save xml file:
		# Store in same directory as .json files, w/ same name:
		filedir, filename = self.get_filedir_filename()  # self.ID)  #This should be unnecessary...
		print("Filedir, filename are:", filedir, filename)
		#filename = filename.replace('.json', '.xml')
		if not os.path.exists(filedir):
			os.makedirs(filedir)
		print("Saving XML file to ", filedir+'/'+filename)
		root = xml_tree.getroot()
		xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')  #tostring imported from xml.etree.ElementTree
		#xml_tree.write(open(filedir+'/'+filename), 'wb')  #.replace('.json', '.xml'), 'wb'))
		with open(filedir+'/'+filename, 'w') as f:
			f.write(xmlstr)

	# Return a list of all files to be uploaded to the DB
	# (i.e. all files in the object's storage dir with "upload" in the filename)
	def filesToUpload(self):
		fdir, fname = self.get_filedir_filename()
		# Grab all files in that directory
		print("Preparing to upload {}, files {}".format(self, glob.glob(fdir + "/*upload*")))
		return glob.glob(fdir + "/*upload*")

	# NEW:  All parts/assembly steps use this, bc can't write multiple XML tags w/ same name
	@property
	def comments_concat(self):
		return ';;'.join(self.comments)


# NEW FOR TOOLING:
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
		#if self.institution is None:
		#	print("ERROR:  Object needs a location before it can be saved!")
		#	return None, None
		if ID is None:
			ID = self.ID
		if institution is None:
			institution = self.institution
		filedir  = os.sep.join([ DATADIR, self.FILEDIR.format(ID=ID, institution=institution, century = CENTURY.format(ID//100)) ])
		filename = self.FILENAME.format(ID=ID, institution=institution)
		return filedir, filename

	# NEW:  For search page
	# Added
	def add_part_to_list(self):
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not self.ID in data.keys():
				dcreated = time.localtime()
				if self.ID == None:  print("ERROR:  self.ID in add_part_to_list (tool) is None!")
				if self.institution == None:  print("ERROR:  self.institution in add_part_to_list (tool) is None!")
				# Key difference here:  Key is (ID, institution)
				data["{}_{}".format(self.ID, self.institution)] = '{}-{}-{}'.format(dcreated.tm_mon, dcreated.tm_mday, dcreated.tm_year)
		with open(self.partlistfile, 'w') as opfl:
			json.dump(data, opfl)


	def load(self, ID, institution, on_property_missing = "warn"):
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		print("LOADING TOOL")
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not "{}_{}".format(ID, institution) in data.keys():  # Key modification
				print("TOOL LOAD FAILED, was looking for " + "{}_{}".format(ID, institution))
				print("data.keys() =", data.keys())
				self.clear()
				return False
		# (else:)
		print("FOUND TOOL!")

		if ID == -1:
			self.clear()
			return False
		if institution == None:
			self.clear()
			return False

		filedir, filename = self.get_filedir_filename(ID, institution)
		xml_file = os.sep.join([filedir, filename])

		print("Loading from file:", xml_file)

		if not os.path.exists(xml_file):
			self.clear()
			return False

		xml_tree = parse(xml_file)

		self._load_from_dict(self.XML_STRUCT_DICT, xml_tree)

		print("Finished loading, ID type is ", type(self.ID))
		print("...and location is", self.location)

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


###### NEW:  PARENT CLASSES FOR PARTS AND ASSEMBLY STEPS #######

class fsobj_part(fsobj):
	# Var storing names of table to request XML files from
	PART_TABLE = 'parts'  # By default
	# Also requires XML_STRUCT_DICT

	# This WAS the same for all parts, turns out some have MANUFACTURERs while baseplates don't...
	# Are there additional attrs to request...?
	XML_STRUCT_DICT = None

	# Must customize XML_UPLOAD_DICT slightly for each part type
	XML_UPLOAD_DICT = None
	XML_CONSTS = None

	# NEW:  Want to ....
	def __init__(self):  # Maybe this could be done OUTSIDE of init...but not sure I want to risk it.
		super(fsobj_part, self).__init__()
		# Add all other vars to XML_STRUCT_DICT
		# (so they will be saved accordingly)
		#print("\nINIT: ADDING PROPERTIES")
		#print(self.PROPERTIES)
		for var in self.PROPERTIES + self.PROPERTIES_COMMON:
			# WARNING:  XML_STRUCT_DICT is {'data':{'row': and THEN the useful vars
			if var not in self.XML_CONSTS:  self.XML_STRUCT_DICT['data']['row'][var] = var



	# save() must also create and save the XML file for uploading...

	def save(self):
		# Ordinary save; should take care of XML stuff normally.
		super(fsobj_part, self).save()
		
		# Get upload XML struct from self.XML_UPLOAD_DICT
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not self.ID in data.keys():
				self.add_part_to_list()

		# Generate XML tree:
		struct_dict = self.XML_UPLOAD_DICT
		xml_tree = self.generate_xml(struct_dict)

		# Save xml file:
		# Store in same directory as .json files, w/ same name:
		filedir, filename = self.get_filedir_filename()  # self.ID)  #This should be unnecessary...
		filename = filename.replace('.xml', '_upload.xml')
		print("Saving UPLOAD XML file to ", filedir+'/'+filename)
		root = xml_tree.getroot()
		xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')  #tostring imported from xml.etree.ElementTree
		# Need to correct header...
		xmlstr = xmlstr.replace("version=\"1.0\" ", "version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"")
		with open(filedir+'/'+filename, 'w') as f:
			#f.write("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>")
			f.write(xmlstr)



	# load() requires downloading ability, but is otherwise normal.

	def load(self, ID, on_property_missing = "warn", query_db=True):
		print("LOADING PART {}".format(ID))
		if ID == "" or ID == None:
			self.clear()
			return False

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not str(ID) in data.keys():
				if not query_db:
					#print("Part not found, and no DB query requested.  Returning false...")
					return False
				#print("PART NOT FOUND.  REQUESTING FROM DB...")
				search_conditions = {'SERIAL_NUMBER':'\''+ID+'\''}  # Only condition needed; ID must be surrounded by quotes
				# For each XML file/table needed, make a request:
				# Should automatically determine where file should be saved AND add part to list
				self.ID = ID
				part_request = self.request_XML(self.PART_TABLE, search_conditions)
				#print("request_XML completed")
				if not part_request:
					print("Part not found.  Returning false...")
					self.clear()
					return False
				#self.add_part_to_list()  # done in request_xml; also takes care of filename.
				#dcreated = time.localtime()
				#dt = '{}-{}-{}'.format(dcreated.tm_mon, dcreated.tm_mday, dcreated.tm_year)
			else:
				dt = data[str(ID)]  # date created

		filedir, filename = self.get_filedir_filename(ID)  #, date=dt)
		xml_file = os.sep.join([filedir, filename])

		if not os.path.exists(xml_file):
			print("ERROR:  Step is present in partlistfile OR downloaded, but XML file {} does not exist!".format(xml_file))
			self.clear()
			return False

		xml_tree = parse(xml_file)
		self._load_from_dict(self.XML_STRUCT_DICT, xml_tree)

		self.ID = ID
		return True


	# NEW: Must save to correct location!
	def request_XML(self, table_name, search_conditions, suffix=None):
		print("CALLING request_XML")
		# Same as the assembly version, EXCEPT TIME_START -> .

		# NOTE NOTE NOTE:  Must save file in correct location AND add_part_to_list!
		# suffix is added to the end of the filename (will be _cond)
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
			print("Error:  Could not download files from DB:")
			print(e)
			return False

		xml_string = minidom.parseString(data).toprettyxml(indent="    ")
		# Output is an empty XML file, header len 61
		# NOTE:  Should be a SINGLE XML result!
		if len(xml_string) < 62:
			print("No files match the search criteria")
			return False
		# Store requested file
		xml_tree = fromstring(xml_string)
		ID = xml_tree.find('.//SERIAL_NUMBER').text
		dcreated = time.localtime()
		date = '{}-{}-{}'.format(dcreated.tm_mon, dcreated.tm_mday, dcreated.tm_year)   #xml_tree.find('.//TIME_START')
		# file date format = {}-{}-{}, mdy
		# XML date format = 26-MAR-18
		# https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
		#dt = datetime.datetime.strptime(date, '%d-%b-%y')

		#print("TEST:  found date", date)
		filedir, filename = self.get_filedir_filename(ID, date)

		if suffix:  filename = filename.replace('.xml', suffix+'.xml')

		if not os.path.exists(filedir):
			os.makedirs(filedir)
		#print("WRITING TO FILE:", os.path.join(filedir, filename))
		with open(os.path.join(filedir, filename), 'w') as f:
			f.write(xml_string)

		self.add_part_to_list(date=date)

		return True



class fsobj_assembly(fsobj):
	# Vars storing names of tables to request XML files from
	ASSM_TABLE = None
	COND_TABLE = None
	
	# Also requires XML_STRUCT_DICT (for gui storage only),
	# ...XML_UPLOAD_DICT, XML_COND_DICT (BOTH for uploading, see child class definitions).
	# NOTE that the protomodule creation file is created by the protomodule class, and must be uploaded before these.

	def __init__(self):  # Maybe this could be done OUTSIDE of init...but not sure I want to risk it.
		super(fsobj, self).__init__()
		# Add all other vars to XML_STRUCT_DICT
		# (so they will be saved accordingly)
		#print("\nINIT: ADDING PROPERTIES")
		#print(self.PROPERTIES)
		self.XML_STRUCT_DICT = {'data':{'row':{
			# Fill below
		}}}
		for var in self.PROPERTIES + self.PROPERTIES_COMMON:
			# WARNING:  XML_STRUCT_DICT is {'data':{'row': and THEN the useful vars
			self.XML_STRUCT_DICT['data']['row'][var] = var

	def save(self):
		super(fsobj_assembly, self).save()
		# This one handles self.XML_STRUCT_DICT...

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
		xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')  #tostring imported from xml.etree.ElementTree
		xmlstr = xmlstr.replace("version=\"1.0\" ", "version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"")
		with open(filedir+'/'+fname_cond, 'w') as f:
			f.write(xmlstr)



	def load(self, ID, on_property_missing = "warn"):
		if ID == -1 or ID == None:
			self.clear()
			return False

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not str(ID) in data.keys():
				print("ASSEMBLY STEP NOT FOUND.  REQUESTED CONDITION TABLES:")
				print("**TEMPORARY:  Part downloading disabled for testing!**")
				return False
				"""
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
					print("Assembly step not found.  Returning false...")
					self.clear()
					return False
				# Otherwise, both files are found!  Load from both of them.
				self.add_part_to_list()
				self.add_part_to_list()
				dcreated = time.localtime()
				dt = '{}-{}-{}'.format(dcreated.tm_mon, dcreated.tm_mday, dcreated.tm_year)
				"""
			else:
				# Note:  Names saved in partlistfile as str, not as int
				dt = data[str(ID)]  # date created


		filedir, filename = self.get_filedir_filename(ID)  #, date=dt)
		print("Searching for xml file ", filedir, filename)
		condname = filename.replace('.xml', '_cond.xml')
		xml_file      = os.sep.join([filedir, filename])
		#xml_file_cond = os.sep.join([filedir, condname])

		if not os.path.exists(xml_file):
			print("ERROR:  Step is present in partlistfile OR downloaded, but XML file {} does not exist!".format(xml_file))
			self.clear()
			return False

		xml_tree = parse(xml_file)
		self._load_from_dict(self.XML_STRUCT_DICT, xml_tree)

		# NOTE:  Now saving cond file ONLY as an upload file.  Load all info from standard file.
		"""
		xml_tree = parse(xml_file_cond)
		
		cond_vars = {'TIME_START':'cure_start', 'TIME_STOP':'cure_stop',
					 'TEMP_DEGC':'cure_temperature', 'HUMIDITY_PRCNT':'cure_humidity'}
		for tag, var in cond_vars.items():
			itemdata = xml_tree.find('.//'+tag)
			if itemdata.text.replace('.','',1).isdigit():
				idt = float(itemdata.text)
			else:
				idt = itemdata.text
			setattr(self, var, idt)
		"""

		self.ID = ID
		return True



	"""
	# NEW: Must save to correct location!
	def request_XML(self, table_name, search_conditions, suffix=None):
		# NOTE NOTE NOTE:  Must save file in correct location AND add_part_to_list!
		# suffix is added to the end of the filename (will be _cond)
		if self.ID == None or self.ID == -1:
			print("self.ID is None or \"\"; ignoring")
			return False

		#filedir, filename = self.get_filedir_filename(self.ID)
		#condname = filename.replace('.xml', '_cond.xml')

		sql_template = 'select * from hgc_int2r.{} p'
		sql_request = sql_template.format(table_name)
		sql_request = sql_request + ' where'
		# search_conditions is a dict:  {param_name:param_value}
		for param, value in search_conditions.items():
			sql_request = sql_request + ' p.{}={}'.format(param, value)
		print("TEMP:  Using sql command")
		print(sql_request)

		try:
			api = rh.RhApi(url='https://cmsdca.cern.ch/hgc_rhapi', debug=True, sso='login')
			data = api.xml(sql_request, verbose=True)
		except rh.RhApiRowLimitError as e:
			print("Error:  Could not download files from DB:")
			print(e)
			return False

		xml_str = minidom.parseString(data).toprettyxml(indent="    ")
		# Output is an empty XML file, header len 61
		# NOTE:  Should be a SINGLE XML result!
		if len(xml_str) < 62:
			print("No files match the search criteria")
			print("TEMP:  XML string is")
			print(xml_str)
			return False
		# Store requested file
		xml_tree = fromstring(xml_str)
		ID = int(xml_tree.find('.//ID').text)
		date = xml_tree.find('.//TIME_START')
		# file date format = {}-{}-{}, mdy
		# XML date format = 26-MAR-18
		# https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
		dt = datetime.strptime(date, '%d-%b-%y')
		print("TEST:  found date", dt.strftime('%m-%d-%Y'))
		filedir, filename = self.get_filedir_filename(ID, date)

		if suffix:  filename = filename.replace('.xml', suffix+'.xml')

		print("WRITING TO FILE:", os.path.join([filedir, filename]))
		with open(os.path.join([filedir, filename]), 'w') as f:
			f.write(xml_str)

		self.add_part_to_list(datetime.strftime('%m-%d-%Y'))

		return True
	"""


###############################################
##################  tooling  ##################
###############################################

class tool_sensor(fsobj_tool):
	OBJECTNAME = "sensor tool"
	FILEDIR = os.sep.join(['tooling','tool_sensor'])
	#FILENAME = 'tool_sensor_{ID:0>5}.json'
	FILENAME = 'tool_sensor_{institution}_{ID:0>5}.xml'
	PROPERTIES = [
		#'size',
		'location',
	]



	# NOTE:  This and below objects must be saved with save_tooling(), not save().


class tool_pcb(fsobj_tool):
	OBJECTNAME = "PCB tool"
	FILEDIR = os.sep.join(['tooling','tool_pcb'])
	#FILENAME = 'tool_pcb_{ID:0>5}.json'
	FILENAME = 'tool_pcb_{institution}_{ID:0>5}.xml'
	PROPERTIES = [
		#'size',  # Removed; everything should be 8 in
		'location',
	]


class tray_assembly(fsobj_tool):
	OBJECTNAME = "assembly tray"
	FILEDIR = os.sep.join(['tooling','tray_assembly'])
	#FILENAME = 'tray_assembly_{ID:0>5}.json'
	FILENAME = 'tray_assembly_{institution}_{ID:0>5}.xml'
	PROPERTIES = [
		#'size',
		'location',
	]


class tray_component_sensor(fsobj_tool):
	OBJECTNAME = "sensor tray"
	FILEDIR = os.sep.join(['tooling','tray_component_sensor'])
	#FILENAME = 'tray_component_sensor_{ID:0>5}.json'
	FILENAME = 'tray_component_sensor_{institution}_{ID:0>5}.xml'
	PROPERTIES = [
		#'size',
		'location',
	]


class tray_component_pcb(fsobj_tool):
	OBJECTNAME = "pcb tray"
	FILEDIR = os.sep.join(['tooling','tray_component_pcb'])
	#FILENAME = 'tray_component_pcb_{ID:0>5}.json'
	FILENAME = 'tray_component_pcb_{institution}_{ID:0>5}.xml'
	PROPERTIES = [
		#'size',
		'location',
	]



###############################################
###########  shipment and reception  ##########
###############################################

class shipment(fsobj):
	OBJECTNAME = "shipment"
	FILEDIR = os.sep.join(['shipments'])
	FILENAME = "shipment_{ID:0>5}.json"
	PROPERTIES = [
		"sender",
		"receiver",
		"date_sent",
		"date_received",

		"sendOrReceive",  #NEW, may be unnecessary
		#= "send" or "receive"
		"fedex_id", # NEW

		"kaptons",
		"baseplates",
		"sensors",
		"pcbs",
		"protomodules",
		"modules",
	]

	"""
	XML_STRUCT_DICT = {'SHIPMENT':{
		'ID':'ID',
		'SENDER':'sender',
		'RECIEVER':'receiver',
		"date_sent",
		"date_received",

		"sendOrReceive",  #NEW, may be unnecessary
		"fedex_id", # NEW

		"kaptons",
		"baseplates",
		"sensors",
		"pcbs",
		"protomodules",
		"modules",

	}}
	"""

	def save(self):
		super(shipment,self).save()

		if not (self.kaptons is None):
			pass
			# kaptons are not given ID or tracked as objects

		if not (self.baseplates is None):
			inst_baseplate = baseplate()
			for ID in self.baseplates:
				success = inst_baseplate.load(ID)
				if success:
					if inst_baseplate.shipments is None:
						inst_baseplate.shipments = []
					if not (self.ID in inst_baseplate.shipments):
						inst_baseplate.shipments.append(self.ID)
						inst_baseplate.save()
					inst_baseplate.clear()
				else:
					print("Baseplate not initialized.  DANGER:  This message indicates a bug is present (see fm.py).")
					# create objects?
					# IN THEORY, this should never be necessary.  If the object doesn't exist, an error message 
					# should pop up in the shipment step, and save() should not be callable...
			del inst_baseplate

		if not (self.sensors is None):
			inst_sensor = sensor()
			for ID in self.sensors:
				success = inst_sensor.load(ID)
				if success:
					if inst_sensor.shipments is None:
						inst_sensor.shipments = []
					if not (self.ID in inst_sensor.shipments):
						inst_sensor.shipments.append(self.ID)
						inst_sensor.save()
					inst_sensor.clear()
				else:
					... # create objects?
			del inst_sensor

		if not (self.pcbs is None):
			inst_pcb = pcb()
			for ID in self.pcbs:
				success = inst_pcb.load(ID)
				if success:
					if inst_pcb.shipments is None:
						inst_pcb.shipments = []
					if not (self.ID in inst_pcb.shipments):
						inst_pcb.shipments.append(self.ID)
						inst_pcb.save()
					inst_pcb.clear()
				else:
					... # create objects?
			del inst_pcb

		if not (self.protomodules is None):
			inst_protomodule = protomodule()
			for ID in self.protomodules:
				success = inst_protomodule.load(ID)
				if success:
					if inst_protomodule.shipments is None:
						inst_protomodule.shipments = []
					if not (self.ID in inst_protomodule.shipments):
						inst_protomodule.shipments.append(self.ID)
						inst_protomodule.save()
					inst_protomodule.clear()
				else:
					... # create objects?
			del inst_protomodule

		if not (self.modules is None):
			inst_module = module()
			for ID in self.modules:
				success = inst_module.load(ID)
				if success:
					if inst_module.shipments is None:
						inst_module.shipments = []
					if not (self.ID in inst_module.shipments):
						inst_module.shipments.append(self.ID)
						inst_module.save()
					inst_module.clear()
				else:
					... # create objects?
			del inst_module




###############################################
#####  components, protomodules, modules  #####
###############################################

class baseplate(fsobj_part):
	OBJECTNAME = "baseplate"
	FILEDIR = os.sep.join(['baseplates','{date}'])
	FILENAME = "baseplate_{ID}.xml"

	PROPERTIES = [
		# shipments and location
		"institution",
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# characteristics (defined upon reception)
		#"serial",   # serial given by manufacturer or distributor.
		"barcode",
		#"manufacturer", # name of company that manufactured this part
		"material",     # physical material
		#"nomthickness", # nominal thickness
		"size",         # hexagon width, numerical. 6 or 8 (integers) for 6-inch or 8-inch
		"shape",        # 
		#"rotation",     # 

		# baseplate qualification 
		#"corner_heights",      # list of corner heights
		"flatness",
		"thickness",           # measure thickness of baseplate
		"grade",   # A, B, or C

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
		"kind_of_part_id",
		"kind_of_part",
		#"location_id",
		"description",
	]

	DEFAULTS = {
		"shipments":[],
		"size":     '8', # This should not be changed!
	}


	XML_STRUCT_DICT = { "data":{"row":{
		"ID":"id_number",
		"PART_PARENT_ID":'parent_id',  #Don't care about this (not needed for upload)
		"KIND_OF_PART_ID":"kind_of_part_id",
		"KIND_OF_PART":"kind_of_part",
		"LOCATION_ID":"location_id",
		"SERIAL_NUMBER":"ID",
		"DESCRIPTION":"description",
	}}}

	XML_UPLOAD_DICT = {"PARTS":{"PART":{
		"KIND_OF_PART":"kind_of_part",
		"RECORD_INSERTION_USER":"insertion_user",
		"SERIAL_NUMBER":"ID",
		"COMMENT_DESCRIPTION":"description",
		"LOCATION":"institution",
		# NEW:
		"THICKNESS":"thickness",
		"FLATNESS":"flatness",
		"MATERIAL":"material",
		"GRADE":"grade",
		"COMMENTS":"comments_concat",
	}}}

	# List of vars that should NOT be edited in the GUI and are only loaded from DB
	# (And some info would be redundant w/ other constants, eg KIND_OF_PART and self.size)
	XML_CONSTS = [
		#'ID',  # does NOT count
		'size',
	]

	# List of vars that are stored as lists.
	# Need to be treated separately @ loading from XML
	ITEMLIST_LIST = ['comments', 'shipments'] # 'corner_heights'


	@property
	def kind_of_part(self): # Determined entirely by size
		if self.size == 6:
			size_str = "Six"
		elif self.size == 8:
			size_str = "Eight"
		elif self.size == None:
			return None
		else:
			print("ERROR:  size {} does not exist".format(self.size))
			return None
		return "HGC {} Inch Plate".format(size_str)
	@kind_of_part.setter
	def kind_of_part(self, value):
		# Parse and read in the baseplate size
		if value is None or value == "None":
			self.size = None
			return
		size_str = value.split()[1]
		if size_str == "Six":
			self.size = 6
		elif size_str == "Eight":
			self.size = 8
		else:
			print("ERROR:  Unexpected baseplate size {} loaded".format(size_str))

	@property
	def location_id(self):
		# LOCATION_DICT maps ID -> name#
		for locID, locname in LOCATION_DICT.items():
			if self.name == locname:  return locID
		print("ERROR:  location not found in LOCATION_DICT")
		return None
	@location_id.setter
	def location_id(self, value):
		if not value in LOCATION_DICT.keys():
			print("Warning:  Found invalid location ID {}".format(value))
		else:
			self.location = LOCATION_DICT[value]


	def ready_step_sensor(self, step_sensor = None, max_flatness = None):
		if step_sensor == self.step_sensor:
			return True, "already part associated with this sensor step"
	
		#if self.num_sensors == 0:  #num_sensors doesn't exist...so just ignore this?
		#	return False, "no sensors found"

		checks = []
		#checks = [
		#	self.check_edges_firm == "pass",
		#	self.check_glue_spill == "pass",
		#	]
		"""
		if self.kapton_flatness is None:
			print("No kapton flatness")  #Currently not set...
			checks.append(False)
		elif not (max_flatness is None):
			if self.kapton_flatness < max_flatness:  print("kapton flat")
			else:  print("kapton not flat")
			checks.append(self.kapton_flatness < max_flatness)
		"""
		#if not self.thickness:
		#	print("thickness false")
		#	checks.append(False)
		if self.flatness is None:  #This one seems a little iffy...
			print("flatness is None (are corner heights missing?)")
			checks.append(False)

		if not all(checks):
			return False, "kaptonized baseplate qualification failed or incomplete"
		else:
			return True, ""


	#CURRENTLY WIP

	def ready_step_pcb(self, step_pcb = None, max_flatness = None):
		if step_pcb == self.step_pcb:
			return True, "already part associated with this pcb step"

		if not (self.step_pcb is None):
			return False, "already part of a protomodule"

		"""if self.num_kaptons == 1:
			checks = [
				self.check_leakage    == "pass",
				self.check_surface    == "pass",
				self.check_edges_firm == "pass",
				self.check_glue_spill == "pass",
			]
			if self.kapton_flatness is None:
				checks.append(False)
			elif not (max_flatness is None):
				checks.append(self.kapton_flatness < max_flatness)

			if not all(checks):
				return False, "kaptonized baseplate qualification failed or incomplete"
			else:
				return True, ""
		"""

		"""if self.num_kaptons == 0:
			checks = []
			if not self.kapton_tape_applied:
				checks.append(False)
			if not self.thickness:
				checks.append(False)
			if self.flatness is None:
				checks.append(False)
			if not (max_flatness is None):
				checks.append(max_flatness > self.flatness)

			if not all(checks):
				return False, "baseplate qualification failed or incomplete"
			else:
				return True, ""
		"""
		return True, ""



class sensor(fsobj_part):
	OBJECTNAME = "sensor"
	FILEDIR = os.sep.join(['sensors','{date}'])
	FILENAME = "sensor_{ID}.xml"
	PROPERTIES = [
		# shipments and location
		"institution",
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# characteristics (defined upon reception)
		"barcode",
		"manufacturer",
		"type",         # NEW:  This is now chosen from a drop-down menu
		"thickness",
		"size",         # 
		"channel_density",  # HD or LD
		"shape",        # 
		"grade",
		#"rotation",     # 

		# sensor qualification
		"inspection", # None if not inspected yet; True if passed; False if failed

		# sensor step
		"step_sensor", # which step_sensor placed this sensor
		"protomodule", # which protomodule this sensor is a part of

		# NOTE:  kapton step has been moved to sensor!
		"step_kapton",
		"check_glue_spill",

		# associations to other objects
		"module", # which module this sensor is a part of

		# New to match Akshay's script
		"insertion_user",
		# NEW:  Data to be read from base XML file
		"id_number",
		"kind_of_part_id",
		"kind_of_part",
		"location_id",
		"description",

	]

	DEFAULTS = {
		"shipments":[],
		"size":    '8',  # DO NOT MODIFY
	}

	XML_STRUCT_DICT = { "data":{"row":{
		#"ID":"id_number",
		"KIND_OF_PART_ID":"kind_of_part_id",
		"KIND_OF_PART":"kind_of_part", #TBD:  Property
		"LOCATION_ID":"location_id", # same...
		"MANUFACTURER":"manufacturer",
		"SERIAL_NUMBER":"ID",
		"DESCRIPTION":"description",  # Can probably leave this blank...
	}}}

	XML_UPLOAD_DICT = {"PARTS":{"PART":{
		"KIND_OF_PART":"kind_of_part",
		"RECORD_INSERTION_USER":"insertion_user",
		"SERIAL_NUMBER":"ID",
		"COMMENT_DESCRIPTION":"description",
		"LOCATION":"institution",
		#"MANUFACTURER":"manufacturer",
		# NEW:
		"THICKNESS":"thickness",
		"VISUAL_INSPECTION":"inspection",
		"GRADE":"grade",
		"COMMENTS":"comments_concat",
		#"PREDEFINED_ATTRIBUTES":{  # Ignore this for now...
		#	"ATTRIBUTE":{
		#		"NAME":"HGC Silicon Sensor Type",
		#		"VALUE":"200DD",
		#	}
		#}
	}}}

	XML_CONSTS = [
		#'ID',  # does NOT count
		'size',
	]

	ITEMLIST_LIST = ['comments', 'shipments']


	"""
	@property
	def kind_of_part(self): # Determined entirely by size
		if self.size == 6:
			size_str = "Six"
		elif self.size == 8:
			size_str = "Eight"
		else:
			print("ERROR:  size {} does not exist".format(self.size))
			return None
		return "HPK {} Inch {} Cell Silicon Sensor".format(size_str, self.channels)
	@kind_of_part.setter
	def kind_of_part(self, value):
		# Parse and read in the baseplate size
		if value is None:
			self.channels = None
			return
		parsestr = value.split() # ex. "HPK Six Inch 256 Cell Silicon Sensor"
		size_str = parsestr[1]
		self.channels = parsestr[3]
		if size_str == "Six":
			self.size = 6
		elif size_str == "Eight":
			self.size = 8
		else:
			print("ERROR:  Unexpected sensor size {} loaded".format(size_str))
	"""


	@property
	def location_id(self):
		# LOCATION_DICT maps ID -> name#
		for locID, locname in LOCATION_DICT.items():
			if self.name == locname:  return locID
		print("ERROR:  location not found in LOCATION_DICT")
		return None
	@location_id.setter
	def location_id(self, value):
		if not value in LOCATION_DICT.keys():
			print("Warning:  Found invalid location ID {}".format(value))
		else:
			self.location = LOCATION_DICT[value]





	# NEWLY MOVED FROM BASEPLATE!!!
	# Should not be passing any of these params yet
	def ready_step_kapton(self, step_kapton = None, max_flatness = None, max_kapton_flatness = None):
		#if step_kapton == self.step_kapton:
		#	return True, "already part associated with this kapton step"

		if not (self.step_sensor is None):
			return False, "already part of a protomodule (has a sensor step)"

		#if not self.step_kapton is None:
		#	# step_kapton has already been assigned, and it isn't the one that's currently being added!
		#	return False, "baseplate already has an assigned kapton step!"
		
		# Kapton qualification checks:
		errstr = ""
		checks = [
			#self.check_edges_firm == "pass",
			self.check_glue_spill == "pass",
			#self.kapton_flatness  != None,
		]
		#if self.kapton_flatness is None:
		#	errstr+=" kapton flatness doesn't exist."
		#	checks.append(False)
		#elif not (max_kapton_flatness is None) and (self.kapton_flatness > max_kapton_flatness):
		#	errstr.append(" kapton flatness {} exceeds max of {}.".format(self.kapton_flatness, max_kapton_flatness))
		#	checks.append(False)

		# Baseplate qualification+preparation checks:
		#if not self.kapton_tape_applied:
		#	errstr+=" kapton tape not applied."
		#	checks.append(False)
		if not self.thickness:
			errstr+=" thickness doesn't exist."
			checks.append(False)
		#if self.flatness is None:
		#	errstr+=" flatness doesn't exist."
		#	checks.append(False)
		#elif not (max_flatness is None):
		#	if max_flatness<self.flatness:
		#		errstr+="kapton flatness "+str(self.flatness)+" exceeds max "+str(max_flatness)+"."
		#		checks.append(False)

		if not all(checks):
			return False, "sensor qualification failed or incomplete. "+errstr
		else:
			return True, ""



class pcb(fsobj_part):
	OBJECTNAME = "PCB"
	FILEDIR = os.sep.join(['pcbs','{date}'])  #,'pcb_{ID}'])
	FILENAME = "pcb_{ID}.xml"
	PROPERTIES = [
		# shipments and location
		"institution",
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# details / measurements / characteristics
		"insertion_user",
		"barcode", 
		"manufacturer", # 
		"type",         # 
		"resolution_type", # NEW
		"num_rocs",     # NEW
		"size",         # 
		"channels",     # 
		"shape",        # 
		#"chirality",    # 

		# pcb qualification
		#"daq",        # name of dataset
		#"daq_ok",     # None if no DAQ yet; True if DAQ is good; False if it's bad
		#"inspection", # Check for exposed gold on backside. None if not inspected yet; True if passed; False if failed
		"grade",
		"thickness",  # 
		"flatness",   # 
		
		# pcb step
		"step_pcb", # which step_pcb placed this pcb
		"module",   # which module this pcb is a part of

		# Associations to datasets
		#"daq_data", # list of all DAQ datasets

		# NEW:  Data to be read from base XML file
		"id_number",
		"kind_of_part_id",
		"kind_of_part",
		"location_id",
		"description",

		"manufacturer",  # for output XML
		"version",
		"batch_number",

		"test_files",
	]

	#PROPERTIES_DO_NOT_SAVE = [
	#	"daq_data",
	#]

	DEFAULTS = {
		"shipments":[],
		#"daq_data":[],
		"size":     '8',
		"comment_description":  "TEST",
		"test_files":[],
	}

	XML_STRUCT_DICT = { "data":{"row":{
		"ID":"id_number",
		"KIND_OF_PART_ID":"kind_of_part_id",
		"KIND_OF_PART":"kind_of_part", #TBD:  Property
		"LOCATION_ID":"location_id", # same...
		"MANUFACTURER":"manufacturer",
		"SERIAL_NUMBER":"ID",
		"VERSION":"version",
		"BATCH_NUMBER":"batch_number",
	}}}

	XML_UPLOAD_DICT = {"PARTS":{"PART":{
		"KIND_OF_PART":"kind_of_part",
		"RECORD_INSERTION_USER":"insertion_user",
		"SERIAL_NUMBER":"ID",
		"COMMENT_DESCRIPTION":"comment_description",
		"LOCATION":"institution",
		"MANUFACTURER":"manufacturer",
		"FLATNESS":"flatness",
		"THICKNESS":"thickness",
		"GRADE":"grade",
		"COMMENTS":"comments_concat",
	}}}

	DAQ_DATADIR = 'daq'

	XML_CONSTS = [
		#'ID',  # does NOT count
		'resolution_type',
	]

	ITEMLIST_LIST = ['comments', 'shipments', 'test_files']

	# WIP, go back and fix!
	"""
	@property
	def kind_of_part(self): # Determined entirely by size
		return "HGC {} Hex PCB".format(self.resolution_type)
	@kind_of_part.setter
	def kind_of_part(self, value):
		# Parse and read in the baseplate size
		res_str = value.split()[1]
		if not res_str in ['HD', 'LD']:
			print("ERROR:  Unexpected resolution type {}".format(res_str))
		self.resolution_type = res_str  # HD or LD
	"""
	
	@property
	def location_id(self):
		# LOCATION_DICT maps ID -> name#
		for locID, locname in LOCATION_DICT.items():
			if self.name == locname:  return locID
		print("ERROR:  location not found in LOCATION_DICT")
		return None
	@location_id.setter
	def location_id(self, value):
		if not value in LOCATION_DICT.keys():
			print("Warning:  Found invalid location ID {}".format(value))
		else:
			self.location = LOCATION_DICT[value]


	def fetch_datasets(self):
		if self.ID is None:
			err = "no pcb loaded; cannot fetch datasets"
			raise ValueError(err)
		filedir, filename = self.get_filedir_filename(self.ID)
		daq_datadir = os.sep.join([filedir, self.DAQ_DATADIR])
		if os.path.exists(daq_datadir):
			self.daq_data = [_ for _ in os.listdir(daq_datadir) if os.path.isfile(os.sep.join([daq_datadir,_]))]
		else:
			self.daq_data = []

	"""
	def load(self,ID):
		success = super(pcb,self).load(ID)
		#if success:
		#	self.fetch_datasets()
		return success
	"""

	# OLD (?)
	"""
	def save(self):  #NEW for XML generation
		
		# FIRST:  If not all necessary vars are defined, don't save the XML file.
		required_vars = [self.size, self.comments, self.location, self.institution]
		#contents = vars(self)
		for vr in required_vars:
			if vr is None:
				# If any undef var found, save the json file only and return
				print("NOTE:  missing required data, baseplate XML not saved.")
				super(pcb, self).save()
				return

		# TAKE 2:  This time, use gen_xml(input_dict) to streamline things.
		part_dict = {
			'KIND_OF_PART':          'HGC {} Inch {} Channel PCB'.format('Six' if self.size=='6' else 'Eight', self.channels),
			'RECORD_INSERTION_USER': self.insertion_user,   # NOTE:  This may have to be redone when XML uploading is implemented!
			'SERIAL_NUMBER':         self.ID,
			'COMMENT_DESCRIPTION':   self.comments,   # Note:  Requires special treatment
			'LOCATION':              self.location,
			'MANUFACTURER':          self.manufacturer,
		}

		parts_dict = {
			'PART': part_dict,
		}
		root_dict = {
			'PARTS': parts_dict,
		}

		# CREATE XML FILE OBJECT:
		xml_tree = self.generate_xml(root_dict)

		# Order changed:
		super(pcb, self).save()

		# Save:
		self.save_xml(xml_tree)
		
		# From old save():
		filedir, filename = self.get_filedir_filename(self.ID)
		if not os.path.exists(os.sep.join([filedir, self.DAQ_DATADIR])):
			os.makedirs(os.sep.join([filedir, self.DAQ_DATADIR]))
		self.fetch_datasets()
		self.fetch_datasets()
	"""

	# OLD
	"""
	def load_daq(self,which):
		if isinstance(which, int):
			which = self.daq_data[which]

		filedir, filename = self.get_filedir_filename()
		file = os.sep.join([filedir, self.DAQ_DATADIR, which])

		print('load {}'.format(file))
	"""


class protomodule(fsobj_part):
	OBJECTNAME = "protomodule"
	FILEDIR = os.sep.join(['protomodules','{date}'])
	FILENAME = 'protomodule_{ID}.xml'
	PROPERTIES = [
		# shipments and location
		"institution",
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# characteristics - taken from child parts upon creation of protomodule
		"insertion_user",
		"thickness",   # sum of baseplate and sensor, plus glue gap
		#"num_kaptons", # from baseplate  # OLD
		"channels",    # from sensor
		"size",        # from baseplate or sensor (identical)
		"shape",       # from baseplate or sensor (identical)
		"grade",
		#"chirality",   # from baseplate
		#"rotation",    # from baseplate or sensor (identical)
		# initial location is also filled from child parts

		# sensor step - filled upon creation
		"step_sensor", # ID of sensor step
		"baseplate",   # ID of baseplate
		"sensor",      # ID of sensor
		"step_kapton", # ID of kapton step (from SENSOR)

		# protomodule qualification
		"offset_translation_x", # translational offset of placement
		"offset_translation_y",
		"offset_rotation",    # rotation offset of placement
		"flatness",           # flatness of sensor surface after curing
		#"check_cracks",       # None if not yet checked; True if passed; False if failed
		#"check_glue_spill",   # None if not yet checked; True if passed; False if failed

		# pcb step
		"step_pcb", # ID of pcb step
		"module",   # ID of module

		# NEW:  Data to be read from base XML file
		"id_number",
		"part_parent_id",
		"kind_of_part_id",
		"kind_of_part",
		"location_id",
		"comment_description",

		"wirebonded",  # Maybe not needed here??
	]

	DEFAULTS = {
		"shipments":[],
		"size":     '8',
		"comment_description":"top layer: pcb",  # SUBJECT TO CHANGE
	}

	
	XML_STRUCT_DICT = { "data":{"row":{
		"ID":"id_number",
		"PART_PARENT_ID":"part_parent_id",
		"KIND_OF_PART_ID":"kind_of_part_id",
		"KIND_OF_PART":"kind_of_part",
		"LOCATION_ID":"location_id",
		"SERIAL_NUMBER":"ID",
	}}}

	XML_UPLOAD_DICT = {"PARTS":{"PART":{
		"KIND_OF_PART":"kind_of_part",
		"SERIAL_NUMBER":"ID",
		#"COMMENT_DESCRIPTION":"comment_description",
		"LOCATION":"location",
		"RECORD_INSERTION_USER":"insertion_user",
		"THICKNESS":"thickness",
		"FLATNESS":"flatness",
		"GRADE":"grade",
		#"PREDEFINED_ATTRIBUTES":{   # Ignore for now per Umesh
		#	"ATTRIBUTE":{
		#		"NAME":"AsmTrayPosn",
		#		"VALUE":"assem_tray_posn",
		#	}
		#}
		"COMMENTS":"comments_concat",
		"CHILDREN":{
			"PART":[{
				"KIND_OF_PART":"baseplate_type",
				"SERIAL_NUMBER":"baseplate",
			},
			{
				"KIND_OF_PART":"sensor_type",
				"SERIAL_NUMBER":"sensor",
			}]
		}
	}}}

	XML_CONSTS = [
		#'ID',  # does NOT count
		'resolution_type',
	]

	ITEMLIST_LIST = ['comments', 'shipments']

	# WIP, go back and fix
	"""
	@property
	def kind_of_part(self): # Determined entirely by size
		if self.size == 6:
			size_str = "Six"
		elif self.size == 8:
			size_str = "Eight"
		else:
			print("ERROR:  size {} does not exist".format(self.size))
			return Nonei
		return "HGC {} Inch Silicon Protomodule".format(size_str)
	@kind_of_part.setter
	def kind_of_part(self, value):
		# Parse and read in the baseplate size
		res_str = value.split()[1]
		if res_str == "Six":
			self.size = 6
		elif res_str == "Eight":
			self.size = 8
		else:
			print("Read unrecognized protomodule size {}".format(res_str))
	"""

	@property
	def assm_tray_pos(self):
		# If has a sensor step, grab the position of this sensor and return it here...
		# "TRPOSN_11" in XML file makes no sense...temporarily using X_Y.
		"""
		if self.step_sensor is None:
			print("assm_tray_posn:  no sensor step yet")
			return "None"
		temp_sensor_step = step_sensor()
		found = temp_sensor_step.load(self.step_sensor)
		if not found:
			print("ERROR in assm_tray_pos:  protomodule has sensor step {}, but none found!".format(self.step_senosr))
			return "None"
		else:
			position = temp_sensor_step.sensors.index(self.ID)
			return "{}_{}".format(position%2+1, position//3+1)
		"""
		return "{}_{}".format(self.assm_tray_row, assm_tray_col)

	@property
	def assm_tray_row(self):
		# If has a sensor step, grab the position of this sensor and return it here...
		# "TRPOSN_11" in XML file makes no sense...temporarily using X_Y.
		if self.step_sensor is None:
			print("assm_tray_posn:  no sensor step yet")
			return "None"
		temp_sensor_step = step_sensor()
		found = temp_sensor_step.load(self.step_sensor)
		if not found:
			print("ERROR in assm_tray_pos:  protomodule has sensor step {}, but none found!".format(self.step_senosr))
			return "None"
		else:
			print("Temp sensor step found.  Sensors:", temp_sensor_step.sensors)
			position = temp_sensor_step.sensors.index(self.ID)
			return position%2+1	

	@property
	def assm_tray_col(self):
		# If has a sensor step, grab the position of this sensor and return it here...
		# "TRPOSN_11" in XML file makes no sense...temporarily using X_Y.
		if self.step_sensor is None:
			print("assm_tray_posn:  no sensor step yet")
			return "None"
		temp_sensor_step = step_sensor()
		found = temp_sensor_step.load(self.step_sensor)
		if not found:
			print("ERROR in assm_tray_pos:  protomodule has sensor step {}, but none found!".format(self.step_senosr))
			return "None"
		else:
			position = temp_sensor_step.sensors.index(self.ID)
			return position//3+1

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


class module(fsobj_part):
	OBJECTNAME = "module"
	FILEDIR    = os.sep.join(['modules','{date}','module_{ID}'])
	FILENAME   = 'module_{ID}.xml'
	PROPERTIES = [
		# shipments and location
		"institution",
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# characteristics - taken from child parts upon creation of module
		"insertion_user",
		"thickness",   # sum of protomodule and sensor, plus glue gap
		"channels",    # from protomodule or pcb (identical)
		"size",        # from protomodule or pcb (identical)
		"shape",       # from protomodule or pcb (identical)
		"grade",
		#"chirality",   # from protomodule or pcb (identical)
		# initial location is also filled from child parts

		# components and steps - filled upon creation
		"baseplate",     # 
		"sensor",        # 
		"protomodule",   # 
		"pcb",           # 
		"step_kapton",   # 
		"step_sensor",   # 
		"step_pcb",      # 

		# module qualification
		#"check_glue_spill",        # None if not yet checked; True if passed; False if failed
		"preinspection",
		"offset_translation_x",
		"offset_translation_y",
		"offset_rotation",

		# wirebonding
		# NEW: NOTE:  This info is filled out using the wirebonding page exclusively!
		"wirebonding_completed",
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
		#"wirebonds_damaged_back",       # list of damaged bonds found during inspection
		#"wirebonds_repaired_back",      # have wirebonds been repaired
		#"wirebonds_repaired_list_back", # list of wirebonds succesfully repaired
		"wirebonds_repaired_user_back", # who repaired bonds


		# front wirebonding
		"wirebonding_front",                # has wirebonding been done
		"wirebonding_skip_channels_front",  # list of channels to ignore
		"wirebonding_unbonded_channels_front", # list of sites that were not wirebonded
		"wirebonding_user_front",           # who performed wirebonding
		"wirebonds_inspected_front",     # whether inspection has happened
		#"wirebonds_damaged_front",       # list of damaged bonds found during inspection
		#"wirebonds_repaired_front",      # have wirebonds been repaired
		#"wirebonds_repaired_list_front", # list of wirebonds succesfully repaired
		"wirebonds_repaired_user_front", # who repaired bonds

		#"wirebonding_shield",
		#"wirebonding_guard",


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
		#"test_bonds_pulled",      # have test bonds been pulled
		"test_bonds_pulled_user", # who pulled test bonds
		"test_bonds_pull_avg",    # average pull strength
		"test_bonds_pull_std",    # stddev of pull strength
		#"test_bonds_pulled_ok",   # is result of test bond pulling ok
		#"test_bonds_rebonded",      # have test bonds been rebonded
		#"test_bonds_rebonded_user", # who rebonded test bonds
		#"test_bonds_rebonded_ok",   # is result of rebonding test bonds ok


		# wirebonding qualification
		#"wirebonding_final_inspection",
		"wirebonding_final_inspection_user",
		"wirebonding_final_inspection_ok",


		# module qualification (final)
		#"hv_cables_attached",      # have HV cables been attached
		#"hv_cables_attached_user", # who attached HV cables
		#"unbiased_daq",      # name of dataset
		#"unbiased_daq_user", # who took dataset
		#"unbiased_daq_ok",   # whether result is ok
		#"iv",      # name of dataset
		#"iv_user", # who took dataset
		#"iv_ok",   # whether result is ok
		#"biased_daq",         # name of dataset
		#"biased_daq_voltage", # voltage at which data was taken
		#"biased_daq_ok",      # whether result is ok

		# datasets
		#"iv_data",  #
		#"daq_data", #

		# NEW:  Data to be read from base XML file
		"id_number",
		"part_parent_id",
		"kind_of_part_id",
		"kind_of_part",
		"location_id",
		"description",

		"test_files",
	]
	
	PROPERTIES_DO_NOT_SAVE = [
		#"iv_data",
		#"daq_data",
	]

	DEFAULTS = {
		"shipments":[],
		'wirebonding_comments':[],
		'encapsulation_comments':[],
		#'iv_data':[],
		#'daq_data':[],
		"size":    '8',
		"test_files":[],
	}

	ITEMLIST_LIST = ['comments', 'shipments', 'wirebonding_comments', 'encapsulation_comments', 'test_files',
		#'wirebonding_unbonded_channels_back',
		'wirebonding_unbonded_channels_front'
	]

	XML_STRUCT_DICT = { "data":{"row":{
		"ID":"id_number",
		"PART_PARENT_ID":"part_parent_id",
		"KIND_OF_PART_ID":"kind_of_part_id",
		"KIND_OF_PART":"kind_of_part",
		"LOCATION_ID":"location_id",
		"SERIAL_NUMBER":"ID",
		"DESCRIPTION":"description",
	}}}

	XML_UPLOAD_DICT = {"PARTS":{"PART":{
		"KIND_OF_PART":"kind_of_part",
		"SERIAL_NUMBER":"ID",
		"COMMENT_DESCRIPTION":"description",
		"LOCATION":"location",
		"RECORD_INSERTION_USER":"insertion_user",
		"GRADE":"grade",
		"COMMENTS":"comments_concat",
		"PREDEFINED_ATTRIBUTES":{
			"ATTRIBUTE":{
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
			},
			{
				"KIND_OF_PART":"pcb_type",
				"SERIAL_NUMBER":"pcb",
			}]
		}
	}}}

	#IV_DATADIR      = 'iv'
	#IV_BINS_DATADIR = 'bins'
	#DAQ_DATADIR     = 'daq'

	#BA_FILENAME = 'ba {which}'
	#BD_FILENAME = 'bd {which}'

	XML_CONSTS = [
		#'ID',  # does NOT count
		'resolution_type',
	]


	# GO BACK and fix
	"""
	@property
	def kind_of_part(self): # Determined entirely by size
		if self.size == 6:
			size_str = "Six"
		elif self.size == 8:
			size_str = "Eight"
		else:
			print("ERROR:  size {} does not exist".format(self.size))
			return None
		return "HGC {} Inch Plate".format(size_str)
	@kind_of_part.setter
	def kind_of_part(self, value):
		# Parse and read in the baseplate size
		res_str = value.split()[1]
		if not res_str in ['HD', 'LD']:
			print("ERROR:  Unexpected resolution type {}".format(res_str))
		self.resolution_type = res_str  # HD or LD
	"""


	# TEMPORARY:  May want to fix this...
	@property
	def wirebonded(self):
		return False

	@property
	def assm_tray_pos(self):
		# If has a sensor step, grab the position of this sensor and return it here...
		# "TRPOSN_11" in XML file makes no sense...temporarily using X_Y.
		if self.step_sensor is None:
			print("assm_tray_posn:  no sensor step yet")
			return "None"
		temp_sensor_step = step_sensor()
		found = temp_sensor_step.load(self.step_sensor)
		if not found:
			print("ERROR in assm_tray_pos:  protomodule has sensor step {}, but none found!".format(self.step_senosr))
			return "None"
		else:
			position = temp_sensor_step.sensors.index(self.ID)
			return "{}_{}".format(position%2, position//3)

	@property
	def protomodule_type(self):
		if self.protomodule is None:
			print("ERROR in protomodule_type:  protomodule is None!")
			return None
		temp_protomodule = protomodule()
		if not temp_protomodule.load(self.protomodule):
			print("ERROR:  Could not find child protomodule {}!".format(self.protomodule))
			return None
		return temp_protomodule.kind_of_part

	@property
	def pcb_type(self):
		if self.pcb is None:
			print("ERROR in pcb_type:  pcb is None!")
			return None
		temp_pcb = pcb()
		if not temp_pcb.load(self.pcb):
			print("ERROR:  Could not find child PCB {}!".format(self.pcb))
			return None
		return temp_pcb.kind_of_part



###############################################
###############  assembly steps  ##############
###############################################

class step_kapton(fsobj):  # NOTE:  Not an assembly object!  (doesn't have 2 XML files, not in DB)
	OBJECTNAME = "kapton step"
	FILEDIR    = os.sep.join(['steps','kapton','{date}'])
	FILENAME   = 'kapton_assembly_step_{ID:0>5}.xml'
	PROPERTIES = [
		'user_performed', # name of user who performed step
		'institution', # institution where step was performed
		'location', # location at institution where step was performed
		#'date_performed', # date step was performed
		'run_start',  # unix time @ start of run
		# Currently replacing all other time info:
		#'run_stop',   # unix time @ end of run

		#'cure_start',       # unix time @ start of curing
		#'cure_stop',        # unix time @ end of curing
		'cure_temperature', # Average temperature during curing (centigrade)
		'cure_humidity',    # Average humidity during curing (percent)

		'kaptons_inspected', # list of kapton inspection results, ordered by component tray location. should all be True (don't use a kapton if it doesn't pass)
		'tools',      # list of pickup tool IDs, ordered by pickup tool location
		#'baseplates', # list of baseplate   IDs, ordered by assembly tray position
		'sensors',  # NEW:  List of sensors!

		'tray_component_sensor', # ID of component tray used
		'tray_assembly',         # ID of assembly tray used
		'batch_araldite',        # ID of araldite batch used
	]


	"""@property
	def cure_duration(self):
		if (self.cure_stop is None) or (self.cure_start is None):
			return None
		else:
			return self.cure_stop - self.cure_start
	"""

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



	def save(self):
		super(step_kapton, self).save()
		inst_sensor = sensor()

		for i in range(6):
			sensor_exists = False if self.sensors[i] is None else inst_sensor.load(self.sensors[i])
			if sensor_exists:

				# If baseplate has no step_kapton or if its step_kapton is the one being edited now:
				if (inst_sensor.step_kapton is None) or (inst_sensor.step_kapton == self.ID):
					inst_sensor.step_kapton = self.ID
					inst_sensor.save()
					inst_sensor.clear()
				else:
					print("ERROR:  Sensor {} has already been assigned a kapton step!".format(inst_sensor.ID))
					print("*WARNING:  ready_step_kapton should prevent this from working!")
					assert(False)

			# Unnecessary code; this would only activate on empty rows and do nothing
			#else:
			#	if not (self.baseplates[i] is None):
			#		print("step_kapton {} cannot write to baseplate {}: does not exist".format(self.ID, self.baseplates[i]))




class step_sensor(fsobj_assembly):
	OBJECTNAME = "sensor step"
	FILEDIR    = os.sep.join(['steps','sensor','{date}'])
	FILENAME   = 'sensor_assembly_step_{ID:0>5}.xml'
	PROPERTIES = [
		'user_performed', # name of user who performed step
		'institution',
		'location', # New--instituition where step was performed

		'run_start',  # New--unix time @ start of run
		'run_stop',  # New--unix time @ end of run

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
		#'batch_loctite',         # ID of loctite  batch used

		# TEMP:
		'kind_of_part_id',
		'kind_of_part',
	]

	ITEMLIST_LIST = ['comments', 'shipments', 'tools', 'sensors', 'baseplates', 'protomodules']

	"""@property
	def cure_duration(self):
		if (self.cure_stop is None) or (self.cure_start is None):
			return None
		else:
			return self.cure_stop - self.cure_start
	"""

	# NOTE WARNING:  Commenting all WIP changes for now

	
	@property
	def temp_property(self):
		return None
	@temp_property.setter
	def temp_property(self, value):
		pass

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

	#@property
	#def xml_location(self):
	#	return "{}, {}".format(self.institution, self.location)

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
			'KIND_OF_PART':'temp_property',  # TBD
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




class step_pcb(fsobj_assembly):
	OBJECTNAME = "PCB step"
	FILEDIR = os.sep.join(['steps','pcb','{date}'])
	FILENAME = 'pcb_assembly_step_{ID:0>5}.xml'
	PROPERTIES = [
		'user_performed', # name of user who performed step
		#'date_performed', # date step was performed
		'institution',
		'location', #Institution where step was performed
		
		'run_start',  # unix time @ start of run
		'run_stop',   # unix time @ start of run
		
		#'cure_start',       # unix time @ start of curing
		#'cure_stop',        # unix time @ end of curing
		'cure_temperature', # Average temperature during curing (centigrade)
		'cure_humidity',    # Average humidity during curing (percent)

		'tools',        # list of pickup tool IDs, ordered by pickup tool location
		'pcbs',         # list of pcb         IDs, ordered by component tray location
		'protomodules', # list of protomodule IDs, ordered by assembly tray location
		'modules',      # list of module      IDs assigned to new modules, by assembly tray location

		'tray_component_pcb', # ID of component tray used
		'tray_assembly',      # ID of assembly  tray used
		'batch_araldite',     # ID of araldite batch used
	]


	# PASTED RECENTLY, needs revision
	ITEMLIST_LIST = ['comments', 'shipments', 'tools', 'pcbs', 'protomodules', 'modules']

	"""@property
	def cure_duration(self):
		if (self.cure_stop is None) or (self.cure_start is None):
			return None
		else:
			return self.cure_stop - self.cure_start
	"""

	# NOTE WARNING:  Commenting all WIP changes for now

	
	@property
	def temp_property(self):
		return None
	@temp_property.setter
	def temp_property(self, value):
		pass

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

	#@property
	#def xml_location(self):
	#	return "{}, {}".format(self.institution, self.location)

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
	RUN_TYPE        = 'HGC 6inch Module Assembly'
	CMT_DESCR = 'Build 6inch modules'
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
			'KIND_OF_PART':'temp_property',  # TBD
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



###############################################
##################  supplies  #################
###############################################

class batch_araldite(fsobj):
	OBJECTNAME = "araldite batch"
	FILEDIR = os.sep.join(['supplies','batch_araldite','{date}'])
	FILENAME = 'batch_araldite_{ID:0>5}.xml'
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
	# Dates should have the format "{}-{}-{} {}:{}:{}".  NOT a property; the UI pages handle the loading.

"""
class batch_loctite(fsobj):
	OBJECTNAME = "loctite batch"
	FILEDIR = os.sep.join(['supplies','batch_loctite','{date}'])
	FILENAME = 'batch_loctite_{ID:0>5}.xml'
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
"""

class batch_wedge(fsobj):
	OBJECTNAME = "wedge batch"
	FILEDIR = os.sep.join(['supplies','batch_wedge','{date}'])
	FILENAME = 'batch_wedge_{ID:0>5}.xml'
	PROPERTIES = [
		#'date_received',
		#'date_expires',
		'is_empty',
	]
	XML_STRUCT_DICT = {'BATCH':{
		'ID':'ID',
		'RECEIVE_DATE':'date_received',
		'EXPIRE_DATE':'date_expires',
		'IS_EMPTY':'is_empty',
		'COMMENTS':'comments'
	}}

class batch_sylgard(fsobj):  # was sylgar_thick
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

"""
class batch_sylgard_thin(fsobj):
	OBJECTNAME = "sylgard (thin) batch"
	FILEDIR = os.sep.join(['supplies','batch_sylgard_thin','{date}'])
	FILENAME = 'batch_sylgard_thin_{ID:0>5}.xml'
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
"""

class batch_bond_wire(fsobj):
	OBJECTNAME = "bond wire batch"
	FILEDIR = os.sep.join(['supplies','batch_bond_wire','{date}'])
	FILENAME = 'batch_bond_wire_{ID:0>5}.xml'
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






if __name__ == '__main__':
	# test features without UI here
	...
