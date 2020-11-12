import os
import json
import numpy

#NEW for xml file generation:
from PyQt5 import QtCore
import datetime
import xml.etree.ElementTree as etree
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import parse
import csv

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
	partlistdir = os.sep.join([DATADIR, 'partlist'])
	if not os.path.exists(partlistdir):
		os.makedirs(partlistdir)

	# Class names MUST match actual class names or stuff will break
	# Note:  Only the first 6 are searchable at the moment; the rest are in case they're needed later.
	# (And because save() now calls add_part_to_list for all objects except tools)
	obj_list = ['baseplate', 'sensor', 'pcb', 'protomodule', 'module', 'shipment',
				'batch_araldite', 'batch_loctite', 'batch_sylgard_thick',
				'batch_sylgard_thin', 'batch_bond_wire',
				'step_kapton', 'step_sensor', 'step_pcb']
	for part in obj_list:
		fname = os.sep.join([partlistdir, part+'s.json'])
		if not os.path.exists(fname):
			with open(fname, 'w') as opfl:
				# Dump an empty list if nothing is found
				json.dump([], opfl)

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
		'baseplate':'HGC Six Inch Plate',  #COMPLICATION
	}


	def __init__(self):
		super(fsobj, self).__init__()
		self.clear() # sets attributes to None

	def __str__(self):
		return "<{} {}>".format(self.OBJECTNAME, self.ID)

	def get_filedir_filename(self, ID = None):
		if ID is None:
			ID = self.ID
		filedir  = os.sep.join([ DATADIR, self.FILEDIR.format(ID=ID, century = CENTURY.format(ID//100)) ])
		filename = self.FILENAME.format(ID=ID)
		return filedir, filename


	# NEW:  For search page
	def add_part_to_list(self):
		part_name = self.__class__.__name__
		partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		# If file does not exist, something has gone wrong
		with open(partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not self.ID in data:
				data.append(self.ID)
		with open(partlistfile, 'w') as opfl:
			json.dump(data, opfl)


	def save(self, objname = 'fsobj'):  #NOTE:  objname param is new
		filedir, filename = self.get_filedir_filename(self.ID)
		file = os.sep.join([filedir, filename])
		if not os.path.exists(filedir):
			os.makedirs(filedir)
		if not os.path.exists(file):
			self.add_part_to_list()

		with open(file, 'w') as opfl:
			if hasattr(self, 'PROPERTIES_DO_NOT_SAVE'):
				contents = vars(self)
				filtered_contents = {_:contents[_] for _ in contents.keys() if _ not in self.PROPERTIES_DO_NOT_SAVE}
				json.dump(filtered_contents, opfl, indent=4)
			else:
				json.dump(vars(self), opfl, indent=4)



	def load(self, ID, on_property_missing = "warn"):
		# NOTE:  May have to be redone for XML.

		if ID == -1:
			self.clear()
			return False

		filedir, filename = self.get_filedir_filename(ID)
		file = os.sep.join([filedir, filename])

		if not os.path.exists(file):
			self.clear()
			return False

		with open(file, 'r') as opfl:
			data = json.load(opfl)

		if not (data['ID'] == ID):
			err = "ID in data file ({}) does not match ID of filename ({})".format(data['ID'],ID)
			raise ValueError(err)

		self.ID = ID

		data_keys = data.keys()
		PROPERTIES = self.PROPERTIES + self.PROPERTIES_COMMON
		DEFAULTS = {**self.DEFAULTS_COMMON, **getattr(self, 'DEFAULTS', {})}

		props_in_data = [prop in data_keys for prop in PROPERTIES]
		if hasattr(self, "PROPERTIES_DO_NOT_SAVE"):
			props_in_pdns = [prop in self.PROPERTIES_DO_NOT_SAVE for prop in PROPERTIES]
		else:
			props_in_pdns = [False for prop in PROPERTIES]

		for i,prop in enumerate(PROPERTIES):
			prop_in_data = props_in_data[i]
			prop_in_pdns = props_in_pdns[i]

			if prop_in_data:

				if prop_in_pdns:
					err = "object {} with ID {} data file {} has property {}, which is in PROPERTIES_DO_NOT_SAVE".format(type(self).__name__, ID, file, prop)
					raise ValueError(err)

				else:
					setattr(self, prop, data[prop])

			else:
				prop_default = DEFAULTS[prop] if prop in DEFAULTS.keys() else None

				if prop_in_pdns:
					setattr(self, prop, prop_default)

				else:
					if on_property_missing == "warn":
						print("Warning: object {} with ID {} missing property {}. Setting to {}.".format(type(self).__name__, ID, prop, prop_default))
						setattr(self, prop, prop_default)
					elif on_property_missing == "error":
						err = "object {} with ID {} missing property {}".format(type(self).__name__, ID, prop)
						raise ValueError(err)
					elif on_property_missing == "no_warn":
						setattr(self, prop, prop_default)
					else:
						err = "object {} with ID {} missing property {}. on_property_missing is {}; should be 'warn', 'error', or 'no_warn'".format(type(self).__name__, ID, prop, on_property_missing)
						raise ValueError(err)

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
		# Reads a dictionary, and returns an XML element 'element_name' filled with the contents of that dictionary.
		# NOTE:  This must be able to work recursively.  I.e. if one of the objs in the input_dict is a dict,
		#    it reads *that* dictionary and creates an element for it, +appends it to current element.  Etc.

		parent = Element(element_name)
		
		for item_name, item in input_dict.items():
			if type(item) == dict:
				# Recursive case: Create an element from the child dictionary.
				child = self.dict_to_element(item, item_name)
				parent.append(child)
			elif type(item) == list:
				# Base case 1:  List of comments.  Create an element for each one.
				for comment in item:
					child = Element(item_name)
					child.text = comment
					parent.append(child)
			else:
				# Base case 2:
				child = Element(item_name)
				child.text = item
				parent.append(child)
				# Special case for PARTs:
				if item_name == 'PART':
					child.set('mode','auto')

		return parent


	# NEW--to avoid repetition
	# Must be implemented separately for tools, if those are eventually needed...
	def save_xml(self, xml_tree):
		# Save xml file:
		# Store in same directory as .json files, w/ same name:
		filedir, filename = self.get_filedir_filename(self.ID)
		filename = filename.replace('.json', '.xml')
		if not os.path.exists(filedir):
			os.makedirs(filedir)
		print("Saving XML file to ", filedir+'/'+filename)
		xml_tree.write(open(filedir+'/'+filename.replace('.json', '.xml'), 'wb'))






# NEW FOR TOOLING:
# These need to be treated separately because they're saved based on ID+institution and not just institution
# Mostly identical to fsobj, but with institution added as a primary key.


class fsobj_tool(fsobj):
	"""PROPERTIES_COMMON = {
		'institution',
	]

	DEFAULTS_COMMON = {
		'institution':None,
	}"""

	# NEW--used only for tooling parts.
	def get_filedir_filename(self, ID = None, institution = None):
		#if self.institution is None:
		#	print("ERROR:  Object needs a location before it can be saved!")
		#	return None, None
		if ID is None:
			ID = self.ID
		if institution is None:
			instiution = self.institution
		filedir  = os.sep.join([ DATADIR, self.FILEDIR.format(ID=ID, institution=institution, century = CENTURY.format(ID//100)) ])
		filename = self.FILENAME.format(ID=ID, institution=institution)
		return filedir, filename

	def save(self):

		#NOTE:  Tools require special treatment.
		#       IDs are NOT unique.  ID+location is unique.  Need to use this instead to name the file.
		filedir, filename = self.get_filedir_filename(self.ID, self.institution)
		file = os.sep.join([filedir, filename])
		if not os.path.exists(filedir):
			os.makedirs(filedir)

		with open(file, 'w') as opfl:
			if hasattr(self, 'PROPERTIES_DO_NOT_SAVE'):
				contents = vars(self)
				filtered_contents = {_:contents[_] for _ in contents.keys() if _ not in self.PROPERTIES_DO_NOT_SAVE}
				json.dump(filtered_contents, opfl, indent=4)
			else:
				json.dump(vars(self), opfl, indent=4)

	
	def load(self, ID, institution, on_property_missing = "warn"):
		# NOTE:  May have to be redone for XML.
		if ID == -1:
			self.clear()
			return False
		if institution == None:
			self.clear()
			return False

		# Main difference is here:
		filedir, filename = self.get_filedir_filename(ID, institution)
		file = os.sep.join([filedir, filename])

		if not os.path.exists(file):
			self.clear()
			return False

		with open(file, 'r') as opfl:
			data = json.load(opfl)

		if not (data['ID'] == ID):
			err = "ID in data file ({}) does not match ID of filename ({})".format(data['ID'],ID)
			raise ValueError(err)
		if not (data['institution'] == institution):
			err = "institution in data file ({}) does not match institution of filename ({})".format(data['institution'], institution)

		self.ID = ID
		self.institution = institution

		data_keys = data.keys()
		PROPERTIES = self.PROPERTIES + self.PROPERTIES_COMMON
		DEFAULTS = {**self.DEFAULTS_COMMON, **getattr(self, 'DEFAULTS', {})}

		props_in_data = [prop in data_keys for prop in PROPERTIES]
		if hasattr(self, "PROPERTIES_DO_NOT_SAVE"):
			props_in_pdns = [prop in self.PROPERTIES_DO_NOT_SAVE for prop in PROPERTIES]
		else:
			props_in_pdns = [False for prop in PROPERTIES]

		for i,prop in enumerate(PROPERTIES):
			prop_in_data = props_in_data[i]
			prop_in_pdns = props_in_pdns[i]

			if prop_in_data:

				if prop_in_pdns:
					err = "object {} with ID {} data file {} has property {}, which is in PROPERTIES_DO_NOT_SAVE".format(type(self).__name__, ID, file, prop)
					raise ValueError(err)

				else:
					setattr(self, prop, data[prop])

			else:
				prop_default = DEFAULTS[prop] if prop in DEFAULTS.keys() else None

				if prop_in_pdns:
					setattr(self, prop, prop_default)

				else:
					if on_property_missing == "warn":
						print("Warning: object {} with ID {} missing property {}. Setting to {}.".format(type(self).__name__, ID, prop, prop_default))
						setattr(self, prop, prop_default)
					elif on_property_missing == "error":
						err = "object {} with ID {} missing property {}".format(type(self).__name__, ID, prop)
						raise ValueError(err)
					elif on_property_missing == "no_warn":
						setattr(self, prop, prop_default)
					else:
						err = "object {} with ID {} missing property {}. on_property_missing is {}; should be 'warn', 'error', or 'no_warn'".format(type(self).__name__, ID, prop, on_property_missing)
						raise ValueError(err)

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



###############################################
##################  tooling  ##################
###############################################

class tool_sensor(fsobj_tool):
	OBJECTNAME = "sensor tool"
	FILEDIR = os.sep.join(['tooling','tool_sensor'])
	#FILENAME = 'tool_sensor_{ID:0>5}.json'
	FILENAME = 'tool_sensor_{institution}_{ID:0>5}.json'
	PROPERTIES = [
		#'size',
		'location',
	]

	# NOTE:  This and below objects must be saved with save_tooling(), not save().


class tool_pcb(fsobj_tool):
	OBJECTNAME = "PCB tool"
	FILEDIR = os.sep.join(['tooling','tool_pcb'])
	#FILENAME = 'tool_pcb_{ID:0>5}.json'
	FILENAME = 'tool_pcb_{institution}_{ID:0>5}.json'
	PROPERTIES = [
		#'size',  # Removed; everything should be 8 in
		'location',
	]


class tray_assembly(fsobj_tool):
	OBJECTNAME = "assembly tray"
	FILEDIR = os.sep.join(['tooling','tray_assembly'])
	#FILENAME = 'tray_assembly_{ID:0>5}.json'
	FILENAME = 'tray_assembly_{institution}_{ID:0>5}.json'
	PROPERTIES = [
		#'size',
		'location',
	]


class tray_component_sensor(fsobj_tool):
	OBJECTNAME = "sensor tray"
	FILEDIR = os.sep.join(['tooling','tray_component_sensor'])
	#FILENAME = 'tray_component_sensor_{ID:0>5}.json'
	FILENAME = 'tray_component_sensor_{institution}_{ID:0>5}.json'
	PROPERTIES = [
		#'size',
		'location',
	]


class tray_component_pcb(fsobj_tool):
	OBJECTNAME = "pcb tray"
	FILEDIR = os.sep.join(['tooling','tray_component_pcb'])
	#FILENAME = 'tray_component_pcb_{ID:0>5}.json'
	FILENAME = 'tray_component_pcb_{institution}_{ID:0>5}.json'
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

class baseplate(fsobj):
	OBJECTNAME = "baseplate"
	FILEDIR = os.sep.join(['baseplates','{century}'])
	FILENAME = "baseplate_{ID:0>5}.json"
	PROPERTIES = [
		# shipments and location
		"institution",
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# characteristics (defined upon reception)
		"serial",   # serial given by manufacturer or distributor.
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
		"step_kapton", # ID of step_kapton that applied the kapton to it

		# kaptonized baseplate qualification (1)
		#"check_leakage",    # None if not checked yet; True if passed; False if failed
		#"check_surface",    # None if not checked yet; True if passed; False if failed
		"check_edges_firm", # None if not checked yet; True if passed; False if failed
		"check_glue_spill", # None if not checked yet; True if passed; False if failed
		"kapton_flatness",  # flatness of kapton layer after curing

		# kapton application (2) - for double kapton baseplates
		# REMOVED -- see above
		#"step_kapton_2", # ID of the step_kapton that applied the second kapton

		# sensor application
		"step_sensor", # which step_sensor used it
		"protomodule", # what protomodule (ID) it's a part of; None if not part of any

		# Associations to other objects
		"module", # what module (ID) it's a part of; None if not part of any

		# NEW to match XML script
		"insertion_user",
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

	def ready_step_kapton(self, step_kapton = None, max_flatness = None, max_kapton_flatness = None):
		if step_kapton == self.step_kapton:
			return True, "already part associated with this kapton step"

		if not (self.step_sensor is None):
			return False, "already part of a protomodule (has a sensor step)"

		if not self.step_kapton is None:
			# step_kapton has already been assigned, and it isn't the one that's currently being added!
			return False, "baseplate already has an assigned kapton step!"
		
		if self.material == "PCB":
			return False, "baseplate is a PCB baseplate"

		# Kapton qualification checks:
		errstr = ""
		checks = [
			#self.check_leakage    == "pass",
			#self.check_surface    == "pass",
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
			return False, "baseplate qualification failed or incomplete. "+errstr
		else:
			return True, ""


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

	
	def save(self):  #NEW for XML generation
		
		# FIRST:  If not all necessary vars are defined, don't save the XML file.
		required_vars = [self.size, self.serial, self.comments, self.location, self.institution]
		#contents = vars(self)
		for vr in required_vars:
			if vr is None:
				# If any undef var found, save the json file only and return
				print("NOTE:  missing required data, baseplate XML not saved.")
				super(baseplate, self).save()
				print("Saved baseplate!")
				return

		# TAKE 2:  This time, use gen_xml(input_dict) to streamline things.
		# Match XML schema in  https://cmsdca.cern.ch/hgc_loader/hgc/int2r/doc/doc#type_part
		part_dict = {
			'PART_ID':               str(self.ID),
			'KIND_OF_PART':          'HGC {} Inch Kaptonized Plate'.format('Six' if self.size=='6' else 'Eight'),
			'MANUFACTURER':          self.manufacturer,
			'BARCODE':               'PLACEHOLDERVAL',
			'SERIAL_NUMBER':         self.serial,
			'VERSION':               self.material,   #THIS MAY BE WRONG
			'LOCATION':              self.location,
			'INSTITUTION':           self.institution,
			'RECORD_INSERTION_USER': self.insertion_user,
			'COMMENT_DESCRIPTION':   self.comments,
		}
		parts_dict = {
			'PART': part_dict,
		}
		root_dict = {
			'PARTS': parts_dict,
		}

		# CREATE XML FILE OBJECT:
		xml_tree = self.generate_xml(root_dict)

		# Save:
		self.save_xml(xml_tree)

		# Save old json file:
		super(baseplate, self).save()



class sensor(fsobj):
	OBJECTNAME = "sensor"
	FILEDIR = os.sep.join(['sensors','{century}'])
	FILENAME = "sensor_{ID:0>5}.json"
	PROPERTIES = [
		# shipments and location
		"institution",
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# characteristics (defined upon reception)
		"serial",   # 
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

		# associations to other objects
		"module", # which module this sensor is a part of

		# New to match Akshay's script
		"insertion_user",
	]

	DEFAULTS = {
		"shipments":[],
		"size":    '8',  # DO NOT MODIFY
	}

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
			'SERIAL_NUMBER':         self.serial,
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

		# Save:
		self.save_xml(xml_tree)
		
		# Save old json file:
		super(sensor, self).save()



class pcb(fsobj):
	OBJECTNAME = "PCB"
	FILEDIR = os.sep.join(['pcbs','{century}','pcb_{ID:0>5}'])
	FILENAME = "pcb_{ID:0>5}.json"
	PROPERTIES = [
		# shipments and location
		"institution",
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# details / measurements / characteristics
		"insertion_user",
		"serial",   # NEW
		"barcode",  # NEW
		"manufacturer", # 
		"type",         # 
		"size",         # 
		"channels",     # 
		"shape",        # 
		"chirality",    # 
		#"rotation",     # 

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
			'SERIAL_NUMBER':         self.serial,
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

		# Save:
		self.save_xml(xml_tree)
		
		# Save old json file:
		super(pcb, self).save()

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



class protomodule(fsobj):
	OBJECTNAME = "protomodule"
	FILEDIR = os.sep.join(['protomodules','{century}'])
	FILENAME = 'protomodule_{ID:0>5}.json'
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
		"step_kapton", # ID of kapton step (from baseplate)

		# protomodule qualification
		"offset_translation", # translational offset of placement
		"offset_rotation",    # rotation offset of placement
		"flatness",           # flatness of sensor surface after curing
		"check_cracks",       # None if not yet checked; True if passed; False if failed
		"check_glue_spill",   # None if not yet checked; True if passed; False if failed

		# pcb step
		"step_pcb", # ID of pcb step
		"module",   # ID of module
	]

	DEFAULTS = {
		"shipments":[],
		"size":     '8',
	}


# NOTE:  Does not currently have a XML file!  Akshay's script just generated the assembly/condition file.


class module(fsobj):
	OBJECTNAME = "module"
	FILEDIR    = os.sep.join(['modules','{century}','module_{ID:0>5}'])
	FILENAME   = 'module_{ID:0>5}.json'
	PROPERTIES = [
		# shipments and location
		"institution",
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# characteristics - taken from child parts upon creation of module
		"insertion_user",
		"thickness",   # sum of protomodule and sensor, plus glue gap
		#"num_kaptons", # from protomodule # Removed, no longer necessary
		"channels",    # from protomodule or pcb (identical)
		"size",        # from protomodule or pcb (identical)
		"shape",       # from protomodule or pcb (identical)
		"chirality",   # from protomodule or pcb (identical)
		#"rotation",    # from protomodule or pcb (identical)
		# initial location is also filled from child parts

		# components and steps - filled upon creation
		"baseplate",     # 
		"sensor",        # 
		"protomodule",   # 
		"pcb",           # 
		"step_kapton",   # 
		#"step_kapton_2", # Removed, no longer necessary
		"step_sensor",   # 
		"step_pcb",      # 

		# module qualification
		"check_glue_spill",        # None if not yet checked; True if passed; False if failed
		"check_glue_edge_contact", # None if not yet checked; True if passed; False if failed
		"unbonded_daq",      # name of dataset
		"unbonded_daq_user", # who performed test
		"unbonded_daq_ok",   # whether the output passes muster

		# wirebonding
		"wirebonding",                # has wirebonding been done
		"wirebonding_unbonded_sites", # list of sites that were not wirebonded
		"wirebonding_user",           # who performed wirebonding
		"test_bonds",             # is this a module for which test bonds will be done?
		"test_bonds_pulled",      # have test bonds been pulled
		"test_bonds_pulled_user", # who pulled test bonds
		"test_bonds_pulled_ok",   # is result of test bond pulling ok
		"test_bonds_rebonded",      # have test bonds been rebonded
		"test_bonds_rebonded_user", # who rebonded test bonds
		"test_bonds_rebonded_ok",   # is result of rebonding test bonds ok
		"wirebonds_inspected",     # whether inspection has happened
		"wirebonds_damaged",       # list of damaged bonds found during inspection
		"wirebonds_repaired",      # have wirebonds been repaired
		"wirebonds_repaired_list", # list of wirebonds succesfully repaired
		"wirebonds_repaired_user", # who repaired bonds

		# wirebonding qualification
		"wirebonding_final_inspection",
		"wirebonding_final_inspection_user",
		"wirebonding_final_inspection_ok",

		# encapsulation
		"encapsulation",             # has encapsulation been done
		"encapsulation_user",        # who performed encapsulation
		"encapsulation_cure_start", # (unix) time at start of encapsulation
		"encapsulation_cure_stop",  # (unix) time at end of encapsulation
		"encapsulation_inspection", # None if not yet inspected; True if pased; False if failed

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
	]
	
	PROPERTIES_DO_NOT_SAVE = [
		"iv_data",
		"daq_data",
	]

	DEFAULTS = {
		"shipments":[],
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
	"""  WIP
	def load(self, ID):
		root = Element('ROOT')
		tree = ElementTree(root)
		root.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
		header = Element('HEADER')
		root.append(header)
		typ = Element('TYPE')
		header.append(typ)
		ext = Element('EXTENSION_TABLE_NAME')
		typ.append(ext)
		ext.text = 'HGC_PRTO_MOD_ASMBLY'
		name = Element('NAME')
		name.text = 'HGC Six Inch Proto Module Assembly'
		typ.append(name)
		run = Element('RUN')
		header.append(run)
		run_name = Element('RUN_NAME')
		run_name.text = 'HGC 6inch Proto Module Assembly'
		run.append(run_name)
		run_begin = Element('RUN_BEGIN_TIMESTAMP')
		run_begin.text = 'time'
		run.append(run_begin)
		run_end = Element('RUN_END_TIMESTAMP')
		run_end.text = 'time'
		run.append(run_end)
		user = Element('INITIATED_BY_USER')
		user.text = self.my_name
		run.append(user)
		loc = Element('LOCATION')
		loc.text = self.modules[2]
		run.append(loc)
		comment = Element('COMMENT_DESCRIPTION')
		comment.text = 'Build 6inch proto modules'
		run.append(comment)
		dataset = Element('DATA_SET')
		root.append(dataset)
		comment2 = Element('COMMENT_DESCRIPTION')
		dataset.append(comment2)
		comment2.text = 'Proto-module' + str(self.modules[0]) + 'Assembly'
		version = Element('VERSION')
		dataset.append(version)
		version.text = '1'
		part = Element('PART')
		dataset.append(part)
		kop = Element('KIND_OF_PART')
		part.append(kop)
		kop.text = 'HGC Six Inch Silicon Proto Module'
		SN = Element('SERIAL_NUMBER')
		part.append(SN)
		SN.text = 'Proto-module' + str(self.modules[0])
		data = Element('DATA')
		dataset.append(data)
		data_fields = ['ASMBL_TRAY_NAME','PRTO_SER_NUM','PRTO_ASM_COL','PRTO_ASM_ROW','COMP_TRAY_NAME','PCB_SER_NUM','PCB_THKNES_MM',
						'PCB_CMP_ROW','PCB_CMP_COL','PCB_TOOL_NAME','PCB_TOOL_NAME','PCB_TOOL_HT_SET','PCB_TOOL_HT_CHK','GLUE_TYPE','GLUE_BATCH_NUM']                      
		data_text = ['UCSB_ASMBLY_TRAY_00','proto-module'+ self.modules[0],'1','1','UCSB_COMP_TRAY_00','pcb'+self.modules[1],
						'1','1','0.0001','0.0001','0.0002', 'UCSB_PCKUP_TOOL_11','GLUE','Batch1']
		counter = 0
		while counter < len(data_fields):
			elem = Element(data_fields[counter])
			elem.text = data_text[counter]
			data.append(elem)
			counter += 1
		tree.write(open('module.xml','wb'))

		# Save .json file using the old save() function:
		super(baseplate, self).save()

		# Save .xml file:
		# Store in same directory as .json files, w/ same name:
		filedir, filename = self.get_filedir_filename(self.ID)
		#filename = self.FILENAME.format(ID=self.ID)  #Copied from get_filedir_filename()
		print("Saving file to ", filedir+'/'+filename.replace('.json', '.xml'))
		tree.write(open(filedir+'/'+filename.replace('.json', '.xml'), 'wb'))
		print('Created baseplate XML file')


		success = super(module, self).load(ID)
		if success:
			self.fetch_datasets()
		return success
	"""


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

class step_kapton(fsobj):
	OBJECTNAME = "kapton step"
	FILEDIR    = os.sep.join(['steps','kapton','{century}'])
	FILENAME   = 'kapton_assembly_step_{ID:0>5}.json'
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
		'baseplates', # list of baseplate   IDs, ordered by assembly tray position

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

	def save(self):
		super(step_kapton, self).save()
		inst_baseplate = baseplate()

		for i in range(6):
			baseplate_exists = False if self.baseplates[i] is None else inst_baseplate.load(self.baseplates[i])
			if baseplate_exists:

				# If baseplate has no step_kapton or if its step_kapton is the one being edited now:
				if (inst_baseplate.step_kapton is None) or (inst_baseplate.step_kapton == self.ID):
					inst_baseplate.step_kapton = self.ID
					inst_baseplate.save()
					inst_baseplate.clear()
				else:
					print("ERROR:  Baseplate {} has already been assigned a kapton step!")
					print("*WARNING:  ready_step_kapton should prevent this from working!")
					assert(False)


			else:
				if not (self.baseplates[i] is None):
					print("step_kapton {} cannot write to baseplate {}: does not exist".format(self.ID, self.baseplates[i]))




class step_sensor(fsobj):
	OBJECTNAME = "sensor step"
	FILEDIR    = os.sep.join(['steps','sensor','{century}'])
	FILENAME   = 'sensor_assembly_step_{ID:0>5}.json'
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
	]


	"""@property
	def cure_duration(self):
		if (self.cure_stop is None) or (self.cure_start is None):
			return None
		else:
			return self.cure_stop - self.cure_start
	"""

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
						'RUN_BEGIN_TIMESTAMP':str(self.run_start),
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
								'SNSR_X_OFFST':'TEMP',  #NOTE:  WIP
								'SNSR_Y_OFFSET':'TEMP',  #NOTE:  WIP
								'SNSR_ANG_OFFSET':'TEMP',  #NOTE:  WIP
								'SNSR_TOOL_NAME':'{}_PCKUP_TOOL_{}'.format(snsr_tool.location, snsr_tool.ID),
								'SNSR_TOOL_HT_SET':'TEMP',  #NOTE:  Also WIP
								'SNSR_TOOL_HT_CHK':'TEMP',
								
								# Need to test QDate.year--should work if type(date_received)==QDate
								'GLUE_TYPE':'Araldite {}'.format(glue_batch.date_received[0]),
								'GLUE_BATCH_NUM':str(self.batch_araldite),
								'SLVR_EPXY_TYPE':'Loctite Ablestik',
								'SLVR_EXPY_BATCH_NUM':str(self.batch_loctite),
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

		root_dict['DATA_SET'] = data_sets
		root_dict_cond['DATA_SET'] = data_sets_cond

		xml_tree      = self.generate_xml(root_dict)
		xml_tree_cond = self.generate_xml(root_dict_cond)

		self.save_xml(xml_tree)
		self.save_xml(xml_tree_cond)



class step_pcb(fsobj):
	OBJECTNAME = "PCB step"
	FILEDIR = os.sep.join(['steps','pcb','{century}'])
	FILENAME = 'pcb_assembly_step_{ID:0>5}.json'
	PROPERTIES = [
		'user_performed', # name of user who performed step
		#'date_performed', # date step was performed
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
	]


	@property
	def cure_duration(self):
		if (self.cure_stop is None) or (self.cure_start is None):
			return None
		else:
			return self.cure_stop - self.cure_start

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
				inst_module.step_kapton   = inst_baseplate.step_kapton   if baseplate_exists   else None
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
	FILEDIR = os.sep.join(['supplies','batch_araldite','{century}'])
	FILENAME = 'batch_araldite_{ID:0>5}.json'
	PROPERTIES = [
		'date_received',
		'date_expires',
		'is_empty',
	]


class batch_loctite(fsobj):
	OBJECTNAME = "loctite batch"
	FILEDIR = os.sep.join(['supplies','batch_loctite','{century}'])
	FILENAME = 'batch_loctite_{ID:0>5}.json'
	PROPERTIES = [
		'date_received',
		'date_expires',
		'is_empty',
	]


class batch_sylgard_thick(fsobj):
	OBJECTNAME = "sylgard (thick) batch"
	FILEDIR = os.sep.join(['supplies','batch_sylgard_thick','{century}'])
	FILENAME = 'batch_sylgard_thick_{ID:0>5}.json'
	PROPERTIES = [
		'date_received',
		'date_expires',
		'is_empty',
	]


class batch_sylgard_thin(fsobj):
	OBJECTNAME = "sylgard (thin) batch"
	FILEDIR = os.sep.join(['supplies','batch_sylgard_thin','{century}'])
	FILENAME = 'batch_sylgard_thin_{ID:0>5}.json'
	PROPERTIES = [
		'date_received',
		'date_expires',
		'is_empty',
	]


class batch_bond_wire(fsobj):
	OBJECTNAME = "bond wire batch"
	FILEDIR = os.sep.join(['supplies','batch_bond_wire','{century}'])
	FILENAME = 'batch_bond_wire_{ID:0>5}.json'
	PROPERTIES = [
		'date_received',
		'date_expires',
		'is_empty',
	]






if __name__ == '__main__':
	# test features without UI here
	...
