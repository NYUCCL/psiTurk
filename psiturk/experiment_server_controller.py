import os, sys
import subprocess
import signal
from threading import Thread, Event
import urllib2
import datetime
import socket


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Supporting functions
#   general purpose helper functions used by the dashboard server and controller
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def is_port_available(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return 0
    except:
        return 1

def wait_until_online(function, **kwargs):
    """
    Uses Wait_For_State to wait for the server to come online, then runs the given function.
    """
    kword_keys = kwargs.keys()
    if 'ip' in kword_keys and 'port' in kword_keys:
        ip = kwargs['ip']
        port = kwargs['port']
    awaiting_service = Wait_For_State(lambda: is_port_available(ip, port), function)
    awaiting_service.start()
    return awaiting_service


#----------------------------------------------------------------
# handles waiting for processes which we don't control (e.g., 
# browser requests)
#----------------------------------------------------------------
class Wait_For_State(Thread):
    """
    Waits for a state-checking function to return True, then runs a given
    function. For example, this is used to launch the browser once the server is
    started up.  
    
    Example:
    t = Wait_For_State(lambda: server.check_port_state(), lambda: print "Server has started!")
    t.start()
    t.cancel() # Cancels thread
    """
    def __init__(self, state_function, function, pollinterval=1):
        Thread.__init__(self)
        self.function = function
        self.state_function = state_function
        self.pollinterval = pollinterval
        self.finished = Event()
        self.final = lambda: ()

    def cancel(self):
        self.finished.set()
    
    def run(self):
        while not self.finished.is_set():
            if self.state_function():
                self.function()
                self.finished.set()
            else:
                self.finished.wait(self.pollinterval)

#----------------------------------------------
# vanilla exception handler
#----------------------------------------------
class ExperimentServerControllerException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#----------------------------------------------
# simple wrapper class to control the 
# starting/stopping of experiment server
#----------------------------------------------
class ExperimentServerController:
    def __init__(self, port=None, hostname="localhost", ip='127.0.0.1'):
        self.port = port
        self.ip = ip
        self.hostname = hostname
    
    def get_ppid(self):
        if not self.is_port_available():
            url = "http://{hostname}:{port}/ppid".format(hostname=self.hostname, port=self.port)
            ppid_request = urllib2.Request(url)
            ppid =  urllib2.urlopen(ppid_request).read()
            return ppid
        else:
            raise ExperimentServerControllerException("Cannot shut down experiment server, server not online")
    
    def shutdown(self, ppid=None):
        if not ppid:
            ppid = self.get_ppid()
        print("Shutting down experiment server at pid %s..." % ppid)
        try:
            os.kill(int(ppid), signal.SIGKILL)
        except ExperimentServerControllerException:
            print ExperimentServerControllerException
    
    def is_port_available(self):
        return is_port_available(self.ip, self.port)

    def startup(self):
        server_command = "{python_exec} '{server_script}'".format(
            python_exec = sys.executable,
            server_script = os.path.join(os.path.dirname(__file__), "psiturk_server.py")
        )
        if self.is_port_available():
            print("Running experiment server with command:", server_command)
            subprocess.Popen(server_command, shell=True, close_fds=True)
            return("Experiment server launching...")
        else:
            return("Experiment server is already running...")
