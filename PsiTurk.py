#!/usr/bin/env python
# myapp.run

from psiturk_server import PsiTurkServer
import subprocess
import socket
import time
import psutil
import os
import sys
import argparse
import zmq
import time


parser = argparse.ArgumentParser(description='Launch psiTurk and psiTurk dashboard.')
parser.add_argument('-p', '--port', default=5000,
                    help='optional port for dashboard. default is 5000.')
parser.add_argument('-k', '--kill', default=False,
                    help='kill dashboard.')
args = parser.parse_args()
dashboard_port = args.port


def listen_for_dashboard(pubsub_socket_port):
    context = zmq.Context()
    pubsub_socket = context.socket(zmq.SUB)
    pubsub_socket.bind("tcp://127.0.0.1:" + pubsub_socket_port)
    topicfilter = "dashboard"
    pubsub_socket.setsockopt(zmq.SUBSCRIBE, '')
    return pubsub_socket

def get_dashboard_port():
    return(dashboard_port)

# if args.kill:
#     kill_dashboard(p)

def launch_dashboard_server():
    # Launch dashboard kernel
    p = subprocess.Popen("python dashboard_server.py ", shell=True, preexec_fn=os.setsid)
    return p
    # subprocess.Popen("python psiturk_server.py", shell=True)

def kill_dashboard(process):
    os.killpg(process.pid, signal.SIGTERM)

def launch_psiturk():
    # pubsub_socket = listen_for_dashboard(open_port)
    launch_dashboard_server(open_port)
    # while True:
    #     string = pubsub_socket.recv()
    #     topic, message = string.split()
    #     print string
    #     sys.stdout.flush()
    #     if topic == "dashboard" and message == "up":
    #         pass
    #         # launch_browser(open_port)

launch_dashboard_server()
