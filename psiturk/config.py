
import os
from ConfigParser import ConfigParser

# Load up config file
configfilepath = os.path.join(os.getcwd(),
                              'config.txt')
config = ConfigParser()
config.read( configfilepath )
