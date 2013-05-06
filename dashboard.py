import ConfigParser
import os

Config = ConfigParser.ConfigParser()

class PsiTurkConfig:
    def __init__(self, filename):
        self.filename = filename
        if not os.path.exists(self.filename):
            print("Creating config file...")
            self.load_default_config()
        else:
            print("Using current config file...")
            self.load_default_config()
            self.load_config()

    def set(self, section, key, value):
        configfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      self.filename)
        cfgfile = open(configfilepath, 'w')
        Config.set(section, key, value)
        Config.write(cfgfile)
        cfgfile.close()

    def get(self, section, key):
        if Config.has_option(section, key):
            return(Config.get(section, key))
        else:
            print("Option not available.")
            return(False)

    def get_serialized(self):
        # Serializing data is necessary to communicate w/ backbone frontend.
        if not os.path.exists(self.filename):
            print("No config file present!")
        else:
            return(Config._sections)

    def load_default_config(self):
        # Open new config file
        configfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      self.filename)
        cfgfile = open(configfilepath, 'w')
        sections = ['AWS Access', 'HIT Configuration', 'Database Parameters',
                    'Server Parameters', 'Task Parameters']
        map(Config.add_section, sections)

        # AWS Access Section
        Config.set('AWS Access', 'aws_access_key_id', 'YourAccessKeyId')
        Config.set('AWS Access', 'aws_secret_access_key', 'YourSecreteAccessKey')

        # HIT Configuration
        Config.set('HIT Configuration', 'title', 'Perceptual Reaction Time')
        Config.set('HIT Configuration', 'description', 'Make a series of perceptual judgments.')
        Config.set('HIT Configuration', 'keywords', 'Perception, Psychology')
        Config.set('HIT Configuration', 'question_url', 'http://localhost:5001/mturk')
        Config.set('HIT Configuration', 'max_assignments', '10')
        Config.set('HIT Configuration', 'HIT_lifetime', '24')
        Config.set('HIT Configuration', 'reward', '1')
        Config.set('HIT Configuration', 'duration', '2')
        Config.set('HIT Configuration', 'US_only', 'true')
        Config.set('HIT Configuration', 'Approve_Requirement', '95')
        Config.set('HIT Configuration', 'using_sandbox', 'true')

        # Database Parameters
        Config.set('Database Parameters', 'database_url', 'sqlite:///participants.db')
        Config.set('Database Parameters', 'table_name', 'turkdemo')

        #Server Parameters
        Config.set('Server Parameters', 'host', 'localhost')
        Config.set('Server Parameters', 'port', '5001')
        Config.set('Server Parameters', 'cutoff_time', '30')
        Config.set('Server Parameters', 'support_IE', 'true')
        Config.set('Server Parameters', 'logfile', 'server.log')
        Config.set('Server Parameters', 'loglevel', '2')
        Config.set('Server Parameters', '0', 'DEBUG')
        Config.set('Server Parameters', '1', 'INFO')
        Config.set('Server Parameters', '2', 'WARNING')
        Config.set('Server Parameters', '3', 'ERROR')
        Config.set('Server Parameters', '4', 'CRITICAL')
        Config.set('Server Parameters', 'debug', 'true')
        Config.set('Server Parameters', 'login_username', 'examplename')
        Config.set('Server Parameters', 'login_pw', 'examplepassword')

        # Task Parameters
        Config.set('Task Parameters', 'code_version', '1.0')
        Config.set('Task Parameters', 'num_conds', '1')
        Config.set('Task Parameters', 'num_counters', '1')

        # Write config file to drive
        Config.write(cfgfile)
        cfgfile.close()

    def load_config(self):
        configfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      self.filename)
        Config.read(str(configfilepath))

        # AWS Access Section
        self.aws_access_key_id = Config.get('AWS Access', 'aws_access_key_id', 'YourAccessKeyId')
        self.aws_secret_access_key = Config.get('AWS Access', 'aws_secret_access_key', 'YourSecreteAccessKey')

        # HIT Configuration
        self.title = Config.get('HIT Configuration', 'title')
        self.description = Config.get('HIT Configuration', 'description')
        self.keywords = Config.get('HIT Configuration', 'keywords')
        self.question_url = Config.get('HIT Configuration', 'question_url')
        self.max_assignments = Config.get('HIT Configuration', 'max_assignments')
        self.HIT_lifetime = Config.get('HIT Configuration', 'HIT_lifetime')
        self.reward = Config.get('HIT Configuration', 'reward')
        self.duration = Config.get('HIT Configuration', 'duration')
        self.US_only = Config.get('HIT Configuration', 'US_only')
        self.Approve_Requirment = Config.get('HIT Configuration', 'Approve_Requirement')

        # Database Parameters
        self.database_url = Config.get('Database Parameters', 'database_url')
        self.table_name =  Config.get('Database Parameters', 'table_name')

        #Server Parameters
        self.host = Config.get('Server Parameters', 'host')
        self.port = Config.get('Server Parameters', 'port')
        self.cutoff_time = Config.get('Server Parameters', 'cutoff_time')
        self.support_IE = Config.get('Server Parameters', 'support_IE')
        self.logfile = Config.get('Server Parameters', 'logfile')
        self.loglevel = Config.get('Server Parameters', 'loglevel')
        self.debug = Config.get('Server Parameters', 'debug')
        self.login_username = Config.get('Server Parameters', 'login_username')
        self.login_pw = Config.get('Server Parameters', 'login_pw')

        # Task Parameters
        self.code_version = Config.get('Task Parameters', 'code_version')
        self.num_conds = Config.get('Task Parameters', 'num_conds')
        self.num_counters = Config.get('Task Parameters', 'num_counters')
