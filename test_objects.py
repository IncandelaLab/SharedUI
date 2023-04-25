from filemanager import fm
import pytest # NEW

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


objlist = ['baseplate', 'sensor', 'pcb', 'protomodule', 'module']

@pytest.mark.parametrize("objtype", objlist)
	
def test_bad_load(objtype):
	test_obj = getattr(fm, objtype)()
	assert(not test_obj.load("THIS_SHOULD_FAIL"))

def test_load_save(objtype):
	test_obj = getattr(fm, objtype)()
	objname = objtype+"_TEST"
	test_obj.new(objname)
	test_obj.institution = "CERN"
	test_obj.insertion_user = "pmasterson"
	test_obj.save()
	test_obj.clear()
	test_obj.load(objname)
	assert(test_obj.institution == "CERN" and test_obj.insertion_user == "pmasterson")



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

#test_step_sensor = fm.step_sensor()
#test_assembly_step(test_step_sensor, "")
#test_step_sensor.load("FAILURE")
#test_step_sensor.load(63560)




