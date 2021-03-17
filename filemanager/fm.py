import os
import json
import numpy
import time
import subprocess

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

import rhapi as rh
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
				'batch_araldite', 'batch_loctite', 'batch_sylgard_thick',
				'batch_sylgard_thin', 'batch_bond_wire',
				'tool_sensor', 'tool_pcb', 'tray_assembly', 'tray_component_sensor', 'tray_component_pcb',
				'step_kapton', 'step_sensor', 'step_pcb']
	for part in obj_list:
		fname = os.sep.join([partlistdir, part+'s.json'])
		if not os.path.exists(fname):
			with open(fname, 'w') as opfl:
				# Dump an empty dict if nothing is found
				# NOTE:  Format of dictionary is {ID:creation-date-string, ...}
				json.dump({}, opfl)

loadconfig()




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
		for item_name, item in struct_dict.items():
			# item_name = XML tag name, item = name of var/prop to assign
			if type(item) is dict:
				self._load_from_dict(item, xml_tree)
			# If item must be stored as a list in the class:
			elif item in self.ITEMLIST_LIST:  #len(xml_tree.findall(item_name)) > 1:  # If multiple items found:
				itemdata = xml_tree.findall('.//'+item_name)  # List of all contents of matching tags
				# NOTE:  Items could be text or ints!  Convert accordingly.
				itemdata = [it.text for it in itemdata]
				if itemdata != []:
					if itemdata[0].isdigit():  itemdata = [int(it.text) for it in itemdata]
				setattr(self, item, itemdata)  # Should be a list containing contents; just assign it to the var
			else:
				print("_load_from_dict: ordinary item found!")
				itemdata = xml_tree.find('.//'+item_name)  # NOTE:  itemdata is an Element, not text!
				print("Item text is", itemdata.text, "; item is", item)
				if itemdata.text.isdigit():  # If int:
					idt = int(itemdata.text)
				elif itemdata.text.replace('.','',1).isdigit():  # If float:
					idt = float(itemdata.text)
				elif itemdata.text == 'True':  idt = True
				elif itemdata.text == 'False': idt = False
				else:  # If string
					idt = itemdata.text
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

		return True



	def new(self, ID):
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
		# Generate XML ElementTree from input_dictionary, and return the ElementTree.
		# Note:  does not save XML file!
		# Note:  input_dict is a list of all items contained by the ROOT.  ROOT is not included, but 
		#        is generated automatically.

		root = Element('ROOT')
		root.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
		tree = ElementTree(root)

		for item_name, item in input_dict.items():
			# Note:  Need to add a case if one of the items is a list.
			# For files where multiple DATA_SETs w/ the same name are needed.
			if type(item) == list:
				for item_ in item:
					child = self.dict_to_element(item_, item_name)
					root.append(child)
			else:
				child = self.dict_to_element(item, item_name)
				root.append(child)
		return tree


	def dict_to_element(self, input_dict, element_name):
		# Reads a dictionary, and returns an XML element 'element_name' filled with the contents of the current object
		# structured according to that dictionary.
		# NOTE:  This must be able to work recursively.  I.e. if one of the objs in the input_dict is a dict,
		#    it reads *that* dictionary and creates an element for it, +appends it to current element.  Etc.

		parent = Element(element_name)
		
		for item_name, item in input_dict.items():
			# CHANGE FOR NEW XML SYSTEM:
			# item is a list (comments), dict (another XML layer), or string (var)
			# If string, use getattr()
			print("dict_to_element:  SAVING: ", item_name, item)
			if type(item) == dict:
				# Recursive case: Create an element from the child dictionary.
				child = self.dict_to_element(item, item_name)
				parent.append(child)
			elif type(getattr(self, item, None)) == list:  #type(item) == list:
				# Base case 1:  List of comments.  Create an element for each one.
				print("Found comment list: ", getattr(self, item, None))
				for comment in getattr(self, item, None):
					child = Element(item_name)
					child.text = comment
					parent.append(child)
			else:
				print("INSERTING BASE ITEM", item_name, item)
				# Base case 2:
				child = Element(item_name)
				child.text = str(getattr(self, item, None))  # item should be the var name!
				# Fill attrs that don't exist w/ None
				# This SHOULD work with properties!
				print("    Creating element {} with contents {}".format(item_name, child.text))
				parent.append(child)
				# Special case for PARTs:
				if item_name == 'PART':
					child.set('mode','auto')

		return parent


	# NEWLY REWORKED
	# Should be fully general--all objects can use this if XML_STRUCT_DICT works.
	# Need separate implementation for tools?
	# NOTE:  Can pass new_struct_dict if multiple XML files must be saved for a part/assembly step.
	def save(self, new_struct_dict=None, new_fname=None):  #save_xml(self, xml_tree):
		if new_struct_dict is None and not new_fname is None:
			print("ERROR IN SAVE():  Got a new struct dict, but not a corresponding filename!")

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
		# Now redundant
		#filedir, filename = self.get_filedir_filename(self.ID)
		#file = os.sep.join([filedir, filename])
		#if not os.path.exists(filedir):
		#	os.makedirs(filedir)

		# Generate XML tree:
		struct_dict = self.XML_STRUCT_DICT if new_struct_dict is None else new_struct_dict
		xml_tree = self.generate_xml(struct_dict)  #self.XML_STRUCT_DICT)

		# Save xml file:
		# Store in same directory as .json files, w/ same name:
		filedir, filename = self.get_filedir_filename()  # self.ID)  #This should be unnecessary...
		#filename = filename.replace('.json', '.xml')
		if not os.path.exists(filedir):
			os.makedirs(filedir)
		print("Saving XML file to ", filedir+'/'+filename)
		root = xml_tree.getroot()
		xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')  #tostring imported from xml.etree.ElementTree
		#xml_tree.write(open(filedir+'/'+filename), 'wb')  #.replace('.json', '.xml'), 'wb'))
		with open(filedir+'/'+filename, 'w') as f:
			f.write(xmlstr)





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

	# This is the same for all parts!  (For now)
	# Are there additional attrs to request...?
	XML_STRUCT_DICT = { "data":{"row":{
		"ID":"id_number",
		"SERIAL_NUMBER":"ID",
		"KIND_OF_PART_ID":"kind_of_part_id",  #TBD:  Property...BUT sensors will never be created from scratch, so can probably just ignore this!
		"KIND_OF_PART":"kind_of_part", #TBD:  Property
		"LOCATION_ID":"location_id", # same...
		"DESCRIPTION":"description",  # Can probably leave this blank...
	}}}


	# save() functions normally -- only 1 XML file is required.
	# load() requires downloading ability, but is otherwise normal.

	def load(self, ID, on_property_missing = "warn"):
		print("LOADING PART")
		if ID == -1:
			self.clear()
			return False

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not str(ID) in data.keys():
				print("PART NOT FOUND.  REQUESTING FROM DB...")
				search_conditions = {'SERIAL_NUMBER':'\''+ID+'\''}  # Only condition needed; ID must be surrounded by quotes
				# For each XML file/table needed, make a request:
				# Should automatically determine where file should be saved AND add part to list
				self.ID = ID
				part_request = self.request_XML(self.PART_TABLE, search_conditions)
				print("request_XML completed")
				if not part_request:
					print("Part not found.  Returning false...")
					self.clear()
					return False
				#self.add_part_to_list()  # done in request_xml; also takes care of filename.
				#dcreated = time.localtime()
				#dt = '{}-{}-{}'.format(dcreated.tm_mon, dcreated.tm_mday, dcreated.tm_year)
			else:
				dt = data[ID]  # date created

		filedir, filename = self.get_filedir_filename(ID)  #, date=dt)
		xml_file = os.sep.join([filedir, filename])

		if not os.path.exists(xml_file):
			print("ERROR:  Step is present in partlistfile OR downloaded, but XML file {} does not exist!".format(xml_file))
			self.clear()
			return False

		xml_tree = parse(xml_file)
		self._load_from_dict(self.XML_STRUCT_DICT, xml_tree)

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
		print("TEMP:  Using sql command")
		print(sql_request)

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
			print("TEMP:  XML string is")
			print(xml_string)
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

		print("TEST:  found date", date)
		filedir, filename = self.get_filedir_filename(ID, date)

		if suffix:  filename = filename.replace('.xml', suffix+'.xml')

		if not os.path.exists(filedir):
			os.makedirs(filedir)
		print("WRITING TO FILE:", os.path.join(filedir, filename))
		with open(os.path.join(filedir, filename), 'w') as f:
			f.write(xml_string)

		self.add_part_to_list(date=date)

		return True



class fsobj_assembly(fsobj):
	# Vars storing names of tables to request XML files from
	ASSM_TABLE = None
	COND_TABLE = None
	# Also requires XML_STRUCT_DICT, XML_COND_DICT

	def save(self, new_struct_dict=None, new_fname=None):
		# Needs special treatment:  Must write to 2 files, not just one!
		# Ignoring new_struct_dict here...may not need it anymore.

		# CURRENT PLAN:  Use 2 DICTS, one for each file.  Write to the first normally; write to the second manually.

		if new_struct_dict is None and not new_fname is None:
			print("ERROR IN SAVE() (assembly):  Got a new struct dict, but not a corresponding filename!")

		super(fsobj, self).save(new_struct_dict=new_struct_dict, new_fname=new_fname)
		# This one handles self.XML_STRUCT_DICT...
		# ...now handle self.XML_COND_DICT:

		# Generate XML tree:
		struct_dict = self.XML_COND_DICT
		xml_tree = self.generate_xml(struct_dict)  #self.XML_STRUCT_DICT)
		# NOTE:  Attrs missing from the assembly object will just be set to str(None) in the XML file

		# Save xml file:
		# Store in same directory as .json files, w/ same name:
		filedir, filename = self.get_filedir_filename()  # self.ID)  #This should be unnecessary...
		fname_cond = filename.replace('.xml', '_cond.xml')
		if not os.path.exists(filedir):
			print("WEIRD ERROR: filedir {} for cond file does not exist after calling super().save()!".format(filedir))
			os.makedirs(filedir)
		print("Saving XML file to ", filedir+'/'+filename)
		root = xml_tree.getroot()
		xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')  #tostring imported from xml.etree.ElementTree
		#xml_tree.write(open(filedir+'/'+filename), 'wb')  #.replace('.json', '.xml'), 'wb'))
		with open(filedir+'/'+filename, 'w') as f:
			f.write(xmlstr)



	def load(self, ID, on_property_missing = "warn"):
		if ID == -1:
			self.clear()
			return False

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not str(ID) in data.keys():
				print("ASSEMBLY STEP NOT FOUND.  REQUESTED CONDITION TABLES:")
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
			else:
				dt = data[ID]  # date created


		filedir, filename = self.get_filedir_filename(ID, date=dt)
		condname = filename.replace('.xml', '_cond.xml')
		xml_file      = os.sep.join([filedir, filename])
		xml_file_cond = os.sep.join([filedir, condname])

		if not os.path.exists(xml_file):
			print("ERROR:  Step is present in partlistfile OR downloaded, but XML file {} does not exist!".format(xml_file))
			self.clear()
			return False

		xml_tree = parse(xml_file)
		self._load_from_dict(self.XML_STRUCT_DICT, xml_tree)

		# Don't want to call _load_from_dict on the cond file, so...
		# Load the desired vars manually.
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

		return True


	# NEW: Must save to correct location!
	def request_XML(self, table_name, search_conditions, suffix=None):
		# NOTE NOTE NOTE:  Must save file in correct location AND add_part_to_list!
		# suffix is added to the end of the filename (will be _cond)
		filedir, filename = self.get_filedir_filename(ID)
		condname = filename.replace('.xml', '_cond.xml')

		sql_template = 'select * from hgc_int2r.{} p'
		sql_request = sql_template.format(table_name)
		sql_request = sql_request + ' where'
		# search_conditions is a dict:  {param_name:param_value}
		for param, value in search_conditions.items():
			sql_request = sql_request + ' {}={}'.format(param, value)
		print("TEMP:  Using sql command")
		print(sql_request)

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
		"manufacturer", # name of company that manufactured this part
		"material",     # physical material
		"nomthickness", # nominal thickness
		"size",         # hexagon width, numerical. 6 or 8 (integers) for 6-inch or 8-inch
		"shape",        # 
		"chirality",    # 
		#"rotation",     # 

		# kapton number
		# REMOVED -- all kapton layers are currently double layers
		#"num_kaptons", # number of kaptons; 0/None for pcb baseplates, 0/None 1 or 2 for metal baseplates

		# baseplate qualification 
		"corner_heights",      # list of corner heights
		#"kapton_tape_applied", # only for metal baseplates (not pcb baseplates)
		                       # True if kapton tape has been applied
		"thickness",           # measure thickness of baseplate

		# kapton application (1)
		#"step_kapton", # ID of step_kapton that applied the kapton to it
		# REMOVED

		# kaptonized baseplate qualification (1)
		#"check_leakage",    # None if not checked yet; True if passed; False if failed
		#"check_surface",    # None if not checked yet; True if passed; False if failed
		"check_edges_firm", # None if not checked yet; True if passed; False if failed
		"check_glue_spill", # None if not checked yet; True if passed; False if failed
		#"kapton_flatness",  # flatness of kapton layer after curing

		# kapton application (2) - for double kapton baseplates
		# REMOVED -- see above
		#"step_kapton_2", # ID of the step_kapton that applied the second kapton

		# sensor application
		"step_sensor", # which step_sensor used it
		"protomodule", # what protomodule (ID) it's a part of; None if not part of any

		# Associations to other objects
		"module", # what module (ID) it's a part of; None if not part of any

		# NEW to match XML script
		"insertion_user", # may not need this...

		# NEW:  Data to be read from base XML file
		"id_number",
		"kind_of_part_id",
		"kind_of_part",
		"location_id",
		"description",
	]

	DEFAULTS = {
		"shipments":[],
		"size":     '8', # This should not be changed!
	}

	#NEW:  List of vars that are manually given to the XML file via Akshay's script and 
	#      should not be saved automatically by the loop over PROPERTIES
	PROPERTIES_SAVED_MANUALLY = [
		"identifier",
		"comments",
		"insertion_user",
	]


	def ready_step_sensor(self, step_sensor = None, max_flatness = None):
		if step_sensor == self.step_sensor:
			return True, "already part associated with this sensor step"
	
		#if self.num_sensors == 0:  #num_sensors doesn't exist...so just ignore this?
		#	return False, "no sensors found"

		checks = [
			self.check_edges_firm == "pass",
			self.check_glue_spill == "pass",
			]
		if self.kapton_flatness is None:
			print("No kapton flatness")  #Currently not set...
			checks.append(False)
		elif not (max_flatness is None):
			if self.kapton_flatness < max_flatness:  print("kapton flat")
			else:  print("kapton not flat")
			checks.append(self.kapton_flatness < max_flatness)
		if not self.thickness:
			print("thickness false")
			checks.append(False)
		if self.flatness is None:  #This one seems a little iffy...
			print("flatness is none")
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
		#"serial",
		"barcode",
		#"manufacturer", # REMOVED; apparently this is all the same?
		"type",         # NEW:  This is now chosen from a drop-down menu
		"size",         # 
		"channels",     # 
		"shape",        # 
		#"rotation",     # 

		# sensor qualification
		"inspection", # None if not inspected yet; True if passed; False if failed

		# sensor step
		"step_sensor", # which step_sensor placed this sensor
		"protomodule", # which protomodule this sensor is a part of
		#NEW, WIP
		#"semi_type",   #semiconductor type--either P or N

		# NOTE:  kapton step has been moved to sensor!
		"step_kapton",
		"kapton_flatness",
		"check_edges_firm",
		"check_glue_spill",
		"thickness",
		"corner_heights",

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

	@property
	def flatness(self):
		# BASEPLATE flatness, not kapton flatness!
		if self.corner_heights is None:
			return None
		else:
			if None in self.corner_heights:
				return None
			else:
				return max(self.corner_heights) - min(self.corner_heights)


	# NEWLY MOVED FROM BASEPLATE!!!
	def ready_step_kapton(self, step_kapton = None, max_flatness = None, max_kapton_flatness = None):
		if step_kapton == self.step_kapton:
			return True, "already part associated with this kapton step"

		if not (self.step_sensor is None):
			return False, "already part of a protomodule (has a sensor step)"

		if not self.step_kapton is None:
			# step_kapton has already been assigned, and it isn't the one that's currently being added!
			return False, "baseplate already has an assigned kapton step!"
		
		# Kapton qualification checks:
		errstr = ""
		checks = [
			self.check_edges_firm == "pass",
			self.check_glue_spill == "pass",
			self.kapton_flatness  != None,
		]
		if self.kapton_flatness is None:
			errstr+=" kapton flatness doesn't exist."
			checks.append(False)
		elif not (max_kapton_flatness is None) and (self.kapton_flatness > max_kapton_flatness):
			errstr.append(" kapton flatness {} exceeds max of {}.".format(self.kapton_flatness, max_kapton_flatness))
			checks.append(False)

		# Baseplate qualification+preparation checks:
		#if not self.kapton_tape_applied:
		#	errstr+=" kapton tape not applied."
		#	checks.append(False)
		if not self.thickness:
			errstr+=" thickness doesn't exist."
			checks.append(False)
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

	def save(self):  #NEW for XML generation
		
		# FIRST:  If not all necessary vars are defined, don't save the XML file.
		required_vars = [self.size, self.comments, self.location, self.institution]
		#contents = vars(self)
		for vr in required_vars:
			if vr is None:
				# If any undef var found, save the json file only and return
				print("NOTE:  missing required data, baseplate XML not saved.")
				super(sensor, self).save()
				return

		# TAKE 2:  This time, use gen_xml(input_dict) to streamline things.
		name_dict = {
			'NAME':  'HGC Silicon Sensor Type',
			'VALUE': '200DD',
		}
		attr_dict = {
			'ATTRIBUTE': name_dict,
		}
		part_dict = {
			'KIND_OF_PART':          'HPK {} Inch {} Cell Silicon Sensor'.format('Six' if self.size=='6'
																				else 'Eight', self.channels),
			'RECORD_INSERTION_USER': self.insertion_user,   # NOTE:  This may have to be redone when XML uploading is implemented!
			'SERIAL_NUMBER':         self.ID,
			'COMMENT_DESCRIPTION':   self.comments,   # Note:  Requires special treatment
			'LOCATION':              self.location,
			'MANUFACTURER':          "DUMMY_MANUFACTURER", #self.manufacturer,
			'PREDEFINED_ATTRIBUTES': attr_dict,
		}
		parts_dict = {
			'PART': part_dict,
		}
		root_dict = {
			'PARTS': parts_dict,
		}

		# CREATE XML FILE OBJECT:
		xml_tree = self.generate_xml(root_dict)

		# Save json (order fixed):
		super(sensor, self).save()

		# Save:
		self.save_xml(xml_tree)
		


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
		"chirality",    # 


		# pcb qualification
		"daq",        # name of dataset
		"daq_ok",     # None if no DAQ yet; True if DAQ is good; False if it's bad
		"inspection", # Check for exposed gold on backside. None if not inspected yet; True if passed; False if failed
		"thickness",  # 
		"flatness",   # 
		
		# pcb step
		"step_pcb", # which step_pcb placed this pcb
		"module",   # which module this pcb is a part of

		# Associations to datasets
		"daq_data", # list of all DAQ datasets

		# NEW:  Data to be read from base XML file
		"id_number",
		"kind_of_part_id",
		"kind_of_part",
		"location_id",
		"description",
	]

	PROPERTIES_DO_NOT_SAVE = [
		"daq_data",
	]

	DEFAULTS = {
		"shipments":[],
		"daq_data":[],
		"size":     '8',
	}

	DAQ_DATADIR = 'daq'

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

	def load(self,ID):
		success = super(pcb,self).load(ID)
		if success:
			self.fetch_datasets()
		return success


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


	def load_daq(self,which):
		if isinstance(which, int):
			which = self.daq_data[which]

		filedir, filename = self.get_filedir_filename()
		file = os.sep.join([filedir, self.DAQ_DATADIR, which])

		print('load {}'.format(file))



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
		"chirality",   # from baseplate
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
		"check_cracks",       # None if not yet checked; True if passed; False if failed
		"check_glue_spill",   # None if not yet checked; True if passed; False if failed

		# pcb step
		"step_pcb", # ID of pcb step
		"module",   # ID of module

		# NEW:  Data to be read from base XML file
		"id_number",
		"kind_of_part_id",
		"kind_of_part",
		"location_id",
		"description",
	]

	DEFAULTS = {
		"shipments":[],
		"size":     '8',
	}


# NOTE:  Does not currently have a XML file!  Akshay's script just generated the assembly/condition file.


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
		"chirality",   # from protomodule or pcb (identical)
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
		"check_glue_spill",        # None if not yet checked; True if passed; False if failed
		#"check_glue_edge_contact", # None if not yet checked; True if passed; False if failed
		#"unbonded_daq",      # name of dataset
		#"unbonded_daq_user", # who performed test
		#"unbonded_daq_ok",   # whether the output passes muster

		# wirebonding
		# NEW: NOTE:  This info is filled out using the wirebonding page exclusively!
		"wirebonding_comments",  # Comments from wirebonding page only

		# back wirebonding
		"wirebonding_back",                # has wirebonding been done
		"wirebonding_unbonded_channels_back", # list of sites that were not wirebonded
		"wirebonding_user_back",           # who performed wirebonding
		"wirebonds_inspected_back",     # whether inspection has happened
		"wirebonds_damaged_back",       # list of damaged bonds found during inspection
		"wirebonds_repaired_back",      # have wirebonds been repaired
		"wirebonds_repaired_list_back", # list of wirebonds succesfully repaired
		"wirebonds_repaired_user_back", # who repaired bonds


		# front wirebonding
		"wirebonding_front",                # has wirebonding been done
		"wirebonding_skip_channels_front",  # list of channels to ignore
		"wirebonding_unbonded_channels_front", # list of sites that were not wirebonded
		"wirebonding_user_front",           # who performed wirebonding
		"wirebonds_inspected_front",     # whether inspection has happened
		"wirebonds_damaged_front",       # list of damaged bonds found during inspection
		"wirebonds_repaired_front",      # have wirebonds been repaired
		"wirebonds_repaired_list_front", # list of wirebonds succesfully repaired
		"wirebonds_repaired_user_front", # who repaired bonds

		"wirebonding_shield",
		"wirebonding_guard",


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

		# test bonds
		"test_bonds",             # is this a module for which test bonds will be done?
		"test_bonds_pulled",      # have test bonds been pulled
		"test_bonds_pulled_user", # who pulled test bonds
		"test_bonds_pulled_ok",   # is result of test bond pulling ok
		#"test_bonds_rebonded",      # have test bonds been rebonded
		#"test_bonds_rebonded_user", # who rebonded test bonds
		#"test_bonds_rebonded_ok",   # is result of rebonding test bonds ok


		# wirebonding qualification
		"wirebonding_final_inspection",
		"wirebonding_final_inspection_user",
		"wirebonding_final_inspection_ok",


		# module qualification (final)
		"hv_cables_attached",      # have HV cables been attached
		"hv_cables_attached_user", # who attached HV cables
		"unbiased_daq",      # name of dataset
		"unbiased_daq_user", # who took dataset
		"unbiased_daq_ok",   # whether result is ok
		"iv",      # name of dataset
		"iv_user", # who took dataset
		"iv_ok",   # whether result is ok
		"biased_daq",         # name of dataset
		"biased_daq_voltage", # voltage at which data was taken
		"biased_daq_ok",      # whether result is ok

		# datasets
		"iv_data",  #
		"daq_data", #

		# NEW:  Data to be read from base XML file
		"id_number",
		"kind_of_part_id",
		"kind_of_part",
		"location_id",
		"description",
	]
	
	PROPERTIES_DO_NOT_SAVE = [
		"iv_data",
		"daq_data",
	]

	DEFAULTS = {
		"shipments":[],
		'wirebonding_comments':[],
		'iv_data':[],
		'daq_data':[],
		"size":    '8',
	}

	IV_DATADIR      = 'iv'
	IV_BINS_DATADIR = 'bins'
	DAQ_DATADIR     = 'daq'

	BA_FILENAME = 'ba {which}'
	BD_FILENAME = 'bd {which}'

	def fetch_datasets(self):
		if self.ID is None:
			err = "no module loaded; cannot fetch datasets"
			raise ValueError(err)

		filedir, filename = self.get_filedir_filename(self.ID)
		iv_datadir  = os.sep.join([filedir, self.IV_DATADIR])
		daq_datadir = os.sep.join([filedir, self.DAQ_DATADIR])
		if os.path.exists(iv_datadir):
			self.iv_data  = [_ for _ in os.listdir(iv_datadir ) if os.path.isfile(os.sep.join([iv_datadir ,_]))]
		else:
			self.iv_datadir = []
		if os.path.exists(daq_datadir):
			self.daq_data = [_ for _ in os.listdir(daq_datadir) if os.path.isfile(os.sep.join([daq_datadir,_]))]
		else:
			self.daq_data = []


	def save(self):
		super(module, self).save()
		filedir, filename = self.get_filedir_filename(self.ID)
		if not os.path.exists(os.sep.join([filedir, self.IV_DATADIR, self.IV_BINS_DATADIR])):
			os.makedirs(os.sep.join([filedir, self.IV_DATADIR, self.IV_BINS_DATADIR]))
		if not os.path.exists(os.sep.join([filedir, self.DAQ_DATADIR])):
			os.makedirs(os.sep.join([filedir, self.DAQ_DATADIR]))
		self.fetch_datasets()

	def load_iv(self, which):
		if isinstance(which, int):
			which = self.iv_data[which]
		filedir, filename = self.get_filedir_filename(self.ID)
		file = os.sep.join([filedir, self.IV_DATADIR, which])
		
		if os.path.exists(file):
			return numpy.loadtxt(file)
		else:
			return None

	def load_iv_bins(self, which, direction='ad'):
		if isinstance(which, int):
			which = self.iv_data[which]

		load_a = 'a' in direction
		load_d = 'd' in direction

		if (not load_a) and (not load_d):
			err = 'must load at least one of ascending ("a") or descending ("d"), or both ("ad", default). Given {}'.format(direction)
			raise ValueError(err)

		filedir, filename = self.get_filedir_filename(self.ID)
		iv_bins_datadir = os.sep.join([filedir, self.IV_DATADIR, self.IV_BINS_DATADIR])

		file_a = os.sep.join([iv_bins_datadir, self.BA_FILENAME.format(which=which)])
		file_d = os.sep.join([iv_bins_datadir, self.BD_FILENAME.format(which=which)])

		if not (os.path.exists(file_a) and os.path.exists(file_d)):
			self.make_iv_bins(which)

		to_return = []

		if load_a:
			data_a = numpy.loadtxt(file_a)
			to_return.append(data_a)
			
		if load_d:
			data_d = numpy.loadtxt(file_d)
			to_return.append(data_d)

		return to_return

	def load_daq(self, which):
		if isinstance(which, int):
			which = self.daq_data[which]

		filedir, filename = self.get_filedir_filename(self.ID)
		file = os.sep.join([filedir, self.DAQ_DATADIR, which])
		print('load {}'.format(file))

	def make_iv_bins(self, which, force=False):
		"""Creates bins for specified dataset. Won't overwrite unless force = True"""
		# call automatically when loading bins if bins don't exist yet
		# add kwarg to load_iv_bins to override this and force creation of bins from raw iv data
		if isinstance(which, int):
			which = self.iv_data[which]
		
		raw_data = self.load_iv(which)

		asc_bins  = []
		desc_bins = []

		first_bin    = None
		last_bin     = None
		this_bin     = []
		this_voltage = raw_data[0,1]
		this_bin_asc = None
		for data_point in raw_data:
			if data_point[1] == this_voltage:
				this_bin.append(data_point)
			else:
				if first_bin is None:
					first_bin = this_bin
				else:
					if this_bin_asc:
						asc_bins.append(this_bin)
					else:
						desc_bins.append(this_bin)

				if data_point[1] > this_voltage:
					this_bin_asc = True
				else:
					this_bin_asc = False

				this_voltage = data_point[1]
				this_bin     = [data_point]

		fb_raw = numpy.array(first_bin)
		lb_raw = numpy.array(this_bin)
		ab_raw = [numpy.array(_) for _ in asc_bins]
		db_raw = [numpy.array(_) for _ in desc_bins]

		fb_mean = fb_raw[0:].mean(0)
		lb_mean = lb_raw[0:].mean(0)
		ab_mean = numpy.array([_[0:].mean(0) for _ in ab_raw])
		db_mean = numpy.array([_[0:].mean(0) for _ in db_raw])

		filedir, filename = self.get_filedir_filename(self.ID)

		ba_filename = os.sep.join([filedir, self.IV_DATADIR, self.IV_BINS_DATADIR, self.BA_FILENAME]).format(which=which)
		bd_filename = os.sep.join([filedir, self.IV_DATADIR, self.IV_BINS_DATADIR, self.BD_FILENAME]).format(which=which)

		numpy.savetxt(ba_filename, ab_mean)
		numpy.savetxt(bd_filename, db_mean)




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
		#'date_performed', # date step was performed
		'institution',
		'location', # New--instituition where step was performed

		'run_start',  # New--unix time @ start of run
		#'run_stop',  # New--unix time @ end of run

		# Note:  Semiconductors types are stored in the sensor objects

		#'cure_start',       # unix time @ start of curing
		#'cure_stop',        # unix time @ end of curing
		'cure_temperature', # Average temperature during curing (centigrade)
		'cure_humidity',    # Average humidity during curing (percent)

		'tools',        # list of pickup (sensor) tool IDs, ordered by pickup tool location
		'sensors',      # list of sensor      IDs, ordered by component tray position
		'baseplates',   # list of baseplate   IDs, ordered by assembly tray position
		'protomodules', # list of protomodule IDs assigned to new protomodules, by assembly tray location

		'tray_component_sensor', # ID of component tray used
		'tray_assembly',         # ID of assembly  tray used
		'batch_araldite',        # ID of araldite batch used
		'batch_loctite',         # ID of loctite  batch used

		# TEMP:
		'kind_of_part_id',
		'kind_of_part',
	]


	"""@property
	def cure_duration(self):
		if (self.cure_stop is None) or (self.cure_start is None):
			return None
		else:
			return self.cure_stop - self.cure_start
	"""
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

	# WIP
	@property
	def kind_of_part_id(self):
		# TODO:
		# Load created protomodule and return the type!  Will require a protomodule property.
		return str(self.kind_of_part_id)

	@kind_of_part_id.setter
	def kind_of_part_id(self, value):
		print("PROPERTY SETTER:  Setting kind of part ID")
		# TODO:  Set part geometry/etc in accordance w/ input value
		self.kind_of_part_id = str(value)

	#@property
	#def kind_of_part(self):
	#	return ''

	@property
	def assembly_tray_name(self):
		return 

	@assembly_tray_name.setter(self):
		pass

	@property
	def baseplate_serial(self):
		pass

	@property
	def assembly_row(self):
		pass

	@property
	def assembly_col(self):
		pass

	@property
	def comp_tray_name(self):
		pass

	@property
	def sensor_tool_name(self):
		pass


	# FOR NEW ASSEMBLY CLASS:
	ASSM_TABLE = 'c4220'
	COND_TABLE = 'c4260'

	# Vars for tables - constants
	COND_ID = 4220
	COND_NAME = 'HGC Six Inch Proto Module Assembly'
	TEMP = None
	KIND_ID = 4200
	GLUE_TYPE = 'Araldite'
	SLVR_EPXY_TYPE = 'Locetite Ablestik'

	XML_STRUCT_DICT = {'data':{'row':{  # WIP
		# Leave out ID--should be assigned by DB loader! (?)
		'KIND_OF_CONDITION_ID':	'COND_ID',  # PROPERTY:  from protomod type
		'KIND_OF_CONDITION':	'COND_NAME',  # SAME
		'CONDITION_DATA_SET_ID':'temp_property',  # TBD
		'KIND_OF_PART_ID':		'kind_of_part_id',  # PROPERRY:  from protomod
		'KIND_OF_PART':			'kind_of_part',  # PROPERTY:  from protmod
		#'PART_ID':				'protomodule',  # PROPERTY...but this gets set in the DB??
		'PART_SERIAL_NUMBER':	'protomodule_id',  # from protomod
		'ASMBL_TRAY_NAME':		'assembly_tray_name',
		'PLT_SER_NUM':			'baseplate_serial',
		'PLT_ASM_ROW':			'assembly_row',
		'PLT_ASM_COL':			'assembly_col',
		'PLT_FLTNES_MM':		'baseplate_flatness',
		'PLT_THKNES_MM':		'baseplate_thickness',
		'COMP_TRAY_NAME':		'comp_tray_name',
		'SNSR_SER_NUM':			'sensor_serial',
		'SNSR_CMP_ROW':			'assembly_row',  # These should always be the same as above...right?
		'SNSR_CMP_COL':			'assembly_col',
		'SNSR_X_OFFST':			'temp_property',  # Not sure if this is necessary...
		'SNSR_Y_OFFST':			'temp_property',
		'SNSR_ANG_OFFST':		'temp_property',
		'SNSR_TOOL_NAME':		'sensor_tool_name',
		'SNSR_TOOL_HT_SET':		'temp_property',  # Necessary??
		'SNSR_TOOL_HT_CHK':		'temp_property',
		'GLUE_TYPE':			'GLUE_TYPE',
		'GLUE_BATCH_NUM':		'batch_araldite',
		'SLVR_EPXY_TYPE':		'SLVR_EPXY_TYPE',
		'SLVR_EPXY_BATCH_NUM':	'batch_loctite',
	}}}

	# NOTE:  This may be wrong!  Got it from the schema online...
	XML_COND_DICT = {'data':{'row':{  # WIP
		'':'',
	}}}




		type_dict = {
						'EXTENSION_TABLE_NAME':'HGC_PRTO_MOD_ASMBLY',
						'NAME':'HGC {} Inch Proto Module Assembly'.format('Six' if baseplate_.size==6 else 'Eight'),
					}
		run_dict =  {
						'RUN_TYPE':'HGC {}inch Proto Module Assembly'.format(baseplate_.size),
						'RUN_NUMBER':str(self.ID),
						'RUN_BEGIN_TIMESTAMP':self.run_start_xml,
						'RUN_END_TIMESTAMP':"PLACEHOLDER", #self.run_stop,
						'INITIATED_BY_USER':self.user_performed,
						'LOCATION':"{}, {}".format(self.institution, self.location),
						'COMMENT_DESCRIPTION':'Build {}inch proto modules'.format(baseplate_.size),
					}
		header_dict = {
						'TYPE':type_dict,
						'RUN':run_dict,
					}
		root_dict['HEADER'] = header_dict

		# COND file:
		root_cond = Element('ROOT')
		root_cond.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
		type_dict_cond = {
						'EXTENSION_TABLE_NAME':'HGC_PRTO_MOD_ASMBLY_COND',
						'NAME':'HGC {} Inch Proto Module Curing Cond'.format('Six' if baseplate_.size==6 else 'Eight'),
					}
		run_dict_cond = {
						'RUN_NAME':'HGC {}inch Proto Module Assembly'.format(baseplate_.size),
						#'RUN_NUMBER':self.ID,
						'RUN_BEGIN_TIMESTAMP':self.run_start,  #WIP (add to GUI)
						'RUN_END_TIMESTAMP':"PLACEHOLDER",  #self.run_stop,  #WIP
						'INITIATED_BY_USER':self.user_performed,
						'LOCATION':self.location,  #WIP (add to GUI)
						'COMMENT_DESCRIPTION':'Build {}inch proto modules'.format(baseplate_.size),
					}
		header_dict_cond = {
						'TYPE':type_dict,
						'RUN':run_dict,
					  }
		root_dict_cond['HEADER'] = header_dict_cond

					data_dict = {
								# WIP:
								'ASMBL_TRAY_NAME':'{}_ASMBLY_TRAY_{}'.format(asmbl_tray.location, asmbl_tray.ID),
								# Reminder:  PLT==baseplate
								'PLT_SER_NUM':'{}'.format(inst_baseplate.ID),
								'PLT_ASM_ROW':str((i // 3) + 1),
								'PLT_ASM_COL':str((i % 2) + 1),
								# NOTE:  Make sure .flatness() works
								'PLT_FLTNES_MM':str(inst_baseplate.flatness),
								'PLT_THKNES_MM':str(inst_baseplate.thickness),
								# ADD location to:
								'COMP_TRAY_NAME':'{}_COMP_TRAY_{}'.format(comp_tray.institution, comp_tray.ID),
								'SNSR_SER_NUM':str(snsr.ID),
								'SNSR_CMP_ROW':str((i // 3) + 1),
								'SNSR_CMP_COL':str((i % 2) + 1),   #Should == PLT_ASM_ROW, etc above
								
								# NOTE:  I assume these are measured during the placement step, not taken from view_sensor.ui.  Need to check.
								'SNSR_X_OFFST':str(inst_protomodule.offset_translation_x),  #NOTE:  WIP
								'SNSR_Y_OFFST':str(inst_protomodule.offset_translation_y),  #NOTE:  WIP
								'SNSR_ANG_OFFSET':str(snsr.offset_rotation),  #NOTE:  WIP
								'SNSR_TOOL_NAME':'{}_PCKUP_TOOL_{}'.format(snsr_tool.location, snsr_tool.ID),
								'SNSR_TOOL_HT_SET':'TEMP',  #NOTE:  Also WIP
								'SNSR_TOOL_HT_CHK':'TEMP',
								
								# Need to test QDate.year--should work if type(date_received)==QDate
								'GLUE_TYPE':'Araldite',   # {}".format(glue_batch.date_received[0]),
								'GLUE_BATCH_NUM':'Batch_{:03d}'.format(self.batch_araldite),
								'SLVR_EPXY_TYPE':'Loctite Ablestik',
								'SLVR_EXPY_BATCH_NUM':'Batch_{:03d}'.format(self.batch_loctite),
							}
					part_dict = {
								'KIND_OF_PART':'HGC {} Inch Silicon Proto Module'.format('Six' if snsr.size==6 else 'Eight'),
								'SERIAL_NUMBER':'{}_HGC_TST_PRTMOD_{}'.format(self.location, self.ID),
							}
					dataset_dict = {
								'COMMENT_DESCRIPTION':'{}_HGC_TST_PRTMOD_{} Assembly'.format(self.institution, self.ID),
								'VERSION':'1',  # Assumed
								'PART':part_dict,
								'DATA':data_dict,
							}




	# WIP

	def save(self):
		# Perform ordinary json save
		super(step_sensor, self).save()
		inst_baseplate   = baseplate()
		inst_sensor      = sensor()
		inst_protomodule = protomodule()

		root_dict      = {}   # Will eventually contain 1 HEADER, and 1-6 DATA_SETs.
		root_dict_cond = {}  # Same
		# Update corresponding baseplates, sensors, etc.
		# ADDED:  Also save BuildProtoModules, BuldProtoModules_Cond XML files.
		# Create headers
		# New:  Dictionary-based approach.
		# Grab an arbitrary baseplate to get the size
		baseplate_ = baseplate()
		baseplate_.load(self.baseplates[0])


		type_dict = {
						'EXTENSION_TABLE_NAME':'HGC_PRTO_MOD_ASMBLY',
						'NAME':'HGC {} Inch Proto Module Assembly'.format('Six' if baseplate_.size==6 else 'Eight'),
					}
		run_dict =  {
						'RUN_TYPE':'HGC {}inch Proto Module Assembly'.format(baseplate_.size),
						'RUN_NUMBER':str(self.ID),
						'RUN_BEGIN_TIMESTAMP':self.run_start_xml,
						'RUN_END_TIMESTAMP':"PLACEHOLDER", #self.run_stop,
						'INITIATED_BY_USER':self.user_performed,
						'LOCATION':", ".format(self.institution, self.location),
						'COMMENT_DESCRIPTION':'Build {}inch proto modules'.format(baseplate_.size),
					}
		header_dict = {
						'TYPE':type_dict,
						'RUN':run_dict,
					}
		root_dict['HEADER'] = header_dict

		# COND file:
		root_cond = Element('ROOT')
		root_cond.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
		type_dict_cond = {
						'EXTENSION_TABLE_NAME':'HGC_PRTO_MOD_ASMBLY_COND',
						'NAME':'HGC {} Inch Proto Module Curing Cond'.format('Six' if baseplate_.size==6 else 'Eight'),
					}
		run_dict_cond = {
						'RUN_NAME':'HGC {}inch Proto Module Assembly'.format(baseplate_.size),
						#'RUN_NUMBER':self.ID,
						'RUN_BEGIN_TIMESTAMP':self.run_start,  #WIP (add to GUI)
						'RUN_END_TIMESTAMP':"PLACEHOLDER",  #self.run_stop,  #WIP
						'INITIATED_BY_USER':self.user_performed,
						'LOCATION':self.location,  #WIP (add to GUI)
						'COMMENT_DESCRIPTION':'Build {}inch proto modules'.format(baseplate_.size),
					}
		header_dict_cond = {
						'TYPE':type_dict,
						'RUN':run_dict,
					  }
		root_dict_cond['HEADER'] = header_dict_cond
		

		# BODY OF FILE:

		# Load tray info for later use
		asmbl_tray = tray_assembly()
		comp_tray  = tray_component_sensor()
		glue_batch = batch_araldite()
		#slvr_epxy  = batch_loctite()
		asmbl_tray.load(self.tray_assembly, self.institution)
		comp_tray.load(self.tray_component_sensor, self.institution)
		glue_batch.load(self.batch_araldite, self.institution)
		#slvr_epxy.load(self.batch_loctite)
		
		data_sets = []  # Store the dictionaries for each DATA_SET/protomodule
		data_sets_cond = []

		for i in range(6):

			baseplate_exists   = False if self.baseplates[i]   is None else inst_baseplate.load(  self.baseplates[i]  )
			sensor_exists      = False if self.sensors[i]      is None else inst_sensor.load(     self.sensors[i]     )
			protomodule_exists = False if self.protomodules[i] is None else inst_protomodule.load(self.protomodules[i])

			if baseplate_exists:
				inst_baseplate.step_sensor = self.ID
				inst_baseplate.protomodule = self.protomodules[i]
				inst_baseplate.save()

			else:
				if not (self.baseplates[i] is None):
					print("cannot write property to baseplate {}: does not exist".format(self.baseplates[i]))

			if sensor_exists:
				inst_sensor.step_sensor = self.ID
				inst_sensor.protomodule = self.protomodules[i]
				inst_sensor.save()
			else:
				if not (self.sensors[i] is None):
					print("cannot write property to sensor {}: does not exist".format(self.sensors[i]))

			if not (self.protomodules[i] is None):
				if not protomodule_exists:
					inst_protomodule.new(self.protomodules[i])
				inst_protomodule.channels    = inst_sensor.channels       if sensor_exists    else None
				inst_protomodule.size        = inst_baseplate.size        if baseplate_exists else None
				inst_protomodule.shape       = inst_baseplate.shape       if baseplate_exists else None
				inst_protomodule.chirality   = inst_baseplate.chirality   if baseplate_exists else None
				inst_protomodule.location    = MAC
				inst_protomodule.institution = inst_sensor.institution
				inst_protomodule.step_sensor = self.ID
				inst_protomodule.baseplate   = self.baseplates[i]
				inst_protomodule.sensor      = self.sensors[i]
				inst_protomodule.save()

				if not all([baseplate_exists,sensor_exists]):
					print("WARNING: trying to save step_sensor {}. Some parts do not exist. Could not create all associations.")
					print("baseplate:{} sensor:{}".format(inst_baseplate.ID,inst_sensor.ID))
				
				else:
					# ** NOTE/NEW: ** Create DATA_SET section of XML file.
					# Code is streamlined slightly:  Use a dictionary for every element w/ sub-elements.  Key:value is 'VAR_NAME':value...
					# ...unless value = multiple entries, in which case value = a dict.
					# Convert 1->1,1; 2->1,2; 3->2,1; etc.
					snsr = sensor()
					snsr.load(self.sensors[i])
					snsr_tool = tool_sensor()
					snsr_tool.load(self.tools[i], self.institution)

					
					data_dict = {
								# WIP:
								'ASMBL_TRAY_NAME':'{}_ASMBLY_TRAY_{}'.format(asmbl_tray.location, asmbl_tray.ID),
								# Reminder:  PLT==baseplate
								'PLT_SER_NUM':'{}'.format(inst_baseplate.ID),
								'PLT_ASM_ROW':str((i // 3) + 1),
								'PLT_ASM_COL':str((i % 2) + 1),
								# NOTE:  Make sure .flatness() works
								'PLT_FLTNES_MM':str(inst_baseplate.flatness),
								'PLT_THKNES_MM':str(inst_baseplate.thickness),
								# ADD location to:
								'COMP_TRAY_NAME':'{}_COMP_TRAY_{}'.format(comp_tray.institution, comp_tray.ID),
								'SNSR_SER_NUM':str(snsr.ID),
								'SNSR_CMP_ROW':str((i // 3) + 1),
								'SNSR_CMP_COL':str((i % 2) + 1),   #Should == PLT_ASM_ROW, etc above
								
								# NOTE:  I assume these are measured during the placement step, not taken from view_sensor.ui.  Need to check.
								'SNSR_X_OFFST':str(inst_protomodule.offset_translation_x),  #NOTE:  WIP
								'SNSR_Y_OFFST':str(inst_protomodule.offset_translation_y),  #NOTE:  WIP
								'SNSR_ANG_OFFSET':str(snsr.offset_rotation),  #NOTE:  WIP
								'SNSR_TOOL_NAME':'{}_PCKUP_TOOL_{}'.format(snsr_tool.location, snsr_tool.ID),
								'SNSR_TOOL_HT_SET':'TEMP',  #NOTE:  Also WIP
								'SNSR_TOOL_HT_CHK':'TEMP',
								
								# Need to test QDate.year--should work if type(date_received)==QDate
								'GLUE_TYPE':'Araldite',   # {}".format(glue_batch.date_received[0]),
								'GLUE_BATCH_NUM':'Batch_{:03d}'.format(self.batch_araldite),
								'SLVR_EPXY_TYPE':'Loctite Ablestik',
								'SLVR_EXPY_BATCH_NUM':'Batch_{:03d}'.format(self.batch_loctite),
							}
					part_dict = {
								'KIND_OF_PART':'HGC {} Inch Silicon Proto Module'.format('Six' if snsr.size==6 else 'Eight'),
								'SERIAL_NUMBER':'{}_HGC_TST_PRTMOD_{}'.format(self.location, self.ID),
							}
					dataset_dict = {
								'COMMENT_DESCRIPTION':'{}_HGC_TST_PRTMOD_{} Assembly'.format(self.institution, self.ID),
								'VERSION':'1',  # Assumed
								'PART':part_dict,
								'DATA':data_dict,
							}

					data_sets.append(dataset_dict)


					# COND file:
					
					data_dict_cond = {
								# WIP:
								'CURING_TIME_HRS':'',
								# NOTE:  Need to check the time/date format
								'TIME_START':str(self.run_start),
								'TIME_END':"PLACEHOLDER", #self.cure_stop,
								'TEMP_DEGC':str(self.cure_temperature),
								'HUMIDITY_PRCNT':str(self.cure_humidity),
								}
					part_dict_cond = {
								'KIND_OF_PART':'HGC {} Inch Silicon Proto Module'.format('Six' if snsr.size==6 else 'Eight'),
								'SERIAL_NUMBER':'{}_HGC_TST_PRTMOD_{}'.format(self.location, self.ID),
								}
					dataset_dict_cond = {
								'COMMENT_DESCRIPTION':'Proto Module PRTMOD_{:0<3} Assembly'.format(self.ID),
								'VERSION':'1',  # Assumed
								'PART':part_dict_cond,
								'DATA':data_dict_cond,
								}
					
					data_sets_cond.append(dataset_dict_cond)
					


			inst_baseplate.clear()
			inst_sensor.clear()
			inst_protomodule.clear()

		# SAVE output:

		#root_dict['DATA_SET'] = data_sets
		#root_dict_cond['DATA_SET'] = data_sets_cond

		#xml_tree      = self.generate_xml(root_dict)
		#xml_tree_cond = self.generate_xml(root_dict_cond)

		#self.save_xml(xml_tree)
		#self.save_xml(xml_tree_cond)



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
		#'run_stop',   # unix time @ start of run
		
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
	]

	"""
	@property
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
		super(step_pcb,self).save()
		
		inst_baseplate   = baseplate()
		inst_sensor      = sensor()
		inst_pcb         = pcb()
		inst_protomodule = protomodule()
		inst_module      = module()

		for i in range(6):

			pcb_exists         = False if (self.pcbs[i]         is None) else inst_pcb.load(         self.pcbs[i]         )
			protomodule_exists = False if (self.protomodules[i] is None) else inst_protomodule.load( self.protomodules[i] )
			module_exists      = False if (self.modules[i]      is None) else inst_module.load(      self.modules[i]      )

			if pcb_exists:
				inst_pcb.step_pcb = self.ID
				inst_pcb.module = self.modules[i]
				inst_pcb.save()

			if protomodule_exists:
				inst_protomodule.step_pcb = self.ID
				inst_protomodule.module = self.modules[i]
				inst_protomodule.save()

				baseplate_exists = False if (inst_protomodule.baseplate is None) else inst_baseplate.load(inst_protomodule.baseplate)
				sensor_exists    = False if (inst_protomodule.sensor    is None) else inst_sensor.load(   inst_protomodule.sensor   )

				if baseplate_exists:
					inst_baseplate.module = self.modules[i]
					inst_baseplate.save()

				if sensor_exists:
					inst_sensor.module = self.modules[i]
					inst_sensor.save()
			else:
				baseplate_exists = False
				sensor_exists    = False

			if not (self.modules[i] is None):
				if not module_exists:
					inst_module.new(self.modules[i])
				inst_module.baseplate   = inst_baseplate.ID   if baseplate_exists   else None
				inst_module.sensor      = inst_sensor.ID      if sensor_exists      else None
				inst_module.pcb         = inst_pcb.ID         if pcb_exists         else None
				inst_module.protomodule = inst_protomodule.ID if protomodule_exists else None
				inst_module.step_kapton   = inst_sensor.step_kapton    if sensor_exists      else None
				inst_module.step_sensor = inst_protomodule.step_sensor if protomodule_exists else None
				inst_module.step_pcb    = self.ID
				inst_module.channels    = inst_sensor.channels       if sensor_exists    else None
				inst_module.size        = inst_pcb.size              if pcb_exists       else None
				inst_module.shape       = inst_pcb.shape             if pcb_exists       else None
				inst_module.chirality   = inst_pcb.chirality         if pcb_exists       else None
				inst_module.location    = MAC
				inst_module.save()

				if not all([baseplate_exists, sensor_exists, pcb_exists, protomodule_exists]):
					print("WARNING: trying to save step_pcb {}. Some parts do not exist. Could not create all associations.".format(self.ID))
					print("baseplate:{} sensor:{} pcb:{} protomodule:{} module:{}".format(inst_baseplate.ID,inst_sensor.ID,inst_pcb.ID,inst_protomodule.ID,inst_module.ID))




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


class batch_sylgard_thick(fsobj):
	OBJECTNAME = "sylgard (thick) batch"
	FILEDIR = os.sep.join(['supplies','batch_sylgard_thick','{date}'])
	FILENAME = 'batch_sylgard_thick_{ID:0>5}.xml'
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
