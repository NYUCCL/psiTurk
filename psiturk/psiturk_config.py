import os
from distutils import file_util
from ConfigParser import SafeConfigParser

class PsiturkConfig(SafeConfigParser):
    def __init__(self, localConfig="config.txt", globalConfigName=".psiturkconfig", **kwargs):

        # If working in OpenShift, move global config file in data directory (has access rights)
        if 'OPENSHIFT_SECRET_TOKEN' in os.environ:
            globalConfig = os.environ['OPENSHIFT_DATA_DIR'] + globalConfigName
        elif 'PSITURK_GLOBAL_CONFIG_LOCATION' in os.environ:
            globalConfig = os.environ['PSITURK_GLOBAL_CONFIG_LOCATION'] + globalConfigName
        else: # if nothing is set default to user's home directory
            globalConfig = "~/" + globalConfigName

        self.parent = SafeConfigParser
        self.parent.__init__(self, **kwargs)
        self.localFile = localConfig
        self.globalFile = os.path.expanduser(globalConfig)
        # psiturkConfig contains two additional SafeConfigParser's holding the values
        # of the local and global config files. This lets us write to the local or global file
        # separately without writing all fields to both.
        self.localParser = self.parent(**kwargs)
        self.globalParser = self.parent(**kwargs)

    def load_config(self):
        defaults_folder = os.path.join(os.path.dirname(__file__), "default_configs")
        local_defaults_file = os.path.join(defaults_folder, "local_config_defaults.txt")
        global_defaults_file = os.path.join(defaults_folder, "global_config_defaults.txt")
        if not os.path.exists(self.localFile):
            print "ERROR - no config.txt file in the current directory. \n\nAre you use this directory is a valid psiTurk experiment?  If you are starting a new project run 'psiturk-setup-example' first."
            exit()
        self.localParser.read( self.localFile)
        if not os.path.exists(self.globalFile):
            if 'OPENSHIFT_SECRET_TOKEN' in os.environ:
                print "No '.psiturkconfig' file found in your " + os.environ['OPENSHIFT_DATA_DIR'] + " directory.\nCreating default " + self.globalFile + " file."
            elif 'PSITURK_GLOBAL_CONFIG_LOCATION' in os.environ:
                print "No '.psiturkconfig' file found in your " + os.environ['PSITURK_GLOBAL_CONFIG_LOCATION'] + " directory.\nCreating default " + self.globalFile + " file."
            else:
                print "No '.psiturkconfig' file found in your home directory.\nCreating default ~/.psiturkconfig file."
            file_util.copy_file(global_defaults_file, self.globalFile)
        self.globalParser.read(self.globalFile)
        # read default global and local, then user's global and local. This way
        # any field not in the user's files will be set to the default value.
        self.read([global_defaults_file, local_defaults_file, self.globalFile, self.localFile])

    def write(self, changeGlobal=False):
        """
        write to the user's global or local config file.
        """
        filename = self.localFile
        configObject = self.localParser
        if changeGlobal:
            filename = self.globalFile
            configObject = self.globalParser
        with open(filename, 'w') as fp:
            configObject.write(fp)

    def set(self, section, field, value, changeGlobal=False,  *args, **kwargs):
        """
        Set the given field in the given section to the given value.
        Return True if the server needs to be rebooted.
        """
        self.parent.set(self, section, field, str(value), *args, **kwargs)
        if changeGlobal:
            self.globalParser.set(section, field, str(value), *args, **kwargs)
        else:
            self.localParser.set(section, field, str(value), *args, **kwargs)
        self.write(changeGlobal)
        if section in ["Server Parameters","Task Parameters","Database Parameters"]:
            return True
        else:
            return False

