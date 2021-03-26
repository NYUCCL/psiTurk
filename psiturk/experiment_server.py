from __future__ import generator_stop
from gunicorn.app.base import Application
from gunicorn import util
import multiprocessing
from psiturk.psiturk_config import PsiturkConfig
import os
import sys
import hashlib
import signal
from gevent import monkey
monkey.patch_all()

config = PsiturkConfig()
config.load_config()


def sigint_handler(signal, frame):
    """
    Give feedback when ^C is submitted by user.

    Unfortunately, this does not tell psiturk interactive to update server status
    """
    print('^C: shutting down server processes.')
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


class ExperimentServer(Application):
    """
    Custom Gunicorn Server Application that serves up the Experiment application
    """

    def __init__(self, app_dir=None):
        """__init__ method
        Load the base config and assign some core attributes.
        """

        self.loglevels = ["debug", "info", "warning", "error", "critical"]
        self.load_user_config()
        self.usage = None
        self.callable = None
        self.options = self.user_options
        self.prog = None
        self.do_load_config()
        if app_dir:
            self.cfg.set('chdir', app_dir) # get directory
            self.chdir() # change to it
        self.user_options = {}
        print("Now serving on", "http://" + self.options["bind"])

    def init(self, *args):
        """init method
        Takes our custom options from self.options and creates a config
        dict which specifies custom settings.
        """
        cfg = {}
        for k, v in list(self.options.items()):
            if k.lower() in self.cfg.settings and v is not None:
                cfg[k.lower()] = v
        return cfg

    def load(self):
        """load method
        Imports our application and returns it to be run.
        """
        return util.import_app("psiturk.experiment:app")

    def load_user_config(self):
        # config calls these threads to avoid confusing with workers
        workers = config.get('Server Parameters', "threads")
        if workers == "auto":
            workers = str(multiprocessing.cpu_count() * 2 + 1)

        if int(workers) > 1 and config.getboolean('Server Parameters',
                                                  'do_scheduler'):
            raise Exception((
                'Scheduler is not thread-safe, '
                'but {} gunicorn workers requested! Refusing to start!'
                ).format(workers)
            )

        self.loglevels = ["debug", "info", "warning", "error", "critical"]

        # add unique identifier of this psiturk project folder
        project_hash = hashlib.sha1(os.getcwd().encode()).hexdigest()[:12]
        self.user_options = {
            'bind': config.get('Server Parameters', "host") + ":" + config.get('Server Parameters', "port"),
            'workers': workers,
            'worker_class': 'gevent',
            'loglevels': self.loglevels,
            'loglevel': self.loglevels[config.getint("Server Parameters", "loglevel")],
            'accesslog': config.get('Server Parameters', "accesslog"),
            'errorlog': config.get('Server Parameters', "errorlog"),
            'proc_name': 'psiturk_experiment_server_' + project_hash,
            'limit_request_line': '0',
        }

        if config.get("Server Parameters", "certfile") and config.get("Server Parameters", "keyfile"):
            print("Loading SSL certs for server...")
            ssl_options = {
                'certfile': config.get('Server Parameters', "certfile"),
                'keyfile': config.get('Server Parameters', "keyfile")
            }
            self.user_options.update(ssl_options)

        if config.has_option("Server Parameters", "server_timeout"):
            self.user_options.update(
                {'timeout': config.get('Server Parameters', "server_timeout")})


def launch(app_dir=None):
    ExperimentServer(app_dir).run()


if __name__ == "__main__":
    launch()
