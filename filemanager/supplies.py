import json
import time
import glob
import os
import sys

from PyQt5 import QtCore
import datetime
from filemanager import fm

###############################################
##################  supplies  #################
###############################################

class fsobj_supply(fm.fsobj):
	def is_expired(self):
		if self.date_expires is None or self.date_received is None:
			return False
		ydm = tmp_sylgard.date_expires.split('-')
		expires = QtCore.QDate(int(ydm[2]), int(ydm[0]), int(ydm[1]))
		return QtCore.QDate.currentDate() > expires

	PROPERTIES = [
		'date_received',
		'date_expires',
		'is_empty',
		'comments',
	]


######################
### SUPPLY CLASSES ###
######################

class batch_araldite(fsobj_supply):
	OBJECTNAME = "araldite batch"
	FILEDIR = os.sep.join(['supplies','batch_araldite','{date}'])
	FILENAME = 'batch_araldite_{ID:0>5}.xml'


class batch_wedge(fsobj_supply):
	OBJECTNAME = "wedge batch"
	FILEDIR = os.sep.join(['supplies','batch_wedge','{date}'])
	FILENAME = 'batch_wedge_{ID:0>5}.xml'


class batch_sylgard(fsobj_supply):  # was sylgar_thick
	OBJECTNAME = "sylgard batch"
	FILEDIR = os.sep.join(['supplies','batch_sylgard','{date}'])
	FILENAME = 'batch_sylgard_{ID:0>5}.xml'
	PROPERTIES = [
		'date_received',
		'date_expires',
		'is_empty',
		'curing_agent',
		'comments'
	]


class batch_bond_wire(fsobj_supply):
	OBJECTNAME = "bond wire batch"
	FILEDIR = os.sep.join(['supplies','batch_bond_wire','{date}'])
	FILENAME = 'batch_bond_wire_{ID:0>5}.xml'






