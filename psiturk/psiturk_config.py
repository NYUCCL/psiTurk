import os
from ConfigParser import SafeConfigParser

class PsiturkConfig(SafeConfigParser):
    def __init__(self, localConfig="config.txt", globalConfig="~/.psiturkconfig", **kwargs):
        self.parent = SafeConfigParser
        self.parent.__init__(self, **kwargs)
        self.localFile = localConfig
        self.globalFile = os.path.expanduser(globalConfig)
        self.localParser = self.parent(**kwargs)
        self.globalParser = self.parent(**kwargs)

    def load_config(self):
        if not os.path.exists(self.localFile):
            print "ERROR - no config.txt file in the current directory. \n\nAre you use this directory is a valid psiTurk experiment?  If you are starting a new project run 'psiturk-setup-example' in an empty directory."
            exit()
        self.localParser.read(self.localFile)
        if not os.path.exists(self.globalFile):
            print "No '.psiturkconfig' file found in your home directory.\nCreating default '.psiturkconfig' file."
            self.write_default_global()
        else:
            self.globalParser.read(self.globalFile)
        self.read([self.globalFile, self.localFile])

    def write(self, changeGlobal=False):
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
        if section in ["Server Parameters","Task Parameters"]:
            return True
        else:
            return False


    def write_default_global(self):
        sections = ['AWS Access', 'psiTurk Access']
        map(self.add_section, sections)
        map(self.globalParser.add_section, sections)

        # AWS Access Section
        self.set('AWS Access', 'aws_access_key_id', 'YourAccessKeyId', True)
        self.set('AWS Access', 'aws_secret_access_key', 'YourSecretAccessKey', True)
        self.set('AWS Access', 'aws_region', 'us-east-1', True)

        # psiTurk Access
        self.set('psiTurk Access', 'psiturk_access_key_id', 'YourAccessKeyId', True)
        self.set('psiTurk Access', 'psiturk_secret_access_id', 'YourSecretAccessKey', True)
        

    def write_default_local(self):
        sections = ['HIT Configuration', 'Database Parameters',
                    'Server Parameters', 'Task Parameters', 'Shell Parameters']
        map(self.add_section, sections)
        map(self.localParser.add_section, sections)

        # HIT Configuration
        self.set('HIT Configuration', 'title', 'Stroop task')
        self.set('HIT Configuration', 'description', 'Judge the color of a series of words.')
        self.set('HIT Configuration', 'amt_keywords', 'Perception, Psychology')
        self.set('HIT Configuration', 'lifetime', '24')
        self.set('HIT Configuration', 'US_only', 'true')
        self.set('HIT Configuration', 'Approve_Requirement', '95')
        self.set('HIT Configuration', 'contact_email_on_error', 'youremail@gmail.com')
        self.set('HIT Configuration', 'ad_group', 'My research project')
        self.set('HIT Configuration', 'psiturk_keywords', 'stroop')
        self.set('HIT Configuration', 'organization_name', 'New Great University')
        self.set('HIT Configuration', 'browser_exclude_rule', 'MSIE, mobile, tablet')

        # Database Parameters
        self.set('Database Parameters', 'database_url', 'sqlite:///participants.db')
        self.set('Database Parameters', 'table_name', 'turkdemo')

        #Server Parameters
        self.set('Server Parameters', 'host', 'localhost')
        self.set('Server Parameters', 'port', '22362')
        self.set('Server Parameters', 'cutoff_time', '30')
        self.set('Server Parameters', 'logfile', 'server.log')
        self.set('Server Parameters', 'loglevel', '2')
        self.set('Server Parameters', 'debug', 'true')
        self.set('Server Parameters', 'login_username', 'examplename')
        self.set('Server Parameters', 'login_pw', 'examplepassword')
        self.set('Server Parameters', 'threads', 'auto')
        
        # Task Parameters
        self.set('Task Parameters', 'experiment_code_version', '1.0')
        self.set('Task Parameters', 'num_conds', '1')
        self.set('Task Parameters', 'num_counters', '1')

        # Shell Parameters
        self.set('Shell Parameters', 'live_mode_at_launch', 'false')
