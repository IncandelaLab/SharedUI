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




"""
class protomodule(fsobj_part):
	OBJECTNAME = "protomodule"
	FILEDIR = os.sep.join(['protomodules','{date}'])
	FILENAME = 'protomodule_{ID}.json'

	# Note:  serial_number == self.ID
	COND_PROPERTIES = [
		# Read/write from cond:
		"asmbl_tray_name",
		"plt_ser_num",
		"plt_asm_row",
		"plt_asm_col",
		"plt_fltnes_mm",
		"plt_thknes_mm",
		"comp_tray_name",
		"snsr_ser_num",
		"snsr_cmp_row",
		"snsr_cmp_col",
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
		"plt_grade",
		"snsr_tool_feet_chk",
		"snsr_step"
	]

	LOCAL_PROPERTIES = [
		# Locally-saved, not part of DB:
		"location",  # location at institution
		#"protomodule",  # TBD
		"module",
	]

	# Derived properties:
	# material (from display_name)
	# geometry
	# channel density

	DEFAULTS = {
		"size":     '8', # This should not be changed!
		"display_name": "None None Si ProtoModule None None"
	}


	XML_COND_TEMPLATE = {
		"HEADER":fsobj_db.COND_HEADER_DICT,
		"DATA_SET":{
			"COMMENT_DESCRIPTION":"comment_description",
			"VERSION":"VNUM",
			"PART":{
				"SERIAL_NUMBER":"ID",
				"KIND_OF_PART":"kind_of_part",
			},
			"DATA":{
				"ASMBL_TRAY_NAME":"asmbl_tray_name",
				"PLT_SER_NUM":"plt_ser_num",
				"PLT_ASM_ROW":"plt_asm_row",
				"PLT_ASM_COL":"plt_asm_col",
				"PLT_FLTNS_MM":"plt_fltns_mm",
				"PLT_CHKNES_MM":"plt_thknes_mm",
				"COMP_TRAY_NAME":"comp_tray_name",
				"SNSR_SER_NUM":"snsr_ser_num",
				"SNSR_COMP_ROW":"snsr_cmp_row",
				"SNSR_X_OFFST":"snsr_x_offst",
				"SNSR_T_OFFST":"snsr_y_offst",
				"SNSR_ANG_OFFSET":"snsr_ang_offset",
				"SNSR_TOOL_NAME":"snsr_tool_name",
				"SNSR_TOOL_HT_SET":"snsr_tool_ht_set",
				"SNSR_TOOL_HT_CHK":"snsr_tool_ht_chk",
				"GLUE_TYPE":"glue_type",
				"GLUE_BATCH_NUM":"glue_batch_num",
				"SLVR_EPXY_TYPE":"slvr_epxy_type",
				"SLVR_EPXY_BATCH_NUM":"slvr_epxy_batch_num",
				"PLT_GRADE":"plt_grade",
				"SNSR_TOOL_FEET_CHK":"snsr_tool_feet_chk",
				"SNSR_STEP":"snsr_step"

			}
		}
	}

	# for HEADER_DICT
	COND_TABLE = "HGC_PRTO_MOD_ASMBLY"
	TABLE_DESC = "HGC Six Inch Proto Module Assembly"

	# List of vars that should NOT be edited in the GUI and are only loaded from DB
	# (And some info would be redundant w/ other constants, eg KIND_OF_PART and self.size)
	XML_CONSTS = [
		'size',
	]


	# Note:  auto-complete this if part is created from baseplate/sensor/etc
	@property
	def kind_of_part(self):
		return self.display_name
		#"{} Baseplate {} {}".format(self.material, self.channel_density, self.shape)

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


	@property
	def assem_tray_pos(self):
		return 
		#return "TRPOSN_{}{}".format(self.tray_row, tray_col)

	@property
	def comp_tray_pos(self):
		return "CMPOSN_{}{}".format(self.tray_row, tray_col)

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
	def tray_row(self):
		posn = self.tray_posn()
		if posn == "None":  return posn
		else:  return posn%2+1

	@property
	def tray_col(self):
		posn = self.tray_posn()
		if posn == "None": return posn
		else:  return posn//3+1
	
	@property
	def baseplate_type(self):
		if self.baseplate is None:
			print("In baseplate_type:  protomod has no baseplate!")
			return None
		temp_baseplate = baseplate()
		if not temp_baseplate.load(self.baseplate):
			print("ERROR:  failed to load baseplate {} in baseplate_type!".format(self.baseplate))
			return None
		return temp_baseplate.description

	@property
	def sensor_type(self):
		if self.sensor is None:
			print("In sensor_type:  protomod has no sensor!")
			return None
		temp_sensor = sensor()
		if not temp_sensor.load(self.sensor):
			print("ERROR:  failed to load sensor {} in sensor_type!".format(self.sensor))
			return None
		return temp_sensor.description

	@property
	def resolution(self):
		if self.sensor is None:
			print("ERROR in module resolution:  sensor is None!")
			return None
		temp_sensor = sensor()
		if not temp_sensor.load(self.sensor):
			print("ERROR:  Could not find child sensor {}!".format(self.sensor))
			return None
		return temp_sensor.resolution


	def ready_step_pcb(self, step_pcb = None):
		if self.step_pcb and self.step_pcb != step_pcb:
			return False, "already assigned to module {}".format(self.module)
		return True, ""

		



class module(fsobj_part):
	OBJECTNAME = "module"
	FILEDIR    = os.sep.join(['modules','{date}','module_{ID}'])
	FILENAME   = 'module_{ID}.json'

	# Note:  serial_number == self.ID
	COND_PROPERTIES = [
		# Read/write from cond:
		"asmbl_tray_name",
		"prto_ser_num",
		"prto_asm_row",
		"prto_asm_col",
		"comp_tray_name",
		"pcb_ser_num",
		"pcb_fltnes_mm",
		"pcb_thknes_mm",
		"pcb_cmp_row",
		"pcb_cmp_col",
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
		"bond_iull_user",  # typo in DB.......
		"bond_pull_avg",
		"bond_pull_stddev",
		"final_inspxn_user",
		"final_inspxn_ok",
		"wirebond_comments"
	]

	LOCAL_PROPERTIES = [
		# Locally-saved, not part of DB:
		"location",  # location at institution
		#"protomodule",  # TBD
	]

	# Derived properties:
	# material (from display_name)
	# geometry
	# channel density

	DEFAULTS = {
		"size":     '8', # This should not be changed!
		"display_name": "None None Si ProtoModule None None"
	}


	XML_COND_TEMPLATE = {
		"HEADER":fsobj_db.COND_HEADER_DICT,
		"DATA_SET":{
			"COMMENT_DESCRIPTION":"comment_description",
			"VERSION":"VNUM",
			"PART":{
				"SERIAL_NUMBER":"ID",
				"KIND_OF_PART":"kind_of_part",
			},
			"DATA":{
				"ASMBL_TRAY_NAME":"asmbl_tray_name",
				"PRTO_SER_NUM":"prto_ser_num",
				"PRTO_ASM_ROW":"prto_asm_row",
				"PRTO_ASM_COL":"prto_asm_col",
				"COMP_TRAY_NAME":"comp_tray_name",
				"PCB_SER_NUM":"pcb_ser_num",
				"PCB_FLTNES_MM":"pcb_fltnes_mm",
				"PCB_THKNES_MM":"pcb_thknes_mm",
				"PCB_CMP_ROW":"pcb_cmp_row",
				"PCB_CMP_COL":"pcb_cmp_col",
				"PCB_TOOL_NAME":"pcb_tool_name",
				"PCB_TOOL_HT_SET":"pcb_tool_ht_set",
				"PCB_TOOL_HT_CHK":"pcb_tool_ht_chk",
				"GLUE_TYPE":"glue_type",
				"GLUE_BATCH_NUM":"glue_batch_num",
				"PCB_TOOL_FEET_CHK":"pcb_tool_feet_chk",
				"MOD_GRADE":"mod_grade",
				"PCB_STEP":"pcb_step",
				"PCB_PLCMENT_X_OFFST":"pcb_plcment_x_offst",
				"PCB_PLCMENT_Y_OFFST":"pcb_plcment_y_offst",
				"SNSR_ANG_OFFSET":"snsr_ang_offset",
				"MOD_FLTNS_MM":"mod_fltns_mm",
				"MOD_FLTNS_MM":"mod_fltns_mm"
			}
		}
	}

	# Wirebonding-specific:
	WIREBOND_TABLE_NAME = "HGC_MOD_WIREBOND_TEST"
	WIREBOND_HEADER_DICT = {
		'TYPE':{
			'EXTENSION_TABLE_NAME':'WIREBOND_TABLE_NAME',
			'NAME':'TABLE_DESC',
		},
		'RUN':{
			'RUN_NAME':'RUN_TYPE',
			'RUN_BEGIN_TIMESTAMP':'run_begin_timestamp_',  # Format:  2018-03-26 00:00:00
			'RUN_END_TIMESTAMP':'run_end_timestamp_',
			'INITIATED_BY_USER':'initiated_by_user',
			'LOCATION':'location',
			'COMMENT_DESCRIPTION':'comment_description',
		}
	}
	XML_WIREBOND_TEMPLATE = {
		"HEADER":fsobj_db.COND_HEADER_DICT,
		"DATA_SET":{
			"COMMENT_DESCRIPTION":"comment_description",
			"VERSION":"VNUM",
			"PART":{
				"SERIAL_NUMBER":"ID",
				"KIND_OF_PART":"kind_of_part",
			},
			"DATA":{
				"BOND_WIRE_BATCH_NUM":"bond_wire_batch_num",
				"PRE_INSPECTION":"pre_inspection",
				"SYLGARD_BATCH":"sylgard_batch",
				"WEDGE_BATCH":"wedge_batch",
				"BACK_BONDS":"back_bonds",
				"BACK_BONDS_DATE":"back_bonds_date",
				"BACK_BONDS_USER":"back_bonds_user",
				"BACK_UNBONDED":"back_unbonded",
				"BACK_BOND_INSPXN":"back_bond_inspxn",
				"BACK_REPAIR_USER":"back_repair_user",
				"FRONT_BONDS":"front_bonds",
				"FRONT_BONDS_DATE":"front_bonds_date",
				"FRONT_BONDS_USER":"front_bonds_user",
				"FRONT_SKIP":"front_skip",
				"FRONT_UNBONDED":"front_unbonded",
				"FRONT_BOND_INSPXN":"front_bond_inspxn",
				"FRONT_REPAIR_USER":"front_repair_user",
				"BACK_ENCAP":"back_encap",
				"BACK_ENCAP_USER":"back_encap_user",
				"BACK_ENCAP_CURE_START":"back_encap_cure_start",
				"BACK_ENCAP_CURE_STOP":"back_encap_cure_stop",
				"BACK_ENCAP_INSPXN":"back_encap_inspxn",
				"FRONT_ENCAP":"front_encap",
				"FRONT_ENCAP_USER":"front_encap_user",
				"FRONT_ENCAP_CURE_START":"front_encap_cure_start",
				"FRONT_ENCAP_CURE_STOP":"front_encap_cure_stop",
				"FRONT_ENCAP_INSPXN":"front_encap_inspxn",
				"IS_TEST_BOND_MODULE":"is_test_bond_module",
				"BOND_IULL_USER":"bond_iull_user",  # typo in DB.......
				"BOND_PULL_AVG":"bond_pull_avg",
				"BOND_PULL_STDDEV":"bond_pull_stddev",
				"FINAL_INSPXN_USER":"final_inspxn_user",
				"FINAL_INSPXN_OK":"final_inspxn_ok",
				"WIREBOND_COMMENTS":"wirebond_comments"

			}
		}
	}


	# for HEADER_DICT
	COND_TABLE = "HGC_MOD_ASMBLY"
	TABLE_DESC = "HGC Six Inch Module Assembly"

	# List of vars that should NOT be edited in the GUI and are only loaded from DB
	# (And some info would be redundant w/ other constants, eg KIND_OF_PART and self.size)
	XML_CONSTS = [
		'size',
	]


	# Properties are same as protomodule's
	# Note:  auto-complete this if part is created from baseplate/sensor/etc
	@property
	def kind_of_part(self):
		return self.display_name

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

	# NEW:  Need to add an additional file/etc to handle wirebonding

	def save(self):
		# This one handles the json files
		super(module, self).save()

		# Additionally:  Write wirebonding XML file
		filedir, filename = self.get_filedir_filename()
		fname_wirebond = filename.replace('.json', '_wirebonding_upload.xml')

		xml_tree = self.generate_xml(self.XML_WIREBOND_TEMPLATE)
		root = xml_tree.getroot()
		xmlstr = minidom.parseString(tostring(root)).toprettyxml(indent = '    ')  #tostring imported from xml.etree.ElementTree
		xmlstr = xmlstr.replace("version=\"1.0\" ", "version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"")
		with open(filedir+'/'+fname_wirebond, 'w') as f:
			f.write(xmlstr)


	# Revamped
	def load(self, ID, on_property_missing = "warn"):
		if ID == "" or ID == -1 or ID == None:
			self.clear()
			return False

		part_name = self.__class__.__name__
		self.partlistfile = os.sep.join([ DATADIR, 'partlist', part_name+'s.json' ])
		data = None
		with open(self.partlistfile, 'r') as opfl:
			data = json.load(opfl)
		if str(ID) in data.keys():
			print("      FOUND in partlistfile, can quick load")
			dt = data[str(ID)]
			super(fsobj_part, self).load(ID)

		else:
			if not ENABLE_DB_COMMUNICATION:
				print("**TEMPORARY:  Object not found, and downloading disabled for testing!**")
				return False

			# Use DB_CURSOR and self.SQL_REQUEST to find XML files
			# Data from part table
			print("Requesting part data")
			DB_CURSOR.execute(self.sql_request_part(ID))
			# Reformat
			columns = [col[0] for col in DB_CURSOR.description]
			DB_CURSOR.rowfactory = lambda *args: dict(zip(columns, args))
			data_part = DB_CURSOR.fetchone()
			if data_part is None:
				# Part not found
				print("SQL query found nothing")
				return False

			# Data from cond table
			print("Requesting cond data")
			print("QUERY:")
			print(self.sql_request_cond(ID))
			DB_CURSOR.execute(self.sql_request_cond(ID))
			# Reformat
			columns = [col[0] for col in DB_CURSOR.description]
			DB_CURSOR.rowfactory = lambda *args: dict(zip(columns, args))
			data_cond = DB_CURSOR.fetchone()
			# data_* is now a dict:  {"SERIAL_NUMBER":"xyz", "THICKNESS":"0.01", ...}

			# Load all data into self.
			# DB col names are [local var name].upper()
			print("Downloaded part data:")
			print(data_part)
			print("Downloaded cond data:")
			print(data_cond)

			def fill_self(data_x):
				for colname, var in data_x.items():
					# NOTE:  datetime objs cannot be stored as json, or simply sent to xml...so stringify
					if type(var) == datetime.datetime:
						dstring = "{}-{}-{} {:02d}:{:02d}:{:02d}".format(var.year, var.month, var.day, var.hour, var.minute, var.second)
						setattr(self, colname.lower(), dstring)
					elif type(var) == datetime.date:
						dstring = "{}-{}-{}".format(var.year, var.month, var.day)
						setattr(self, colname.lower(), dstring)
					else:
						setattr(self, colname.lower(), var)
			fill_self(data_part)
			fill_self(data_cond)

			# Data is now in python obj.  Ensure save:
			self.ID = ID
			self.save()

		#self.ID = ID
		return True

"""


