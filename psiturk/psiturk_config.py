from __future__ import print_function
import six
from distutils import file_util
import os
from future import standard_library
standard_library.install_aliases()
import os
import sys
from distutils import file_util
import six
if six.PY2:
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser


class PsiturkConfig(ConfigParser):

    def __init__(self, localConfig="config.txt",
                 globalConfigName=".psiturkconfig", **kwargs):

        if 'PSITURK_GLOBAL_CONFIG_LOCATION' in os.environ:
            globalConfig = os.path.join(
                os.environ['PSITURK_GLOBAL_CONFIG_LOCATION'], globalConfigName)
        else:  # if nothing is set default to user's home directory
            globalConfig = "~/" + globalConfigName
        self.parent = ConfigParser
        self.parent.__init__(self, **kwargs)
        self.localFile = localConfig
        self.globalFile = os.path.expanduser(globalConfig)

    def load_config(self):
        defaults_folder = os.path.join(
            os.path.dirname(__file__), "default_configs")
        local_defaults_file = os.path.join(
            defaults_folder, "local_config_defaults.txt")
        global_defaults_file = os.path.join(
            defaults_folder, "global_config_defaults.txt")
        if not os.path.exists(self.localFile):
            print ("ERROR - no config.txt file in the current "
                   "directory. \n\n Are you sure this directory "
                   "is a valid psiTurk experiment?  "
                   "If you are starting a new project run "
                   "'psiturk-setup-example' first.")
            sys.exit()
        if not os.path.exists(self.globalFile):
            if 'PSITURK_GLOBAL_CONFIG_LOCATION' in os.environ:
                print ("No '.psiturkconfig' file found in your " +
                       os.environ['PSITURK_GLOBAL_CONFIG_LOCATION'] +
                       " directory.\nCreating default " +
                       self.globalFile + " file.")
            else:
                print ("No '.psiturkconfig' file found in your "
                       "home directory.\nCreating default "
                       "~/.psiturkconfig file.")
            file_util.copy_file(global_defaults_file, self.globalFile)

        # Read default global and local, then user's global and local. This way
        # any field not in the user's files will be set to the default value.
        self.read([global_defaults_file, local_defaults_file,
                   self.globalFile, self.localFile])

        # heroku reads from env vars instead of .psiturkconfig
        for section in ['psiTurk Access', 'AWS Access']:
            for (name, value) in self.items(section):
                if name in os.environ:
                    self.set(section, name, os.environ[name])

        # heroku dynamically assigns your app a port, so you can't set the
        # port to a fixed number database url is also dynamic
        if 'ON_HEROKU' in os.environ:
            self.set('Server Parameters', 'port', os.environ['PORT'])
            self.set('Database Parameters', 'database_url',
                     os.environ['DATABASE_URL'])
