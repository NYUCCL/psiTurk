import os
from distutils import dir_util, file_util
from psiturk_config import PsiturkConfig

example_dir = os.path.join(os.path.dirname(__file__), "example")
default_config_file = os.path.join(os.path.dirname(__file__), "default_configs/local_config_defaults.txt")
default_global_config_file = os.path.join(os.path.dirname(__file__), "default_configs/global_config_defaults.txt")

# If working in OpenShift, global config file lives in data directory
if 'OPENSHIFT_SECRET_TOKEN' in os.environ:
    globalConfigPath = os.environ['OPENSHIFT_DATA_DIR'] + ".psiturkconfig"
else:
    globalConfigPath = "~/.psiturkconfig"

global_config_file = os.path.expanduser(globalConfigPath)
example_target = os.path.join(os.curdir, "psiturk-example")
config_target = os.path.join(example_target, "config.txt")

def setup_example():
	if os.path.exists(example_target):
		print "Error, `psiturk-example` directory already exists.  Please remove it then re-run the command."
	else:
		print "Creating new folder `psiturk-example` in the current working directory"
		os.mkdir(example_target)
		print "Copying", example_dir, "to", example_target
		dir_util.copy_tree(example_dir, example_target)
		# change to target director
		print "Creating default configuration file (config.txt)"
                file_util.copy_file(default_config_file , config_target)
		os.chdir(example_target)
		os.rename('custom.py.txt', 'custom.py')

        if not os.path.exists(global_config_file):
            print "No '.psiturkconfig' file found in your home directory.\nCreating default '~/.psiturkconfig' file."
            file_util.copy_file(default_global_config_file, global_config_file)


if __name__=="__main__":
	setup_example()
