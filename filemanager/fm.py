import os
import json



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

	DATADIR = data['datadir']
	MAC     = data['MAC']

loadconfig()



class fsobj(object):
	PROPERTIES_COMMON = [
		'comments',
		]

	DEFAULTS_COMMON = {
		'comments':[],
	}

	def __init__(self):
		super(fsobj, self).__init__()
		self.clear() # sets attributes to None


	def get_filedir_filename(self, ID = None):
		if ID is None:
			ID = self.ID
		filedir  = os.sep.join([ DATADIR, self.FILEDIR.format(ID=ID, century = '{:0>3}__'.format(ID//100)) ])
		filename = self.FILENAME.format(ID=ID)
		return filedir, filename


	def save(self):
		filedir, filename = self.get_filedir_filename(self.ID)
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


	def load(self, ID, on_property_missing = "warn"):
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
		for prop in PROPERTIES:
			setattr(self, prop, None)
		# For clearing, we don't check or set defaults
		# All properties, including ID, are set to None
		# Attempts to use an object when it has been cleared are meant to produce errors




###############################################
##################  tooling  ##################
###############################################

class tool_sensor(fsobj):
	FILEDIR = os.sep.join(['tooling','tool_sensor'])
	FILENAME = 'tool_sensor_{ID:0>5}.json'
	PROPERTIES = [
		'size',
	]


class tool_pcb(fsobj):
	FILEDIR = os.sep.join(['tooling','tool_pcb'])
	FILENAME = 'tool_pcb_{ID:0>5}.json'
	PROPERTIES = [
		'size',
	]


class tray_assembly(fsobj):
	FILEDIR = os.sep.join(['tooling','tray_assembly'])
	FILENAME = 'tray_assembly_{ID:0>5}.json'
	PROPERTIES = [
		'size',
	]


class tray_component_sensor(fsobj):
	FILEDIR = os.sep.join(['tooling','tray_component_sensor'])
	FILENAME = 'tray_component_sensor_{ID:0>5}.json'
	PROPERTIES = [
		'size',
	]


class tray_component_pcb(fsobj):
	FILEDIR = os.sep.join(['tooling','tray_component_pcb'])
	FILENAME = 'tray_component_pcb_{ID:0>5}.json'
	PROPERTIES = [
		'size'
	]




###############################################
###########  shipment and reception  ##########
###############################################

class shipment(fsobj):
	...


class reception(fsobj):
	...



###############################################
###############  assembly steps  ##############
###############################################

class step_kapton(fsobj):
	FILEDIR    = os.sep.join(['steps','kapton','{century}'])
	FILENAME   = 'kapton_assembly_step_{ID:0>5}.json'
	PROPERTIES = [
		'user',             # name of person who performed step
		'step_start',       # unix time @ start of step
		'cure_start',       # unix time @ start of curing
		'cure_stop',        # unix time @ end of curing
		'cure_temperature', # Average temperature during curing (centigrade)
		'cure_humidity',    # Average humidity during curing (percent)

		'tools',        # list of pickup tool IDs, ordered by pickup tool location
		'kaptons',      # list of kapton      IDs, ordered by component tray position
		'baseplates',   # list of baseplate   IDs, ordered by assembly tray position

		'locs_tool',      # tool locations           visited by each pick-and-place, in the order that pick-and-places were performed
		'locs_component', # component tray locations visited by each pick-and-place, in the order that pick-and-places were performed
		'locs_assembly',  # assembly tray locations  visited by each pick-and-place, in the order that pick-and-places were performed
		                  # If the first pick-and-places takes the tool from tool location 1, picks up the component at location 1,
		                  # and puts it on the baseplate at location 1 (etc.,) then each of these will be [1, 2, 3, ... ]

		'tray_component_sensor', # ID of component tray used
		'tray_assembly',         # ID of assembly tray used
		'batch_araldite',        # ID of araldite batch used
	]

	@property
	def cure_duration(self):
		if (self.cure_stop is None) or (self.cure_start is None):
			return None
		else:
			return self.cure_stop - self.cure_start


class step_sensor(fsobj):
	FILEDIR    = os.sep.join(['steps','sensor','{century}'])
	FILENAME   = 'sensor_assembly_step_{ID:0>5}.json'
	PROPERTIES = [
		'user',             # name of person who performed step
		'step_start',       # unix time @ start of step
		'cure_start',       # unix time @ start of curing
		'cure_stop',        # unix time @ end of curing
		'cure_temperature', # Average temperature during curing (centigrade)
		'cure_humidity',    # Average humidity during curing (percent)

		'tools',        # list of pickup tool IDs, ordered by pickup tool location
		'sensors',      # list of sensor      IDs, ordered by component tray position
		'baseplates',   # list of baseplate   IDs, ordered by assembly tray position
		'protomodules', # list of protomodule IDs assigned to new modules, by assembly tray position

		'tool_pickups',         # tool locations           visited by pick-and-places, in the order that pick-and-places were performed
		'component_pickups',    # component tray locations visited by pick-and-places, in the order that pick-and-places were performed
		'component_placements', # assembly tray locations  visited by pick-and-places, in the order that pick-and-places were performed
		                        # If the first pick-and-places takes the tool from tool location 1, picks up the component at location 1,
		                        # and puts it on the protomodule at location 1 (etc.,) then each of these will be [1, 2, 3, ... ]

		'tray_component_sensor', # ID of component tray used
		'tray_assembly',         # ID of assembly tray used
		'batch_araldite',        # ID of araldite batch used
		'batch_silver',          # ID of silver epoxy batch used
	]

	@property
	def cure_duration(self):
		if (self.cure_stop is None) or (self.cure_start is None):
			return None
		else:
			return self.cure_stop - self.cure_start

	
class step_pcb(fsobj):
	...


###############################################
#####  components, protomodules, modules  #####
###############################################

class baseplate(fsobj):
	FILEDIR = os.sep.join(['baseplates','{century}'])
	FILENAME = "baseplate_{ID:0>5}.json"
	PROPERTIES = [
		"identifier",   # idenfitier given by manufacturer or distributor. not the same as ID!
		"material",     #
		"nomthickness", # nominal thickness
		"size",         # hexagon width, numerical. 6 or 8 (integers) for 6-inch or 8-inch
		"manufacturer", # 

		"protomodule",  # what protomodule (ID) it's a part of; None if not part of any
		"module",       # what module      (ID) it's a part of; None if not part of any

		"corner_heights", # list of corner heights
	]

	@property
	def flatness(self):
		if self.corner_heights is None:
			return None
		else:
			return max(self.corner_heights) - min(self.corner_heights)


class sensor(fsobj):
	FILEDIR = os.sep.join(['sensors','{century}'])
	FILENAME = "sensor_{ID:0>5}.json"
	PROPERTIES = [
		"identifier",
		"type",
		"size",
		"channels",
		"manufacturer",
		"protomodule",
		"module",
	]


class pcb(fsobj):
	FILEDIR = os.sep.join(['pcbs','{century}','pcb_{ID:0>5}'])
	FILENAME = "pcb_{ID:0>5}.json"
	PROPERTIES = [
		"identifier",
		"thickness",
		"flatness",
		"size",
		"channels",
		"manufacturer",
		"module",
		"daq_data"
	]

	PROPERTIES_DO_NOT_SAVE = [
		"daq_data",
	]

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

	def save(self):
		super(pcb,self).save()
		filedir, filename = self.get_filedir_filename(self.ID)
		if not os.path.exists(os.sep.join([filedir, self.DAQ_DATADIR])):
			os.makedirs(os.sep.join([filedir, self.DAQ_DATADIR]))
		self.fetch_datasets()

	def load_daq(self,which):
		if isinstance(which, int):
			which = self.daq_data[which]

		filedir, filename = self.get_filedir_filename()
		file = os.sep.join([filedir, self.DAQ_DATADIR, which])

		print('load {}'.format(file))

class protomodule(fsobj):
	...


class module(fsobj):
	FILEDIR    = os.sep.join(['modules','{century}','module_{ID:0>5}'])
	FILENAME   = 'module_{ID:0>5}.json'
	PROPERTIES = [
		"baseplate",
		"sensor",
		"protomodule",
		"pcb",

		"step_kapton",
		"step_sensor",
		"step_pcb",

		"thickness",
		"kaptontype",

		"iv_data",
		"daq_data",
	]
	PROPERTIES_DO_NOT_SAVE = [
		"iv_data",
		"daq_data",
	]

	IV_DATADIR      = 'iv'
	IV_BINS_DATADIR = 'bins'
	DAQ_DATADIR     = 'daq'

	BA_FILENAME = 'ba {}'
	BD_FILENAME = 'bd {}'


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


	def load(self, ID):
		success = super(module, self).load(ID)
		if success:
			self.fetch_datasets()
		return success


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
		print('load {}'.format(file))


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
		if load_a:
			file_a = os.sep.join([iv_bins_datadir, self.BA_FILENAME.format(which)])
			#data_a = numpy.loadtxt(file_a)
			print("load {}".format(file_a))
		if load_d:
			file_d = os.sep.join([iv_bins_datadir, self.BD_FILENAME.format(which)])
			#data_b = numpy.loadtxt(file_b)
			print("load {}".format(file_d))

		to_return = []
		if load_a:to_return.append(file_a) # replace with data_a, data_d after making it actually load stuff
		if load_d:to_return.append(file_d) #
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
		...


###############################################
##################  supplies  #################
###############################################

class batch_araldite(fsobj):
	FILEDIR = os.sep.join(['supplies','batch_araldite','{century}'])
	FILENAME = 'batch_araldite_{ID:0>5}.json'
	PROPERTIES = [
		'date_received',
		'date_expires',
	]

class batch_loctite(fsobj):
	FILEDIR = os.sep.join(['supplies','batch_loctite','{century}'])
	FILENAME = 'batch_loctite_{ID:0>5}.json'
	PROPERTIES = [
		'date_received',
		'date_expires',
	]

class batch_sylgard_thick(fsobj):
	FILEDIR = os.sep.join(['supplies','batch_sylgard_thick','{century}'])
	FILENAME = 'batch_sylgard_thick_{ID:0>5}.json'
	PROPERTIES = [
		'date_received',
		'date_expires',
	]

class batch_sylgard_thin(fsobj):
	FILEDIR = os.sep.join(['supplies','batch_sylgard_thin','{century}'])
	FILENAME = 'batch_sylgard_thin_{ID:0>5}.json'
	PROPERTIES = [
		'date_received',
		'date_expires',
	]

class batch_bond_wire(fsobj):
	FILEDIR = os.sep.join(['supplies','batch_bond_wire','{century}'])
	FILENAME = 'batch_bond_wire_{ID:0>5}.json'
	PROPERTIES = [
		'date_received',
		'date_expires',
	]





if __name__ == '__main__':

	m = module()
	m.load(30945)

	# ts = tool_sensor()
	# ts.load(0)
	# ts.comments = ['comment 1', 'comment 2', 'spam and eggs']
	# ts.save()

	# tp = tool_pcb()
	# tp.load(0)
	# tp.comments = ['pcb comment 1','spam egg sausage and spam','ni','nu']
	# tp.save()

	# ta = tray_assembly()
	# ta.new(0)
	# ta.save()

	# tcs = tray_component_sensor()
	# tcs.new(0)
	# tcs.save()

	# tcp = tray_component_pcb()
	# tcp.new(0)
	# tcp.save()