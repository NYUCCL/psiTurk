#!/usr/bin/env python
# myapp.run

from psiturk_server import PsiTurkServer
import subprocess
import time
import psutil
import webbrowser
from config import config
import os


DASHBOARD_PORT = "5000"  # TODO(Todd, Jay): Change this to user defined param via app

# TODO(): Find a better way to ensure that the dash's port is ready.
def kill_port(kill_port):
    str_port_kill = ':' + kill_port
    p = subprocess.Popen(['lsof', '-i', str_port_kill, '-t'], stdout=subprocess.PIPE)
    out = p.communicate()[0]
    ports = [int(port) for port in out.split('\n')[:-1]]
    commands = [(proc.name, proc.ppid) for proc in psutil.process_iter() if proc.ppid in ports]
    [os.kill(port, 9) for command, port in commands if command == 'Python']  # sig 9 is porbably too harsh

kill_port(DASHBOARD_PORT)

# Launch dashboard kernel
subprocess.Popen("python dashboard_server.py", shell=True)
time.sleep(2)  # Ensure that dashboard has sufficient time to load before launching browser
subprocess.Popen("python psiturk_server.py", shell=True)

launchurl = "http://"+config.get("Server Parameters", "host")+":"+DASHBOARD_PORT+"/dashboard"
webbrowser.open(launchurl, new=1, autoraise=True)
