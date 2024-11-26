import json
import time
import glob
import os
import sys
import requests

from PyQt5 import QtCore
import datetime

from jinja2 import Template

#import rhapi_nolock as rh

# import oracledb

# IMPORTANT NOTE:  Setting this to false disables DB communication.  Purely for debugging.
# ENABLE_DB_COMMUNICATION = False
ENABLE_DB_COMMUNICATION = True
CON = None
DB_CURSOR = None

# def db_connect():
# 	if not ENABLE_DB_COMMUNICATION:
# 		return
# 	CON = oracledb.connect(user="CMS_HGC_PRTTYPE_HGCAL_READER", password="HGCAL_Reader_2016", dsn="localhost:10131/int2r_lb.cern.ch")  # create connection
# 	DB_CURSOR = CON.cursor()



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

LOCAL_REMOTE_PROPS_DICT_PARTS = {
	'kind_of_part' : 'kind',
	'location' : 'location',
	'record_insertion_user' : 'record_insertion_user',
	'flatness' : 'flatness',
	'thickness' : 'thickness',
	'grade' : 'grade',
	'comments' : 'comments',
	# baseplate
	'manufacturer' : 'manufacturer_id',
	'weight' : 'weight',
	# pcb
	# 'test_files' : 'test_file_name',
}

LOCAL_REMOTE_PROPS_DICT_PROTOMODULE = {
    'kind_of_part' : 'kind',
	'location' : 'location',
	'record_insertion_user' : 'record_insertion_user',
	'flatness' : 'prto_fltnes_mm',
	'thickness' : 'prto_thknes_mm',
	'grade' : 'prto_grade',
	'step_sensor' : 'snsr_step',
	'snsr_x_offst' : 'snsr_x_offst',
	'snsr_y_offst' : 'snsr_y_offst',
	'snsr_ang_offst' : 'snsr_ang_offset',
}

LOCAL_REMOTE_PROPS_DICT_MODULE = {
	'kind_of_part' : 'kind',
	'location' : 'location',
	'record_insertion_user' : 'record_insertion_user',
	'flatness' : 'mod_fltns_mm',
	'thickness' : 'mod_ave_thkns_mm',
	'max_thickness' : 'mod_max_thkns_mm',
	'grade' : 'mod_grade',
	'step_pcb' : 'pcb_step',
	'pcb_plcment_x_offset' : 'pcb_plcment_x_offset',
	'pcb_plcment_y_offset' : 'pcb_plcment_y_offset',
	'pcb_plcment_ang_offset' : 'pcb_plcment_ang_offset',
}

CLASSNAME_QCKEYS_DICT = {
	'baseplate' : ['baseplate'],
	'sensor' : ['sensor'],
	'pcb' : ['pcb'],
	'protomodule' : ['protomodule_assembly_condition', 'protomodule_assembly'],
	'module' : ['module_assembly_condition', 'module_assembly', 'module_wirebond'],
}

CENTURY = '{:0>3}__'

CFG_FILE = 'cfg.json'
CWD = os.getcwd()
if not CWD.endswith('filemanager'):
	CWD = os.sep.join([CWD,'filemanager'])

# Directory to store all temp part data
DATADIR = None
# Directory where all XML templates are found (hardcoded)
TEMPLATEDIR = None

# setup() MUST be called before creating an instance of any fsobj subclass.  It:
# - defines a directory DATADIR where all object data is stored
# - creates files & directories in DATADIR for organizing object data

def setup(datadir=None, database='int2r'):
	global DATADIR
	global TEMPLATEDIR
	global DATABASE
	global REMOTE_LIST_DIR
	global API_URL

	DATABASE = database
	REMOTE_LIST_DIR = 'partlist_remote_{}'.format(database)
	API_URL = 'https://hgcapi{}.web.cern.ch'.format('-cmsr' if database == 'cmsr' else '')

	if datadir==None:
		DATADIR = os.sep.join([os.getcwd(), 'filemanager_data'])  # data['datadir']
	else:
		DATADIR = datadir
	TEMPLATEDIR = os.sep.join([os.getcwd(), 'filemanager', 'xml_templates'])

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
                'batch_tape_50', 'batch_tape_120',
				'tool_sensor', 'tool_pcb', 'tray_assembly', 'tray_component_sensor', 'tray_component_pcb',
				'step_sensor', 'step_pcb']  # step_kapton removed
	for part in obj_list:
		fname = os.sep.join([partlistdir, part+'s.json'])
		if not os.path.exists(fname):
			with open(fname, 'w') as opfl:
				# Dump an empty dict if nothing is found
				# NOTE:  Format of dictionary is {ID:creation-date-string, ...}
				json.dump({}, opfl)

	# NEW for remote central DB searching: HGCAL API - will need to figure out the CERN auth in the future
	if ENABLE_DB_COMMUNICATION:
		obj_list_remote = ['baseplate', 'pcb', 'protomodule', 'module']  # sensor search is desabled for now
		for part in obj_list_remote:
			fetchRemoteDB(part, db=database)
	
#setup()


def fetchRemoteDB(part, db='int2r', location=None):
	partlistdir_remote = os.sep.join([DATADIR, REMOTE_LIST_DIR])
	if not os.path.exists(partlistdir_remote):
		os.makedirs(partlistdir_remote)

	fname = os.sep.join([partlistdir_remote, part+'s.json'])

	# Make the GET request
	url = '{}/mac/parts/types/{}s'.format(API_URL, part)
	
	remote_data = {}
	max_page = -1
	limit = 1000

	# Get page zero, and max page
	response_0 = _get_response(url, limit, 0, location)
	print(f"Fetched data from {url} page 0")
	# print(f"Fetching data from {url} page 0: {response_0}")
	if response_0:
		max_page = response_0['pagination']['pages_total']
		remote_data['parts'] = response_0['parts']
		print(f"{part} max page {max_page}")

		for npage in range(1, max_page):
			print(f"Fetching data from {url} page {npage}")
			response = _get_response(url, limit, npage, location)
			if not response:
				# report error and exit
				print(f"Error: Failed to fetch data from {url} page {npage}")
				exit(1)
			remote_data['parts'].extend(response['parts'])
	else:
		print(f"Error: Failed to fetch data from {url}")
		exit(1)

	if not os.path.exists(fname):
		# Store the response JSON data in a new file
		with open(fname, 'w') as opfl:
			# Dump an empty dict if nothing is found
			# NOTE:  Format of dictionary is {ID:creation-date-string, ...}
			# json.dump({}, opfl)
			json.dump(remote_data, opfl, indent=4)
			print("central DB JSON data saved to '{}'".format(fname))

	else:
		# Update existing JSON file
		with open(fname, 'r') as file:
			local_data = json.load(file)

		if local_data != remote_data:
			# Store the updated JSON data in the local file
			with open(fname, 'w') as opfl:
				json.dump(remote_data, opfl, indent=4)
				print("Local JSON data updated for '{}'".format(part))

def _get_response(url, limit, npage, location):
	url += '?page={}'.format(npage)  # only fetch page 0 (assuming limit is large enough)
	if limit:  # request limited by limit
		url += '&limit={}'.format(limit)
	if location:  # request filtered by location
		url += '&location={}'.format(location)
	
	headers = {'accept': 'application/json'}
	response = requests.get(url, headers=headers)
	if response.status_code == 200:
		return response.json()
	else:
		print(f"Failed to fetch data from {url}: {response.status_code} - {response.text}")
		return None

###############################################
############# UserManager class ###############
###############################################


class UserManager:

	def __init__(self, userFile="userInfoFile"):
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



###############################################
############## fsobj base class ###############
###############################################

class fsobj(object):
	OBJECTNAME = "fsobj"
	# Var for storing all obj properties:
	PROPERTIES = []
	DEFAULTS = {}

	# List containing locations of all xml template files to write
	XML_TEMPLATES = []

	# True if assembly step (multiple DATA_SETs per output file), else False
	# TBD
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
		# ID param is for tools:  self.ID is NOT the key that must be saved!
		# Instead, "ID_institution" is used.
		id_ = self.ID if ID is None else ID

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not id_ in data.keys():
				# Note creation date and pass it to the dict
				dcreated = time.localtime()
				if date:
					dc = date
				else:
					dc = '{}-{}-{}'.format(dcreated.tm_mon, dcreated.tm_mday, dcreated.tm_year)
				data[str(id_)] = dc
		with open(self.partlistfile, 'w') as opfl:
			json.dump(data, opfl)


	def load(self, ID):
		self.clear()
		if ID == -1 or ID == None:
			return False

		# First, check partlistfile to confirm existence.
		# If not found in partlistfile, return false.
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not str(ID) in data.keys():
				return False

		filedir, filename = self.get_filedir_filename(ID)
		json_file = os.sep.join([filedir, filename])
		# Fix error: change the tool/supply xml file name to json
		xml_files = glob.glob(filedir + '/*' + ID +'*.xml')
		# there are >=2 xml tmls for parts, make sure this won't affect them
		# batch in filename so only changes the supplies
		if 'batch' in filename and len(xml_files) == 1 and not os.path.exists(json_file):
			print('Rename file {} to {}'.format(os.path.basename(xml_files[0]), filename))
			os.rename(xml_files[0], os.sep.join([filedir, filename]))
		assert os.path.exists(json_file), "Part {} in partlist has no json file {}!".format(ID, json_file)
		with open(json_file, 'r') as opfl:
			data = json.load(opfl)

		self.ID = ID
		data_keys = data.keys()
		props_in_data = [prop in data_keys for prop in self.PROPERTIES]
		# for each property stored in xml file, load:
		for i,prop in enumerate(self.PROPERTIES):
			prop_in_data = props_in_data[i]
			if prop_in_data:
				setattr(self, prop, data[prop])
			else:
				prop_default = self.DEFAULTS[prop] if prop in self.DEFAULTS.keys() else None

		return True

	def load_remote(self, ID, full=True):
		self.clear()
		if ID == -1 or ID == None:
			return False
		
		part_name = self.__class__.__name__
		if part_name not in ['baseplate', 'pcb', 'sensor', 'protomodule', 'module']:
			return False
		
		remote_partlistfile = os.sep.join([ DATADIR, REMOTE_LIST_DIR, part_name+'s.json' ])

		data_keys = []

		response = None
		request_success = False
		if full:
			# Make the GET request
			url = '{}/mac/part/{}/full'.format(API_URL, ID)
			headers = {'accept': 'application/json'}
			response = requests.get(url, headers=headers)

			# Check if the request was successful
			if response.status_code == 200:
				response_json = response.json()
				request_success = True
			else:
				response_json = {}
		else:
			with open(remote_partlistfile, 'r') as opfl:
				data = json.load(opfl)
				for part_data in data['parts']:
					if part_data['serial_number'] == ID:
						response = part_data
			response_json = response

		# Check if the full info is needed or the request was successful
		if ((not full) and bool(response_json)) or request_success:
			data_keys = []
			
			# print("!!! remote response_json: ", response_json)
			# general keys
			data_keys += response_json.keys()
			
			if full:
				data_keys.remove('qc')
				# QC keys
				qc_keys = CLASSNAME_QCKEYS_DICT[part_name]
				for qc_key in qc_keys:
					if bool(response_json['qc']) and qc_key in response_json['qc'].keys():
						data_keys += response_json['qc'][qc_key].keys()
			
			# Load corresponding properties
			if part_name in ['baseplate', 'sensor', 'pcb']:
				LOCAL_REMOTE_PROPS_DICT = LOCAL_REMOTE_PROPS_DICT_PARTS
			elif part_name == 'protomodule':
				LOCAL_REMOTE_PROPS_DICT = LOCAL_REMOTE_PROPS_DICT_PROTOMODULE
			elif part_name == 'module':
				LOCAL_REMOTE_PROPS_DICT = LOCAL_REMOTE_PROPS_DICT_MODULE

			for prop in self.PROPERTIES:
				# only load the properties in the LOCAL_REMOTE_PROPS_DICT
				if prop in LOCAL_REMOTE_PROPS_DICT.keys():
					remote_prop = LOCAL_REMOTE_PROPS_DICT[prop]
					if remote_prop in response_json.keys():
						setattr(self, prop, response_json[remote_prop])
					# load full info
					elif full:
						for qc_key in qc_keys:
							if bool(response_json['qc']) and qc_key in response_json['qc'].keys() \
           					and remote_prop in response_json['qc'][qc_key].keys():
								setattr(self, prop, response_json['qc'][qc_key][remote_prop])
						# load children
						if 'children' in data_keys:
							children = response_json['children']
							for child in children:
								if 'kind' in child.keys():
									kind = child['kind']
									if 'Baseplate' in kind:
										setattr(self, 'baseplate', child['serial_number'])
									if 'Sensor' in kind:
										setattr(self, 'sensor', child['serial_number'])
									if 'Hexaboard' in kind:
										setattr(self, 'pcb', child['serial_number'])
									if 'ProtoModule' in kind:
										setattr(self, 'protomodule', child['serial_number'])
						if 'parent' in data_keys:
							parents = response_json['parent']
							for parent in parents:
								if 'kind' in parent.keys():
									kind = parent['kind']
									if 'ProtoModule' in kind:
										setattr(self, 'protomodule', parent['serial_number'])
									# only shows the first parent
									elif 'Module' in kind:
										setattr(self, 'module', parent['serial_number'])
			self.ID = ID
			return True
		else:
			if response:
				print(f"Failed to fetch data: {response.status_code} - {response.text}")
			else:
				print(f"Part {ID} not found in remote partlist")
			return False

	def new(self, ID):
		self.ID = ID
		for prop in self.PROPERTIES:
			setattr(self, prop, self.DEFAULTS[prop] if prop in self.DEFAULTS.keys() else None)


	def clear(self):
		self.ID = None
		for prop in self.PROPERTIES:
			setattr(self, prop, self.DEFAULTS.get(prop, None))


	def save(self):
		# NOTE:  Can't check item existence via filepath existence, bc filepath isn't known until after item creation!
		# Instead, go into partlist dict and check to see whether item exists:
		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
			if not str(self.ID) in data.keys():
				# Can't get filedir from get_filedir_filename()...
				# ...until the date has been set via add_part_to_list.  Do that now.
				self.add_part_to_list()

		filedir, filename = self.get_filedir_filename()
		file = os.sep.join([filedir, filename])
		if not os.path.exists(filedir):
			os.makedirs(filedir)	

		with open(file, 'w') as opfl:
			json.dump(vars(self), opfl, indent=4)


	# utility for generate_xml():
	# create dict of all attrs and values for this object,
	# INCLUDING attrs/@properties of all parent classes.
	# {'thickness': 0.01, 'comments_concat': 'comment1;;comment2', ...}
	def dump_all_attrs(self):
		prop_dict = {}
		# Add all ordinary object attributes:
		for prop in self.PROPERTIES:
			prop_dict[prop] = getattr(self, prop, None)
		# now get managed attributes/@properties of that class:
		# (must also do recursively, for all parent classes)
		parents = type(self).__bases__  # tuple of parent classes
		classes = [type(self)]
		for p in parents:
			classes.append(p)
		# Now, for each class:  get all @properties and add to prop_dict
		for cl in classes:
			for name, var in vars(cl).items():
				if isinstance(var, property):
					prop_dict[name] = getattr(self, name)
		# Since ID is treated separately...
		prop_dict["ID"] = self.ID
		return prop_dict

	# NEW:  If obj has XML template files, write them.
	def generate_xml(self):
		# save():  Required so it calls add_part_to_list (for filedir_filename)
		print("FM:  Generating XML")
		print("XML templates are:", self.XML_TEMPLATES)
		self.save()
		filedir, filename = self.get_filedir_filename()
		for template in self.XML_TEMPLATES:
			template_file = os.sep.join([TEMPLATEDIR, self.OBJECTNAME, template])
			# Make sure the file exists
			if not os.path.exists(template_file):
				continue
			with open(template_file, 'r') as file:
				template_content = file.read()
			template = Template(template_content)
			# render on dict of all attributes + properties:
			rendered = template.render(self.dump_all_attrs())
			# outfile name:  [outfilename]_[templatename].xml
			template_file_name = os.path.basename(template_file)
			outfile = filename.replace(".json", "") + "_" + template_file_name
			with open(os.sep.join([filedir, outfile]), 'w') as file:
				print("Writing to", os.sep.join([filedir, outfile]))
				file.write(rendered)

	# Return all XML files to upload (full filepath)
	def filesToUpload(self):
		if self.XML_TEMPLATES is None:  return None
		filedir, filename = self.get_filedir_filename()
		upFiles = []
		for template_file in self.XML_TEMPLATES:
			template_file_name = os.path.basename(template_file)
			outfile = filename.replace(".json", "") + "_" + template_file_name
			outfile_fullname = os.sep.join([filedir, outfile])
			upFiles.append(outfile_fullname)
		return upFiles


	# join all comments into a single ;;-separated string, max 4k chars
	@property
	def comments_concat(self):
		cmts = ';;'.join(self.comments)
		# Impose len reqt of 4000 chars (for DB; actual limit unknown/TBD)
		if len(cmts) > 4000:
			print("WARNING:  Total combined comments length for {} exceeds 4000 chars - last {} chars truncated".format(self.ID, len(cmts)-4000))
			cmts = cmts[:4000]
		return cmts







