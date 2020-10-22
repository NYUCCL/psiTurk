from __future__ import generator_stop
import hashlib
import time
import psutil
import socket
from threading import Thread, Event
import webbrowser
import subprocess
import sys
import os
import logging

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)  # TODO: let this be configurable
stream_formatter = logging.Formatter('%(message)s')
stream_handler.setFormatter(stream_formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Supporting functions
#   general purpose helper functions used by the dashboard server and controller
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def is_port_available(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return False
    except socket.timeout:
        logger.error("*** Failed to test port availability. "
                     "Check that host is set properly in config.txt")
        return True
    except socket.error as e:
        return True


def wait_until_online(function, ip, port):
    """
    Uses WaitForState to wait for the server to come online, then runs the given function.
    """
    awaiting_service = WaitForState(
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
class WaitForState(Thread):
    """
    Waits for a state-checking function to return True, then runs a given
    function. For example, this is used to launch the browser once the server is
    started up.

    Example:
    t = WaitForState(lambda: server.check_port_state(), lambda: print "Server has started!")
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

    def restart(self):
        self.shutdown()
        self.startup()

    def on_terminate(self, proc: psutil.Process):
        logger.debug("process {} terminated with exit code {}".format(
            proc, proc.returncode))

    def kill_process_tree(self, proc: psutil.Process):
        """Kill process tree with given process object.

        Caller should be prepared to catch psutil Process class exceptions.
        """
        children = proc.children(recursive=True)
        children.append(proc)
        for c in children:
            c.terminate()
        gone, alive = psutil.wait_procs(children, timeout=10, callback=self.on_terminate)
        for survivor in alive:
            survivor.kill()

    def shutdown(self, ppid=None):
        proc_hash = self.get_project_hash()
        psiturk_master_procs = [p for p in psutil.process_iter(
            ['pid', 'cmdline', 'exe', 'name']) if proc_hash in str(p.info) and
                               'master' in str(p.info)]
        if len(psiturk_master_procs) < 1:
            logger.warning('No active server process found.')
            self.server_running = False
            return
        for p in psiturk_master_procs:
            logger.info('Shutting down experiment server at pid %s ... ' % p.info['pid'])
            try:
                self.kill_process_tree(p)
            except psutil.NoSuchProcess as e:
                logger.error('Attempt to shut down PID {} failed with exception {}'.format(
                    p.as_dict['pid'], e
                ))
        # NoSuchProcess exceptions imply server is not running, so seems safe.
        self.server_running = False

    def check_server_process_running(self, process_hash):
        server_process_running = False
        for proc in psutil.process_iter():
            if process_hash in str(proc.as_dict(['cmdline'])):
                server_process_running = True
                break
        return server_process_running

    def get_project_hash(self):
        project_hash = 'psiturk_experiment_server_{}'.format(
            hashlib.sha1(os.getcwd().encode()).hexdigest()[:12]
        )
        return project_hash

    def is_server_running(self):
        process_hash = self.get_project_hash()
        server_process_running = self.check_server_process_running(process_hash)
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
        return is_port_available(self.config.get("Server Parameters", "host"),
                                 self.config.getint("Server Parameters", "port"))

    def startup(self):
        server_script = os.path.join(os.path.dirname(
            __file__), "experiment_server.py")
        server_command = f"{sys.executable} '{server_script}'"
        server_status = self.is_server_running()
        if server_status == 'no':
            subprocess.Popen(server_command, shell=True, close_fds=True)
            logging.info("Experiment server launching...")
            self.server_running = True
        elif server_status == 'maybe':
            logging.error("Error: Not sure what to tell you...")
        elif server_status == 'yes':
            logging.warning("Experiment server may be already running...")
        elif server_status == 'blocked':
            logging.warning(
                "Another process is running on the desired port. Try using a different port number.")
        time.sleep(1.2)  # Allow CLI to catch up.
