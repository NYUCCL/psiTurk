
import os
from ConfigParser import ConfigParser

# Load up config file
configfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'config.txt')
config = ConfigParser()
config.read( configfilepath )
