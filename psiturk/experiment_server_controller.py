import os
import sys
import subprocess
import signal
import webbrowser
from threading import Thread, Event
import urllib2
import socket
import psutil
import time
import hashlib


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

    def kill_child_processes(self, parent_pid, sig=signal.SIGTERM):
        if os.uname()[0] is 'Linux':
            ps_command = subprocess.Popen('pstree -p %d | perl -ne \'print "$1 "\
                                          while /\((\d+)\)/g\'' % parent.pid,
                                          shell=True, stdout=subprocess.PIPE)
            ps_output = ps_command.stdout.read()
            retcode = ps_command.wait()
            assert retcode == 0, "ps command returned %d" % retcode
            for pid_str in ps_output.split("\n")[:-1]:
                os.kill(int(pid_str), sig)
        if os.uname()[0] is 'Darwin':
            child_pid = parent.get_children(recursive=True)
            for pid in child_pid:
                pid.send_signal(signal.SIGTERM)

    def is_server_running(self):
        project_hash = hashlib.sha1(os.getcwd()).hexdigest()[:12]
        # find server processes run by this user from this folder
        PROCNAME = "psiturk_experiment_server_" + project_hash
        cmd = "ps -o pid,command | grep '"+ PROCNAME + "' | grep -v grep | awk '{print $1}'"
        psiturk_exp_processes = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output = psiturk_exp_processes.stdout.readlines()
        parent = psutil.Process(psiturk_exp_processes.pid)
        self.kill_child_processes(parent.pid)
        
        if output:
            is_psiturk_using_port = True
        else:
            is_psiturk_using_port = False
        is_port_open = self.is_port_available()
        #print self.server_running, " ", portopen
        if is_port_open and is_psiturk_using_port:  # This should never occur
            return 'maybe'
        elif not is_port_open and not is_psiturk_using_port:
            return 'blocked'
        elif is_port_open and not is_psiturk_using_port:
            return 'no'
        elif not is_port_open and is_psiturk_using_port:
            return 'yes'

    def is_port_available(self):
        return is_port_available(self.config.get("Server Parameters", "host"), self.config.getint("Server Parameters", "port"))

    def startup(self):
        server_command = "{python_exec} '{server_script}'".format(
            python_exec = sys.executable,
            server_script = os.path.join(os.path.dirname(__file__), "experiment_server.py")
        )
        server_status = self.is_server_running()
        if server_status == 'no':
            #print "Running experiment server with command:", server_command
            subprocess.Popen(server_command, shell=True, close_fds=True)
            print "Experiment server launching..."
            self.server_running = True
        elif server_status == 'maybe':
            print "Error: Not sure what to tell you..."
        elif server_status == 'yes':
            print "Experiment server may be already running..."
        elif server_status == 'blocked':
            print "Another process is running on the desired port. Try using a different port number."
        time.sleep(1.2)  # Allow CLI to catch up.

