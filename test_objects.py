from filemanager import fm, supplies, tools, parts
import pytest # NEW
import shutil
import os

# Script that runs some automated tests on all object (part, assembly step, etc) classes.
# Run all tests automatically with `pytest test_objects.py`.
# `pytest -rP test_objects.py` will send all print() output to the console (useful for debugging).
# Test XML files will be written to TEST_FILEMANAGER/.


# TO TEST:
# For each base object (incl protomod, mod):
# - load nonexistent obj
#    - TEST:  Fails
# - load new object, set inst+user, save
#    - TEST:  Verify saved
# - clear object
#    - TEST:  Verify cleared
# - reload original obj
#    - TEST:  Verify inst+user re-set
#
# Part creation for protomodule, module / assembly step objects
# - Assembly steps TBD
# - create test baseplate+sensor, save
# - create test protomodule from the above, save, load
#    - TEST:  verify thickness/type have been passed to new object correctly
# - create test pcb, save
# - create test module from the above, save, load
#    - TEST:  verify thickness/type have been passed to new object correctly
#
# Assembly step testing:
# - TBD - test UI pages, not just fm objects?  Might be tough to implement...

# Pass in temp dir for file storage

datadir = "/Users/phillip/Research/SharedUI/TEST_FILEMANAGER"
# remote temp data dir, if it already exists
if os.path.isdir(datadir):
	shutil.rmtree(datadir)
fm.setup(datadir=datadir)
print("SETUP RESULT DIR:", fm.DATADIR)


partlist = ['baseplate', 'sensor', 'pcb']#, 'protomodule', 'module']
toollist = ['tool_sensor', 'tool_pcb', 'tray_assembly', 'tray_component_sensor', 'tray_component_pcb']
suplist = ['batch_araldite', 'batch_wedge', 'batch_sylgard', 'batch_bond_wire']


@pytest.mark.parametrize("parttype", partlist)
def test_bad_load_part(parttype):
	test_part = getattr(parts, parttype)()
	assert not test_part.load("THIS_SHOULD_FAIL")

# Note:  This also generates XML files in TEST_FILEMANAGER for inspection
@pytest.mark.parametrize("parttype", partlist)
def test_load_save(parttype):
	test_part = getattr(parts, parttype)()
	objname = parttype+"_TEST"
	test_part.new(objname)
	test_part.institution = "CERN"
	test_part.insertion_user = "pmasterson"
	test_part.save()
	test_part.clear()
	test_part.load(objname)
	assert test_part.institution == "CERN" and test_part.insertion_user == "pmasterson"

@pytest.mark.parametrize("parttype", partlist)
def test_xml(parttype):
	test_part = getattr(parts, parttype)()
	objname = parttype+"_TEST_XML"
	test_part.new(objname)
	# Note:  Can't set all attrs, just the common fsobj_part ones
	# Also can't set kind_of_part, format is part-dependent
	test_part.record_insertion_user = 'phmaster'
	test_part.location = 'UCSB'
	test_part.comment_description.append('comment description')
	test_part.initiated_by_user = 'phmaster'
	test_part.flatness = 0.01
	test_part.thickness = 0.01  # Note - may be a str for sensors, float otherwise
	test_part.grade = 'A'
	test_part.comments.extend(['comment_a', 'comment 2'])
	# part-specific:
	if parttype == 'baseplate':
		test_part.manufacturer = 'HQU'
	elif parttype == 'sensor':
		test_part.visual_inspection = 'pass'
		test_part.test_file_name = 'testfile.abc'
	elif parttype == 'pcb':
		test_part.test_file_name = 'testfile.def'
	test_part.generate_xml()
	assert True # Always passes, must check the output manually
	# Could maybe automate this someday

@pytest.mark.parametrize("parttype", partlist)()
def test_kindOfPart(parttype):
	test_part = getattr(parts, parttype)()
	objname = parttype+"_TEST_NAME"
	test_part.new(objname)
	if parttype == "baseplate":
		test_part.mat_type = 'CuW/Kapton'
		test_part.channel_density = 'LD'
		test_part.geometry = 'Full'
		target = 'CuW/Kapton Baseplate LD Full'
		assert test_part.kind_of_part == target, \
               'kind_of_part assigned incorrectly:  wanted `{}`, got `{}`'.format(target, test_part.kind_of_part)
	elif parttype == "sensor":
		test_part.sen_type = '200um'
		test_part.channel_density = 'LD'
		test_part.geometry = 'Full'
		target = '200um Si Sensor LD Full'
		assert test_part.kind_of_part == target, \
               'kind_of_part assigned incorrectly:  wanted `{}`, got `{}`'.format(target, test_part.kind_of_part)
	elif parttype == "pcb":
		test_part.channel_density = 'LD'
		test_part.geometry = 'Full'
		target = 'PCB LD Full'
		assert test_part.kind_of_part == target, \
               'kind_of_part assigned incorrectly:  wanted `{}`, got `{}`'.format(target, test_part.kind_of_part)
	else:
		assert False, "Proto/mod kindOfPart not implemented"


@pytest.mark.parametrize("tooltype", toollist)
def test_bad_load_tool(tooltype):
	test_tool = getattr(tools, tooltype)()
	assert not test_tool.load("THIS_SHOULD_FAIL", "FAIL")

@pytest.mark.parametrize("tooltype", toollist)
def test_tools(tooltype):
	test_tool = getattr(tools, tooltype)()
	objname = tooltype+"_TEST"
	test_tool.new(objname, "UCSBTEST")
	test_tool.location = "CERN"
	test_tool.save()
	test_tool.clear()
	test_tool.load(objname, "UCSBTEST")
	assert test_tool.location == "CERN"


@pytest.mark.parametrize("suptype", suplist)
def test_bad_load_supply(suptype):
	test_sup = getattr(supplies, suptype)()
	assert not test_sup.load("THIS_SHOULD_FAIL")

@pytest.mark.parametrize("suptype", suplist)
def test_supplies(suptype):
	test_sup = getattr(supplies, suptype)()
	objname = suptype+"_TEST"
	test_sup.new(objname)
	test_sup.is_empty = True
	test_sup.save()
	test_sup.clear()
	test_sup.load(objname)
	assert test_sup.is_empty



"""
def test_asssembly_step(test_obj, test_ID):
	print("******TESTING: ", test_obj)
	first_result = test_obj.load("THIS SHOULD FAIL")
	print("***First result should be False:", first_result)
	test_obj.new('test_serial_number')
	test_obj.institution = 'UCSB'
	test_obj.insertion_user = 'pmasterson'
	print("***Test ID, institution after setting:", test_obj.ID, test_obj.institution)
	test_obj.save()
	test_obj.clear()
	test_obj.load('test_serial_number')
	print("***Test ID, institution after loading again:", test_obj.ID, test_obj.institution)
	print("***ATTEMPTING TO LOAD REAL OBJECT:")
	test_obj.clear()
	test_obj.load(test_serial)
	print("***LOADED REAL OBJECT.  Attempting to save...")
	test_obj.save()
	print("***All tests completed and passed!\n\n")
"""



