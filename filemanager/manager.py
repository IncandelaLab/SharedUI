import os
import numpy
import shutil

CWD = os.getcwd()

nstr = lambda v:'' if v is None else str(v)


COMM_STR      = '#'            # comment string - lines starting with this string will be ignored
WHITESPACE    = ' \t\r'        # whitespace - these character will be stripped from lines, variable names, and values
MANAGER_DIR   = 'filemanager'  # 
PROGRAM_NAME  = 'filemanager'  # 
CFGSETUP_NAME = 'cfgsetup.py'  # 
CFG_NAME      = 'config.txt'   # 


if __name__=='__main__':
	FM_DIR   = os.sep.join([CWD])
	CFG_PATH = os.sep.join([FM_DIR,CFG_NAME])
else:
	# assumes this is being run from one directory up
	# will not work if imported from any other location
	FM_DIR   = os.sep.join([CWD,MANAGER_DIR])
	CFG_PATH = os.sep.join([FM_DIR,CFG_NAME])




####################################
### Module folder and file names ###
####################################
MODULE_DIR       = 'modules'
MODULE_FOLDER    = 'module_{MPC}_{ID}'
MODULE_IV_FOLDER = 'IV'
MODULE_DETAILS   = 'details.txt'
MODULE_IV_BINS_FOLDER = 'bins'
MODULE_IV_BA_FILENAME = 'ba {}'
MODULE_IV_BD_FILENAME = 'bd {}'

BASEPLATE_DIR     = 'baseplates'
BASEPLATE_FOLDER  = 'baseplate_{MPC}_{ID}'
BASEPLATE_DETAILS = 'details.txt'

SENSOR_DIR     = 'sensors'
SENSOR_FOLDER  = 'sensor_{MPC}_{ID}'
SENSOR_DETAILS = 'details.txt'

PCB_DIR     = 'PCBs'
PCB_FOLDER  = 'PCB_{MPC}_{ID}'
PCB_DETAILS = 'details.txt'

STEP_DIR = 'steps'
KAPTON_STEP_DIR = os.sep.join([STEP_DIR,'kapton_steps'])
SENSOR_STEP_DIR = os.sep.join([STEP_DIR,'sensor_steps'])
PCB_STEP_DIR    = os.sep.join([STEP_DIR,'PCB_steps'])
KAPTON_STEP_FOLDER = 'kapton_step_{MPC}_{ID}'
SENSOR_STEP_FOLDER = 'sensor_step_{MPC}_{ID}'
PCB_STEP_FOLDER    = 'PCB_step_{MPC}_{ID}'
KAPTON_STEP_DETAILS = 'details.txt'
SENSOR_STEP_DETAILS = 'details.txt'
PCB_STEP_DETAILS    = 'details.txt'


DATADIR_SUBFOLDERS = [
	MODULE_DIR,
	BASEPLATE_DIR,
	SENSOR_DIR,
	PCB_DIR,
]

STRUCT_FOLDERS = [
	MODULE_FOLDER,
	BASEPLATE_FOLDER,
	SENSOR_FOLDER,
	PCB_FOLDER,
]




###############
## Test data ##
###############

LOAD_TEST_OBJECTS = True
TEST_OBJECT_ID = 0
TEST_OBJECT_TEMPLATE_DIR = "setup_datadir"




####################
### details vars ###
####################
DETAILS_BASEPLATE = {
	'ID'           : [int        ],
	'identifier'   : [str  , ""  ],
	'material'     : [str  , ""  ],
	'nomthickness' : [float, -1.0],
	'flatness'     : [float, -1.0],
	'size'         : [float, -1.0],
	'manufacturer' : [str  , ""  ],
	'onModuleID'   : [int  , -1  ],
	'c0'           : [float,  0.0],
	'c1'           : [float,  0.0],
	'c2'           : [float,  0.0],
	'c3'           : [float,  0.0],
	'c4'           : [float,  0.0],
	'c5'           : [float,  0.0],
}

DETAILS_SENSOR = {
	'ID'           : [int        ],
	'identifier'   : [str  , ""  ],
	'type'         : [str  , ""  ],
	'size'         : [float, -1.0],
	'channels'     : [int  , -1  ],
	'manufacturer' : [str  , ""  ],
	'onModuleID'   : [int  , -1  ],
}

DETAILS_PCB = {
	'ID'           : [int        ],
	'identifier'   : [str  , ""  ],
	'thickness'    : [float, -1.0],
	'flatness'     : [float, -1.0],
	'size'         : [float, -1.0],
	'channels'     : [int  , -1  ],
	'manufacturer' : [str  , ""  ],
	'onModuleID'   : [int  , -1  ],
}

DETAILS_MODULE = {
	'ID'         : [int        ],
	'baseplate'  : [int  , -1  ],
	'sensor'     : [int  , -1  ],
	'PCB'        : [int  , -1  ],
	'thickness'  : [float, -1.0],
	'kaptontype' : [str  , -1  ],
	'kaptonstep' : [int  , -1  ],
	'sensorstep' : [int  , -1  ],
	'PCBstep'    : [int  , -1  ],
}

DETAILS_KAPTON_STEP = {
	'ID'            : [int    ],
	'who'           : [str, ""],
	'date'          : [str, ""],
	'time'          : [str, ""],
	'cure_start'    : [str, ""],
	'cure_stop'     : [str, ""],
	'cure_duration' : [str, ""],
	'cure_temp'     : [str, ""],
	'cure_hum'      : [str, ""],
	'module_1'      : [int, -1],
	'module_2'      : [int, -1],
	'module_3'      : [int, -1],
	'module_4'      : [int, -1],
	'module_5'      : [int, -1],
	'module_6'      : [int, -1],
	'araldite_batch': [str, ""],
}

DETAILS_SENSOR_STEP = {
	
}

DETAILS_PCB_STEP = {
	
}

CAST_DICTS = {
	'baseplate'  : DETAILS_BASEPLATE,
	'sensor'     : DETAILS_SENSOR,
	'PCB'        : DETAILS_PCB,
	'module'     : DETAILS_MODULE,
	'kapton_step': DETAILS_KAPTON_STEP,
	'sensor_step': DETAILS_SENSOR_STEP,
	'PCB_step'   : DETAILS_PCB_STEP,
}





######################
### file functions ###
######################
def _save_dict(d,fileout,sep='=',just=True):
	lines = []
	if just:
		lmax  = max([len(_) for _ in d.keys()])
		for item in d.items():
			if sep in item[0] or sep in str(item[1]):
				print("Warning: key <{}> or value <{}> contains separator <{}>".format(*item,sep))
			else:
				lines.append(' '.join([item[0].ljust(lmax),sep,nstr(item[1])]))
	else:
		for item in d.items():
			if sep in item[0] or sep in str(item[1]):
				print("Warning: key <{}> or value <{}> contains separator <{}>".format(*item,sep))
			else:
				lines.append(' '.join([item[0],sep,nstr(item[1])]))
	cont = '\n'.join(lines)
	opfl=open(fileout,'w')
	opfl.write(cont)
	opfl.close()

def _load_dict(filein,sep='=',whitespace=' \r\t'):
	if not os.path.exists(filein):
		return None
	opfl=open(filein,'r')
	cont=opfl.read()
	opfl.close()
	lines=cont.splitlines()
	d={}
	for i,line in enumerate(lines):
		if line.startswith(COMM_STR):
			continue
		if len(line.strip(whitespace)) == 0:
			continue
		if line.count('=')==1:
			var,_,val=line.partition('=')
			var=var.strip(whitespace)
			val=val.strip(whitespace)
			if not bool(var):
				print("Warning: line {} in file {} has empty var {}".format(i,filein,var))
			elif val in d.keys():
				print("Warning: line {} in file <{}> contains value <{}> that has already been declared in the file".format(i,filein,val))
			else:
				d.update([ [var,val] ])
		else:
			print("Warning: line {} in file <{}> does not have exactly one separator ('{}')".format(i,filein,sep))
	return d

def _cast_dict(d,form_dict):
	if d is None:return d
	cast_d = {}

	# attempt to case line values to expected types
	for item in d.items():
		if item[0] in form_dict.keys():
			if bool(item[1]) is False: # empty value is treated the same as key not present
				pass                   # no warning is given if there is no value
			else:
				try:
					value = form_dict[item[0]][0](item[1])
					cast_d.update([ [item[0], value] ])
				except:
					# invalid value is still a warning even if there's a default value
					print("Warning: var <{}> with value <{}> cannot be interpreted as {}".format(item[0],item[1],form_dict[item[0]][0]))
		else:
			print("Warning: var <{}> not expected".format(item[0]))

	# check that all expected keys are present; default to default values for missing keys
	for key in form_dict.keys():
		if not (key in cast_d.keys()):
			if len(form_dict[key]) == 1:
				print("Warning: var <{}> invalid or not present".format(key))
			else:
				cast_d.update([ [key,form_dict[key][1]] ])

	return cast_d

def _load_and_cast_dict(filein,form_dict,sep='=',whitespace=' \r\t'):
	uncast_dict = _load_dict(filein,sep,whitespace)
	return _cast_dict(uncast_dict,form_dict)

def _list_files(folder,ext=None):
	if os.path.exists(folder):
		files = [_ for _ in os.listdir(folder) if os.path.isfile( os.sep.join([folder,_]) )]
		if ext is None:
			return files
		else:
			return [_ for _ in files if _.endswith('.{}'.format(ext))]
	else:
		return None






######################
### data functions ###
######################
def make_bins(raw_data,discard_first_point_per_bin=False):
	# takes [ [t, V, I, Vmeas], ... ]
	# returns [ [Vbin, Iavg, ... ], ... ]
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
				if len(this_bin) == 1 and discard_first_point_per_bin:
					print("Warning: found bin of length 1. Bins of length 1 are ignored when discarding first point per bin.")
				elif this_bin_asc:
					asc_bins.append(this_bin)
				elif not this_bin_asc:
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

	fb_mean = fb_raw[discard_first_point_per_bin:].mean(0)
	lb_mean = lb_raw[discard_first_point_per_bin:].mean(0)
	ab_mean = numpy.array([_[discard_first_point_per_bin:].mean(0) for _ in ab_raw])
	db_mean = numpy.array([_[discard_first_point_per_bin:].mean(0) for _ in db_raw])

	return fb_mean, lb_mean, ab_mean, db_mean







#####################
### manager class ###
#####################
class manager(object):
	def __init__(self):
		configSuccess = self._loadConfig()
		if not configSuccess:
			print("{} could not load config".format(PROGRAM_NAME))
			print("restore file manually or run {}{} to generate new config file".format(CWD+os.sep,CFGSETUP_NAME))
			raise Exception

		else:
			self._check_datadir()
			if LOAD_TEST_OBJECTS:
				self._check_test_objects()
			self._join_directories()


	def _loadConfig(self):
		if not (os.path.exists(CFG_PATH)):
			print("config file for {} does not exist".format(PROGRAM_NAME))
			return False

		opfl = open(CFG_PATH,'r')
		cont = opfl.read()
		opfl.close()
		lines = cont.splitlines()

		if len(lines) == 0:
			print("config file is empty")
			return False

		cfgVars = {}
		for i,line in enumerate(lines):
			if not ('=' in line):
				print("warning: {} config has nondeclarative line <{}> at line number {}".format(PROGRAM_NAME,line,i))
			else:
				var,_,val = line.partition('=')
				cfgVars.update([[var.strip(WHITESPACE),val.strip(WHITESPACE)]])

		if not ('datadir' in cfgVars.keys()):
			print("missing config variable: datadir")
			return False

		if not ('MPC' in cfgVars.keys()):
			print("missing config variable: MPC")
			return False

		global DATADIR
		DATADIR = cfgVars['datadir']

		global MPC
		MPC = cfgVars['MPC']

		if not (os.path.exists(DATADIR)):
			print("config data directory does not exist")
			return True

		return True

	def _check_datadir(self):
		if not (os.path.exists(DATADIR)):
			print("Creating data directory...")
			os.makedirs(DATADIR)

		for DATADIR_SUBFOLDER in DATADIR_SUBFOLDERS:
			if not os.path.exists(os.sep.join([DATADIR, DATADIR_SUBFOLDER])):
				print("Creating data subfolder {}".format(os.sep.join([DATADIR, DATADIR_SUBFOLDER])))
				os.mkdir(os.sep.join([DATADIR, DATADIR_SUBFOLDER]))

	def _check_test_objects(self):
		for i,STRUCT_FOLDER in enumerate(STRUCT_FOLDERS):
			
			TEST_OBJECT_FOLDER = os.sep.join([DATADIR, DATADIR_SUBFOLDERS[i], STRUCT_FOLDER.format(MPC=MPC, ID=TEST_OBJECT_ID)])
			if not os.path.exists(TEST_OBJECT_FOLDER):

				TEST_OBJECT_TEMPLATE = os.sep.join([FM_DIR, TEST_OBJECT_TEMPLATE_DIR, DATADIR_SUBFOLDERS[i], STRUCT_FOLDER.format(MPC=MPC, ID=TEST_OBJECT_ID)])
				print("Creating test object {}".format(TEST_OBJECT_FOLDER))
				shutil.copytree(TEST_OBJECT_TEMPLATE,TEST_OBJECT_FOLDER)

			# print('')
			# print(TEST_OBJECT_TEMPLATE)
			# print(TEST_OBJECT_FOLDER)
			# print('')

	def _join_directories(self):
		"""Creates global dicts of object folders and details files"""

		global OBJECT_FOLDERS
		global DETAILS_FILES

		OBJECT_FOLDERS = {
			'baseplate'  : os.sep.join([ DATADIR,   BASEPLATE_DIR,   BASEPLATE_FOLDER ]),
			'sensor'     : os.sep.join([ DATADIR,      SENSOR_DIR,      SENSOR_FOLDER ]),
			'PCB'        : os.sep.join([ DATADIR,         PCB_DIR,         PCB_FOLDER ]),
			'module'     : os.sep.join([ DATADIR,      MODULE_DIR,      MODULE_FOLDER ]),
			'kapton_step': os.sep.join([ DATADIR, KAPTON_STEP_DIR, KAPTON_STEP_FOLDER ]),
			'sensor_step': os.sep.join([ DATADIR, SENSOR_STEP_DIR, SENSOR_STEP_FOLDER ]),
			'PCB_step'   : os.sep.join([ DATADIR,    PCB_STEP_DIR,    PCB_STEP_FOLDER ]),
		}

		DETAILS_FILES = {
			'baseplate'  : os.sep.join([ OBJECT_FOLDERS['baseplate'  ],   BASEPLATE_DETAILS ]),
			'sensor'     : os.sep.join([ OBJECT_FOLDERS['sensor'     ],      SENSOR_DETAILS ]),
			'PCB'        : os.sep.join([ OBJECT_FOLDERS['PCB'        ],         PCB_DETAILS ]),
			'module'     : os.sep.join([ OBJECT_FOLDERS['module'     ],      MODULE_DETAILS ]),
			'kapton_step': os.sep.join([ OBJECT_FOLDERS['kapton_step'], KAPTON_STEP_DETAILS ]),
			'sensor_step': os.sep.join([ OBJECT_FOLDERS['sensor_step'], SENSOR_STEP_DETAILS ]),
			'PCB_step'   : os.sep.join([ OBJECT_FOLDERS['PCB_step'   ],    PCB_STEP_DETAILS ]),
		}



	########################
	### module functions ###
	########################
	def loadModuleIV(self,ID,file):
		rawfile = os.sep.join([DATADIR,MODULE_DIR,MODULE_FOLDER.format(MPC=MPC,ID=ID),MODULE_IV_FOLDER,file])
		bafile  = os.sep.join([DATADIR,MODULE_DIR,MODULE_FOLDER.format(MPC=MPC,ID=ID),MODULE_IV_FOLDER,MODULE_IV_BINS_FOLDER,MODULE_IV_BA_FILENAME.format(file)])
		bdfile  = os.sep.join([DATADIR,MODULE_DIR,MODULE_FOLDER.format(MPC=MPC,ID=ID),MODULE_IV_FOLDER,MODULE_IV_BINS_FOLDER,MODULE_IV_BD_FILENAME.format(file)])
		if not(os.path.exists(rawfile)):
			print("Warning: tried to load nonexistent IV file <{}>".format(rawfile))
			return None #, None, None
		rawdata = numpy.loadtxt(rawfile)
		if not (os.path.exists(bafile) and os.path.exists(bdfile)):
			print("bins do not exist yet for IV dataset <{}>. creating them...".format(rawfile))
			bf, bl, ba, bd = make_bins(rawdata)
			print("saving bins...")
			numpy.savetxt(bafile,ba)
			numpy.savetxt(bdfile,bd)
		else:
			ba = numpy.loadtxt(bafile)
			bd = numpy.loadtxt(bdfile)
		return rawdata, ba, bd

	def _load_module_details(self,ID):
		folder       = os.sep.join([DATADIR,MODULE_DIR,MODULE_FOLDER.format(MPC=MPC,ID=ID)])
		details_file = os.sep.join([folder,MODULE_DETAILS])
		iv_folder    = os.sep.join([folder,MODULE_IV_FOLDER])
		return _load_and_cast_dict(details_file,DETAILS_MODULE), _list_files(iv_folder)

	def _change_module_details(self,ID,change_dict,new=False):
		folder  = os.sep.join([DATADIR,MODULE_DIR,MODULE_FOLDER.format(MPC=MPC,ID=ID)])
		file    = os.sep.join([folder,MODULE_DETAILS])
		cast_to = DETAILS_MODULE
		if new:
			self._create_module(ID)
			self._createDetails(ID,file,cast_to,change_dict)
		else:
			self._changeDetails(file,cast_to,change_dict)

	def _create_module(self,ID):
		folder      = os.sep.join([DATADIR,MODULE_DIR,MODULE_FOLDER.format(MPC=MPC,ID=ID)])
		iv_folder   = os.sep.join([folder,MODULE_IV_FOLDER])
		bins_folder = os.sep.join([iv_folder,MODULE_IV_BINS_FOLDER])
		if os.path.exists(folder):
			print("Warning: tried to create existing module with ID {}".format(ID))
			return False
		os.mkdir(folder)
		os.mkdir(iv_folder)
		os.mkdir(bins_folder)
		return True



	#############################################
	## loading, changing, and creating details ##
	#############################################

	def loadObjectDetails(self,objecttype,ID):
		if objecttype == 'module':
			return self._load_module_details(ID)
		else:
			return self._load_object_details(objecttype,ID)

	def changeObjectDetails(self,objecttype,ID,change_dict,new=False):
		if objecttype == 'module':
			return self._change_module_details(ID,change_dict,new)
		else:
			return self._change_object_details(objecttype,ID,change_dict,new)

	def _load_object_details(self,objecttype,ID):
		file = DETAILS_FILES[objecttype].format(MPC=MPC,ID=ID)
		return _load_and_cast_dict(file,CAST_DICTS[objecttype])

	def _change_object_details(self,objecttype,ID,change_dict,new=False):
		folder  = OBJECT_FOLDERS[objecttype].format(MPC=MPC,ID=ID)
		file    = DETAILS_FILES[objecttype].format(MPC=MPC,ID=ID)
		cast_to = CAST_DICTS[objecttype]
		if new:
			self._create_object(objecttype,ID)
			self._createDetails(ID,file,cast_to,change_dict)
		else:
			self._changeDetails(file,cast_to,change_dict)

	def _create_object(self,objecttype,ID):
		folder = OBJECT_FOLDERS[objecttype].format(MPC=MPC,ID=ID)
		if os.path.exists(folder):
			print("Warning: tried to create existing {} with ID {}".format(objecttype,ID))
			return False
		os.mkdir(folder)
		return True

	def _createDetails(self, ID, file, cast_to, details):
		#os.mkdir(folder)
		cast_details = {}
		cast_details.update([['ID',ID]])
		for key,val in details.items():
			val_cast = cast_to[key][0](val)
			cast_details.update([[key,val_cast]])
		_save_dict(cast_details, file)

	def _changeDetails(self, file, cast_to, change_dict):
		details = _load_and_cast_dict(file,cast_to)
		for key,val in change_dict.items():
			if key in details.keys():
				try:
					val = cast_to[key][0](val)
					details[key] = val
				except:
					print("Warning: tried to change variable <{}> to value not interpretable as <{}>".format(key,cast_to[key][0]))
			else:
				print("Warning: tried to change value of invalid variable <{}>".format(key))
		_save_dict(details,file)



################################################
### System test - if program is run directly ###
################################################
if __name__ == '__main__':
	m = manager()
	# m.changeKaptonStepDetails(0,{'who':'wo'})
	# print(m.loadKaptonStepDetails(0))
	print(m.loadModuleDetails(0))
	print(m.loadBaseplateDetails(0))
	print(m.loadSensorDetails(0))
	print(m.loadPCBDetails(0))
