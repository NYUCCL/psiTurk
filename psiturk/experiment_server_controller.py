import os, sys
import subprocess
import signal
import webbrowser
from threading import Thread, Event
import urllib2
import socket


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Supporting functions
#   general purpose helper functions used by the dashboard server and controller
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def is_port_available(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return False
    except socket.timeout:
        print "*** Failed to test port availability. Check that host\nis set properly in config.txt"
        return True
    except socket.error,e:
        return True

def wait_until_online(function, ip, port):
    """
    Uses Wait_For_State to wait for the server to come online, then runs the given function.
    """
    awaiting_service = Wait_For_State(lambda: not is_port_available(ip, port), function)
    awaiting_service.start()
    return awaiting_service

def launch_browser(host, port, route):
    launchurl = "http://{host}:{port}/{route}".format(host=host, port=port, route=route)
    webbrowser.open(launchurl, new=1, autoraise=True)

def launch_browser_when_online(ip, port, route):
    return wait_until_online(lambda: launch_browser(ip, port, route), ip, port)


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
    def __init__(self, config):
        self.config = config
        self.server_running = False

    def get_ppid(self):
        if not self.is_port_available():
            url = "http://{hostname}:{port}/ppid".format(hostname=self.config.get("Server Parameters", "host"), port=self.config.getint("Server Parameters", "port"))
            ppid_request = urllib2.Request(url)
            ppid =  urllib2.urlopen(ppid_request).read()
            return ppid
        else:
            raise ExperimentServerControllerException("Cannot shut down experiment server, server not online")

    def restart(self):
        self.shutdown()
        self.startup()

    def shutdown(self, ppid=None):
        if not ppid:
            ppid = self.get_ppid()
        print("Shutting down experiment server at pid %s..." % ppid)
        try:
            os.kill(int(ppid), signal.SIGKILL)
            self.server_running = False
        except ExperimentServerControllerException:
            print ExperimentServerControllerException
        else:
            self.server_running = False

    def is_server_running(self):
        portopen = self.is_port_available()
        #print self.server_running, " ", portopen
        if self.server_running and portopen:  # server running but port open, maybe starting up
            return 'maybe'
        elif not self.server_running and not portopen: # server not running but port blocked maybe shutting down
            return 'maybe'
        elif self.server_running and not portopen: # server running, port blocked, makes sense
            return 'yes'
        elif not self.server_running and portopen: # server off, port open, makes sense
            return 'no'

    def is_port_available(self):
        return is_port_available(self.config.get("Server Parameters", "host"), self.config.getint("Server Parameters", "port"))

    def startup(self, useSandbox):
        server_command = "{python_exec} '{server_script}' {sandbox}".format(
            python_exec = sys.executable,
            server_script = os.path.join(os.path.dirname(__file__), "experiment_server.py"),
            sandbox = useSandbox
        )
        if self.is_port_available() and not self.server_running:
            #print "Running experiment server with command:", server_command
            subprocess.Popen(server_command, shell=True, close_fds=True)
            print "Experiment server launching..."
            self.server_running = True
        else:
            print "Experiment server may be already running..."
