import os
import json
import numpy

BASEPLATE_MATERIALS_NO_KAPTON = ['pcb']

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

	DATADIR = data['datadir']
	MAC     = data['MAC']

loadconfig()



###############################################
############## fsobj base class ###############
###############################################

class fsobj(object):
	PROPERTIES_COMMON = [
		'comments',
		]

	DEFAULTS ={
	
	}

	DEFAULTS_COMMON = {
		'comments':[],
	}

	def __init__(self):
		super(fsobj, self).__init__()
		self.clear() # sets attributes to None


	def get_filedir_filename(self, ID = None):
		if ID is None:
			ID = self.ID
		filedir  = os.sep.join([ DATADIR, self.FILEDIR.format(ID=ID, century = CENTURY.format(ID//100)) ])
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
		DEFAULTS   = {**self.DEFAULTS, **self.DEFAULTS_COMMON}
		for prop in PROPERTIES:
			setattr(self, prop, DEFAULTS.get(prop, None))
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
		'num_sites',
	]


class tray_component_sensor(fsobj):
	FILEDIR = os.sep.join(['tooling','tray_component_sensor'])
	FILENAME = 'tray_component_sensor_{ID:0>5}.json'
	PROPERTIES = [
		'size',
		'num_sites',
	]


class tray_component_pcb(fsobj):
	FILEDIR = os.sep.join(['tooling','tray_component_pcb'])
	FILENAME = 'tray_component_pcb_{ID:0>5}.json'
	PROPERTIES = [
		'size',
		'num_sites',
	]




###############################################
###########  shipment and reception  ##########
###############################################

class shipment(fsobj):
	FILEDIR = os.sep.join(['shipments'])
	FILENAME = "shipment_{ID:0>5}.json"
	PROPERTIES = [
		"sender",
		"receiver",
		"date_sent",
		"date_received",

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
					... # create objects?
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
			del m




###############################################
#####  components, protomodules, modules  #####
###############################################

class baseplate(fsobj):
	FILEDIR = os.sep.join(['baseplates','{century}'])
	FILENAME = "baseplate_{ID:0>5}.json"
	PROPERTIES = [
		# shipments and location
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# characteristics (defined upon reception)
		"identifier",   # idenfitier given by manufacturer or distributor.
		"manufacturer", # name of company that manufactured this part
		"material",     # physical material
		"nomthickness", # nominal thickness
		"size",         # hexagon width, numerical. 6 or 8 (integers) for 6-inch or 8-inch
		"shape",        # 
		"chirality",    # 
		"rotation",     # 

		# kapton number
		"num_kaptons", # number of kaptons; 0/None for pcb baseplates, 0/None 1 or 2 for metal baseplates

		# baseplate qualification 
		"corner_heights",      # list of corner heights
		"kapton_tape_applied", # only for metal baseplates (not pcb baseplates)
		                       # True if kapton tape has been applied
		"thickness",           # measure thickness of baseplate

		# kapton application (1)
		"step_kapton", # ID of step_kapton that applied the kapton to it

		# kaptonized baseplate qualification (1)
		"check_leakage",    # None if not checked yet; True if passed; False if failed
		"check_surface",    # None if not checked yet; True if passed; False if failed
		"check_edges_firm", # None if not checked yet; True if passed; False if failed
		"check_glue_spill", # None if not checked yet; True if passed; False if failed
		"kapton_flatness",  # flatness of kapton layer after curing

		# kapton application (2) - for double kapton baseplates
		"step_kapton_2", # ID of the step_kapton that applied the second kapton

		# kaptonized baseplate qualification (2) - for double kapton baseplates
		"check_leakage_2",    # None if not checked yet; True if passed; False if failed
		"check_surface_2",    # None if not checked yet; True if passed; False if failed
		"check_edges_firm_2", # None if not checked yet; True if passed; False if failed
		"check_glue_spill_2", # None if not checked yet; True if passed; False if failed
		"kapton_flatness_2",  # flatness of kapton layer after curing

		# sensor application
		"step_sensor", # which step_sensor used it
		"protomodule", # what protomodule (ID) it's a part of; None if not part of any

		# Associations to other objects
		"module", # what module (ID) it's a part of; None if not part of any
	]

	DEFAULTS = {
		"shipments":[],
	}

	@property
	def flatness(self):
		if self.corner_heights is None:
			return None
		else:
			if None in self.corner_heights:
				return None
			else:
				return max(self.corner_heights) - min(self.corner_heights)

	def ready_step_kapton(self, step_kapton = None, max_flatness = None):
		...

	def ready_step_sensor(self, step_sensor = None, max_flatness = None):
		...

	# def ready_step_kapton(self, step_kapton=None):
	# 	if not (step_kapton is None):
	# 		if step_kapton == self.step_kapton:
	# 			return True, "baseplate {} already associated with step_kapton {}".format(self.ID, step_kapton)
	# 		else:
	# 			return False, "baseplate {} associated with step_kapton {}; cannot associate with step_kapton {}".format(self.ID, step_kapton, self.step_kapton)

	# 	if self.material is None:
	# 		return False, "baseplate {} material not set".format(self.ID)

	# 	if self.material in BASEPLATE_MATERIALS_NO_KAPTON:
	# 		return False, "baseplate {} material is {}; does not need kapton".format(self.ID, self.material)

	# 	if self.corner_heights is None:
	# 		return False, 

	# def ready_step_sensor(self):


class sensor(fsobj):
	FILEDIR = os.sep.join(['sensors','{century}'])
	FILENAME = "sensor_{ID:0>5}.json"
	PROPERTIES = [
		# shipments and location
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# characteristics (defined upon reception)
		"identifier",   # 
		"manufacturer", # 
		"type",         # 
		"size",         # 
		"channels",     # 
		"shape",        # 
		"rotation",     # 

		# sensor qualification
		"inspection", # None if not inspected yet; True if passed; False if failed

		# sensor step
		"step_sensor", # which step_sensor placed this sensor
		"protomodule", # which protomodule this sensor is a part of

		# associations to other objects
		"module", # which module this sensor is a part of
	]

	DEFAULTS = {
		"shipments":[],
	}


class pcb(fsobj):
	FILEDIR = os.sep.join(['pcbs','{century}','pcb_{ID:0>5}'])
	FILENAME = "pcb_{ID:0>5}.json"
	PROPERTIES = [
		# shipments and location
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# details / measurements / characteristics
		"identifier",   # 
		"manufacturer", # 
		"size",         # 
		"channels",     # 
		"shape",        # 
		"chirality",    # 
		"rotation",     # 

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
	FILEDIR = os.sep.join(['protomodules','{century}'])
	FILENAME = 'protomodule_{ID:0>5}.json'
	PROPERTIES = [
		# shipments and location
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# characteristics - taken from child parts upon creation of protomodule
		"thickness",   # sum of baseplate and sensor, plus glue gap
		"num_kaptons", # from baseplate
		"channels",    # from sensor
		"size",        # from baseplate or sensor (identical)
		"shape",       # from baseplate or sensor (identical)
		"chirality",   # from baseplate
		"rotation",    # from baseplate or sensor (identical)
		# initial location is also filled from child parts

		# sensor step - filled upon creation
		"step_sensor", # ID of sensor step
		"baseplate",   # ID of baseplate
		"sensor",      # ID of sensor

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
	}


class module(fsobj):
	FILEDIR    = os.sep.join(['modules','{century}','module_{ID:0>5}'])
	FILENAME   = 'module_{ID:0>5}.json'
	PROPERTIES = [
		# shipments and location
		"location",  # physical location of part
		"shipments", # list of shipments that this part has been in

		# characteristics - taken from child parts upon creation of module
		"thickness",   # sum of protomodule and sensor, plus glue gap
		"num_kaptons", # from protomodule
		"channels",    # from protomodule or pcb (identical)
		"size",        # from protomodule or pcb (identical)
		"shape",       # from protomodule or pcb (identical)
		"chirality",   # from protomodule or pcb (identical)
		"rotation",    # from protomodule or pcb (identical)
		# initial location is also filled from child parts

		# components and steps - filled upon creation
		"baseplate",     # 
		"sensor",        # 
		"protomodule",   # 
		"pcb",           # 
		"step_kapton",   # 
		"step_kapton_2", # 
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
	FILEDIR    = os.sep.join(['steps','kapton','{century}'])
	FILENAME   = 'kapton_assembly_step_{ID:0>5}.json'
	PROPERTIES = [
		'user_performed', # name of user who performed step
		'date_performed', # date step was performed
		
		'cure_start',       # unix time @ start of curing
		'cure_stop',        # unix time @ end of curing
		'cure_temperature', # Average temperature during curing (centigrade)
		'cure_humidity',    # Average humidity during curing (percent)

		'kaptons_inspected', # list of kapton inspection results, ordered by component tray location. should all be True (don't use a kapton if it doesn't pass)
		'tools',      # list of pickup tool IDs, ordered by pickup tool location
		'baseplates', # list of baseplate   IDs, ordered by assembly tray position

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

	def save(self):
		super(step_kapton, self).save()
		inst_baseplate = baseplate()
		
		for i in range(6):
			baseplate_exists = False if self.baseplates[i] is None else inst_baseplate.load(self.baseplates[i])
			if baseplate_exists:

				which_kapton_layer = None

				if (inst_baseplate.step_kapton is None) or (inst_baseplate.step_kapton == self.ID):
					which_kapton_layer = 1

				else:
					if (inst_baseplate.step_kapton_2 is None) or (inst_baseplate.step_kapton_2 == self.ID):
						which_kapton_layer = 2

				if which_kapton_layer is None:
					print("step_kapton cannot write ID {} to baseplate {}: already has two kapton steps")

				else:
					if which_kapton_layer == 1:
						inst_baseplate.step_kapton = self.ID
					elif which_kapton_layer == 2:
						inst_baseplate.step_kapton_2 = self.ID

					num_kaptons = 0
					if not (inst_baseplate.step_kapton   is None): num_kaptons += 1
					if not (inst_baseplate.step_kapton_2 is None): num_kaptons += 1
					inst_baseplate.num_kaptons = num_kaptons

					inst_baseplate.save()
					inst_baseplate.clear()

			else:
				if not (self.baseplates[i] is None):
					print("step_kapton {} cannot write to baseplate {}: does not exist".format(self.ID, self.baseplates[i]))




class step_sensor(fsobj):
	FILEDIR    = os.sep.join(['steps','sensor','{century}'])
	FILENAME   = 'sensor_assembly_step_{ID:0>5}.json'
	PROPERTIES = [
		'user_performed', # name of user who performed step
		'date_performed', # date step was performed
		
		'cure_start',       # unix time @ start of curing
		'cure_stop',        # unix time @ end of curing
		'cure_temperature', # Average temperature during curing (centigrade)
		'cure_humidity',    # Average humidity during curing (percent)

		'tools',        # list of pickup tool IDs, ordered by pickup tool location
		'sensors',      # list of sensor      IDs, ordered by component tray position
		'baseplates',   # list of baseplate   IDs, ordered by assembly tray position
		'protomodules', # list of protomodule IDs assigned to new protomodules, by assembly tray location

		'tray_component_sensor', # ID of component tray used
		'tray_assembly',         # ID of assembly  tray used
		'batch_araldite',        # ID of araldite batch used
		'batch_loctite',         # ID of loctite  batch used
	]


	@property
	def cure_duration(self):
		if (self.cure_stop is None) or (self.cure_start is None):
			return None
		else:
			return self.cure_stop - self.cure_start

	def save(self):
		super(step_sensor, self).save()
		inst_baseplate   = baseplate()
		inst_sensor      = sensor()
		inst_protomodule = protomodule()

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
				inst_protomodule.num_kaptons = inst_baseplate.num_kaptons if baseplate_exists else None
				inst_protomodule.channels    = inst_sensor.channels       if sensor_exists    else None
				inst_protomodule.size        = inst_baseplate.size        if baseplate_exists else None
				inst_protomodule.shape       = inst_baseplate.shape       if baseplate_exists else None
				inst_protomodule.chirality   = inst_baseplate.chirality   if baseplate_exists else None
				inst_protomodule.rotation    = inst_baseplate.rotation    if baseplate_exists else None
				inst_protomodule.location    = MAC
				inst_protomodule.step_sensor = self.ID
				inst_protomodule.baseplate   = self.baseplates[i]
				inst_protomodule.sensor      = self.sensors[i]
				inst_protomodule.save()

				if not all([baseplate_exists,sensor_exists]):
					print("WARNING: trying to save step_sensor {}. Some parts do not exist. Could not create all associations.")
					print("baseplate:{} sensor:{}".format(inst_baseplate.ID,inst_sensor.ID))
			
			inst_baseplate.clear()
			inst_sensor.clear()
			inst_protomodule.clear()




class step_pcb(fsobj):
	FILEDIR = os.sep.join(['steps','pcb','{century}'])
	FILENAME = 'pcb_assembly_step_{ID:0>5}.json'
	PROPERTIES = [
		'user_performed', # name of user who performed step
		'date_performed', # date step was performed
		
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
				print("PCB EXISTS")
				inst_pcb.step_pcb = self.ID
				inst_pcb.module = self.modules[i]
				inst_pcb.save()

			if protomodule_exists:
				print("PROTOMODULE EXISTS")
				inst_protomodule.step_pcb = self.ID
				inst_protomodule.module = self.modules[i]
				inst_protomodule.save()

				baseplate_exists = False if (inst_protomodule.baseplate is None) else inst_baseplate.load(inst_protomodule.baseplate)
				sensor_exists    = False if (inst_protomodule.sensor    is None) else inst_sensor.load(   inst_protomodule.sensor   )

				if baseplate_exists:
					print("BASEPLATE EXISTS")
					inst_baseplate.module = self.modules[i]
					inst_baseplate.save()

				if sensor_exists:
					print("SENSOR EXISTS")
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
				inst_module.step_kapton_2 = inst_baseplate.step_kapton_2 if baseplate_exists   else None
				inst_module.step_sensor = inst_protomodule.step_sensor if protomodule_exists else None
				inst_module.step_pcb    = self.ID
				inst_module.num_kaptons = inst_baseplate.num_kaptons if baseplate_exists else None
				inst_module.channels    = inst_sensor.channels       if sensor_exists    else None
				inst_module.size        = inst_pcb.size              if pcb_exists       else None
				inst_module.shape       = inst_pcb.shape             if pcb_exists       else None
				inst_module.chirality   = inst_pcb.chirality         if pcb_exists       else None
				inst_module.rotation    = inst_pcb.rotation          if pcb_exists       else None
				inst_module.location    = MAC
				inst_module.save()

				if not all([baseplate_exists, sensor_exists, pcb_exists, protomodule_exists]):
					print("WARNING: trying to save step_pcb {}. Some parts do not exist. Could not create all associations.".format(self.ID))
					print("baseplate:{} sensor:{} pcb:{} protomodule:{} module:{}".format(inst_baseplate.ID,inst_sensor.ID,inst_pcb.ID,inst_protomodule.ID,inst_module.ID))




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
	# test features without UI here
	...
