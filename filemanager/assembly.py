import json
import time
import glob
import os
import sys

from PyQt5 import QtCore
import datetime

#import rhapi_nolock as rh
# For DB requests:
import cx_Oracle

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
	# Note:  fsobj_db is currently minimalistic, only really contains cond header
	# Could very feasibly remove at this point?

	# Goals:
	# Init arr of 6 protomodules
	# Upon load:
	# - sql query for protomod IDs matching step name
	# - Download all into local protomodules
	# GUI:
	# - Access all step-specific info via attrs that get info from child protomods
	# Upon save:
	# - TBD


	def __init__(self):
		# protomods start None, get filled only once they're known to exist
		self.protomodules = [None for i in range(6)]

	def load(self):
		super(fsobj_step, self).save()
		# NOTE:  This will have to do work.
		# Query DB, then download all relevant parts for this step...
		# ...THEN load step.


	#def save(self):
	#	super(fsobj_part, self).save()
	# MAYBE:  Update step ID of child parts + save?
	# - no, need to manually assign part info anyway


class step_sensor(fsobj_step):
	OBJECTNAME = "sensor step"
	FILEDIR    = os.sep.join(['steps','sensor','{date}'])
	FILENAME   = 'sensor_step_{ID:0>5}.json'

	EXTRA_PROPERTIES = [
		'baseplates',
		'sensors',
		'protomodules',
		# run_begin/end_timestamp:  inherited
		'check_tool_feet',
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

	# Helper fn - get var from protomodules:
	# - find the first non-None proto
	# - get the var and return it
	def get_var_from_proto(self, var):
		tmp_proto_ID = None
		for i in range(6):
			if self.protomodules[i]:
				tmp_proto_ID = self.protomodules[i]
				break
		if tmp_proto_ID is None:  return None
		tmp_proto = parts.protomodule()
		assert tmp_proto.load(tmp_proto_ID), "Could not load protomodule {} in sensor step {}".format(tmp_proto_ID, self.ID)
		return getattr(tmp_proto, var, None)

	# utility:  given var, set var for all protomodules
	def set_var_from_proto(self, var, data):
		tmp_proto = parts.protomodule()
		for i in range(6):
			if self.protomodules[i]:
				tmp_proto.load(self.protomodules[i])
				setattr(tmp_proto, var, data)
				tmp_proto.save()


	# get a list of vars from protomodules (shsr_tool_names, etc)
	def get_vars_from_proto(self, var):
		tmp_proto = parts.protomodule()
		data = []
		for i in range(6):
			if not self.protomodules[i]:  continue
			tmp_proto.load(self.protomodules[i])
			data.append(getattr(tmp_proto, var, None))
		return data
	
	def set_vars_from_proto(self, var, data):
		tmp_proto = parts.protomodule()
		for i in range(6):
			if not self.protomodules[i]:  continue
			tmp_proto.load(self.protomodules[i])
			setattr(tmp_proto, var, data[i])
			tmp_proto.save()

	# pre-assembly properties
	@property
	def record_insertion_user(self):
		return self.get_var_from_proto("record_insertion_user")
	@record_insertion_user.setter
	def record_insertion_user(self, value):
		self.set_var_from_proto("record_insertion_user", value)

	@property
	def run_begin_timestamp(self):
		return self.get_var_from_proto("run_begin_timestamp")
	@run_begin_timestamp.setter
	def run_begin_timestamp(self, value):
		self.set_var_from_proto("run_begin_timestamp", value)

	@property
	def run_end_timestamp(self):
		return self.get_var_from_proto("run_end_timestamp")
	@run_end_timestamp.setter
	def run_end_timestamp(self, value):
		self.set_var_from_proto("run_end_timestamp", value)

	@property
	def glue_batch_num(self):
		return self.get_var_from_proto("glue_batch_num")
	@glue_batch_num.setter
	def glue_batch_num(self, value):
		self.set_var_from_proto("glue_batch_numo", value)

	@property
	def asmbl_tray_name(self):
		return self.get_var_from_proto("asmbl_tray_name")
	@asmbl_tray_name.setter
	def asmbl_tray_name(self, value):
		self.set_var_from_proto("asmbl_tray_name", value)

	@property
	def comp_tray_name(self):
		return self.get_var_from_proto("comp_tray_name")
	@comp_tray_name.setter
	def comp_tray_name(self, value):
		self.set_var_from_proto("comp_tray_name", value)

	@property
	def snsr_tool_names(self):
		return self.get_vars_from_proto("snsr_tool_name")
	@snsr_tool_names.setter
	def snsr_tool_names(self, value):
		self.set_vars_from_proto("snsr_tool_name", value)

	# post-assembly properties
	@property
	def cure_begin_timestamp(self):
		return self.get_var_from_proto("cure_begin_timestamp")
	@cure_begin_timestamp.setter
	def cure_begin_timestamp(self, value):
		self.set_var_from_proto("cure_begin_timestamp", value)

	@property
	def cure_end_timestamp(self):
		return self.get_var_from_proto("cure_end_timestamp")
	@cure_end_timestamp.setter
	def cure_end_timestamp(self, value):
		self.set_var_from_proto("cure_end_timestamp", value)

	@property
	def temp_degc(self):
		return self.get_var_from_proto("temp_degc")
	@temp_degc.setter
	def temp_degc(self, value):
		self.set_var_from_proto("temp_degc", value)

	@property
	def humidity_prcnt(self):
		return self.get_var_from_proto("humidity_prcnt")
	@humidity_prcnt.setter
	def humidity_prcnt(self, value):
		self.set_var_from_proto("humidity_prcnt", value)

	@property
	def test_file_name(self):
		return self.get_var_from_proto("test_file_name")
	@test_file_name.setter
	def test_file_name(self, value):
		self.set_var_from_proto("test_file_name", value)

	@property
	def grades(self):
		return self.get_vars_from_proto("grade")
	@grades.setter
	def grades(self, value):
		self.set_vars_from_proto("grade", value)

	@property
	def snsr_x_offsts(self):
		return self.get_vars_from_proto("snsr_x_offst")
	@snsr_x_offsts.setter
	def snsr_x_offsts(self, value):
		self.set_vars_from_proto("snsr_x_offst", value)

	@property
	def snsr_y_offsts(self):
		return self.get_vars_from_proto("snsr_y_offst")
	@snsr_y_offsts.setter
	def snsr_y_offsts(self, value):
		self.set_vars_from_proto("snsr_y_offst", value)

	@property
	def snsr_ang_offsts(self):
		return self.get_vars_from_proto("snsr_ang_offst")
	@snsr_ang_offsts.setter
	def snsr_ang_offsts(self, value):
		self.set_vars_from_proto("snsr_ang_offst", value)

	@property
	def thicknesses(self):
		return self.get_vars_from_proto("thickness")
	@thicknesses.setter
	def thicknesses(self, value):
		self.set_vars_from_proto("thickness", value)

	@property
	def flatnesses(self):
		return self.get_vars_from_proto("flatness")
	@flatnesses.setter
	def flatnesses(self, value):
		self.set_vars_from_proto("flatness", value)


class step_pcb(fsobj_step):
	OBJECTNAME = "PCB step"
	FILEDIR = os.sep.join(['steps','pcb','{date}'])
	FILENAME = 'pcb_step_{ID:0>5}.json'

	EXTRA_PROPERTIES = [
		'pcbs',
		'protomodules',
		'modules',
	]
	
	EXTRA_DEFAULTS = {
		'pcbs': [None for i in range(6)],
		'protomodules': [None for i in range(6)],
		'modules': [None for i in range(6)],
	}




