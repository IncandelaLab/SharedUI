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
import jinja2

#import rhapi_nolock as rh
from xml.dom import minidom


from filemanager import fm


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




### PARENT CLASS FOR PARTS


class fsobj_part(fm.fsobj):
	# COND_TABLE varies, defined in each class
	# Table names:  CMS_HGC_HGCAL_COND.x
	# baseplates:  SI_MODULE_BASEPLATE
	# sensors:     SI_MODULE_SENSOR
	# PCBs:        FLATNS_PBC_ROCS_DATA
	# protomods:   HGC_PRTO_MOD_ASMBLY_COND
	# mods:        HGC_MOD_ASMBLY_COND


	PART_PROPERTIES = [
		# upload file:
		'kind_of_part',  # Note:  each class has a different EXTRA_DEFAULT value
		'record_insertion_user',
		'location',
		'comment_description',
		# cond file:  header
		'initiated_by_user',
		# note: run_begin/end_timestamp defined below
		# cond file:  data_set
		'flatness',
		'thickness',
		'grade',
		'comments',
	]

	PART_DEFAULTS = {
		'comments': '',
		'comment_description': '',  # Currently unused
	}

	# Properties unique to class
	EXTRA_PROPERTIES = []
	EXTRA_DEFAULTS = {}


	def __init__(self):
		self.PROPERTIES = self.PART_PROPERTIES + self.EXTRA_PROPERTIES
		self.DEFAULTS = {**self.PART_DEFAULTS, **self.EXTRA_DEFAULTS}  #self.PART_DEFAULTS | self.EXTRA_DEFAULTS  # | == incl or
		super(fsobj_part, self).__init__()


	#### NOTE - WIP - may need to redefine
	# property institution_id() - use INSTITUTION_DICT, +setter (set inst from ID)

	# Note:  Comments have max 4k chars

	@property
	def comments_upload(self):
		# NOTE:  Can't upload empty string, so...
		if self.comments is None:  return "None"
		if self.comments == "":  return "None"
		return self.comments[:4000] if len(self.comments)>4000 else self.comments

	@property
	def run_begin_timestamp_(self):
		if getattr(self, 'run_begin_timestamp', None) is None:
			return str(datetime.datetime.now())
		else:
			return self.run_begin_timestamp

	@property
	def run_end_timestamp_(self):
		if getattr(self, 'run_end_timestamp', None) is None:
			return str(datetime.datetime.now())
		else:
			return self.run_end_timestamp

	@property
	def run_begin_date_(self):
		if getattr(self, 'run_begin_date', None) is None:
			return str(datetime.datetime.now())
		else:
			return self.run_begin_date

	@property
	def run_end_date_(self):
		if getattr(self, 'run_end_date', None) is None:
			return str(datetime.datetime.now())
		else:
			return self.run_end_date


###############################################
#####  components, protomodules, modules  #####
###############################################

class baseplate(fsobj_part):
	OBJECTNAME = "baseplate"
	FILEDIR = os.sep.join(['baseplates','{date}'])
	FILENAME = "baseplate_{ID}.json"

	XML_TEMPLATES = [
		'build_upload.xml',
		'cond_upload.xml',
	]

	# Note:  serial_number == self.ID

	# NEW:  All common PROPERTIES are set in parent class, inherited
	# Specify only baseplate-specific properties
	EXTRA_PROPERTIES = [
		# build_upload file:
		'manufacturer',
		# build_cond file:
		# other:
		'protomodule',
		'step_sensor',
		# GUI-only:
		'barcode',
	]

	EXTRA_DEFAULTS = {
		# display_name ->
		"kind_of_part": "None Baseplate None None"
	}


	# Commented for now - wait for API implementation
	#LOCAL_PROPERTIES = [
	#	# Locally-saved, not part of DB:
	#	"institution_location",  # location at institution
	#	"protomodule",  # TBD
	#	"module",
	#]


	# Derived properties:
    # geometry (from display_name)
	# material
	# channel density

	@property
	def geometry(self):
		if self.kind_of_part == "None Baseplate None None":  return None
		return self.kind_of_part.split()[3]
	@geometry.setter
	def geometry(self, value):
		splt = self.kind_of_part.split(" ")
		splt[3] = str(value)
		self.kind_of_part = " ".join(splt)

	@property
	def material(self):
		return self.kind_of_part.split()[0]
	@material.setter  # eventually, these will not be used
	def material(self, value):
		# Cannot replace bc of case w/ multiple Nones
		# split, then change and recombine
		splt = self.kind_of_part.split(" ")
		splt[0] = str(value)
		self.kind_of_part = " ".join(splt)

	@property
	def channel_density(self):
		if self.kind_of_part == "None Baseplate None None":  return None
		return self.kind_of_part.split()[2]
	@channel_density.setter
	def channel_density(self, value):
		splt = self.kind_of_part.split(" ")
		splt[2] = str(value)
		self.kind_of_part = " ".join(splt)


	def ready_step_sensor(self, step_sensor = None):
		# POSSIBLE:  Query DB to check for sensors?
		# unless this is already done via goto/etc...
		if self.step_sensor and self.step_sensor != step_sensor:
			return False, "already assigned to protomodule {}".format(self.protomodule)
		return True, ""


class sensor(fsobj_part):
	OBJECTNAME = "sensor"
	FILEDIR = os.sep.join(['sensors','{date}'])
	FILENAME = "sensor_{ID}.json"

	XML_TEMPLATES = [
		'build_upload.xml',
		'cond_upload.xml',
	]

	# Note:  serial_number == self.ID

	# NEW:  All common PROPERTIES are set in parent class, inherited
	# Specify only baseplate-specific properties
	EXTRA_PROPERTIES = [
		# build_upload file:
		# build_cond file:
		# Note:  'tested_by' = record_insertion_user
		# run_begin_date_ is a property
		'visual_inspection',
		'test_files', #_name',
		# other:
		'protomodule',
		'step_sensor',
		# GUI only:
		'barcode',
	]

	EXTRA_DEFAULTS = {
		# display_name ->
		"kind_of_part": "None Si Sensor None None"
	}


	# Returns sensor thickness in mm
	@property  # Note: not a measured value
	def thickness_float(self):
		thkns = self.sen_type.split('um')[0]
		if thkns == "None":
			return None
		else:
			return float(thkns)/1000

	@property
	def sen_type(self):
		if self.kind_of_part is None:  return None
		return self.kind_of_part.split()[0]
	@sen_type.setter  # eventually, these will not be used
	def sen_type(self, value):
		# NOTE:  This is a string, eg 200um
		# Cannot replace bc of case w/ multiple Nones
		# split, then change and recombine
		splt = self.kind_of_part.split(" ")
		splt[0] = value
		splt[3] = "HD" if value == "120um" else "LD"
		self.kind_of_part = " ".join(splt)

	@property
	def geometry(self):
		if self.kind_of_part is None:  return None
		return self.kind_of_part.split()[4]
	@geometry.setter
	def geometry(self, value):
		splt = self.kind_of_part.split(" ")
		splt[4] = str(value)
		self.kind_of_part = " ".join(splt)


	@property
	def channel_density(self):
		if self.kind_of_part is None:  return None
		return self.kind_of_part.split()[3]

	@property
	def test_date_(self):
		return str(datetime.date.today())

	def ready_step_sensor(self, step_sensor = None):
		if self.step_sensor and self.step_sensor != step_sensor:
			return False, "already assigned to protomodule {}".format(self.protomodule)

		# Kapton qualification checks:
		errstr = ""
		checks = [
			True, #self.inspection == "pass",
		]
		#if self.kapton_flatness is None:
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
	OBJECTNAME = "pcb"
	FILEDIR = os.sep.join(['pcbs','{date}'])
	FILENAME = "pcb_{ID}.json"

	XML_TEMPLATES = [
		'build_upload.xml',
		'cond_upload.xml',
	]

	# Note:  serial_number == self.ID

	# NEW:  All common PROPERTIES are set in parent class, inherited
	# Specify only baseplate-specific properties
	EXTRA_PROPERTIES = [
		# build_upload file:
		# build_cond file:
		# run_begin_date_ is a property
		'test_files',
		# other:
		'module',
		'step_pcb',
		# GUI only:
		'barcode',
	]

	EXTRA_DEFAULTS = {
		"kind_of_part": "PCB None None",
	}


	# no mat_type
	@property
	def channel_density(self):
		if self.kind_of_part == "PCB None None":  return None
		return self.kind_of_part.split()[1]
	@channel_density.setter
	def channel_density(self, value):
		splt = self.kind_of_part.split(" ")
		splt[1] = str(value)
		self.kind_of_part = " ".join(splt)

	@property
	def geometry(self):
		if self.kind_of_part == "PCB None None":  return None
		return self.kind_of_part.split()[2]
	@geometry.setter
	def geometry(self, value):
		splt = self.kind_of_part.split(" ")
		splt[2] = str(value)
		self.kind_of_part = " ".join(splt)

	@property
	def test_date_(self):
		return str(datetime.date.today())

	def ready_step_pcb(self, step_pcb = None):
		if self.step_pcb and self.step_pcb != step_pcb:
			return False, "already assigned to module {}".format(self.module)
		return True, ""




class protomodule(fsobj_part):
	OBJECTNAME = "protomodule"
	FILEDIR = os.sep.join(['protomodules','{date}'])
	FILENAME = "protomodule_{ID}.json"

	XML_TEMPLATES = [
		'build_upload.xml',
		'cond_upload.xml',
		'assembly_upload.xml',
	]

	# Note:  serial_number == self.ID

	# NEW:  All common PROPERTIES are set in parent class, inherited
	# Specify only baseplate-specific properties
	EXTRA_PROPERTIES = [
		# build_upload file:
		# build_cond file:
		# run_begin_date_ is a property
		# other:
		'baseplate', # serial, not actual object
		'sensor',
		'module',
		'step_sensor',
		'step_pcb',

		# Properties for assembly data:
		# Read/write from cond:
		'run_begin_timestamp',  # note:  start/end of assembly run, not curing
		'run_end_timestamp',
		"asmbl_tray_name",
		"plt_ser_num",
		#"plt_asm_row", # property
		#"plt_asm_col", # property
		"comp_tray_name",
		"snsr_ser_num",
		#"snsr_cmp_row", # property
		#"snsr_cmp_col", # property
		"snsr_x_offst",
		"snsr_y_offst",
		"snsr_ang_offst",
		"snsr_tool_name",
		"snsr_tool_ht_set",
		"snsr_tool_ht_chk",
		"glue_type", # araldite
		"glue_batch_num",
		"slvr_epxy_type",
		"slvr_epxy_batch_num",
		"grade",
		"snsr_tool_feet_chk",
		"batch_tape_50",
		"batch_tape_120",

		# for cond page:
		#"curing_time_hrs",  # property
		"cure_begin_timestamp",
		"cure_end_timestamp",
		"temp_degc",
		"humidity_prcnt",
		#'test_file_name',  # now 'xml_file_name' in step only
	]

	EXTRA_DEFAULTS = {
		"kind_of_part": "None None Si ProtoModule None None",
		"glue_type": "Araldite",
		"snsr_tool_ht_set": 0,
		"snsr_tool_ht_chk": 0,
	}


	@property
	def curing_time_hrs(self):
		if self.cure_begin_timestamp is None: return None
		t_begin = datetime.datetime.strptime(self.cure_begin_timestamp, "%Y-%m-%d %H:%M:%S%z")
		t_end   = datetime.datetime.strptime(self.cure_end_timestamp,   "%Y-%m-%d %H:%M:%S%z")
		return (t_end - t_begin).seconds/(3600.0) + (t_end - t_begin).days * 24


	# PROPERTIES:
	# Required to set kind_of_part:  geometry, sen_type (sets chann density), baseplate_material (sets calo type)

	@property
	def geometry(self):
		if self.kind_of_part == "None None Si ProtoModule None None":  return None
		return self.kind_of_part.split()[5]
	@geometry.setter
	def geometry(self, value):
		splt = self.kind_of_part.split(" ")
		splt[5] = str(value)
		self.kind_of_part = " ".join(splt)

	# Note:  baseplate_material determines calorimeter_type!
	@property
	def baseplate_material(self):  # avoid accessing it without setter
		if self.kind_of_part == "None None Si ProtoModule None None":  return None
		em_or_had = self.kind_of_part.split()[0]
		return 'CuW/Kapton' if em_or_had == 'EM' else 'PCB/Kapton'
	@baseplate_material.setter
	def baseplate_material(self, value):
		# CuW -> EM, PCB -> HAD, CF -> HAD
		splt = self.kind_of_part.split(" ")
		splt[0] = 'EM' if value == 'CuW/Kapton' else 'HAD'
		self.kind_of_part = " ".join(splt)

	# Note:  sen_type determines HD/LD!
	@property
	def sen_type(self):
		if self.kind_of_part == "None None Si ProtoModule None None":  return None
		print("SEN_TYPE: type is", self.kind_of_part)
		return self.kind_of_part.split()[1]
	@sen_type.setter
	def sen_type(self, value):
		splt = self.kind_of_part.split(" ")
		splt[1] = str(value)
		splt[4] = "HD" if value == "120um" else "LD"
		self.kind_of_part = " ".join(splt)

	@property
	def calorimeter_type(self):
		if self.kind_of_part == "None None Si ProtoModule None None":  return None
		return self.kind_of_part.split()[0]

	@property
	def channel_density(self):
		if self.kind_of_part == "None None Si ProtoModule None None":  return None
		return self.kind_of_part.split()[4]


	# Note:  thickness_nominal is 100, 300, etc.  'thickness' = actual measured thickness
	@property
	def thickness_nominal(self):
		if self.sen_type is None:  return None
		print("thickness_nom:  split sen type is", self.sen_type.split('um'))
		return float(self.sen_type.split('um')[0])/1000


	@property
	def kind_of_part_baseplate(self):
		tmp_baseplate = baseplate()
		if not tmp_baseplate.load(self.baseplate):  return None
		return tmp_baseplate.kind_of_part

	@property
	def kind_of_part_sensor(self):
		tmp_sensor = sensor()
		if not tmp_sensor.load(self.sensor):  return None
		return tmp_sensor.kind_of_part



	## Assembly data properties:


	# return position in GUI, 0-5
	@property
	def tray_posn(self):
		# If has a sensor step, grab the position of this sensor and return it here...
		if self.step_sensor is None:
			print("Warning:  assm_tray_posn:  no sensor step yet")
			return "None"
		from filemanager import assembly # avoid circular import
		temp_sensor_step = assembly.step_sensor()
		found = temp_sensor_step.load(self.step_sensor)
		assert found, "ERROR in tray_posn:  module has pcb step {}, but none found!".format(self.step_pcb)
		position = temp_sensor_step.protomodules.index(self.ID)
		return position

	@property
	def asm_row(self):
		posn = self.tray_posn
		print("in plt_asm_row: tray posn is:", posn)
		if posn == "None":  return posn
		else:  return posn%2+1

	@property
	def asm_col(self):
		posn = self.tray_posn
		if posn == "None": return posn
		else:  return posn//3+1

	@property
	def adhesive_type(self):
		if self.batch_tape_50 != None:
			return self.batch_tape_50 + ";;" + self.batch_tape_120
		else:
			return self.glue_batch_num


	## Functions

	# new():  Optionally, create proto from baseplate and sensor objects
	# Note:  baseplate and sensor must be the actual objects, not IDs
	def new(self, ID, baseplate_=None, sensor_=None):
		super(protomodule, self).new(ID)
		# if no sensor/baseplate, create and return normally
		if not baseplate_ and not sensor_:  return
		# if not all of the above, throw error
		assert baseplate_ and sensor_, "Error creating protomodule: baseplate is {}, sensor is {}, sensor step is {}".format(baseplate_, sensor_)

		# if baseplate and sensor, auto-fill protomodule type, plus baseplate, sensor fields:
		self.baseplate = baseplate_.ID
		self.sensor = sensor_.ID
		self.location = baseplate_.location
		self.geometry = baseplate_.geometry
		self.baseplate_material = baseplate_.material
		self.sen_type = sensor_.sen_type
		# Finally, add proto as parent to baseplate/sensor
		baseplate_.protomodule = self.ID
		baseplate_.save()
		sensor_.protomodule = self.ID
		sensor_.save()

	def generate_xml(self):
		# Make sure that all required info is present
		# if step_sensor.is_complete (or something similar)...
		super(protomodule, self).generate_xml()


	def ready_step_pcb(self, step_pcb = None):
		if self.step_pcb and self.step_pcb != step_pcb:
			return False, "already assigned to module {}".format(self.module)
		return True, ""

		


class module(fsobj_part):
	OBJECTNAME = "module"
	FILEDIR = os.sep.join(['modules','{date}'])
	FILENAME = "module_{ID}.json"

	XML_TEMPLATES = [
		'build_upload.xml',
		'cond_upload.xml',
		'assembly_upload.xml',
		'wirebond_upload.xml',
	]

	# Note:  serial_number == self.ID

	# NEW:  All common PROPERTIES are set in parent class, inherited
	# Specify only baseplate-specific properties
	EXTRA_PROPERTIES = [
		# general:
		"baseplate",
		"sensor",
		"pcb",  # add baseplate, etc?
		"protomodule",
		"step_sensor",
		"step_pcb",

		# Currently not used in XML/uploading
		"test_files",

		# for assembly page:
		"run_begin_timestamp",
		"run_end_timestamp",
		"asmbl_tray_name",
		"comp_tray_name",
		"pcb_ser_num",
		#"pcb_cmp_row", # property
		#"pcb_cmp_col", # property
		"pcb_tool_name",
		"pcb_tool_ht_set",
		"pcb_tool_ht_chk",
		"glue_type",
		"glue_batch_num",
		"pcb_tool_feet_chk",
		"mod_grade",
		"pcb_plcment_x_offset",
		"pcb_plcment_y_offset",
		"pcb_plcment_ang_offset",
		"batch_tape_50",
		"batch_tape_120",

		# for cond page:
		"cure_begin_timestamp",
		"cure_end_timestamp",
		#"time_start",  # run_begin_timestamp?
		#"time_stop",
		"temp_degc",
		"humidity_prcnt",

		# wirebonding:
		"bond_wire_batch_num",
		"pre_inspection",
		"sylgard_batch",
		"wedge_batch",
		"back_bonds",
		"back_bonds_date",
		"back_bonds_user",
		"back_unbonded",
		"back_bond_inspxn",
		"back_repair_user",
		"front_bonds",
		"front_bonds_date",
		"front_bonds_user",
		"front_skip",
		"front_unbonded",
		"front_bond_inspxn",
		"front_repair_user",
		"back_encap",
		"back_encap_user",
		"back_encap_cure_start",
		"back_encap_cure_stop",
		"back_encap_inspxn",
		"front_encap",
		"front_encap_user",
		"front_encap_cure_start",
		"front_encap_cure_stop",
		"front_encap_inspxn",
		"is_test_bond_module",
		"bond_pull_user",
		"bond_pull_avg",
		"bond_pull_stddev",
		"final_inspxn_user",
		"final_inspxn_ok",
		"wirebond_comments",
		"encapsulation_comments",
	]

	EXTRA_DEFAULTS = {
		"kind_of_part": "None None Si Module None None",
		"wirebond_comments": [],
		"encapsulation_comments": [],
		"snsr_tool_ht_set": 0,
		"snsr_tool_ht_chk": 0,
	}



	# Properties are same as protomodule's
	# Note:  set kind_of_part with geometry, sen_type, baseplate_material (all from proto)

	@property
	def curing_time_hrs(self):
		if self.cure_begin_timestamp is None: return None
		t_begin = datetime.datetime.strptime(self.cure_begin_timestamp, "%Y-%m-%d %H:%M:%S%z")
		t_end   = datetime.datetime.strptime(self.cure_end_timestamp,   "%Y-%m-%d %H:%M:%S%z")
		return (t_end - t_begin).seconds/(3600.0) + (t_end - t_begin).days * 24

	@property
	def geometry(self):
		if self.kind_of_part is None:  return None
		return self.kind_of_part.split()[5]
	@geometry.setter
	def geometry(self, value):
		splt = self.kind_of_part.split(" ")
		splt[5] = str(value)
		self.kind_of_part = " ".join(splt)

	# Note:  sen_type determines channel_density!
	@property
	def sen_type(self):
		return self.kind_of_part.split()[1]
	@sen_type.setter
	def sen_type(self, value):
		splt = self.kind_of_part.split(" ")
		splt[1] = str(value)
		print("sen_type setter: splt, value is", splt, value)
		splt[4] = "HD" if value == "120um" else "LD"
		self.kind_of_part = " ".join(splt)

	# Note:  baseplate_material determines calorimeter_type!
	@property
	def baseplate_material(self):  # avoid accessing it without setter
		if self.kind_of_part == "None None Si Module None None":  return None
		em_or_had = self.kind_of_part.split()[0]
		return 'CuW/Kapton' if em_or_had == 'EM' else 'PCB/Kapton'
	@baseplate_material.setter
	def baseplate_material(self, value):
		# CuW -> EM, PCB -> HAD, CF -> HAD
		splt = self.kind_of_part.split(" ")
		splt[0] = 'EM' if value == 'CuW/Kapton' else 'HAD'
		self.kind_of_part = " ".join(splt)

	@property
	def calorimeter_type(self):
		if self.kind_of_part == "None None Si Module None None":  return None
		return self.kind_of_part.split()[0]

	@property
	def channel_density(self):
		if self.kind_of_part == "None None Si Module None None":  return None
		return self.kind_of_part.split()[4]


	@property
	def kind_of_part_pcb(self):
		tmp_pcb = pcb()
		if not tmp_pcb.load(self.pcb):  return None
		return tmp_pcb.kind_of_part

	@property
	def kind_of_part_protomodule(self):
		tmp_proto = protomodule()
		if not tmp_proto.load(self.protomodule):  return None
		return tmp_proto.kind_of_part


	# TEMPORARY:  NOTE:  Must fix this...
	@property
	def wirebonding_compled(self):
		return self.back_bond_inspxn and \
		       self.front_bond_inspxn and \
		       self.back_encap_inspxn and \
               self.front_encap_inspxn and \
		       self.final_inspxn_ok == 'pass'


	# return position in GUI, 0-5
	@property
	def tray_posn(self):
		# If has a pcb step, grab the position of this mod and return it here...
		if self.step_pcb is None:
			print("Warning:  tray_posn:  no pcb step yet")
			return "None"
		from filemanager import assembly
		temp_pcb_step = assembly.step_pcb()
		found = temp_pcb_step.load(self.step_pcb)
		assert found, "ERROR in tray_posn:  module has pcb step {}, but none found!".format(self.step_pcb)
		position = temp_pcb_step.modules.index(self.ID)
		return position

	@property
	def asm_row(self):
		posn = self.tray_posn
		if posn == "None":  return posn
		else:  return posn%2+1

	@property
	def asm_col(self):
		posn = self.tray_posn
		if posn == "None": return posn
		else:  return posn//3+1

	@property
	def pcb_thickness(self):
		return None

	@property
	def wirebond_comments_concat(self):
		return ";;".join(self.wirebond_comments)
	
	@property
	def wirebonding_completed(self):
		print("back {} inspxn {}\nfront {} inspxn {}\nbacken {} fronen {}\nfinal {}".format(self.back_bonds, self.back_bond_inspxn, self.front_bonds, self.front_bond_inspxn, self.back_encap_inspxn, self.front_encap_inspxn, self.final_inspxn_ok))
		return self.back_bonds and \
		self.back_bond_inspxn and \
		self.front_bonds and \
		self.front_bond_inspxn and \
		self.back_encap_inspxn == 'pass' and \
		self.front_encap_inspxn == 'pass' and \
		self.final_inspxn_ok == 'pass'

	@property
	def adhesive_type(self):
		if self.batch_tape_50 != None:
			return self.batch_tape_50 + ";;" + self.batch_tape_120
		else:
			return self.glue_batch_num


	# new():  Optionally, create proto from baseplate and sensor objects
	# Note:  baseplate and sensor must be the actual objects, not IDs
	# NOTE:  Must also set sensor step ID!  (Implement into this?)
	def new(self, ID, pcb_=None, protomodule_=None):
		super(module, self).new(ID)
		if not pcb_ and not protomodule_:  return
		assert pcb_ or protomodule_, "Error creating module: pcb is {}, protomodule is {}".format(pcb_, protomodule_)

		# Perform some checks
		errs = []
		if pcb_.geometry != protomodule_.geometry:
			errs.append("PCB geometry {} does not match protomodule geometry {}".format(pcb_.geometry, protomodule_.geometry))
		if pcb_.channel_density != protomodule_.channel_density:
			errs.append("PCB channel density {} does not match protomodule channel density {}".format(pcb_.channel_density, protomodule_.channel_density))
		if not pcb_.ready_step_pcb():
			errs.append("PCB is already mounted on module {}, PCB step {}!".format(pcb_.module, pcb.step_pcb))
		if not protomodule_.ready_step_pcb():
			errs.append("Protomodule is already mounted on module {}, PCB step {}!".format(protomodule.module, protomodule_.step_pcb))

		if len(errs) > 0:
			self.clear()
			print("ERROR:  Module {} not created from PCB {} and protomodule {}!  Errors:".format(self.ID, pcb_.ID, protomodule_.ID))
			print("\n".join(errs))
			return

		# if baseplate and sensor, auto-fill protomodule type, plus baseplate, sensor fields:
		self.baseplate = protomodule_.baseplate
		self.sensor = protomodule_.sensor
		self.pcb = pcb_.ID
		self.protomodule = protomodule_.ID
		self.location = protomodule_.location
		self.geometry = pcb_.geometry
		self.baseplate_material = protomodule_.baseplate_material
		self.sen_type = protomodule_.sen_type


	def generate_xml(self):
		# Make sure that all required info is present
		# if step_sensor.is_complete (or something similar)...
		# ALSO, check wirebonding finished
		super(module, self).generate_xml()



