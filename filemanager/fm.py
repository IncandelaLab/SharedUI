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
from jinja2 import Template

#import rhapi_nolock as rh
# For DB requests:
import cx_Oracle
from xml.dom import minidom

# IMPORTANT NOTE:  Setting this to false disables DB communication.  Purely for debugging.
ENABLE_DB_COMMUNICATION = False


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

# Directory to store all temp part data
DATADIR = None
# Directory where all XML templates are found (hardcoded)
TEMPLATEDIR = None

# setup() MUST be called before creating an instance of any fsobj subclass.  It:
# - defines a directory DATADIR where all object data is stored
# - creates files & directories in DATADIR for organizing object data

def setup(datadir=None):
	global DATADIR
	global TEMPLATEDIR

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
				'tool_sensor', 'tool_pcb', 'tray_assembly', 'tray_component_sensor', 'tray_component_pcb',
				'step_sensor', 'step_pcb']  # step_kapton removed
	for part in obj_list:
		fname = os.sep.join([partlistdir, part+'s.json'])
		if not os.path.exists(fname):
			with open(fname, 'w') as opfl:
				# Dump an empty dict if nothing is found
				# NOTE:  Format of dictionary is {ID:creation-date-string, ...}
				json.dump({}, opfl)

#setup()


# Set up DB_CURSOR object for SQL requests:
"""
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
"""

# moved to mainUI: (must call after tunnel)
#connectOracle()


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



###############################################
############## fsobj base class ###############
###############################################

class fsobj(object):
	# Var for storing all obj properties:
	PROPERTIES = []
	DEFAULTS = {}

	# List containing locations of all xml template files to write
	# If non-empty, read each and write
	XML_TEMPLATES = []

	OBJECTNAME = "fsobj"

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
		#PROPERTIES = self.PROPERTIES
		#DEFAULTS = #getattr(self, 'DEFAULTS', {})

		props_in_data = [prop in data_keys for prop in self.PROPERTIES]
		print("data_keys:", data_keys)
		print("Properties:", self.PROPERTIES)
		print("props in data", props_in_data)

		for i,prop in enumerate(self.PROPERTIES):
			prop_in_data = props_in_data[i]

			if prop_in_data:
				setattr(self, prop, data[prop])
			else:
				prop_default = self.DEFAULTS[prop] if prop in self.DEFAULTS.keys() else None

		return True



	def new(self, ID):
		# NOTE:  Should never be called on an existing object.
		# The only person you can blame for doing this is yourself.
		self.ID = ID
		#PROPERTIES = self.PROPERTIES + self.PROPERTIES_COMMON
		#DEFAULTS = {**self.DEFAULTS_COMMON, **getattr(self, 'DEFAULTS', {})}
		print("Defaults are:", self.DEFAULTS)
		for prop in self.PROPERTIES:
			print("Setting property {} to {}".format(prop, self.DEFAULTS[prop] if prop in self.DEFAULTS.keys() else None))
			setattr(self, prop, self.DEFAULTS[prop] if prop in self.DEFAULTS.keys() else None)


	def clear(self):
		self.ID = None
		#PROPERTIES = self.PROPERTIES + self.PROPERTIES_COMMON
		#DEFAULTS   = {**self.DEFAULTS, **self.DEFAULTS_COMMON}
		for prop in self.PROPERTIES:
			setattr(self, prop, self.DEFAULTS.get(prop, None))
		# For clearing, we don't check or set defaults
		# All properties, including ID, are set to None
		# Attempts to use an object when it has been cleared are meant to produce errors



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


	# NEW:  If obj has XML template files, write them.
	def generate_xml(self):
		# save():  Required for add_part_to_list (for filedir_filename)
		self.save()
		filedir, filename = self.get_filedir_filename()
		for template in self.XML_TEMPLATES:
			template_file = os.sep.join([TEMPLATEDIR, self.OBJECTNAME, template])
			print("DEBUG:  Opening template file", template_file)
			with open(template_file, 'r') as file:
				template_content = file.read()
			template = Template(template_content)
			rendered = template.render()
			# outfile name:  [outfilename]_[templatename].xml
			template_file_name = os.path.basename(template_file)
			outfile = filename.replace(".xml", "") + "_" + template_file_name
			print("TEMP:  Writing to XML output file", os.sep.join([filedir, outfile]))
			with open(os.sep.join([filedir, outfile]), 'w') as file:
				file.write(rendered)

	# Return all XML files to upload (full filepath)
	def filesToUpload(self):
		if self.XML_TEMPLATES is None:  return None
		filedir, filename = self.get_filedir_filename()
		upFiles = []
		for xt in self.XML_TEMPLATES:
			template_file_name = os.path.basename(template_file)
			outfile =  filename.replace(".xml", "") + "_" + template_file_name
			upFiles.append(outfile)
		return upFiles


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







