# myapp.mycustomapplication
from gunicorn.app.base import Application
from gunicorn import util
import multiprocessing
from psiturk_config import PsiturkConfig
import os
import hashlib

config = PsiturkConfig()
config.load_config()

class ExperimentServer(Application):
    '''
    Custom Gunicorn Server Application that serves up the Experiment application
    '''

    def __init__(self):
        '''__init__ method
        Load the base config and assign some core attributes.
        '''
        self.load_user_config()
        self.usage = None
        self.callable = None
        self.options = self.user_options
        self.prog = None
        self.do_load_config()
        if 'OPENSHIFT_SECRET_TOKEN' in os.environ:
            my_ip = os.environ['OPENSHIFT_APP_DNS']
            print "Now serving on " + os.environ['OPENSHIFT_APP_DNS']
        else:
            print "Now serving on", "http://" + self.options["bind"]

    def init(self, *args):
        '''init method
        Takes our custom options from self.options and creates a config
        dict which specifies custom settings.
        '''
        cfg = {}
        for k, v in self.options.items():
            if k.lower() in self.cfg.settings and v is not None:
                cfg[k.lower()] = v
        return cfg

    def load(self):
        '''load method
        Imports our application and returns it to be run.
        '''
        return util.import_app("psiturk.experiment:app")

    def load_user_config(self):
        workers = config.get("Server Parameters", "threads")  # config calls these threads to avoid confusing with workers
        if workers == "auto":
            workers = str(multiprocessing.cpu_count() * 2 + 1)

        self.loglevels = ["debug", "info", "warning", "error", "critical"]

        def on_exit(server):
            ''' 
            this is hooked so that it can be called when 
            the server is shut down via CTRL+C. Otherwise
            there is no notification to the user that the server
            has shut down until they hit `enter` and see that 
            the cmdloop prompt suddenly says "server off"
            '''
            print 'Caught ^C, experiment server has shut down.'
            print 'Press `enter` to continue.'

        # add unique identifier of this psiturk project folder
        project_hash = hashlib.sha1(os.getcwd()).hexdigest()[:12]
        self.user_options = {
            'bind': config.get("Server Parameters", "host") + ":" + config.get("Server Parameters", "port"),
            'workers': workers,
            'loglevels': self.loglevels,
            'loglevel': self.loglevels[config.getint("Server Parameters", "loglevel")],
            # 'accesslog': config.get("Server Parameters", "logfile"),
            'errorlog': config.get("Server Parameters", "logfile"),
            'proc_name': 'psiturk_experiment_server_' + project_hash,
            'limit_request_line': '0',
            'on_exit': on_exit
        }

        if config.has_option("Server Parameters", "certfile") and config.has_option("Server Parameters", "keyfile"):
            print "Loading SSL certs for server..."
            ssl_options = {
                'certfile' : config.get("Server Parameters", "certfile"),
                'keyfile' : config.get("Server Parameters", "keyfile")
            }
            self.user_options.update(ssl_options)

        if config.has_option("Server Parameters", "server_timeout"):
            self.user_options.update({'timeout': config.get("Server Parameters", "server_timeout")})

        if 'ON_HEROKU' in os.environ:
            self.user_options.update({
                'accesslog' : '-',
                'errorlog' : '-'
                })


def launch():
    ExperimentServer().run()

if __name__ == "__main__":
    launch()
