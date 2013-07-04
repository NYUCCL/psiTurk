#!/usr/bin/env python
# myapp.run

import os, sys, subprocess
#from signal import signal, SIGINT, pause
import argparse

class PsiTurkLauncher:
    def __init__(self, dashboard_port):
        self.executable = sys.executable
        self.directory = os.path.dirname(os.path.abspath(__file__))
        self.dashboard_port = dashboard_port
    
    def launch_dashboard_server(self):
        # Launch dashboard kernel
        #dashboard_call = "{pythonexec} {directory}/dashboard_server.py -p {port}".format(pythonexec=self.executable, directory=self.directory, port=self.dashboard_port)
        #self.process = subprocess.Popen(dashboard_call, shell=True, preexec_fn=os.setsid)
        subprocess.check_call([self.executable, os.path.join(self.directory, "dashboard_server.py"), "-p", str(self.dashboard_port)])

    def kill_dashboard(self):
        self.process.terminate()

def launch():
    parser = argparse.ArgumentParser(description='Launch psiTurk and psiTurk dashboard.')
    parser.add_argument('-p', '--port', default=22361,
                        help='optional port for dashboard. default is 72361.')
    args = parser.parse_args()
    dashboard_port = args.port
    
    launcher = PsiTurkLauncher(dashboard_port)
    #signal(SIGINT, launcher.kill_dashboard)
    
    launcher.launch_dashboard_server()
    #pause()

if __name__=="__main__":
    launch()
