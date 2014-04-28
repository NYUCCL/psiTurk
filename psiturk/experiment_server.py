# myapp.mycustomapplication
from gunicorn.app.base import Application
from gunicorn import util
import multiprocessing
from psiturk_config import PsiturkConfig
import sys

config = PsiturkConfig()
config.load_config()

class ExperimentServer(Application):
    '''
    Custom Gunicorn Server Application that serves up the Experiment application
    '''

    def __init__(self, sandbox):
        '''__init__ method
        Load the base config and assign some core attributes.
        '''
        self.sandbox = sandbox
        self.load_user_config()
        self.usage = None
        self.callable = None
        self.options = self.user_options
        self.prog = None
        self.do_load_config()
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
        return util.import_app("psiturk.experiment:start_app(%s)" % self.sandbox)

    def load_user_config(self):
        workers = config.get("Server Parameters", "threads")  # config calls these threads to avoid confusing with workers
        if workers == "auto":
            workers = str(multiprocessing.cpu_count() * 2 + 1)

        self.loglevels = ["debug", "info", "warning", "error", "critical"]

        self.user_options = {
            'bind': config.get("Server Parameters", "host") + ":" + config.get("Server Parameters", "port"),
            'workers': workers,
            'loglevels': self.loglevels,
            'loglevel': self.loglevels[config.getint("Server Parameters", "loglevel")],
            # 'accesslog': config.get("Server Parameters", "logfile"),
            'errorlog': config.get("Server Parameters", "logfile")
        }

def launch(sandbox):
    ExperimentServer(sandbox).run()

if __name__ == "__main__":
    launch(sys.argv[1])
