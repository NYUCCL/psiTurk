import ConfigParser
import datetime
import os
import subprocess
from boto.mturk.connection import MTurkConnection, MTurkRequestError
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import LocaleRequirement, \
    PercentAssignmentsApprovedRequirement, Qualifications
from socketio.namespace import BaseNamespace
from flask import jsonify
import socket
import threading
# from datetime import datetime


# TODO(Jay): Generalize port number from launcher

class MTurkServices:
    def __init__(self, config):
        self.config = config

    def get_active_hits(self):
        self.connect_to_turk()
        # hits = self.mtc.search_hits()
        try:
            hits = self.mtc.get_all_hits()
        except MTurkRequestError:
            print('AWS Credentials invalid')
        active_hits = [hit for hit in hits if not(hit.expired)]
        # active_hits = [hit for hit in hits]
        hits_data = [{'hitid': hit.HITId,
                      'title': hit.Title,
                      'status': hit.HITStatus,
                      'max_assignments': hit.MaxAssignments,
                      'number_assignments_completed': hit.NumberOfAssignmentsCompleted,
                      'number_assignments_pending': hit.NumberOfAssignmentsCompleted,
                      'number_assignments_available': hit.NumberOfAssignmentsAvailable,
                      # 'expired': hit.expired,  # redundant but useful for other queries
                      'creation_time': hit.CreationTime,
                      'expiration': hit.Expiration,
                      'btn': '<button class="btn btn-large">Test</button>'
                      }
                    for hit in active_hits]
        return(hits_data)

    def verify_aws_login(self, key_id, secret_key):
        print "Verifying aws login"
        is_sandbox = self.config.getboolean('HIT Configuration', 'using_sandbox')
        if is_sandbox:
            host = 'mechanicalturk.sandbox.amazonaws.com'
        else:
            host = 'mechanicalturk.amazonaws.com'
        mturkparams = dict(
            aws_access_key_id=key_id,
            aws_secret_access_key=secret_key,
            host=host)
        print(mturkparams)
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
        
        #TODO(): This should probably be moved to a separate method.
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
        is_sandbox = self.config.getboolean('HIT Configuration', 'using_sandbox')
        if is_sandbox:
            host = 'mechanicalturk.sandbox.amazonaws.com'
        else:
            host = 'mechanicalturk.amazonaws.com'
        
        if self.is_signed_up():
            mturkparams = dict(
                aws_access_key_id=self.config.get('AWS Access', 'aws_access_key_id'),
                aws_secret_access_key=self.config.get('AWS Access', 'aws_secret_access_key'),
                host=host)
            self.mtc = MTurkConnection(**mturkparams)
            
            return(self.mtc.get_account_balance()[0])
        else:
            return('-')

    def create_hit(self):
        self.connect_to_turk()
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
        balance = self.check_balance()
        summary = jsonify(balance=str(balance))
        return(summary)


# Pub/sub routine for full-duplex communication between dashboard server and client
# This is critical for server log viewer in dashboard
class ServerNamespace(BaseNamespace):
    sockets = {}
    def recv_connect(self):
        self.sockets[id(self)] = self
    
    def disconnect(self, *args, **kwargs):
        if id(self) in self.sockets:
            del self.sockets[id(self)]
        super(ServerNamespace, self).disconnect(*args, **kwargs)
    # broadcast to all sockets on this channel!
    @classmethod
    def broadcast(self, event, message):
        for ws in self.sockets.values():
            ws.emit(event, message)


class Server:
    def __init__(self, port, ip='127.0.0.1'):
        self.port = port
        self.ip = ip
        self.state = self.is_port_available(self.port)

    def check_port_state(self):
        current_state = self.is_port_available(self.port)
        if current_state is not self.state:
            self.state = current_state
            ServerNamespace.broadcast('status', current_state)  # Update socket listeners

    def is_port_available(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.ip, int(port)))
            s.shutdown(2)
            return 0
        except:
            return 1

    def monitor(self):
        self.check_port_state()
        t = threading.Timer(2, self.monitor)
        t.start()

    def launch_psiturk(self):
        subprocess.Popen("python psiturk_server.py", shell=True)

    def start_monitoring(self):
        ServerNamespace.broadcast('status', self.state)  # Notify socket listeners
        self.monitor()


