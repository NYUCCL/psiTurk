import ConfigParser
import datetime
import os
import subprocess
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import LocaleRequirement, \
    PercentAssignmentsApprovedRequirement, Qualifications
from socketio.namespace import BaseNamespace
from psiturk_server import PsiTurkServer
from flask import jsonify
import socket
import threading
import time
import pytz
import json
# from datetime import datetime
import iso8601  # parses time with timezones (e.g., from Amazon)

# Database 
from db import db_session, init_db
from models import Participant
from sqlalchemy import or_, func


# TODO(Jay): Generalize port number from launcher

Config = ConfigParser.ConfigParser()

class PsiTurkConfig:
    def __init__(self, filename="config.txt"):
        self.filename = filename
        if not os.path.exists(self.filename):
            print("Creating config file...")
            self.load_default_config()
            self.load_config()
            self.generate_hash()
        else:
            self.load_config()
            self.check_hash()

    def check_hash(self):
        if not self.get("Server Parameters", "hash"):
            self.generate_hash()

    # Config methods
    def set(self, section, key, value):
        configfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      self.filename)
        cfgfile = open(configfilepath, 'w')
        Config.set(section, key, value)
        Config.write(cfgfile)
        cfgfile.close()

    def get(self, section, key):
        if Config.has_option(section, key):
            return(Config.get(section, key))
        else:
            print("Option not available.")
            return(False)

    def generate_hash(self):
        self.user_hash = str(os.urandom(16).encode('hex'))
        self.set('Server Parameters', 'hash', self.user_hash)

    def get_serialized(self):
        # Serializing data is necessary to communicate w/ backbone frontend.
        if not os.path.exists(self.filename):
            print("No config file present!")
        else:
            return(Config._sections)

    def set_serialized(self, config_model):
        configfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      self.filename)
        cfgfile = open(configfilepath, 'w')

        for section, fields in config_model.iteritems():
            for field in fields:
                Config.set(section, field, config_model[section][field])

        Config.write(cfgfile)
        cfgfile.close()

    def load_default_config(self):
        # Open new config file
        configfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      self.filename)
        cfgfile = open(configfilepath, 'w')
        sections = ['AWS Access', 'HIT Configuration', 'Database Parameters',
                    'Server Parameters', 'Task Parameters']
        map(Config.add_section, sections)

        # AWS Access Section
        Config.set('AWS Access', 'aws_access_key_id', 'YourAccessKeyId')
        Config.set('AWS Access', 'aws_secret_access_key', 'YourSecreteAccessKey')

        # HIT Configuration
        Config.set('HIT Configuration', 'title', 'Perceptual Reaction Time')
        Config.set('HIT Configuration', 'description', 'Make a series of perceptual judgments.')
        Config.set('HIT Configuration', 'keywords', 'Perception, Psychology')
        Config.set('HIT Configuration', 'question_url', 'http://localhost:5001/mturk')
        Config.set('HIT Configuration', 'max_assignments', '10')
        Config.set('HIT Configuration', 'HIT_lifetime', '24')
        Config.set('HIT Configuration', 'reward', '1')
        Config.set('HIT Configuration', 'duration', '2')
        Config.set('HIT Configuration', 'US_only', 'true')
        Config.set('HIT Configuration', 'Approve_Requirement', '95')
        Config.set('HIT Configuration', 'using_sandbox', 'true')

        # Database Parameters
        Config.set('Database Parameters', 'database_url', 'sqlite:///participants.db')
        Config.set('Database Parameters', 'table_name', 'turkdemo')

        #Server Parameters
        Config.set('Server Parameters', 'host', 'localhost')
        Config.set('Server Parameters', 'port', '5001')
        Config.set('Server Parameters', 'cutoff_time', '30')
        Config.set('Server Parameters', 'support_IE', 'true')
        Config.set('Server Parameters', 'logfile', 'server.log')
        Config.set('Server Parameters', 'loglevel', '2')
        Config.set('Server Parameters', 'debug', 'true')
        Config.set('Server Parameters', 'login_username', 'examplename')
        Config.set('Server Parameters', 'login_pw', 'examplepassword')

        # Task Parameters
        Config.set('Task Parameters', 'code_version', '1.0')
        Config.set('Task Parameters', 'num_conds', '1')
        Config.set('Task Parameters', 'num_counters', '1')

        # Write config file to drive
        Config.write(cfgfile)
        cfgfile.close()

    def load_config(self):
        configfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      self.filename)
        Config.read(str(configfilepath))

        # AWS Access Section
        self.aws_access_key_id = Config.get('AWS Access', 'aws_access_key_id', 'YourAccessKeyId')
        self.aws_secret_access_key = Config.get('AWS Access', 'aws_secret_access_key', 'YourSecreteAccessKey')

        # HIT Configuration
        self.title = Config.get('HIT Configuration', 'title')
        self.description = Config.get('HIT Configuration', 'description')
        self.keywords = Config.get('HIT Configuration', 'keywords')
        self.question_url = Config.get('HIT Configuration', 'question_url')
        self.max_assignments = Config.get('HIT Configuration', 'max_assignments')
        self.HIT_lifetime = Config.get('HIT Configuration', 'HIT_lifetime')
        self.reward = Config.get('HIT Configuration', 'reward')
        self.duration = Config.get('HIT Configuration', 'duration')
        self.US_only = Config.get('HIT Configuration', 'US_only')
        self.Approve_Requirement = Config.get('HIT Configuration', 'Approve_Requirement')
        self.using_sandbox = Config.get('HIT Configuration', 'using_sandbox')

        # Database Parameters
        self.database_url = Config.get('Database Parameters', 'database_url')
        self.table_name =  Config.get('Database Parameters', 'table_name')

        # Server Parameters
        self.host = Config.get('Server Parameters', 'host')
        self.port = Config.get('Server Parameters', 'port')
        self.cutoff_time = Config.get('Server Parameters', 'cutoff_time')
        self.support_IE = Config.get('Server Parameters', 'support_IE')
        self.logfile = Config.get('Server Parameters', 'logfile')
        self.loglevel = Config.get('Server Parameters', 'loglevel')
        self.debug = Config.get('Server Parameters', 'debug')
        self.login_username = Config.get('Server Parameters', 'login_username')
        self.login_pw = Config.get('Server Parameters', 'login_pw')

        # Task Parameters
        self.code_version = Config.get('Task Parameters', 'code_version')
        self.num_conds = Config.get('Task Parameters', 'num_conds')
        self.num_counters = Config.get('Task Parameters', 'num_counters')

class MTurkServices:
    def __init__(self, config=None):
        self.config = config

    def get_active_hits(self):
        self.connect_to_turk()
        # hits = self.mtc.search_hits()
        hits = self.mtc.get_all_hits()
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

    def connect_to_turk(self):
        is_sandbox = json.loads(self.config.using_sandbox.lower())
        if is_sandbox:
            host = 'mechanicalturk.sandbox.amazonaws.com'
        else:
            host = 'mechanicalturk.amazonaws.com'
        mturkparams = dict(
            aws_access_key_id=self.config.aws_access_key_id,
            aws_secret_access_key=self.config.aws_secret_access_key,
            host=host)
        self.mtc = MTurkConnection(**mturkparams)

        #TODO(): This should probably be moved to a separate method.
        # Configure portal
        experimentPortalURL = self.config.question_url
        frameheight = 600
        mturkQuestion = ExternalQuestion(experimentPortalURL, frameheight)

        # Qualification:
        quals = Qualifications()
        approve_requirement = self.config.Approve_Requirement
        quals.add(
            PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo",
                                                  approve_requirement))
        if self.config.US_only:
            quals.add(LocaleRequirement("EqualTo", "US"))

        # Specify all the HIT parameters
        self.paramdict = dict(
            hit_type = None,
            question = mturkQuestion,
            lifetime = datetime.timedelta(hours=int(self.config.HIT_lifetime)),
            max_assignments = self.config.max_assignments,
            title = self.config.title,
            description = self.config.description,
            keywords = self.config.keywords,
            reward = self.config.reward,
            duration = datetime.timedelta(hours=int(self.config.duration)),
            approval_delay = None,
            questions = None,
            qualifications = quals
        )

    def check_balance(self):
        is_sandbox = json.loads(self.config.using_sandbox.lower())
        if is_sandbox:
            host = 'mechanicalturk.sandbox.amazonaws.com'
        else:
            host = 'mechanicalturk.amazonaws.com'

        # Check if AWS acct info has been entered
        is_signed_up = not(self.config.aws_access_key_id == 'YourAccessKeyId') and \
                       not(self.config.aws_secret_access_key == 'YourSecreteAccessKey')

        if is_signed_up:
            mturkparams = dict(
                aws_access_key_id=self.config.aws_access_key_id,
                aws_secret_access_key=self.config.aws_secret_access_key,
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
        self.mtc.extend_hit(hitid, assignments_increment, expiration_increment)

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


class Database:
    def get_participant_status(self):
        allocated = Participant.query.filter(Participant.status == 1).count()
        started = Participant.query.filter(Participant.status == 2).count()
        completed = Participant.query.filter(Participant.status == 3).count()
        debriefed = Participant.query.filter(Participant.status == 4).count()
        credited = Participant.query.filter(Participant.status == 5).count()
        quit_early = Participant.query.filter(Participant.status == 6).count()
        total = Participant.query.count()
        return jsonify(allocated=allocated,
                       started=started,
                       completed=completed,
                       debriefed=debriefed,
                       credited=credited,
                       quit_early=quit_early,
                       total=total)
    # TODO()
    def get_average_time(self):
        pass


class Session:
    def __init__(self):
        pass
