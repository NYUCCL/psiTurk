# coding: utf-8
"""
The initial motivation for this wrapper is to abstract away
the mturk functionality from the shell
"""

import sys
import subprocess
import re
import time
import json
import os
import string
import random
import datetime
import urllib
import signal
from fuzzywuzzy import process

try:
    import gnureadline as readline
except ImportError:
    import readline

import webbrowser
import sqlalchemy as sa

from sqlalchemy import or_, and_
from amt_services import MTurkServices
from psiturk_org_services import PsiturkOrgServices, TunnelServices
from psiturk_config import PsiturkConfig
from psiturk_statuses import *
from db import db_session, init_db
from models import Participant, Hit
from utils import *

class MTurkServicesWrapper():

    _cached_web_services = None
    _cached_dbs_services = None
    _cached_amt_services = None

    @property
    def web_services(self):
        if not self._cached_web_services:
            self._cached_web_services = PsiturkOrgServices(
                self.config.get('psiTurk Access', 'psiturk_access_key_id'),
                self.config.get('psiTurk Access', 'psiturk_secret_access_id'))
        return self._cached_web_services

    def set_web_services(self, web_services):
        self._cached_web_services = web_services

    @property
    def amt_services(self):
        if not self._cached_amt_services:
            self._cached_amt_services = MTurkServices(
                self.config.get('AWS Access', 'aws_access_key_id'), \
                self.config.get('AWS Access', 'aws_secret_access_key'),
                self.sandbox)
        return self._cached_amt_services

    def __init__(self, config=None, web_services=None, tunnel=None, sandbox=None):

        if not config:
            config = PsiturkConfig()
            config.load_config()
        self.config = config

        if web_services:
            self._cached_web_services = web_services

        if not tunnel:
            tunnel = TunnelServices(config)
        self.tunnel = tunnel

        if not sandbox:
            sandbox = config.getboolean('Shell Parameters', 'launch_in_sandbox_mode')
        self.sandbox = sandbox

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   Miscellaneous
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def amt_balance(self):
        ''' Get MTurk balance '''
        return self.amt_services.check_balance()

    def set_sandbox(self, is_sandbox):
        self.sandbox = is_sandbox
        self.amt_services.set_sandbox(is_sandbox)

    def random_id_generator(self, size=6, chars=string.ascii_uppercase +
                            string.digits):
        ''' Generate random id numbers '''
        return ''.join(random.choice(chars) for x in range(size))

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   worker management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    @staticmethod
    def add_bonus_info(assignment_dict):
        " Adds DB-logged worker bonus to worker list data "
        try:
            unique_id = '{}:{}'.format(assignment_dict['workerId'], assignment_dict['assignmentId'])
            worker = Participant.query.filter(
                Participant.uniqueid == unique_id).one()
            assignment_dict['bonus'] = worker.bonus
        except sa.exc.InvalidRequestError:
            # assignment is found on mturk but not in local database.
            assignment_dict['bonus'] = 'not-found-in-study-database'
        return assignment_dict
        
    def count_workers(self, codeversion=None, mode='live', status='completed'):
        ''' 
        Counts the number of participants in the database who have made it through
        the experiment.
        '''
        if not codeversion:
            codeversion = self.config.get('Task Parameters', 'experiment_code_version')
            
        return Participant.query.filter( and_(
                    Participant.status.in_( [3,4,5,7] ),
                    Participant.codeversion == codeversion,
                    Participant.mode == mode
                ) ).count()            
    
    def get_assignments_for_assignment_ids(self, assignment_ids, all_studies=False):
        assignments = [self.amt_services.get_assignment(assignment_id) for assignment_id in assignment_ids]
        return self._get_assignments(assignments, all_studies=all_studies)
        
    def get_assignments_for_hits(self, hit_ids=None, assignment_status=None, all_studies=False):
        '''
        assignment_status, if set, can be one of `Submitted`, `Approved`, or `Rejected`
        '''
        assignments = self.amt_services.get_assignments(assignment_status=assignment_status, chosen_hits=hit_ids)
        return self._get_assignments(assignments, all_studies=all_studies)
        
    def _filter_assignments_for_current_study(self, assignments):
        my_hitids = self._get_local_hitids()
        assignments_filtered = [assignment for assignment in assignments if assignment['hitId'] in my_hitids]
        return assignments_filtered
    
    def _get_assignments(self, assignments, all_studies=False):
        if assignments is False:
            raise Exception('*** failed to get assignments')

        if not all_studies:
            assignments = self._filter_assignments_for_current_study(assignments)

        assignments = [self.add_bonus_info(assignment) for assignment in assignments]
        return assignments
        
    def _get_local_submitted_assignments(self, hit_id=None):
        init_db()
        query = Participant.query.filter(or_(Participant.status == COMPLETED, Participant.status == SUBMITTED))
        if hit_id:
            query.filter(Participant.hitid == hit_id)
        assignments = query.all()
        return assignments
    
    def approve_all_assignments(self, all_studies=False):
        if all_studies:
            result = self._approve_all_assignments_from_mturk()
        else:
            result = self._approve_all_assignments_from_local_records()
        return result
        
    def _approve_all_assignments_from_local_records(self):
        assignments = self._get_local_submitted_assignments()
        results = []
        for assignment in assignments:
            try:
                self.amt_services.approve_assignment(assignment.assignmentid)
                assignment.status = CREDITED
                db_session.add(assignment)
                db_session.commit()
                results.append({'status':'success'})
            except:
                raise
        return results
        
    def _approve_all_assignments_from_mturk(self):
        assignments = self.amt_services.get_assignments(assignment_status="Submitted")
        results = []
        for assignment in assignments:
            try:
                self.approve_assignment(assignment)
                results.append({'status':'success'})
            except:
                raise
        return results

    def approve_assignment(self, assignment, force=False):
        ''' Approve assignment '''
        assignment_id = assignment['assignmentId']
        init_db()
        found_assignment = False
        parts = Participant.query.\
               filter(Participant.assignmentid == assignment_id).\
               filter(Participant.status.in_([3, 4])).\
               all()
        # Iterate through all the people who completed this assignment.
        # This should be one person, and it should match the person who
        # submitted the HIT, but that doesn't always hold.
        status_report = ''
        for part in parts:
            if part.workerid == assignment['workerId']:
                found_assignment = True
                success = self.amt_services.approve_assignment(assignment_id)
                if success:
                    part.status = 5
                    db_session.add(part)
                    db_session.commit()
                    status_report = 'approved worker {} for assignment {}'.format(part.workerid, assignment_id)
                else:
                    error_msg = '*** failed to approve worker {} for assignment {}'.format(part.workerid, assignment_id)
                    raise Exception(error_msg)
            else:
                status_report = 'found unexpected worker {} for assignment {}'.format(part.workerid, assignment_id)
        if not found_assignment:
            # approve assignments not found in DB if the assignment id has been specified
            if force:
                success = self.amt_services.approve_assignment(assignment_id)
                if success:
                    _status_report = 'approved worker {} for assignment {} but not found in DB'.format(worker['workerId'], assignment_id)
                    status_report = '\n'.join([status_report,_status_report])
                else:
                    error_msg = '*** failed to approve worker {} for assignment {}'.format(assignment['workerId'], assignment_id)
                    raise Exception(error_msg)
            # otherwise don't approve, and print warning
            else:
                _status_report = 'worker {} not found in DB for assignment {}. Not automatically approved. Use --force to approve anyway.'.format(assignment['workerId'], assignment_id)
                if status_report:
                    status_report = '\n'.join([status_report,_status_report])
                else:
                    status_report = _status_report
        return status_report
    
    def reject_assignments_for_hit(self, hit_id, all_studies=False):
        if all_studies:
            assignments = self.amt_services.get_assignments("Submitted")
            assignment_ids = [assignment['assignmentId'] for assignment in assignments if \
                              assignment['hitId'] == hit_id]
        else:
            assignments = self._get_local_submitted_assignments()
            assignment_ids = [assignment['assignmentid'] for assignment in assignments]
        return self.reject_assignments(assignment_ids)
        
    def reject_assignments(self, assignment_ids):
        results = []
        for assignment_id in assignment_ids:
            result = self.reject_assignment(assignment_id)
            results.append(result)
        return results
                
    def reject_assignment(self, assignment_id):
        success = self.amt_services.reject_assignment(assignment_id)
        if success:
            message = 'rejected {}'.format(assignment_id)
        else:
            message = '*** failed to reject {}'.format(assignment_id)
        return {'success': success, 'message': message } 

    def unreject_assignment(self, chosen_hit, assignment_ids = None):
        ''' Unreject assignment '''
        if chosen_hit:
            assignments = self.amt_services.get_assignments("Rejected")
            assignment_ids = [assignment['assignmentId'] for assignment in assignments if \
                              assignment['hitId'] == chosen_hit]
        for assignment_id in assignment_ids:
            success = self.amt_services.unreject_assignment(assignment_id)
            if success:
                print 'unrejected %s' % (assignment_id)
            else:
                print '*** failed to unreject', assignment_id

    def bonus_assignment(self, all, chosen_hit, auto, amount, reason='',
                     assignment_ids=None):
        
        mode = 'sandbox' if self.sandbox else 'live'
        
        ''' Bonus assignment '''
        if self.config.has_option('Shell Parameters', 'bonus_message'):
            reason = self.config.get('Shell Parameters', 'bonus_message')
        while not reason:
            user_input = raw_input("Type the reason for the bonus. Workers "
                                   "will see this message: ")
            reason = user_input
            
            
        if all:
            workers = Participant.get_approved(mode=mode)
            for worker in workers:
                if auto:
                    amount = worker.bonus
                success = self.amt_services.bonus_assignment(worker.assignmentid, amount, reason)
                if success:
                    print "gave bonus of $" + str(amount) + " for assignment " + worker.assignmentid
                    worker.status = BONUSED
                    db_session.add(worker)
                    db_session.commit()
            return
            
        # Bonus already-bonused workers if the user explicitly lists their
        # assignment IDs

        override_status = True
        if chosen_hit:
            override_status = False
            assignments = self.amt_services.get_assignments("Approved", chosen_hit)
            if not assignments:
                print "No approved assignments for HIT", chosen_hit
                return
            print 'bonusing assignments for HIT', chosen_hit
        elif len(assignment_ids) == 1:
            assignments = [self.amt_services.get_assignment(assignment_ids[0])]
            if not assignments:
                print "No submissions found for requested assignment ID"
                return
        else:
            assignments = self.amt_services.get_assignments("Approved")
            if not assignments:
                print "No approved assignments found."
                return

            assignments = [assignment for assignment in assignments if \
                              assignment['assignmentId'] in assignment_ids]

        for assignment in assignments:
            assignment_id = assignment['assignmentId']
            try:
                init_db()
                part = Participant.query.\
                       filter(Participant.assignmentid == assignment_id).\
                       filter(Participant.workerid == assignment['workerId']).\
                       filter(Participant.endhit != None).\
                       one()
                if auto:
                    amount = part.bonus
                status = part.status
                if amount <= 0:
                    print "bonus amount <=$0, no bonus given for assignment", assignment_id
                elif status == 7 and not override_status:
                    print "bonus already awarded for assignment", assignment_id
                else:
                    success = self.amt_services.bonus_assignment(assignment_id,
                                                             amount, reason)
                    if success:
                        print "gave bonus of $" + str(amount) + " for assignment " + \
                        assignment_id
                        part.status = 7
                        db_session.add(part)
                        db_session.commit()
                        db_session.remove()
                    else:
                        print "*** failed to bonus assignment", assignment_id
            except Exception as e:
                print e
                print "*** failed to bonus assignment", assignment_id

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   hit management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.

    def tally_hits(self):
        hits = self.get_active_hits(all_studies=False)
        num_hits = 0
        if hits:
            num_hits = len(hits)
        return num_hits

    def _get_local_hitids(self):
        init_db()
        participant_hitids = [part.hitid for part in Participant.query.distinct(Participant.hitid)]
        hit_hitids = [hit.hitid for hit in Hit.query.distinct(Hit.hitid)]
        my_hitids = list(set(participant_hitids + hit_hitids))
        return my_hitids

    def _get_hits(self, all_studies=False):
        # get all hits from amt
        # then filter to just the ones that have an id that appears in either local Hit or Worker tables
        hits = self.amt_services.get_all_hits()
        if not all_studies:
            hits = [hit for hit in hits if hit.options['hitid'] in self._get_local_hitids()]
        return hits

    def get_active_hits(self, all_studies=False):
        hits = self._get_hits(all_studies)
        active_hits = [hit for hit in hits if not hit.options['is_expired']]
        return active_hits

    def get_reviewable_hits(self, all_studies=False):
        hits = self._get_hits(all_studies)
        reviewable_hits = [hit for hit in hits if hit.options['status'] == "Reviewable" \
                           or hit.options['status'] == "Reviewing"]
        return reviewable_hits

    def get_all_hits(self, all_studies=False):
        hits = self._get_hits(all_studies)
        return hits

    def extend_hit(self, hit_id, assignments=None, minutes=None):
        """ Add additional worker assignments or minutes to a HIT.

        Args:
            hit_id: A list conaining one hit_id string.
            assignments: Variable <int> for number of assignments to add.
            minutes: Variable <int> for number of minutes to add.

        Returns:
            A side effect of this function is that the state of a HIT changes
            on AMT servers.

        Raises:

        """

        if self.amt_services.extend_hit(hit_id, assignments_increment=assignments, expiration_increment=minutes):
            print "HIT extended."
                        
    def delete_all_hits(self):
        '''
        Deletes all reviewable hits
        '''
        hits = self.amt_services.get_all_hits()
        hit_ids = [hit.options['hitid'] for hit in hits if \
                   hit.options['status'] == "Reviewable"]
        for hit in hit_ids:
            self.delete_hit(hit_id)
        
    def delete_hit(self, hit_id):
        '''
        Deletes a single hit if it is reviewable
        '''
        # Check that the HIT is reviewable
        status = self.amt_services.get_hit_status(hit_id)
        if not status:
            print "*** Error getting hit status"
            return
        if status != "Reviewable":
            print("*** This hit is not 'Reviewable' and so can not be "
                  "deleted")
            return
        else:
            success = self.amt_services.delete_hit(hit_id)
            # self.web_services.delete_ad(hit)  # also delete the ad
            if success:
                if self.sandbox:
                    print "deleting sandbox HIT", hit_id
                else:
                    print "deleting live HIT", hit_id

    def expire_hit(self, hit_id):
        success = self.amt_services.expire_hit(hit_id)
        if success:
            if self.sandbox:
                print "expiring sandbox HIT", hit_id
            else:
                print "expiring live HIT", hit_id
                
    def expire_all_hits(self):
        hits_data = self.get_active_hits()
        hit_ids = [hit.options['hitid'] for hit in hits_data]
        for hit_id in hit_ids:
            self.expire_hit(hit_id)

    def create_hit(self, num_workers, reward, duration):
        if not num_workers or not reward or not duration:
            raise Exception('Missing arguments')
        ''' Create a HIT '''
        if self.sandbox:
            mode = 'sandbox'
        else:
            mode = 'live'
        server_loc = str(self.config.get('Server Parameters', 'host'))

        use_psiturk_ad_server = self.config.getboolean('Shell Parameters', 'use_psiturk_ad_server')

        if use_psiturk_ad_server:
            if not self.web_services.check_credentials():
                error_msg = '\n'.join(['*****************************',
                                '  Sorry, your psiTurk Credentials are invalid.\n ',
                                '  You cannot create ads and hits until you enter valid credentials in ',
                                '  the \'psiTurk Access\' section of ~/.psiturkconfig.  You can obtain your',
                                '  credentials or sign up at https://www.psiturk.org/login.\n'])
                raise Exception(error_msg)

        if not self.amt_services.verify_aws_login():
            error_msg = '\n'.join(['*****************************',
                             '  Sorry, your AWS Credentials are invalid.\n ',
                             '  You cannot create ads and hits until you enter valid credentials in ',
                             '  the \'AWS Access\' section of ~/.psiturkconfig.  You can obtain your ',
                             '  credentials via the Amazon AMT requester website.\n'])
            raise Exception(error_msg)

        ad_id = None
        if use_psiturk_ad_server:
            ad_id = self.create_psiturk_ad()
            create_failed = False
            fail_msg = None
            if ad_id is not False:
                ad_location = self.web_services.get_ad_url(ad_id, int(self.sandbox))
                hit_config = self.generate_hit_config(ad_location, num_workers, reward, duration)
                hit_id = self.amt_services.create_hit(hit_config)
                if hit_id is not False:
                    if not self.web_services.set_ad_hitid(ad_id, hit_id, int(self.sandbox)):
                        create_failed = True
                        fail_msg = "  Unable to update Ad on http://ad.psiturk.org to point at HIT."
                else:
                    create_failed = True
                    fail_msg = "  Unable to create HIT on Amazon Mechanical Turk."
            else:
                create_failed = True
                fail_msg = "  Unable to create Ad on http://ad.psiturk.org."

        else: # not using psiturk ad server
            ad_location = "{}?mode={}".format(self.config.get('Shell Parameters', 'ad_location'), mode )
            hit_config = self.generate_hit_config(ad_location, num_workers, reward, duration)
            create_failed = False
            hit_id = self.amt_services.create_hit(hit_config)
            if hit_id is False:
                create_failed = True
                fail_msg = "  Unable to create HIT on Amazon Mechanical Turk."

        if create_failed:
            print '\n'.join(['*****************************',
                             '  Sorry, there was an error creating hit and registering ad.'])

            if fail_msg is None:
                fail_msg = ''
            raise Exception(fail_msg)

        # stash hit id in psiturk database
        hit = Hit(hitid=hit_id)
        db_session.add(hit)
        db_session.commit()
        
        return (hit_id, ad_id)

    def create_psiturk_ad(self):
        # register with the ad server (psiturk.org/ad/register) using POST
        if os.path.exists('templates/ad.html'):
            ad_html = open('templates/ad.html').read()
        else:
            print '\n'.join(['*****************************',
                '  Sorry, there was an error registering ad.',
                '  The file ad.html is required to be in the templates folder',
                '  of your project so that the ad can be served.'])
            return

        size_of_ad = sys.getsizeof(ad_html)
        if size_of_ad >= 1048576:
            print '\n'.join(['*****************************',
                '  Sorry, there was an error registering the ad.',
                '  Your local ad.html is %s bytes, but the maximum',
                '  template size uploadable to the ad server is',
                '  1048576 bytes.' % size_of_ad])
            return

        # what all do we need to send to server?
        # 1. server
        # 2. port
        # 3. support_ie?
        # 4. ad.html template
        # 5. contact_email in case an error happens

        if self.tunnel.is_open:
            ip_address = self.tunnel.url
            port = str(self.tunnel.tunnel_port)  # Set by tunnel server.
        elif self.config.has_option('Server Parameters','adserver_revproxy_host'):
            ip_address = self.config.get('Server Parameters', 'adserver_revproxy_host') # misnomer, could actually be a fqdn sans protocol
            if self.config.has_option('Server Parameters','adserver_revproxy_port'):
                port = self.config.getint('Server Parameters','adserver_revproxy_port')
            else:
                port = 80
        else:
            ip_address = str(get_my_ip())
            port = str(self.config.get('Server Parameters', 'port'))

        if self.config.has_option('HIT Configuration', 'allow_repeats'):
            allow_repeats = self.config.getboolean('HIT Configuration', 'allow_repeats')
        else:
            allow_repeats = False

        ad_content = {
            'psiturk_external': True,
            'server': ip_address,
            'port': port,
            'browser_exclude_rule': str(self.config.get('HIT Configuration', 'browser_exclude_rule')),
            'is_sandbox': int(self.sandbox),
            'ad_html': ad_html,
            # 'amt_hit_id': hitid, Don't know this yet
            'organization_name': str(self.config.get('HIT Configuration', 'organization_name')),
            'experiment_name': str(self.config.get('HIT Configuration', 'title', raw=True)),
            'contact_email_on_error': str(self.config.get('HIT Configuration', 'contact_email_on_error')),
            'ad_group': str(self.config.get('HIT Configuration', 'ad_group')),
            'keywords': str(self.config.get('HIT Configuration', 'psiturk_keywords')),
            'allow_repeats': int(allow_repeats)
        }
        ad_id = self.web_services.create_ad(ad_content)
        return ad_id

    def generate_hit_config(self, ad_location, num_workers, reward, duration):
        hit_config = {
            "ad_location": ad_location,
            "approve_requirement": self.config.getint('HIT Configuration', 'Approve_Requirement'),
            "us_only": self.config.getboolean('HIT Configuration', 'US_only'),
            "lifetime": datetime.timedelta(hours=self.config.getfloat('HIT Configuration', 'lifetime')),
            "max_assignments": num_workers,
            "title": self.config.get('HIT Configuration', 'title', raw=True),
            "description": self.config.get('HIT Configuration', 'description', raw=True),
            "keywords": self.config.get('HIT Configuration', 'amt_keywords'),
            "reward": reward,
            "duration": datetime.timedelta(hours=duration),
            "number_hits_approved": self.config.getint('HIT Configuration', 'number_hits_approved'),
            "require_master_workers": self.config.getboolean('HIT Configuration','require_master_workers')
        }
        return hit_config

