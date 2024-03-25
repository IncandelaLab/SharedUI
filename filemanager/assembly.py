import json
import time
import glob
import os
import sys

from PyQt5 import QtCore
import datetime

#import rhapi_nolock as rh

from filemanager import fm, parts


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



###############################################
###############  assembly steps  ##############
###############################################


class fsobj_step(fm.fsobj):
	# Properties unique to class
	EXTRA_PROPERTIES = []
	EXTRA_DEFAULTS = {}

	PART_CLASS = None # protomodule or module
	PART = None # "protomodule", etc

	def __init__(self):
		self.PROPERTIES = self.EXTRA_PROPERTIES
		self.DEFAULTS = self.EXTRA_DEFAULTS
		super(fsobj_step, self).__init__()


	def load(self, ID):
		return super(fsobj_step, self).load(ID)
		# NOTE:  This will have to do work.
		# Query DB, then download all relevant parts for this step...
		# ...THEN load step.


	def save(self):
		super(fsobj_step, self).save()
	# MAYBE:  Update step ID of child parts + save?
	# - no, need to manually assign part info anyway

	def generate_xml(self):
		tmp_part = self.PART_CLASS()
		print("GENERATING XML")
		print("part class is:", self.PART_CLASS)
		parts = getattr(self, self.PART+"s", None)
		print("found parts:", parts)
		for i in range(6):
			if not parts[i]:  continue
			tmp_part.load(parts[i])
			print("Generating xml for:", parts[i])
			tmp_part.generate_xml()


	# Helper fn - get var from parts:
	# - find the first non-None part
	# - get the var and return it
	def get_var_from_part(self, var):
		tmp_part_ID = None
		parts = getattr(self, self.PART+"s", None)
		for i in range(6):
			if parts[i]:
				tmp_part_ID = parts[i]
				break
		if tmp_part_ID is None:  return None
		tmp_part = self.PART_CLASS()
		assert tmp_part.load(tmp_part_ID), "Could not load {} {} in sensor step {}".format(self.PART, tmp_part_ID, self.ID)
		return getattr(tmp_part, var, None)

	# utility:  given var, set var for all parts
	def set_var_from_part(self, var, data):
		tmp_part = self.PART_CLASS()
		parts = getattr(self, self.PART+"s", None)
		for i in range(6):
			if parts[i]:
				tmp_part.load(parts[i])
				setattr(tmp_part, var, data)
				tmp_part.save()


	# get a list of vars from parts (snsr_tool_names, etc)
	def get_vars_from_part(self, var):
		parts = getattr(self, self.PART+"s", None)
		tmp_part = self.PART_CLASS()
		data = []
		for i in range(6):
			if not parts[i]:
				data.append(None)
			else:
				tmp_part.load(parts[i])
				data.append(getattr(tmp_part, var, None))
		return data
	
	def set_vars_from_part(self, var, data):
		parts = getattr(self, self.PART+"s", None)
		tmp_part = self.PART_CLASS()
		for i in range(6):
			if not parts[i]:  continue
			tmp_part.load(parts[i])
			setattr(tmp_part, var, data[i])
			tmp_part.save()


	# properties for both sensor+pcb steps:

	# pre-assembly properties
	@property
	def record_insertion_user(self):
		return self.get_var_from_part("record_insertion_user")
	@record_insertion_user.setter
	def record_insertion_user(self, value):
		self.set_var_from_part("record_insertion_user", value)

	@property
	def run_begin_timestamp(self):
		return self.get_var_from_part("run_begin_timestamp")
	@run_begin_timestamp.setter
	def run_begin_timestamp(self, value):
		self.set_var_from_part("run_begin_timestamp", value)

	@property
	def run_end_timestamp(self):
		return self.get_var_from_part("run_end_timestamp")
	@run_end_timestamp.setter
	def run_end_timestamp(self, value):
		self.set_var_from_part("run_end_timestamp", value)

	@property
	def glue_batch_num(self):
		return self.get_var_from_part("glue_batch_num")
	@glue_batch_num.setter
	def glue_batch_num(self, value):
		self.set_var_from_part("glue_batch_num", value)

	@property
	def batch_tape_50(self):
		return self.get_var_from_part("batch_tape_50")
	@batch_tape_50.setter
	def batch_tape_50(self, value):
		self.set_var_from_part("batch_tape_50", value)

	@property
	def batch_tape_120(self):
		return self.get_var_from_part("batch_tape_120")
	@batch_tape_120.setter
	def batch_tape_120(self, value):
		self.set_var_from_part("batch_tape_120", value)

	#@property
	#def asmbl_tray_name(self):
	#	return self.get_var_from_part("asmbl_tray_name")
	#@asmbl_tray_name.setter
	#def asmbl_tray_name(self, value):
	#	self.set_var_from_part("asmbl_tray_name", value)

	#@property
	#def asmbl_tray_num(self):
	#	if self.asmbl_tray_name is None:  return None
	#	else:  return int(self.asmbl_tray_name.split("_")[1])

	@property
	def asmbl_tray_names(self):
		return self.get_vars_from_part("asmbl_tray_name")
	@asmbl_tray_names.setter
	def asmbl_tray_names(self, value):
		self.set_vars_from_part("asmbl_tray_name", value)

	@property
	def asmbl_tray_nums(self):
		nums = []
		for n in self.asmbl_tray_names:
			if n is None:
				nums.append(None)
			else:
				nums.append(int(n.split("_")[1]))
		return nums

	@property
	def comp_tray_name(self):
		return self.get_var_from_part("comp_tray_name")
	@comp_tray_name.setter
	def comp_tray_name(self, value):
		self.set_var_from_part("comp_tray_name", value)

	@property
	def comp_tray_num(self):
		if self.comp_tray_name is None:  return None
		else:  return int(self.comp_tray_name.split("_")[1])

	# post-assembly properties
	@property
	def cure_begin_timestamp(self):
		return self.get_var_from_part("cure_begin_timestamp")
	@cure_begin_timestamp.setter
	def cure_begin_timestamp(self, value):
		self.set_var_from_part("cure_begin_timestamp", value)

	@property
	def cure_end_timestamp(self):
		return self.get_var_from_part("cure_end_timestamp")
	@cure_end_timestamp.setter
	def cure_end_timestamp(self, value):
		self.set_var_from_part("cure_end_timestamp", value)

	@property
	def temp_degc(self):
		return self.get_var_from_part("temp_degc")
	@temp_degc.setter
	def temp_degc(self, value):
		self.set_var_from_part("temp_degc", value)

	@property
	def humidity_prcnt(self):
		return self.get_var_from_part("humidity_prcnt")
	@humidity_prcnt.setter
	def humidity_prcnt(self, value):
		self.set_var_from_part("humidity_prcnt", value)

	@property
	def grades(self):
		return self.get_vars_from_part("grade")
	@grades.setter
	def grades(self, value):
		self.set_vars_from_part("grade", value)

	@property
	def thicknesses(self):
		return self.get_vars_from_part("thickness")
	@thicknesses.setter
	def thicknesses(self, value):
		self.set_vars_from_part("thickness", value)

	@property
	def flatnesses(self):
		return self.get_vars_from_part("flatness")
	@flatnesses.setter
	def flatnesses(self, value):
		self.set_vars_from_part("flatness", value)




class step_sensor(fsobj_step):
	OBJECTNAME = "sensor step"
	FILEDIR    = os.sep.join(['steps','sensor','{date}'])
	FILENAME   = 'sensor_step_{ID:0>5}.json'

	PART_CLASS = parts.protomodule
	PART = "protomodule"

	EXTRA_PROPERTIES = [
		'baseplates',
		'sensors',
		'protomodules',
		# run_begin/end_timestamp:  inherited
		'xml_file_name', # was test_file_name
	]
	
	EXTRA_DEFAULTS = {
		'baseplates': [None for i in range(6)],
		'sensors': [None for i in range(6)],
		'protomodules': [None for i in range(6)],
	}

	# properties:
	# - insertion_user <- user_performed (record_insertion_user)
	# - run_begin/end_timestamp <- run_start/stop
	# - glue_batch_num <- batch_araldite
	# - asmbl_tray_name <- tray_assembly
	# - comp_tray_name <- tray_component_sensor
	# - snsr_tool_names <- tools
	# post-step properties:
	# NOTE:  All taken from protomodule properties
	# NO vars needed for proto XML are stored here.

	# pre-assembly
	@property
	def snsr_tool_names(self):
		return self.get_vars_from_part("snsr_tool_name")
	@snsr_tool_names.setter
	def snsr_tool_names(self, value):
		self.set_vars_from_part("snsr_tool_name", value)

	@property
	def snsr_tool_nums(self):
		names = self.snsr_tool_names
		nums = []
		for i in range(6):
			if names[i] is None:
				nums.append(None)
			else:
				nums.append(int(names[i].split("_")[1]))
		return nums

	# post-assembly
	@property
	def snsr_x_offsts(self):
		return self.get_vars_from_part("snsr_x_offst")
	@snsr_x_offsts.setter
	def snsr_x_offsts(self, value):
		self.set_vars_from_part("snsr_x_offst", value)

	@property
	def snsr_y_offsts(self):
		return self.get_vars_from_part("snsr_y_offst")
	@snsr_y_offsts.setter
	def snsr_y_offsts(self, value):
		self.set_vars_from_part("snsr_y_offst", value)

	@property
	def snsr_ang_offsts(self):
		return self.get_vars_from_part("snsr_ang_offst")
	@snsr_ang_offsts.setter
	def snsr_ang_offsts(self, value):
		self.set_vars_from_part("snsr_ang_offst", value)

	@property
	def snsr_tool_feet_chk(self):
		return self.get_var_from_part("snsr_tool_feet_chk")
	@snsr_tool_feet_chk.setter
	def snsr_tool_feet_chk(self, value):
		self.set_var_from_part("snsr_tool_feet_chk", value)


class step_pcb(fsobj_step):
	OBJECTNAME = "PCB step"
	FILEDIR = os.sep.join(['steps','pcb','{date}'])
	FILENAME = 'pcb_step_{ID:0>5}.json'

	PART_CLASS = parts.module
	PART = "module"

	EXTRA_PROPERTIES = [
		'pcbs',
		'protomodules',
		'modules',
		'xml_file_name',
	]
	
	EXTRA_DEFAULTS = {
		'pcbs': [None for i in range(6)],
		'protomodules': [None for i in range(6)],
		'modules': [None for i in range(6)],
	}

	# pre-assembly
	@property
	def pcb_tool_names(self):
		return self.get_vars_from_part("pcb_tool_name")
	@pcb_tool_names.setter
	def pcb_tool_names(self, value):
		self.set_vars_from_part("pcb_tool_name", value)

	@property
	def pcb_tool_nums(self):
		names = self.pcb_tool_names
		nums = []
		for i in range(6):
			if names[i] is None:
				nums.append(None)
			else:
				nums.append(int(names[i].split("_")[1]))
		return nums

	# post-assembly
	@property
	def pcb_x_offsts(self):
		return self.get_vars_from_part("pcb_plcment_x_offset")
	@pcb_x_offsts.setter
	def pcb_x_offsts(self, value):
		self.set_vars_from_part("pcb_plcment_x_offset", value)

	@property
	def pcb_y_offsts(self):
		return self.get_vars_from_part("pcb_plcment_y_offset")
	@pcb_y_offsts.setter
	def pcb_y_offsts(self, value):
		self.set_vars_from_part("pcb_plcment_y_offset", value)

	@property
	def pcb_ang_offsts(self):
		return self.get_vars_from_part("pcb_plcment_ang_offset")
	@pcb_ang_offsts.setter
	def pcb_ang_offsts(self, value):
		self.set_vars_from_part("pcb_plcment_ang_offset", value)

	@property
	def pcb_tool_feet_chk(self):
		return self.get_var_from_part("pcb_tool_feet_chk")
	@pcb_tool_feet_chk.setter
	def pcb_tool_feet_chk(self, value):
		self.set_var_from_part("pcb_tool_feet_chk", value)

	@property
	def weights(self):
		return self.get_vars_from_part("weight")
	@weights.setter
	def weights(self, value):
		self.set_vars_from_part("weight", value)
  
	@property
	def max_thicknesses(self):
		return self.get_vars_from_part("max_thickness")
	@max_thicknesses.setter
	def max_thicknesses(self, value):
		self.set_vars_from_part("max_thickness", value)

