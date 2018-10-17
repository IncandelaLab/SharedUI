import os
import numpy

COMMSTR = '#'

def load_file(file):
	if os.path.exists(file):
		opfl = open(file,'r')
		cont = opfl.read()
		opfl.close()
		return cont
	else:
		return None

def process_lines(lines,file,sep='='):
	cfgVars = {}
	for i,line in enumerate(lines):
		if not (sep in line):
			pass
		elif line.startswith(COMMSTR):
			pass
		else:
			var,_,val = line.partition(sep)
			var=var.strip(WHITESPACE)
			if var in cfgVars.keys():
				print("Warning: file {} has two declarations with same variable <{}>".format(file,var))
				print("Ignoring all but first instance")
			else:
				cfgVars.update([[var,val.strip(WHITESPACE)]])
	return cfgVars

def load_lines(file):
	cont = load_file(file)
	if cont is None:return cont
	return process_lines(cont.splitlines(),file)

def list_files(folder):
	if os.path.exists(folder):
		return os.listdir(folder)
	else:
		return None

CWD = os.getcwd()
SEP = os.sep

WHITESPACE    = ' \t\r'
MANAGER_DIR   = 'filemanager'
PROGRAM_NAME  = 'filemanager'
CFGSETUP_NAME = 'cfgsetup.py'
CFG_NAME      = 'config.txt'

if __name__=='__main__':
	CFG_PATH = SEP.join([CWD,CFG_NAME])
else:
	CFG_PATH = SEP.join([CWD,MANAGER_DIR,CFG_NAME])

MODULE_DIR       = 'modules'
MODULE_FOLDER    = 'module_{MPC}_{ID}'
MODULE_IV_FOLDER = 'IV'
MODULE_DETAILS   = 'details.txt'

BASEPLATE_DIR     = 'baseplates'
BASEPLATE_FOLDER  = 'baseplate_{MPC}_{ID}'
BASEPLATE_DETAILS = 'details.txt'

SENSOR_DIR     = 'sensors'
SENSOR_FOLDER  = 'sensor_{MPC}_{ID}'
SENSOR_DETAILS = 'details.txt'

PCB_DIR     = 'PCBs'
PCB_FOLDER  = 'PCB_{MPC}_{ID}'
PCB_DETAILS = 'details.txt'


class manager(object):
	def __init__(self):
		configSuccess = self.loadConfig()
		if not configSuccess:
			print("{} could not load config".format(PROGRAM_NAME))
			print("restore file manually or run {}{} to generate new config file".format(CWD+SEP,CFGSETUP_NAME))
			raise Exception

	def loadModuleIV(self,ID,file):
		file = os.sep.join([DATADIR,MODULE_DIR,MODULE_FOLDER.format(MPC=MPC,ID=ID),MODULE_IV_FOLDER,file])
		return numpy.loadtxt(file)


	def loadModuleDetails(self,ID):
		folder       = os.sep.join([DATADIR,MODULE_DIR,MODULE_FOLDER.format(MPC=MPC,ID=ID)])
		details_file = os.sep.join([folder,MODULE_DETAILS])
		iv_folder    = os.sep.join([folder,MODULE_IV_FOLDER])
		return load_lines(details_file), list_files(iv_folder)

	def loadBaseplateDetails(self,ID):
		file = os.sep.join([DATADIR,BASEPLATE_DIR,BASEPLATE_FOLDER.format(MPC=MPC,ID=ID),BASEPLATE_DETAILS])
		return load_lines(file)

	def loadSensorDetails(self,ID):
		file = os.sep.join([DATADIR,SENSOR_DIR,SENSOR_FOLDER.format(MPC=MPC,ID=ID),SENSOR_DETAILS])
		return load_lines(file)

	def loadPCBDetails(self,ID):
		file = os.sep.join([DATADIR,PCB_DIR,PCB_FOLDER.format(MPC=MPC,ID=ID),PCB_DETAILS])
		return load_lines(file)



	def loadConfig(self):
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
			return False

		return True



if __name__ == '__main__':

	m = manager()
	print(m.loadModuleDetails(0))
	print(m.loadBaseplateDetails(0))
	print(m.loadSensorDetails(0))
	print(m.loadPCBDetails(0))
