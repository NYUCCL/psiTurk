import os
from ConfigParser import SafeConfigParser

class PsiTurkConfig(SafeConfigParser):
    def __init__(self, filename="config.txt", **kwargs):
        self.parent = SafeConfigParser
        self.parent.__init__(self, **kwargs)
        self.filename = filename
        if not os.path.exists(self.filename):
            print("Creating config file...")
            self.write_default_config()
        self.read(self.filename)

    def write(self):
        with open(self.filename, 'w') as fp:
            self.parent.write(self, fp)

    def set(self, section, field, value,  *args, **kwargs):
        self.parent.set(self, section, field, str(value), *args, **kwargs)
        self.write()

    #def read(self):
    #    super(ConfigParser, self).read(self.filename)

    def get_serialized(self):
        # Serializing data is necessary to communicate w/ backbone frontend.
        return self._sections

    def set_serialized(self, config_model):
        for section, fields in config_model.iteritems():
            for field in fields:
                self.set(section, field, config_model[section][field])


    def write_default_config(self):
        sections = ['AWS Access', 'HIT Configuration', 'Database Parameters',
                    'Server Parameters', 'Task Parameters']
        map(self.add_section, sections)
        # AWS Access Section
        self.set('AWS Access', 'aws_access_key_id', 'YourAccessKeyId')
        self.set('AWS Access', 'aws_secret_access_key', 'YourSecreteAccessKey')
        # HIT Configuration
        self.set('HIT Configuration', 'title', 'Perceptual Reaction Time')
        self.set('HIT Configuration', 'description', 'Make a series of perceptual judgments.')
        self.set('HIT Configuration', 'keywords', 'Perception, Psychology')
        self.set('HIT Configuration', 'question_url', 'http://localhost:5001/mturk')
        self.set('HIT Configuration', 'max_assignments', '10')
        self.set('HIT Configuration', 'HIT_lifetime', '24')
        self.set('HIT Configuration', 'reward', '1')
        self.set('HIT Configuration', 'duration', '2')
        self.set('HIT Configuration', 'US_only', 'true')
        self.set('HIT Configuration', 'Approve_Requirement', '95')
        self.set('HIT Configuration', 'using_sandbox', 'true')

        # Database Parameters
        self.set('Database Parameters', 'database_url', 'sqlite:///participants.db')
        self.set('Database Parameters', 'table_name', 'turkdemo')

        #Server Parameters
        self.set('Server Parameters', 'host', 'localhost')
        self.set('Server Parameters', 'port', '22362')
        self.set('Server Parameters', 'cutoff_time', '30')
        self.set('Server Parameters', 'support_IE', 'true')
        self.set('Server Parameters', 'logfile', 'server.log')
        self.set('Server Parameters', 'loglevel', '2')
        self.set('Server Parameters', 'debug', 'true')
        self.set('Server Parameters', 'login_username', 'examplename')
        self.set('Server Parameters', 'login_pw', 'examplepassword')
        
        # Task Parameters
        self.set('Task Parameters', 'code_version', '1.0')
        self.set('Task Parameters', 'num_conds', '1')
        self.set('Task Parameters', 'num_counters', '1')
