#!/usr/bin/env python
# myapp.run

from psiturk_server import PsiTurkServer
import subprocess
import socket
import time
import psutil
import webbrowser
from config import config
import os


DEFAULT_DASHBOARD_PORT = 5000  # TODO(Todd, Jay): Change this to user defined param via app

# TODO(): Find a better way to ensure that the dash's port is ready.

def is_port_available(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', port))
        s.shutdown(1)
        return 0
    except:
        return 1

def find_open_port():
    if is_port_available(DEFAULT_DASHBOARD_PORT):
        open_port = DEFAULT_DASHBOARD_PORT
    else:
        open_port = next(port for port in range(5001, 10000) if is_port_available(port))
    return(open_port)

dashboard_port = find_open_port()

# Launch dashboard kernel
subprocess.Popen("python dashboard_server.py " + str(dashboard_port), shell=True)
time.sleep(3)  # Ensure that dashboard has sufficient time to load before launching browser
subprocess.Popen("python psiturk_server.py", shell=True)

launchurl = "http://"+config.get("Server Parameters", "host")+":"+str(dashboard_port)+"/dashboard"
webbrowser.open(launchurl, new=1, autoraise=True)
