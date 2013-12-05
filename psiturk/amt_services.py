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

class MTurkServices:
    def __init__(self, aws_access_key_id, aws_secret_access_key, is_sandbox):
        self.update_credentials(aws_access_key_id, aws_secret_access_key)
        self.set_sandbox(is_sandbox)
        self.validLogin = self.verify_aws_login()
        if not self.validLogin:
            print 'Sorry, AWS Credentials invalid.\nYou will only be able to '\
                  + 'test experiments locally until you enter\nvalid '\
                  + 'credentials in the AWS Access section of config.txt.'

    def update_credentials(self, aws_access_key_id, aws_secret_access_key):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    def set_sandbox(self, is_sandbox):
        self.is_sandbox = is_sandbox

    def get_active_hits(self):
        if not self.connect_to_turk():
            return False
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
                      } for hit in active_hits]
        return(hits_data)

    def get_workers(self):
        if not self.connect_to_turk():
            return False
        try:
            hits = self.mtc.search_hits(sort_direction='Descending', page_size=20)
            hit_ids = [hit.HITId for hit in hits]
            workers_nested = [self.mtc.get_assignments(
                                hit_id,
                                status="Submitted",
                                sort_by='SubmitTime',
                                page_size=100
                              ) for hit_id in hit_ids]

            workers = [val for subl in workers_nested for val in subl]  # Flatten nested lists
        except MTurkRequestError:
            return(False)
        completed_workers = [worker for worker in workers if worker.AssignmentStatus == "Submitted"]
        worker_data = [{'hitId': worker.HITId,
                        'assignmentId': worker.AssignmentId,
                        'workerId': worker.WorkerId,
                        'submit_time': worker.SubmitTime,
                        'accept_time': worker.AcceptTime
                       } for worker in completed_workers]
        return(worker_data)


    def approve_worker(self, assignment_id):
        if not self.connect_to_turk():
            return(False)
        try:
            self.mtc.approve_assignment(assignment_id, feedback=None)
        except MTurkRequestError:
            return(False)

    def reject_worker(self, assignment_id):
        if not self.connect_to_turk():
            return False
        try:
            self.mtc.reject_assignment(assignment_id, feedback=None)
        except MTurkRequestError:
            return(False)

    def verify_aws_login(self):
        if (self.aws_access_key_id == 'YourAccessKeyId') or (self.aws_secret_access_key == 'YourSecretAccessKey'):
            return False
        else:
            host = 'mechanicalturk.amazonaws.com'
            mturkparams = dict(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                host=host)
            self.mtc = MTurkConnection(**mturkparams)
            try:
                self.mtc.get_account_balance()
            except MTurkRequestError as e:
                print(e.error_message)
                return False
            else:
                return True


    def connect_to_turk(self):
        if not self.validLogin:
            print 'Sorry, AWS credentials invalid.'
            return False
        if self.is_sandbox:
            host = 'mechanicalturk.sandbox.amazonaws.com'
        else:
            host = 'mechanicalturk.amazonaws.com'
        
        mturkparams = dict(
            aws_access_key_id = self.aws_access_key_id,
            aws_secret_access_key = self.aws_secret_access_key,
            host=host)
        self.mtc = MTurkConnection(**mturkparams)
        return True

    def configure_hit(self, hit_config):

        # configure question_url based on the id
        experimentPortalURL = hit_config['ad_location']
        frameheight = 600
        mturkQuestion = ExternalQuestion(experimentPortalURL, frameheight)

        # Qualification:
        quals = Qualifications()
        approve_requirement = hit_config['approve_requirement']
        quals.add(
            PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo",
                                                  approve_requirement))

        if hit_config['us_only']:
            quals.add(LocaleRequirement("EqualTo", "US"))

        # Specify all the HIT parameters
        self.paramdict = dict(
            hit_type = None,
            question = mturkQuestion,
            lifetime = hit_config['lifetime'],
            max_assignments = hit_config['max_assignments'],
            title = hit_config['title'],
            description = hit_config['description'],
            keywords = hit_config['keywords'],
            reward = hit_config['reward'],
            duration = hit_config['duration'],
            approval_delay = None,
            questions = None,
            qualifications = quals
        )

    def check_balance(self):
        if self.is_signed_up():
            if not self.connect_to_turk():
                return('-')
            return(self.mtc.get_account_balance()[0])
        else:
            return('-')

    # TODO (if valid AWS credentials haven't been provided then connect_to_turk() will
    # fail, not error checking here and elsewhere)
    def create_hit(self, hit_config):
        try:
            if not self.connect_to_turk():
                return False
            self.configure_hit(hit_config)
            myhit = self.mtc.create_hit(**self.paramdict)[0]
            self.hitid = myhit.HITId
        except:
            return False
        else:
            return self.hitid
 
    # TODO(Jay): Have a wrapper around functions that serializes them. 
    # Default output should not be serialized.
    def expire_hit(self, hitid):
        if not self.connect_to_turk():
            return False
        self.mtc.expire_hit(hitid)

   def dispose_hit(self, hitid):
        if not self.connect_to_turk():
            return False
        self.mtc.dispose_hit(hitid)

    def extend_hit(self, hitid, assignments_increment=None, expiration_increment=None):
        if not self.connect_to_turk():
            return False
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
