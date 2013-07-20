import os, sys
import subprocess,signal
from threading import Thread, Event
import urllib2
import datetime
from boto.mturk.connection import MTurkConnection, MTurkRequestError
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import LocaleRequirement, \
    PercentAssignmentsApprovedRequirement, Qualifications
from flask import jsonify
import socket
import webbrowser

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

class MTurkServices:
    def __init__(self, config):
        self.config = config

    def get_active_hits(self):
        self.connect_to_turk()
        # hits = self.mtc.search_hits()
        try:
            hits = self.mtc.get_all_hits()
        except MTurkRequestError:
            return(False)
        active_hits = [hit for hit in hits if not(hit.expired)]
        hits_data = [{'hitid': hit.HITId,
                      'title': hit.Title,
                      'status': hit.HITStatus,
                      'max_assignments': hit.MaxAssignments,
                      'number_assignments_completed': hit.NumberOfAssignmentsCompleted,
                      'number_assignments_pending': hit.NumberOfAssignmentsCompleted,
                      'number_assignments_available': hit.NumberOfAssignmentsAvailable,
                      'creation_time': hit.CreationTime,
                      'expiration': hit.Expiration,
                      'btn': '<button class="btn btn-large">Test</button>'
                      }
                    for hit in active_hits]
        return(hits_data)

    def verify_aws_login(self, key_id, secret_key):
        is_sandbox = self.config.getboolean('HIT Configuration', 'using_sandbox')
        if is_sandbox:
            host = 'mechanicalturk.sandbox.amazonaws.com'
        else:
            host = 'mechanicalturk.amazonaws.com'
        mturkparams = dict(
            aws_access_key_id=key_id,
            aws_secret_access_key=secret_key,
            host=host)
        self.mtc = MTurkConnection(**mturkparams)
        try:
            self.mtc.get_account_balance()
        except MTurkRequestError as e:
            print(e.error_message)
            print('AWS Credentials invalid')
            return 0
        else:
            print('AWS Credentials valid')
            return 1

    def connect_to_turk(self):
        is_sandbox = self.config.getboolean('HIT Configuration', 'using_sandbox')
        if is_sandbox:
            host = 'mechanicalturk.sandbox.amazonaws.com'
        else:
            host = 'mechanicalturk.amazonaws.com'
        
        mturkparams = dict(
            aws_access_key_id = self.config.get('AWS Access', 'aws_access_key_id'),
            aws_secret_access_key = self.config.get('AWS Access', 'aws_secret_access_key'),
            host=host)
        self.mtc = MTurkConnection(**mturkparams)
        
    def configure_hit(self):

        # Configure portal
        experimentPortalURL = self.config.get('HIT Configuration', 'question_url')
        frameheight = 600
        mturkQuestion = ExternalQuestion(experimentPortalURL, frameheight)

        # Qualification:
        quals = Qualifications()
        approve_requirement = self.config.get('HIT Configuration', 'Approve_Requirement')
        quals.add(
            PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo",
                                                  approve_requirement))
        if self.config.getboolean('HIT Configuration', 'US_only'):
            quals.add(LocaleRequirement("EqualTo", "US"))

        # Specify all the HIT parameters
        self.paramdict = dict(
            hit_type = None,
            question = mturkQuestion,
            lifetime = datetime.timedelta(hours=self.config.getint('HIT Configuration', 'HIT_lifetime')),
            max_assignments = self.config.get('HIT Configuration', 'max_assignments'),
            title = self.config.get('HIT Configuration', 'title'),
            description = self.config.get('HIT Configuration', 'description'),
            keywords = self.config.get('HIT Configuration', 'keywords'),
            reward = self.config.get('HIT Configuration', 'reward'),
            duration = datetime.timedelta(hours=self.config.getint('HIT Configuration', 'duration')),
            approval_delay = None,
            questions = None,
            qualifications = quals
        )
    
    def is_signed_up(self):
        access_key_id = self.config.get('AWS Access', 'aws_access_key_id')
        access_key = self.config.get('AWS Access', 'aws_secret_access_key')
        return (access_key_id != 'YourAccessKeyId') and \
               (access_key != 'YourSecreteAccessKey')

    def check_balance(self):
        if self.is_signed_up():
            self.connect_to_turk()
            return(self.mtc.get_account_balance()[0])
        else:
            return('-')

    # TODO (if valid AWS credentials haven't been provided then connect_to_turk() will
    # fail, not error checking here and elsewhere)
    def create_hit(self):
        self.connect_to_turk()
        self.configure_hit()
        myhit = self.mtc.create_hit(**self.paramdict)[0]
        self.hitid = myhit.HITId

    # TODO(Jay): Have a wrapper around functions that serializes them. 
    # Default output should not be serialized.
    def expire_hit(self, hitid):
        self.connect_to_turk()
        self.mtc.expire_hit(hitid)

    def extend_hit(self, hitid, assignments_increment=None, expiration_increment=None):
        self.connect_to_turk()
        self.mtc.extend_hit(hitid, assignments_increment=int(assignments_increment))
        self.mtc.extend_hit(hitid, expiration_increment=int(expiration_increment)*60)

    def get_summary(self):
      try:
          balance = self.check_balance()
          summary = jsonify(balance=str(balance))
          return(summary)
      except MTurkRequestError as e:
          print(e.error_message)
          return(False)


class ServerException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Server:
    def __init__(self, port=None, hostname="localhost", ip='127.0.0.1'):
        self.port = port
        self.ip = ip
        self.hostname = hostname
    
    def get_ppid(self):
        if not self.check_port_state():
            url = "http://{hostname}:{port}/ppid".format(hostname=self.hostname, port=self.port)
            ppid_request = urllib2.Request(url)
            ppid =  urllib2.urlopen(ppid_request).read()
            return ppid
        else:
            raise ServerException("Cannot shut down, server not online")
    
    def shutdown(self, ppid=None):
        if not ppid:
            ppid = self.get_ppid()
        print("shutting down PsiTurk server at pid %s..." % ppid)
        try:
            os.kill(int(ppid), signal.SIGKILL)
        except ServerException:
            print ServerException
    
    def startup(self):
        server_command = "{python_exec} '{server_script}'".format(
            python_exec = sys.executable,
            server_script = os.path.join(os.path.dirname(__file__), "psiturk_server.py")
        )
        if self.check_port_state():
            print("Running server with command:", server_command)
            subprocess.Popen(server_command, shell=True)
            return("psiTurk launching...")
        else:
            return("psiturk is already running...")
    
    def launch_browser(self):
        launchurl = "http://{host}:{port}/dashboard".format(host=self.hostname, port=self.port)
        webbrowser.open(launchurl, new=1, autoraise=True)
    
    def check_port_state(self):
        return(self.is_port_available(self.port))
    
    def is_port_available(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.ip, int(port)))
            s.shutdown(2)
            return 0
        except:
            return 1
    
    def wait_until_online(self, function, **kwargs):
        """
        Uses Wait_For_State to wait for the server to come online, then runs the given function.
        """
        awaiting_service = Wait_For_State(lambda: self.check_port_state, function, **kwargs)
        awaiting_service.start()
        return awaiting_service
    
    def launch_browser_when_online(self, **kwargs):
        browser_launch_thread = self.wait_until_online(lambda: self.launch_browser(), **kwargs)
