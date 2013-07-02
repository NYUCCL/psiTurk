#!/usr/bin/env python
# myapp.run

import os, sys, subprocess, signal
import argparse

executable = sys.executable
directory = os.path.dirname(os.path.abspath(__file__))


def launch_dashboard_server(dashboard_port):
    # Launch dashboard kernel
    # TODO must figure out the right directory
    dashboard_call = "{pythonexec} {directory}/dashboard_server.py -p {port}".format(pythonexec=executable, directory=directory, port=dashboard_port)
    subprocess.Popen(dashboard_call, shell=True, preexec_fn=os.setsid)

def kill_dashboard(process):
    os.killpg(process.pid, signal.SIGTERM)

def launch():
    parser = argparse.ArgumentParser(description='Launch psiTurk and psiTurk dashboard.')
    parser.add_argument('-p', '--port', default=22361,
                        help='optional port for dashboard. default is 72361.')
    parser.add_argument('-k', '--kill', default=False,
                        help='kill dashboard.')
    args = parser.parse_args()
    dashboard_port = args.port

    if args.kill:
        kill_dashboard(dashboard_port)
    else:
        launch_dashboard_server(dashboard_port)

if __name__=="__main__":
    launch()
