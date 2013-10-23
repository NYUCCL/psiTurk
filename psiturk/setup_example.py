import os
from distutils import dir_util
from psiturk_config import PsiturkConfig

static_dir = os.path.join(os.path.dirname(__file__), "static_example")
templates_dir = os.path.join(os.path.dirname(__file__), "templates_example")

static_target = os.path.join(os.curdir, "static")
templates_target = os.path.join(os.curdir, "templates")

def setup_example():
    print "Copying", static_dir, "to", static_target
    dir_util.copy_tree(static_dir, static_target)
    print "Copying", templates_dir, "to", templates_target
    dir_util.copy_tree(templates_dir, templates_target)
    print "Creating default configuration file"
    config = PsiturkConfig()


if __name__=="__main__":
    setup_example()
