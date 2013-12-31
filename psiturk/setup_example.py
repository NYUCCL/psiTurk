import os
from distutils import dir_util
from psiturk_config import PsiturkConfig

example_dir = os.path.join(os.path.dirname(__file__), "example")

example_target = os.path.join(os.curdir, "psiturk-example")

def setup_example():
	if os.path.exists(example_target):
		print "Error, `psiturk-example` directory already exists.  Please remove it then re-run the command."
	else:
		print "Creating new folder `psiturk-example` in the current working directory"
		os.mkdir(example_target)
		print "Copying", example_dir, "to", example_target
		dir_util.copy_tree(example_dir, example_target)
		# change to target director
		os.chdir(example_target)
		os.rename('custom.py.txt', 'custom.py')
		print "Creating default configuration file (config.txt)"
		config = PsiturkConfig()
		config.write_default_config()

if __name__=="__main__":
	setup_example()
