# -*- coding: utf-8 -*-
""" This module sets up a demo experiment to use with psiTurk.  """
from __future__ import generator_stop
import os
from distutils import dir_util, file_util

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), "example")
DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__),
                                   "default_configs/local_config_defaults.txt")
DEFAULT_GLOBAL_CONFIG_FILE = os.path.join(os.path.dirname(__file__),
                                          "default_configs/global_config_defaults.txt")

if 'PSITURK_GLOBAL_CONFIG_LOCATION' in os.environ:
    GLOBAL_CONFIG_PATH = os.path.join(os.environ['PSITURK_GLOBAL_CONFIG_LOCATION'],
                                      ".psiturkconfig")
else:
    GLOBAL_CONFIG_PATH = "~/.psiturkconfig"

GLOBAL_CONFIG_FILE = os.path.expanduser(GLOBAL_CONFIG_PATH)
EXAMPLE_TARGET = os.path.join(os.curdir, "psiturk-example")


def setup_example():
    """ Setup example """
    if os.path.exists(EXAMPLE_TARGET):
        print("Error, `psiturk-example` directory already exists. Please \
            remove it then re-run the command.")
    else:
        print("Creating new folder `psiturk-example` in the current working \
            directory")
        os.mkdir(EXAMPLE_TARGET)

        print("Copying", EXAMPLE_DIR, "to", EXAMPLE_TARGET)
        dir_util.copy_tree(EXAMPLE_DIR, EXAMPLE_TARGET)

        file_util.move_file(os.path.join(EXAMPLE_TARGET, 'config.txt.sample'), os.path.join(EXAMPLE_TARGET, 'config.txt'))
        file_util.move_file(os.path.join(EXAMPLE_TARGET, 'custom.py.sample'), os.path.join(EXAMPLE_TARGET, 'custom.py'))


        # change to target directory
        os.chdir(EXAMPLE_TARGET)


if __name__ == "__main__":
    setup_example()
