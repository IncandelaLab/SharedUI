from filemanager import fm, supplies, tools#, parts
import pytest # NEW
import shutil
import os

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


objlist = ['baseplate'] #, 'sensor', 'pcb', 'protomodule', 'module']
toollist = ['tool_sensor', 'tool_pcb', 'tray_assembly', 'tray_component_sensor', 'tray_component_pcb']
suplist = ['batch_araldite', 'batch_wedge', 'batch_sylgard', 'batch_bond_wire']

"""
@pytest.mark.parametrize("objtype", objlist)

def test_bad_load_part(objtype):
	test_obj = getattr(parts, objtype)()
	assert(not test_obj.load("THIS_SHOULD_FAIL"))

def test_load_save(objtype):
	test_obj = getattr(parts, objtype)()
	objname = objtype+"_TEST"
	test_obj.new(objname)
	test_obj.institution = "CERN"
	test_obj.insertion_user = "pmasterson"
	test_obj.save()
	test_obj.clear()
	test_obj.load(objname)
	assert(test_obj.institution == "CERN" and test_obj.insertion_user == "pmasterson")
"""


@pytest.mark.parametrize("tooltype", toollist)
def test_bad_load_tool(tooltype):
	test_tool = getattr(tools, tooltype)()
	assert(not test_tool.load("THIS_SHOULD_FAIL", "FAIL"))

@pytest.mark.parametrize("tooltype", toollist)
def test_tools(tooltype):
	test_tool = getattr(tools, tooltype)()
	objname = tooltype+"_TEST"
	test_tool.new(objname, "UCSBTEST")
	test_tool.location = "CERN"
	test_tool.save()
	test_tool.clear()
	test_tool.load(objname, "UCSBTEST")
	assert(test_tool.location == "CERN")


@pytest.mark.parametrize("suptype", suplist)
def test_bad_load_supply(suptype):
	test_sup = getattr(supplies, suptype)()
	assert(not test_sup.load("THIS_SHOULD_FAIL"))

@pytest.mark.parametrize("suptype", suplist)
def test_supplies(suptype):
	test_sup = getattr(supplies, suptype)()
	objname = suptype+"_TEST"
	test_sup.new(objname)
	test_sup.is_empty = True
	test_sup.save()
	test_sup.clear()
	test_sup.load(objname)
	assert(test_sup.is_empty)



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



