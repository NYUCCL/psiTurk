# -*- coding: utf-8 -*-
""" This module sets up a demo experiment to use with psiTurk.  """

import os
from distutils import dir_util, file_util
# from psiturk_config import PsiturkConfig  # unused

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), "example")
DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__),\
    "default_configs/local_config_defaults.txt")
DEFAULT_GLOBAL_CONFIG_FILE = os.path.join(os.path.dirname(__file__), \
    "default_configs/global_config_defaults.txt")

# If working in OpenShift, global config file lives in data directory
if 'OPENSHIFT_SECRET_TOKEN' in os.environ:
    GLOBAL_CONFIG_PATH = os.environ['OPENSHIFT_DATA_DIR'] + ".psiturkconfig"
else:
    GLOBAL_CONFIG_PATH = "~/.psiturkconfig"

GLOBAL_CONFIG_FILE = os.path.expanduser(GLOBAL_CONFIG_PATH)
EXAMPLE_TARGET = os.path.join(os.curdir, "psiturk-example")
CONFIG_TARGET = os.path.join(EXAMPLE_TARGET, "config.txt")

def setup_example():
    ''' Setup example '''
    if os.path.exists(EXAMPLE_TARGET):
        print "Error, `psiturk-example` directory already exists.  Please \
            remove it then re-run the command."
    else:
        print "Creating new folder `psiturk-example` in the current working \
            directory"
        os.mkdir(EXAMPLE_TARGET)
        print "Copying", EXAMPLE_DIR, "to", EXAMPLE_TARGET
        dir_util.copy_tree(EXAMPLE_DIR, EXAMPLE_TARGET)
        # change to target director
        print "Creating default configuration file (config.txt)"
        file_util.copy_file(DEFAULT_CONFIG_FILE, CONFIG_TARGET)
        os.chdir(EXAMPLE_TARGET)
        os.rename('custom.py.txt', 'custom.py')

        if not os.path.exists(GLOBAL_CONFIG_FILE):
            print "No '.psiturkconfig' file found in your home \
                directory.\nCreating default '~/.psiturkconfig' file."
            file_util.copy_file(DEFAULT_GLOBAL_CONFIG_FILE, GLOBAL_CONFIG_FILE)


if __name__ == "__main__":
    setup_example()
