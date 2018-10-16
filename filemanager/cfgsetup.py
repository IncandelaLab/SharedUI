import os
import sys

DATA_DIR_CONTENTS = {
	''          :['config.txt'],
	'modules'   :{},
	'PCBs'      :{},
	'sensors'   :{}.
	'baseplates':{},
	'supplies'  :{},
	'hardware'  :{
		'gantry'     :{},
		'wirebonder' :{},
		'pull tester':{},
		'test stands':{},
	},
	'steps'     :{
		'kapton application':{},
		'sensor application':{},
		'PCB application'   :{},
	},
}

def choice(options, prompt, msgValid=None, msgInvalid='invalid choice'):
	done=False
	while not done:
		ans = input(prompt)
		if ans in options:
			if msgValid:print(msgValid)
			return ans
		else:
			if msgInvalid:print(msgInvalid)

def validate(validator,prompt,msgValid=None,msgInvalid='invalid choice',psp=None):
	done = False
	while not done:
		ans = input(prompt)
		if validator(ans):
			if msgValid:print(msgValid)
			if psp:ans=psp(ans)
			return ans
		else:
			if msgInvalid:print(msgInvalid)



if __name__ == '__main__':

	print("config setup for filemanager")
	print("")

	print("completing this process will delete any existing config file")
	conf = choice(['y','n','Y','N'],'continue with process? (y/n) : ',msgInvalid='invalid choice').lower()
	if conf == 'n':
		sys.exit()
	print("")

	datadir = validate(os.path.exists,'enter desired data directory : ',msgInvalid='directory does not exist')
	print(datadir)
	print("")

	contents = os.listdir(datadir)
	if len(contents) == 0:
		print("data directory is empty")
		print("setting up directory...")
	else:
		if ''

	# cases for datadir
	# 1) empty -> setup with folders, files; save datadir to config.txt
	# 2) non-empty, contains setup file -> just save datadir to config.txt
	# 3) non-empty, doesn't contain setup file -> warning 