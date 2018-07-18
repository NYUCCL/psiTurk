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

from amt_services import MTurkServices, RDSServices
from psiturk_org_services import PsiturkOrgServices, TunnelServices
from psiturk_config import PsiturkConfig
from db import db_session, init_db
from models import Participant
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
    
    @property
    def db_services(self):
        if not self._cached_dbs_services:
            self._cached_dbs_services = RDSServices(
                self.config.get('AWS Access', 'aws_access_key_id'), \
                self.config.get('AWS Access', 'aws_secret_access_key'),
                self.config.get('AWS Access', 'aws_region'))
        return self._cached_dbs_services
    
    def set_web_services(self, web_services):
        self._cached_web_services = web_services
    
    @property
    def amt_services(self):
        if not self._cached_amt_services:
            self._cached_amt_services = MTurkServices(
                self.config.get('AWS Access', 'aws_access_key_id'), \
                self.config.get('AWS Access', 'aws_secret_access_key'),
                self.config.getboolean('Shell Parameters', 'launch_in_sandbox_mode'))
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
    def add_bonus(worker_dict):
        " Adds DB-logged worker bonus to worker list data "
        try:
            unique_id = '{}:{}'.format(worker_dict['workerId'], worker_dict['assignmentId'])
            worker = Participant.query.filter(
                Participant.uniqueid == unique_id).one()
            worker_dict['bonus'] = worker.bonus
        except sa.exc.InvalidRequestError:
            # assignment is found on mturk but not in local database.
            worker_dict['bonus'] = 'N/A'
        return worker_dict
        
    def get_workers(self, status=None, chosen_hits=None, assignment_ids=None, all_studies=False):
        '''
        Status, if set, can be one of `Submitted`, `Approved`, or `Rejected`
        '''
        if assignment_ids:
            workers = [self.get_worker(assignment_id) for assignment_id in assignment_ids] 
        else:
            workers = self.amt_services.get_workers(assignment_status=status, chosen_hits=chosen_hits)
        
        if workers is False:
            raise Exception('*** failed to get workers')    
        
        if not all_studies:
            my_hitids = self._get_my_hitids()
            workers = [worker for worker in workers if worker['hitId'] in my_hitids]
        
        workers = [self.add_bonus(worker) for worker in workers]
        return workers
        
    def get_worker(self, assignment_id):
        return self.amt_services.get_worker(assignment_id)
     
    def approve_worker(self, worker, force=False):
        ''' Approve worker '''
        assignment_id = worker['assignmentId']
        init_db()
        found_worker = False
        parts = Participant.query.\
               filter(Participant.assignmentid == assignment_id).\
               filter(Participant.status.in_([3, 4])).\
               all()
        # Iterate through all the people who completed this assignment.
        # This should be one person, and it should match the person who
        # submitted the HIT, but that doesn't always hold.
        status_report = ''
        for part in parts:
            if part.workerid == worker['workerId']:
                found_worker = True
                success = self.amt_services.approve_worker(assignment_id)
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
        if not found_worker:
            # approve workers not found in DB if the assignment id has been specified
            if force:
                success = self.amt_services.approve_worker(assignment_id)
                if success:
                    _status_report = 'approved worker {} for assignment {} but not found in DB'.format(worker['workerId'], assignment_id)
                    status_report = '\n'.join([status_report,_status_report])
                else:
                    error_msg = '*** failed to approve worker {} for assignment {}'.format(worker['workerId'], assignment_id)
                    raise Exception(error_msg)
            # otherwise don't approve, and print warning
            else:
                _status_report = 'worker {} not found in DB for assignment {}. Not automatically approved. Use --force to approve anyway.'.format(worker['workerId'], assignment_id)
                if status_report:
                    status_report = '\n'.join([status_report,_status_report])
                else:
                    status_report = _status_report
        return status_report
            
    def worker_reject(self, chosen_hit, assignment_ids = None):
        ''' Reject worker '''
        if chosen_hit:
            workers = self.amt_services.get_workers("Submitted")
            assignment_ids = [worker['assignmentId'] for worker in workers if \
                              worker['hitId'] == chosen_hit]
            print 'rejecting workers for HIT', chosen_hit
        for assignment_id in assignment_ids:
            success = self.amt_services.reject_worker(assignment_id)
            if success:
                print 'rejected', assignment_id
            else:
                print '*** failed to reject', assignment_id

    def worker_unreject(self, chosen_hit, assignment_ids = None):
        ''' Unreject worker '''
        if chosen_hit:
            workers = self.amt_services.get_workers("Rejected")
            assignment_ids = [worker['assignmentId'] for worker in workers if \
                              worker['hitId'] == chosen_hit]
        for assignment_id in assignment_ids:
            success = self.amt_services.unreject_worker(assignment_id)
            if success:
                print 'unrejected %s' % (assignment_id)
            else:
                print '*** failed to unreject', assignment_id

    def worker_bonus(self, chosen_hit, auto, amount, reason='',
                     assignment_ids=None):
        ''' Bonus worker '''
        if self.config.has_option('Shell Parameters', 'bonus_message'):
            reason = self.config.get('Shell Parameters', 'bonus_message')
        while not reason:
            user_input = raw_input("Type the reason for the bonus. Workers "
                                   "will see this message: ")
            reason = user_input
        # Bonus already-bonused workers if the user explicitly lists their
        # assignment IDs
        override_status = True
        if chosen_hit:
            override_status = False
            workers = self.amt_services.get_workers("Approved", chosen_hit)
            if not workers:
                print "No approved workers for HIT", chosen_hit
                return
            print 'bonusing workers for HIT', chosen_hit
        elif len(assignment_ids) == 1:
            workers = [self.amt_services.get_worker(assignment_ids[0])]
            if not workers:
                print "No submissions found for requested assignment ID"    
                return
        else:
            workers = self.amt_services.get_workers("Approved")
            if not workers:
                print "No approved workers found."
                return
            workers = [worker for worker in workers if \
                              worker['assignmentId'] in assignment_ids]
        for worker in workers:
            assignment_id = worker['assignmentId']
            try:
                init_db()
                part = Participant.query.\
                       filter(Participant.assignmentid == assignment_id).\
                       filter(Participant.workerid == worker['workerId']).\
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
                    success = self.amt_services.bonus_worker(assignment_id,
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
            except:
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
    
    def _get_my_hitids(self):
        init_db()
        my_hitids = [part.hitid for part in Participant.query.distinct(Participant.hitid)]
        return my_hitids
        
    def _get_hits(self, all_studies=False):
        amt_hits = self.amt_services.get_all_hits()
        if not amt_hits:
            return []
        # get list of unique hitids from database
        if not all_studies:
            my_hitids = self._get_my_hitids()
            amt_hits = [hit for hit in amt_hits if hit.options['hitid'] in my_hitids]
        return amt_hits
    
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

    def hit_extend(self, hit_id, assignments, minutes):
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

        assert type(hit_id) is list
        assert type(hit_id[0]) is str

        if self.amt_services.extend_hit(hit_id[0], assignments, minutes):
            print "HIT extended."

    def hit_dispose(self, all_hits, hit_ids=None):
        ''' Dispose HIT. '''
        if all_hits:
            hits_data = self.amt_services.get_all_hits()
            hit_ids = [hit.options['hitid'] for hit in hits_data if \
                       hit.options['status'] == "Reviewable"]
        for hit in hit_ids:
            # Check that the HIT is reviewable
            status = self.amt_services.get_hit_status(hit)
            if not status:
                print "*** Error getting hit status"
                return
            if self.amt_services.get_hit_status(hit) != "Reviewable":
                print("*** This hit is not 'Reviewable' and so can not be "
                      "disposed of")
                return
            else:
                success = self.amt_services.dispose_hit(hit)
                # self.web_services.delete_ad(hit)  # also delete the ad
                if success:
                    if self.sandbox:
                        print "deleting sandbox HIT", hit
                    else:
                        print "deleting live HIT", hit

    def hit_expire(self, all_hits, hit_ids=None):
        ''' Expire all HITs. '''
        if all_hits:
            hits_data = self.get_active_hits()
            hit_ids = [hit.options['hitid'] for hit in hits_data]
        for hit in hit_ids:
            success = self.amt_services.expire_hit(hit)
            if success:
                if self.sandbox:
                    print "expiring sandbox HIT", hit
                else:
                    print "expiring live HIT", hit
    

    def hit_create(self, numWorkers, reward, duration):
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
                hit_config = self.generate_hit_config(ad_location, numWorkers, reward, duration)
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
            hit_config = self.generate_hit_config(ad_location, numWorkers, reward, duration)
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
            'experiment_name': str(self.config.get('HIT Configuration', 'title')),
            'contact_email_on_error': str(self.config.get('HIT Configuration', 'contact_email_on_error')),
            'ad_group': str(self.config.get('HIT Configuration', 'ad_group')),
            'keywords': str(self.config.get('HIT Configuration', 'psiturk_keywords')),
            'allow_repeats': int(allow_repeats)
        }
        ad_id = self.web_services.create_ad(ad_content)
        return ad_id
    
    def generate_hit_config(self, ad_location, numWorkers, reward, duration):
        hit_config = {
            "ad_location": ad_location,
            "approve_requirement": self.config.get('HIT Configuration', 'Approve_Requirement'),
            "us_only": self.config.getboolean('HIT Configuration', 'US_only'),
            "lifetime": datetime.timedelta(hours=self.config.getfloat('HIT Configuration', 'lifetime')),
            "max_assignments": numWorkers,
            "title": self.config.get('HIT Configuration', 'title'),
            "description": self.config.get('HIT Configuration', 'description'),
            "keywords": self.config.get('HIT Configuration', 'amt_keywords'),
            "reward": reward,
            "duration": datetime.timedelta(hours=duration),
            "number_hits_approved": self.config.get('HIT Configuration', 'number_hits_approved'),
            "require_master_workers": self.config.getboolean('HIT Configuration','require_master_workers')
        }
        return hit_config
 
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   AWS RDS commands
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def db_aws_list_regions(self):
        ''' List AWS DB regions '''
        regions = self.db_services.list_regions()
        if regions != []:
            print "Avaliable AWS regions:"
        for reg in regions:
            print '\t' + reg,
            if reg == self.db_services.get_region():
                print "(currently selected)"
            else:
                print ''

    def db_aws_get_region(self):
        ''' Get AWS region '''
        print self.db_services.get_region()

    def db_aws_set_region(self, region_name):
        ''' Set AWS region '''
        # interactive = False # Not used
        if region_name is None:
            # interactive = True  # Not used
            self.db_aws_list_regions()
            allowed_regions = self.db_services.list_regions()
            region_name = "NONSENSE WORD1234"
            tries = 0
            while region_name not in allowed_regions:
                if tries == 0:
                    region_name = raw_input('Enter the name of the region you '
                                            'would like to use: ')
                else:
                    print("*** The region name (%s) you entered is not allowed, " \
                          "please choose from the list printed above (use type 'db " \
                          "aws_list_regions'." % region_name)
                    region_name = raw_input('Enter the name of the region you '
                                            'would like to use: ')
                tries += 1
                if tries > 5:
                    print("*** Error, region you are requesting not available.  "
                          "No changes made to regions.")
                    return
        self.db_services.set_region(region_name)
        print "Region updated to ", region_name
        self.config.set('AWS Access', 'aws_region', region_name, True)
        if self.server.is_server_running() == 'yes':
            self.server_restart()

    def db_aws_list_instances(self):
        ''' List AWS DB instances '''
        instances = self.db_services.get_db_instances()
        if not instances:
            print("There are no DB instances associated with your AWS account " \
                "in region " + self.db_services.get_region())
        else:
            print("Here are the current DB instances associated with your AWS " \
                "account in region " + self.db_services.get_region())
            for dbinst in instances:
                print '\t'+'-'*20
                print "\tInstance ID: " + dbinst.id
                print "\tStatus: " + dbinst.status

    def db_aws_delete_instance(self, instance_id):
        ''' Delete AWS DB instance '''
        interactive = False
        if instance_id is None:
            interactive = True

        instances = self.db_services.get_db_instances()
        instance_list = [dbinst.id for dbinst in instances]

        if interactive:
            valid = False
            if len(instances) == 0:
                print("There are no instances you can delete currently.  Use "
                      "`db aws_create_instance` to make one.")
                return
            print "Here are the available instances you can delete:"
            for inst in instances:
                print "\t ", inst.id, "(", inst.status, ")"
            while not valid:
                instance_id = raw_input('Enter the instance identity you would '
                                        'like to delete: ')
                res = self.db_services.validate_instance_id(instance_id)
                if res is True:
                    valid = True
                else:
                    print(res + " Try again, instance name not valid.  Check " \
                        "for typos.")
                if instance_id in instance_list:
                    valid = True
                else:
                    valid = False
                    print("Try again, instance not present in this account.  "
                          "Try again checking for typos.")
        else:
            res = self.db_services.validate_instance_id(instance_id)
            if res is not True:
                print("*** Error, instance name either not valid.  Try again " 
                     "checking for typos.")
                return
            if instance_id not in instance_list:
                print("*** Error, This instance not present in this account.  "
                     "Try again checking for typos.  Run `db aws_list_instances` to "
                     "see valid list.")
                return

        user_input = raw_input(
            "Deleting an instance will erase all your data associated with the "
            "database in that instance.  Really quit? y or n:"
        )
        if user_input == 'y':
            res = self.db_services.delete_db_instance(instance_id)
            if res:
                print("AWS RDS database instance %s deleted.  Run `db " \
                    "aws_list_instances` for current status." % instance_id)
            else:
                print("*** Error deleting database instance %s.  " \
                    "It maybe because it is still being created, deleted, or is " \
                    "being backed up.  Run `db aws_list_instances` for current " \
                    "status." % instance_id)
        else:
            return

    def db_use_aws_instance(self, instance_id, arg):
        ''' set your database info to use the current instance configure a
        security zone for this based on your ip '''
        interactive = False
        if instance_id is None:
            interactive = True

        instances = self.db_services.get_db_instances()
        instance_list = [dbinst.id for dbinst in instances]

        if len(instances) == 0:
            print("There are no instances in this region/account.  Use `db "
                "aws_create_instance` to make one first.")
            return

        # show list of available instances, if there are none cancel immediately
        if interactive:
            valid = False
            print("Here are the available instances you have.  You can only "
                "use those listed as 'available':")
            for inst in instances:
                print "\t ", inst.id, "(", inst.status, ")"
            while not valid:
                instance_id = raw_input('Enter the instance identity you would '
                                        'like to use: ')
                res = self.db_services.validate_instance_id(instance_id)
                if res is True:
                    valid = True
                else:
                    print(res + " Try again, instance name not valid.  Check "
                          "for typos.")
                if instance_id in instance_list:
                    valid = True
                else:
                    valid = False
                    print("Try again, instance not present in this account. "
                          "Try again checking for typos.")
        else:
            res = self.db_services.validate_instance_id(instance_id)
            if res != True:
                print("*** Error, instance name either not valid.  Try again "
                      "checking for typos.")
                return
            if instance_id not in instance_list:
                print("*** Error, This instance not present in this account. "
                      "Try again checking for typos.  Run `db aws_list_instances` to "
                      "see valid list.")
                return

        user_input = raw_input(
            "Switching your DB settings to use this instance. Are you sure you "
            "want to do this? "
        )
        if user_input == 'y':
            # ask for password
            valid = False
            while not valid:
                password = raw_input('enter the master password for this '
                                     'instance: ')
                res = self.db_services.validate_instance_password(password)
                if res != True:
                    print("*** Error: password seems incorrect, doesn't "
                          "conform to AWS rules.  Try again")
                else:
                    valid = True

            # Get instance
            myinstance = self.db_services.get_db_instance_info(instance_id)
            if myinstance:
                # Add security zone to this node to allow connections
                my_ip = get_my_ip()
                if (not self.db_services.allow_access_to_instance(myinstance,
                                                                  my_ip)):
                    print("*** Error authorizing your ip address to connect to " \
                          "server (%s)." % my_ip)
                    return
                print "AWS RDS database instance %s selected." % instance_id

                # Using regular SQL commands list available database on this
                # node
                try:
                    db_url = 'mysql+pymysql://' + myinstance.master_username + ":" \
                        + password + "@" + myinstance.endpoint[0] + ":" + \
                        str(myinstance.endpoint[1])
                    engine = sa.create_engine(db_url, echo=False)
                    eng = engine.connect().execute
                    db_names = eng("show databases").fetchall()
                except:
                    print("***  Error connecting to instance.  Your password "
                          "might be incorrect.")
                    return
                existing_dbs = [db[0] for db in db_names if db not in \
                                [('information_schema',), ('innodb',), \
                                 ('mysql',), ('performance_schema',)]]
                create_db = False
                if len(existing_dbs) == 0:
                    valid = False
                    while not valid:
                        db_name = raw_input("No existing DBs in this instance. "
                                            "Enter a new name to create one: ")
                        res = self.db_services.validate_instance_dbname(db_name)
                        if res is True:
                            valid = True
                        else:
                            print res + " Try again."
                    create_db = True
                else:
                    print "Here are the available database tables"
                    for database in existing_dbs:
                        print "\t" + database
                    valid = False
                    while not valid:
                        db_name = raw_input(
                            "Enter the name of the database you want to use or "
                            "a new name to create  a new one: "
                        )
                        res = self.db_services.validate_instance_dbname(db_name)
                        if res is True:
                            valid = True
                        else:
                            print res + " Try again."
                    if db_name not in existing_dbs:
                        create_db = True
                if create_db:
                    try:
                        connection.execute("CREATE DATABASE %s;" % db_name)
                    except:
                        print("*** Error creating database %s on instance " \
                              "%s" % (db_name, instance_id))
                        return
                base_url = 'mysql+pymysql://' + myinstance.master_username + ":" + \
                    password + "@" + myinstance.endpoint[0] + ":" + \
                    str(myinstance.endpoint[1]) + "/" + db_name
                self.config.set("Database Parameters", "database_url", base_url)
                print("Successfully set your current database (database_url) " \
                      "to \n\t%s" % base_url)
                if (self.server.is_server_running() == 'maybe' or
                        self.server.is_server_running() == 'yes'):
                    self.do_restart_server('')
            else:
                print '\n'.join([
                    "*** Error selecting database instance %s." % arg['<id>'],
                    "Run `db list_db_instances` for current status of instances, only `available`",
                    "instances can be used.  Also, your password may be incorrect."
                ])
        else:
            return


    def db_create_aws_db_instance(self, instid=None, size=None, username=None,
                                  password=None, dbname=None):
        ''' Create db instance on AWS '''
        interactive = False
        if instid is None:
            interactive = True

        if interactive:
            print '\n'.join(['*************************************************',
                             'Ok, here are the rules on creating instances:',
                             '',
                             'instance id:',
                             '  Each instance needs an identifier.  This is the name',
                             '  of the virtual machine created for you on AWS.',
                             '  Rules are 1-63 alphanumeric characters, first must',
                             '  be a letter, must be unique to this AWS account.',
                             '',
                             'size:',
                             '  The maximum size of you database in GB.  Enter an',
                             '  integer between 5-1024',
                             '',
                             'master username:',
                             '  The username you will use to connect.  Rules are',
                             '  1-16 alphanumeric characters, first must be a letter,',
                             '  cannot be a reserved MySQL word/phrase',
                             '',
                             'master password:',
                             '  Rules are 8-41 alphanumeric characters',
                             '',
                             'database name:',
                             '  The name for the first database on this instance.  Rules are',
                             '  1-64 alphanumeric characters, cannot be a reserved MySQL word',
                             '*************************************************',
                             ''])

        if interactive:
            valid = False
            while not valid:
                instid = raw_input('enter an identifier for the instance (see '
                                   'rules above): ')
                res = self.db_services.validate_instance_id(instid)
                if res is True:
                    valid = True
                else:
                    print res + " Try again."
        else:
            res = self.db_services.validate_instance_id(instid)
            if res is not True:
                print res
                return

        if interactive:
            valid = False
            while not valid:
                size = raw_input('size of db in GB (5-1024): ')
                res = self.db_services.validate_instance_size(size)
                if res is True:
                    valid = True
                else:
                    print res + " Try again."
        else:
            res = self.db_services.validate_instance_size(size)
            if res is not True:
                print res
                return

        if interactive:
            valid = False
            while not valid:
                username = raw_input('master username (see rules above): ')
                res = self.db_services.validate_instance_username(username)
                if res is True:
                    valid = True
                else:
                    print res + " Try again."
        else:
            res = self.db_services.validate_instance_username(username)
            if res is not True:
                print res
                return

        if interactive:
            valid = False
            while not valid:
                password = raw_input('master password (see rules above): ')
                res = self.db_services.validate_instance_password(password)
                if res is True:
                    valid = True
                else:
                    print res + " Try again."
        else:
            res = self.db_services.validate_instance_password(password)
            if res is not True:
                print res
                return

        if interactive:
            valid = False
            while not valid:
                dbname = raw_input('name for first database on this instance \
                                   (see rules): ')
                res = self.db_services.validate_instance_dbname(dbname)
                if res is True:
                    valid = True
                else:
                    print res + " Try again."
        else:
            res = self.db_services.validate_instance_dbname(dbname)
            if res is not True:
                print res
                return

        options = {
            'id': instid,
            'size': size,
            'username': username,
            'password': password,
            'dbname': dbname
        }
        instance = self.db_services.create_db_instance(options)
        if not instance:
            print '\n'.join(['*****************************',
                             '  Sorry, there was an error creating db instance.'])
        else:
            print '\n'.join(['*****************************',
                             '  Creating AWS RDS MySQL Instance',
                             '    id: ' + str(options['id']),
                             '    size: ' + str(options['size']) + " GB",
                             '    username: ' + str(options['username']),
                             '    password: ' + str(options['password']),
                             '    dbname: ' +  str(options['dbname']),
                             '    type: MySQL/db.t1.micro',
                             '    ________________________',
                             ' Be sure to store this information in a safe place.',
                             ' Please wait 5-10 minutes while your database is created in the cloud.',
                             ' You can run \'db aws_list_instances\' to verify it was created (status',
                             ' will say \'available\' when it is ready'])
 
    
