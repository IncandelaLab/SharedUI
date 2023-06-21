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
# For DB requests:
import cx_Oracle
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
		'comments': [],
		'comment_description': [],  # Currently unused
	}

	# Properties unique to class
	EXTRA_PROPERTIES = []
	EXTRA_DEFAULTS = {}


	def __init__(self):
		self.PROPERTIES = self.PART_PROPERTIES + self.EXTRA_PROPERTIES
		self.DEFAULTS = self.PART_DEFAULTS | self.EXTRA_DEFAULTS  # | == incl or
		super(fsobj_part, self).__init__()


	#### NOTE - WIP - may need to redefine
	# property institution_id() - use INSTITUTION_DICT, +setter (set inst from ID)

	# Note:  Comments have max 4k chars
	@property
	def comment_description_concat(self):
		catstr = ';;'.join(self.comment_description)
		return catstr[:4000] if len(catstr)>4000 else catstr

	@property
	def comments_concat(self):
		catstr = ';;'.join(self.comments)
		return catstr[:4000] if len(catstr)>4000 else catstr

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
	# material (from display_name)
	# geometry
	# channel density


	@property
	def mat_type(self):
		return self.kind_of_part.split()[0]
	@mat_type.setter  # eventually, these will not be used
	def mat_type(self, value):
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

	@property
	def geometry(self):
		if self.kind_of_part == "None Baseplate None None":  return None
		return self.kind_of_part.split()[3]
	@geometry.setter
	def geometry(self, value):
		splt = self.kind_of_part.split(" ")
		splt[3] = str(value)
		self.kind_of_part = " ".join(splt)

	def ready_step_sensor(self, step_sensor = None, max_flatness = None):
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
		'test_file_name',
		# other:
		'protomodule',
		'step_sensor',
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
		return self.kind_of_part.split()[0]
	@sen_type.setter  # eventually, these will not be used
	def sen_type(self, value):
		# NOTE:  This is a string, eg 200um
		# Cannot replace bc of case w/ multiple Nones
		# split, then change and recombine
		splt = self.kind_of_part.split(" ")
		splt[0] = value
		self.kind_of_part = " ".join(splt)
		self.thickness = self.thickness_float

	@property
	def channel_density(self):
		if self.kind_of_part is None:  return None
		return self.kind_of_part.split()[3]
	@channel_density.setter
	def channel_density(self, value):
		splt = self.kind_of_part.split(" ")
		splt[3] = str(value)
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
	def test_date_(self):
		return str(datetime.date.today())

	# Should not be passing any of these params yet
	def ready_step_sensor(self, step_sensor = None, max_flatness = None):
		if self.step_sensor and self.step_sensor != step_sensor:
			return False, "already assigned to protomodule {}".format(self.protomodule)

		# Kapton qualification checks:
		errstr = ""
		checks = [
			self.inspection == "pass",
		]
		#if self.kapton_flatness is None:
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
		'test_file_name',
		# other:
		'module',
		'step_pcb',
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
		'test_file_name',
		# other:
		'baseplate', # serial
		'sensor',
		'module',
		'step_sensor',
		'step_pcb',
		# Properties for assembly data:
		# Read/write from cond:
		"asmbl_tray_name",
		"plt_ser_num",
		#"plt_asm_row", # property
		#"plt_asm_col", # property
		"plt_fltnes_mm",
		"plt_thknes_mm",
		"comp_tray_name",
		"snsr_ser_num",
		#"snsr_cmp_row", # property
		#"snsr_cmp_col", # property
		"snsr_x_offst",
		"snsr_y_offst",
		"snsr_ang_offset",
		"snsr_tool_name",
		"snsr_tool_ht_set",
		"snsr_tool_ht_chk",
		"glue_type",
		"glue_batch_num",
		"slvr_epxy_type",
		"slvr_epxy_batch_num",
		"grade",
		"snsr_tool_feet_chk",
		"sensor_step",
		# for cond page:
		"curing_time_hrs",
		"time_start",
		"time_stop",
		"temp_degc",
		"humidity_prcnt",
	]

	EXTRA_DEFAULTS = {
		"kind_of_part": "None None Si ProtoModule None None",
	}




	# TODO : name this, decide whether to auto-set or manually set type
	@property
	def calorimeter_type(self):
		if self.kind_of_part == "None None Si ProtoModule None None":  return None
		return self.kind_of_part.split()[0]
	@calorimeter_type.setter
	def calorimeter_type(self, value):
		splt = self.kind_of_part.split(" ")
		splt[0] = str(value)
		self.kind_of_part = " ".join(splt)

	# Note:  baseplate_material determines calorimeter_type!
	@property
	def baseplate_material(self):
		if self.kind_of_part == "None None Si ProtoModule None None":  return None
		em_or_had = self.kind_of_part.split()[0]
		return 'CuW/Kapton' if value == 'EM' else 'PCB/Kapton'
	@baseplate_material.setter
	def baseplate_material(self, value):
		# CuW -> EM, PCB -> HAD
		splt = self.kind_of_part.split(" ")
		splt[0] = 'EM' if value == 'CuW/Kapton' else 'HAD'
		self.kind_of_part = " ".join(splt)


	@property
	def sen_type(self):
		if self.kind_of_part == "None None Si ProtoModule None None":  return None
		return self.kind_of_part.split()[1]
	@sen_type.setter
	def sen_type(self, value):
		splt = self.kind_of_part.split(" ")
		splt[1] = str(value)
		self.kind_of_part = " ".join(splt)

	@property
	def channel_density(self):
		if self.kind_of_part == "None None Si ProtoModule None None":  return None
		return self.kind_of_part.split()[4]
	@channel_density.setter
	def channel_density(self, value):
		splt = self.kind_of_part.split(" ")
		splt[4] = str(value)
		self.kind_of_part = " ".join(splt)

	@property
	def geometry(self):
		if self.kind_of_part == "None None Si ProtoModule None None":  return None
		return self.kind_of_part.split()[5]
	@geometry.setter
	def geometry(self, value):
		splt = self.kind_of_part.split(" ")
		splt[5] = str(value)
		self.kind_of_part = " ".join(splt)

	@property  # Note: not a measured value
	def thickness(self):
		return float(self.sen_type.split('um')[1])/1000

	# def thickness_physical(self):  return actual net thickness of part?


	@property
	def kind_of_part_baseplate(self):
		tmp_baseplate = baseplate()
		assert tmp_baseplate.load(self.baseplate), "Failed to load baseplate {} for protomod {}".format(self.baseplate, self.ID)
		return tmp_baseplate.kind_of_part

	@property
	def kind_of_part_sensor(self):
		tmp_sensor = sensor()
		assert tmp_sensor.load(self.sensor), "Failed to load sensor {} for protomod {}".format(sel     f.sensor, self.ID)
		return tmp_sensor.kind_of_part



	## Assembly data properties:


	# return position in GUI, 0-5
	@property
	def tray_posn(self):
		# If has a sensor step, grab the position of this sensor and return it here...
		if self.step_sensor is None:
			print("Warning:  assm_tray_posn:  no sensor step yet")
			return "None"
		temp_sensor_step = step_sensor()
		found = temp_sensor_step.load(self.step_sensor)
		if not found:
			print("ERROR in tray_posn:  protomodule has sensor step {}, but none found!".format(self.step_sensor))
			return "None"
		else:
			position = temp_sensor_step.sensors.index(self.ID)
			return position

	@property
	def plt_asm_row(self):
		posn = self.tray_posn()
		if posn == "None":  return posn
		else:  return posn%2+1

	@property
	def plt_asm_col(self):
		posn = self.tray_posn()
		if posn == "None": return posn
		else:  return posn//3+1

	@property
	def snsr_cmp_row(self):
		posn = self.tray_posn()
		if posn == "None":  return posn
		else:  return posn%2+1

	@property
	def snsr_cmp_col(self):
		posn = self.tray_posn()
		if posn == "None": return posn
		else:  return posn//3+1


	## Functions

	# new():  Optionally, create proto from baseplate and sensor objects
	# Note:  baseplate and sensor must be the actual objects, not IDs
	# NOTE:  Must also set sensor step ID!  (Implement into this?)
	def new(self, ID, baseplate=None, sensor=None):
		super(protomodule, self).new(ID)
		# if no sensor/baseplate, create and return normally
		if not baseplate and not sensor:  return
		# if one of sensor or baseplate, throw error
		assert baseplate or sensor, "Error creating protomodule: baseplate is {}, sensor is {}".format(baseplate, sensor)

		# Perform some checks
		errs = []
		if baseplate.geometry != sensor.geometry:
			errs.append("Baseplate geometry {} does not match sensor geometry {}".format(baseplate.geometry, sensor.geometry))
		if baseplate.channel_density != sensor.channel_density:
			errs.append("Baseplate channel density {} does not match sensor channel density {}".format(baseplate.channel_density, sensor.channel_density))
		if not baseplate.ready_step_sensor():
			errs.append("Baseplate is already mounted on protomodule {}, sensor step {}!".format(baseplate.protomodule, baseplate.step_sensor))
		if not sensor.ready_step_sensor():
			errs.append("Sensor is already mounted on protomodule {}, sensor step {}!".format(sensor.protomodule, sensor.step_sensor))

		if len(errs) > 0:
			self.clear()
			print("ERROR:  Protomodule {} not created from baseplate {} and sensor {}!  Errors:".format(self.ID, baseplate.ID, sensor.ID))
			print("\n".join(errs))
			return

		# if baseplate and sensor, auto-fill protomodule type, plus baseplate, sensor fields:
		self.baseplate = baseplate.ID
		self.geometry = baseplate.geometry
		self.channel_density = baseplate.channel_density
		self.baseplate_material = baseplate.material
		self.sensor = sensor.ID
		self.sen_type = sensor.sen_type


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
		"pcb",  # add baseplate, etc?
		"protomodule",
		"step_pcb",

		# for assembly page:
		"asmbl_tray_name",
		"comp_tray_name",
		"pcb_ser_num",
		"pcb_fltnes_mm",
		"pcb_thknes_mm",
		#"pcb_cmp_row", # property
		#"pcb_cmp_col", # property
		"pcb_tool_name",
		"pcb_tool_ht_set",
		"pcb_tool_ht_chk",
		"glue_type",
		"glue_batch_num",
		"pcb_tool_feet_chk",
		"mod_grade",
		"pcb_step",
		"pcb_plcment_x_offset",
		"pcb_plcment_y_offset",
		"pcb_plcment_ang_offset",
		"mod_thkns_mm",
		"mod_fltns_mm",

		# for cond page:
		"curing_time_hrs",
		"time_start",
		"time_stop",
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
		"wirebond_comments"
	]

	EXTRA_DEFAULTS = {
		"kind_of_part": "None None Si ProtoModule None None",
	}



	# Properties are same as protomodule's
	# Note:  auto-complete this if part is created from baseplate/sensor/etc
	@property
	def kind_of_part(self):
		return self.display_name

	@property
	def kind_of_part_pcb(self):
		tmp_pcb = pcb()
		assert tmp_pcb.load(self.pcb), "Failed to load pcb {} for mod {}".format(self.pcb, self.ID)
		return tmp_pcb.kind_of_part

	@property
	def kind_of_part_protomodule(self):
		tmp_proto = protomodule()
		assert tmp_proto.load(self.protomodule), "Failed to load protomodule {} for mod {}".format(self.protomodule, self.ID)
		return tmp_proto.kind_of_part

	# TODO : name this, decide whether to auto-set or manually set type
	@property
	def calorimeter_type(self):
		# 'EM' if self.baseplate.material=='CuW' else 'HAD'	
		return self.display_name.split()[0]
	@calorimeter_type.setter  # eventually, these will not be used
	def calorimeter_type(self, value):
		# Cannot replace bc of case w/ multiple Nones
		# split, then change and recombine
		print("CALORIMETER_TYPE SETTER")
		splt = self.display_name.split(" ")
		splt[0] = str(value)
		self.display_name = " ".join(splt)

	@property
	def sen_type(self):
		return self.display_name.split()[1]
	@sen_type.setter  # eventually, these will not be used
	def sen_type(self, value):
		# Cannot replace bc of case w/ multiple Nones
		# split, then change and recombine
		print("SEN_TYPE SETTER")
		splt = self.display_name.split(" ")
		splt[1] = str(value)
		self.display_name = " ".join(splt)

	@property
	def channel_density(self):
		if self.display_name is None:  return None
		return self.display_name.split()[4]
	@channel_density.setter
	def channel_density(self, value):
		splt = self.display_name.split(" ")
		splt[4] = str(value)
		self.display_name = " ".join(splt)

	@property
	def geometry(self):
		if self.display_name is None:  return None
		return self.display_name.split()[5]
	@geometry.setter
	def geometry(self, value):
		splt = self.display_name.split(" ")
		splt[5] = str(value)
		self.display_name = " ".join(splt)


	@property  # Note: not a measured value
	def thickness(self):
		return float(self.sen_type.split('um')[1])/1000
	@thickness.setter
	def thickness(self, value):
		pass


	# TEMPORARY:  NOTE:  Must fix this...
	@property
	def wirebonding_completed(self):
		return self.wirebonding_back and \
		       self.wirebonds_inspected_back and \
		       self.wirebonding_front and \
		       self.wirebonds_inspected_front and \
		       self.encapsulation_inspection_back and \
               self.encapsulation_inspection_front and \
		       self.wirebonding_final_inspection_ok == 'pass'

	@property
	def assem_tray_pos(self):
		return "TRPOSN_{}{}".format(self.tray_posn%2+1, tray_posn//3+1)

	@property
	def comp_tray_pos(self):
		return "CMPOSN_{}{}".format(self.tray_posn%2+1, tray_posn//3+1)
	

	@property
	def tray_posn(self):
		# If has a pcb step, grab the position of this PCB and return it here...
		if self.step_pcb is None:
			print("assm_tray_posn:  no sensor step yet")
			return "None"
		temp_pcb_step = step_pcb()
		found = temp_pcb_step.load(self.step_pcb)
		if not found:
			print("ERROR in tray_posn:  module {} has PCB step {}, but none found!".format(self.ID, self.step_pcb))
			return "None"
		else:
			position = temp_sensor_step.sensors.index(self.ID)
			return position

	@property
	def tray_row(self):
		posn = self.tray_posn()
		if posn == "None":  return posn
		else:  return posn%2+1

	@property
	def tray_col(self):
		posn = self.tray_posn()
		if posn == "None": return posn
		else:  return posn//3+1




	def generate_xml(self):
		# Make sure that all required info is present
		# if step_sensor.is_complete (or something similar)...
		# ALSO, check wirebonding finished
		super(protomodule, self).generate_xml()





