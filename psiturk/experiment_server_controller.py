from __future__ import print_function
import urllib.parse
import urllib.error
import urllib.request
import hashlib
import time
import psutil
import socket
from threading import Thread, Event
import webbrowser
import signal
import subprocess
import sys
import os
from builtins import object
from future import standard_library
standard_library.install_aliases()


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
        print("*** Failed to test port availability. Check that host\nis set properly in config.txt")
        return True
    except socket.error as e:
        return True


def wait_until_online(function, ip, port):
    """
    Uses Wait_For_State to wait for the server to come online, then runs the given function.
    """
    awaiting_service = Wait_For_State(
        lambda: not is_port_available(ip, port), function)
    awaiting_service.start()
    return awaiting_service


def launch_browser(host, port, route):
    launchurl = "http://{host}:{port}/{route}".format(
        host=host, port=port, route=route)
    webbrowser.open(launchurl, new=1, autoraise=True)


def launch_browser_when_online(ip, port, route):
    return wait_until_online(lambda: launch_browser(ip, port, route), ip, port)


# ----------------------------------------------------------------
# handles waiting for processes which we don't control (e.g.,
# browser requests)
# ----------------------------------------------------------------
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

# ----------------------------------------------
# vanilla exception handler
# ----------------------------------------------


class ExperimentServerControllerException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

# ----------------------------------------------
# simple wrapper class to control the
# starting/stopping of experiment server
# ----------------------------------------------


class ExperimentServerController(object):
    def __init__(self, config):
        self.config = config
        self.server_running = False

    def get_ppid(self):
        if not self.is_port_available():
            hostname = self.config.get("psiturk_server", "host")
            port = self.config.getint("psiturk_server", "port")
            url = f"http://{hostname}:{port}/ppid"
            ppid_request = urllib.request.Request(url)
            ppid = urllib.request.urlopen(ppid_request).read()
            return ppid
        else:
            raise ExperimentServerControllerException(
                "Cannot shut down experiment server, server not online")

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
            print(ExperimentServerControllerException)
        else:
            self.server_running = False

    def is_server_running(self):
        project_hash = hashlib.sha1(os.getcwd().encode()).hexdigest()[:12]
        proc_name = "psiturk_experiment_server_" + project_hash
        server_process_running = False
        for proc in psutil.process_iter():
            if proc_name in str(proc.as_dict(['cmdline'])):
                server_process_running = True
                break
        port_is_open = self.is_port_available()
        if port_is_open and server_process_running:  # This should never occur
            return 'maybe'
        elif port_is_open and not server_process_running:
            return 'no'
        elif not port_is_open and server_process_running:
            return 'yes'
        elif not port_is_open and not server_process_running:
            return 'blocked'

    def is_port_available(self):
        return is_port_available(self.config.get("psiturk_server", "host"), self.config.getint("psiturk_server", "port"))

    def startup(self):
        server_script = os.path.join(os.path.dirname(
            __file__), "experiment_server.py")
        server_command = f"{sys.executable} '{server_script}'"
        server_status = self.is_server_running()
        if server_status == 'no':
            #print "Running experiment server with command:", server_command
            subprocess.Popen(server_command, shell=True, close_fds=True)
            print("Experiment server launching...")
            self.server_running = True
        elif server_status == 'maybe':
            print("Error: Not sure what to tell you...")
        elif server_status == 'yes':
            print("Experiment server may be already running...")
        elif server_status == 'blocked':
            print(
                "Another process is running on the desired port. Try using a different port number.")
        time.sleep(1.2)  # Allow CLI to catch up.
