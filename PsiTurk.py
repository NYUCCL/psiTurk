#!/usr/bin/env python
# myapp.run

from psiturk_server import PsiTurkServer
import multiprocessing
import subprocess
from config import config
import webbrowser

DASHBOARD_PORT = "5000"  # TODO(Todd, Jay): Change this to user defined param via app

# Launch dashboard kernel
subprocess.Popen("python dashboard_server.py", shell=True,
                 stdout=subprocess.PIPE,
                 stderr=subprocess.STDOUT)
workers = multiprocessing.cpu_count() * 2 + 1

if __name__ == "__main__":
    loglevels = ["debug", "info", "warning", "error", "critical"]
    options = {
        'bind': config.get("Server Parameters", "host") + ":" + config.get("Server Parameters", "port"),
        'workers': str(multiprocessing.cpu_count() * 2 + 1),
        'loglevels': loglevels,
        'loglevel': loglevels[config.getint("Server Parameters", "loglevel")]
    }

launchurl = "http://"+config.get("Server Parameters", "host")+DASHBOARD_PORT+"/dashboard"
webbrowser.open(launchurl, new=1, autoraise=True)

PsiTurkServer(options).run()
