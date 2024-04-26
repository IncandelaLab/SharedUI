import os
from filemanager import fm

# PARENT CLASS FOR TOOLS:
# These need to be treated separately because they're saved based on ID+institution and not just institution
# Mostly identical to fsobj, but with institution added as a primary key.
# Must "act" as if it's saved w/ 2 primary keys, but actually there's only one.

class fsobj_tool(fm.fsobj):

	# Moved from tool classes
	PROPERTIES = [
		'location',
		'comments',
	]

	#def add_part_to_list(self):
	#	super(fsobj_tool, self).add_part_to_list("{}_{}".format(self.ID, self.institution))

	def load(self, ID, institution):
		return super(fsobj_tool, self).load("{}_{}".format(ID, institution))

	def new(self, ID, institution):
		#self.institution = institution
		super(fsobj_tool, self).new("{}_{}".format(ID, institution))

	@property
	def institution(self):
		 return self.ID.split("_")[1]



###############################################
##################  tooling  ##################
###############################################

class tool_sensor(fsobj_tool):
	OBJECTNAME = "sensor tool"
	FILEDIR = os.sep.join(['tooling','tool_sensor'])
	FILENAME = 'tool_sensor_{ID}.json'


class tool_pcb(fsobj_tool):
	OBJECTNAME = "PCB tool"
	FILEDIR = os.sep.join(['tooling','tool_pcb'])
	FILENAME = 'tool_pcb_{ID}.json'


class tray_assembly(fsobj_tool):
	OBJECTNAME = "assembly tray"
	FILEDIR = os.sep.join(['tooling','tray_assembly'])
	FILENAME = 'tray_assembly_{ID}.json'


class tray_component_sensor(fsobj_tool):
	OBJECTNAME = "sensor tray"
	FILEDIR = os.sep.join(['tooling','tray_component_sensor'])
	FILENAME = 'tray_component_sensor_{ID}.json'


class tray_component_pcb(fsobj_tool):
	OBJECTNAME = "pcb tray"
	FILEDIR = os.sep.join(['tooling','tray_component_pcb'])
	FILENAME = 'tray_component_pcb_{ID}.json'



