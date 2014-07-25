# -*- coding: utf-8 -*-
""" This module is a facade for AMT (Boto) services. """

import boto.rds
import boto.ec2
from boto.exception import EC2ResponseError
# from boto.rds import RDSConnection
from boto.mturk.connection import MTurkConnection, MTurkRequestError
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import LocaleRequirement, \
    PercentAssignmentsApprovedRequirement, Qualifications
from flask import jsonify
import re as re


MYSQL_RESERVED_WORDS_CAP = [
    'ACCESSIBLE', 'ADD', 'ALL', 'ALTER', 'ANALYZE', 'AND', 'AS', 'ASC',
    'ASENSITIVE', 'BEFORE', 'BETWEEN', 'BIGINT', 'BINARY', 'BLOB', 'BOTH',
    'BY', 'CALL', 'CASCADE', 'CASE', 'CHANGE', 'CHAR', 'CHARACTER', 'CHECK',
    'COLLATE', 'COLUMN', 'CONDITION', 'CONSTRAINT', 'CONTINUE', 'CONVERT',
    'CREATE', 'CROSS', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP',
    'CURRENT_USER', 'CURSOR', 'DATABASE', 'DATABASES', 'DAY_HOUR',
    'DAY_MICROSECOND', 'DAY_MINUTE', 'DAY_SECOND', 'DEC', 'DECIMAL', 'DECLARE',
    'DEFAULT', 'DELAYED', 'DELETE', 'DESC', 'DESCRIBE', 'DETERMINISTIC',
    'DISTINCT', 'DISTINCTROW', 'DIV', 'DOUBLE', 'DROP', 'DUAL', 'EACH', 'ELSE',
    'ELSEIF', 'ENCLOSED', 'ESCAPED', 'EXISTS', 'EXIT', 'EXPLAIN', 'FALSE',
    'FETCH', 'FLOAT', 'FLOAT4', 'FLOAT8', 'FOR', 'FORCE', 'FOREIGN', 'FROM',
    'FULLTEXT', 'GET', 'GRANT', 'GROUP', 'HAVING', 'HIGH_PRIORITY',
    'HOUR_MICROSECOND', 'HOUR_MINUTE', 'HOUR_SECOND', 'IF', 'IGNORE', 'IN',
    'INDEX', 'INFILE', 'INNER', 'INOUT', 'INSENSITIVE', 'INSERT', 'INT',
    'INT1', 'INT2', 'INT3', 'INT4', 'INT8', 'INTEGER', 'INTERVAL', 'INTO',
    'IO_AFTER_GTIDS', 'IO_BEFORE_GTIDS', 'IS', 'ITERATE', 'JOIN', 'KEY',
    'KEYS', 'KILL', 'LEADING', 'LEAVE', 'LEFT', 'LIKE', 'LIMIT', 'LINEAR',
    'LINES', 'LOAD', 'LOCALTIME', 'LOCALTIMESTAMP', 'LOCK', 'LONG', 'LONGBLOB',
    'LONGTEXT', 'LOOP', 'LOW_PRIORITY', 'MASTER_BIND',
    'MASTER_SSL_VERIFY_SERVER_CERT', 'MATCH', 'MAXVALUE', 'MEDIUMBLOB',
    'MEDIUMINT', 'MEDIUMTEXT', 'MIDDLEINT', 'MINUTE_MICROSECOND',
    'MINUTE_SECOND', 'MOD', 'MODIFIES', 'NATURAL', 'NOT', 'NO_WRITE_TO_BINLOG',
    'NULL', 'NUMERIC', 'ON', 'OPTIMIZE', 'OPTION', 'OPTIONALLY', 'OR', 'ORDER',
    'OUT', 'OUTER', 'OUTFILE', 'PARTITION', 'PRECISION', 'PRIMARY',
    'PROCEDURE', 'PURGE', 'RANGE', 'READ', 'READS', 'READ_WRITE', 'REAL',
    'REFERENCES', 'REGEXP', 'RELEASE', 'RENAME', 'REPEAT', 'REPLACE',
    'REQUIRE', 'RESIGNAL', 'RESTRICT', 'RETURN', 'REVOKE', 'RIGHT', 'RLIKE',
    'SCHEMA', 'SCHEMAS', 'SECOND_MICROSECOND', 'SELECT', 'SENSITIVE',
    'SEPARATOR', 'SET', 'SHOW', 'SIGNAL', 'SMALLINT', 'SPATIAL', 'SPECIFIC',
    'SQL', 'SQLEXCEPTION', 'SQLSTATE', 'SQLWARNING', 'SQL_BIG_RESULT',
    'SQL_CALC_FOUND_ROWS', 'SQL_SMALL_RESULT', 'SSL', 'STARTING',
    'STRAIGHT_JOIN', 'TABLE', 'TERMINATED', 'THEN', 'TINYBLOB', 'TINYINT',
    'TINYTEXT', 'TO', 'TRAILING', 'TRIGGER', 'TRUE', 'UNDO', 'UNION', 'UNIQUE',
    'UNLOCK', 'UNSIGNED', 'UPDATE', 'USAGE', 'USE', 'USING', 'UTC_DATE',
    'UTC_TIME', 'UTC_TIMESTAMP', 'VALUES', 'VARBINARY', 'VARCHAR',
    'VARCHARACTER', 'VARYING', 'WHEN', 'WHERE', 'WHILE', 'WITH', 'WRITE',
    'XOR', 'YEAR_MONTH', 'ZEROFILL'
]
MYSQL_RESERVED_WORDS = [word.lower() for word in MYSQL_RESERVED_WORDS_CAP]


class MTurkHIT(object):
    ''' Structure for dealing with MTurk HITs '''

    def __init__(self, json_options):
        self.options = json_options

    def __repr__(self):
        return "%s \n\tStatus: %s \n\tHITid: %s \
            \n\tmax:%s/pending:%s/complete:%s/remain:%s \n\tCreated:%s \
            \n\tExpires:%s\n" % (
                self.options['title'],
                self.options['status'],
                self.options['hitid'],
                self.options['max_assignments'],
                self.options['number_assignments_pending'],
                self.options['number_assignments_completed'],
                self.options['number_assignments_available'],
                self.options['creation_time'],
                self.options['expiration']
            )

class RDSServices(object):
    ''' Relational database services via AWS '''

    def __init__(self, aws_access_key_id, aws_secret_access_key,
                 region='us-east-1'):
        self.update_credentials(aws_access_key_id, aws_secret_access_key)
        self.set_region(region)
        self.valid_login = self.verify_aws_login()

        # if not self.valid_login:
        #     print 'Sorry, AWS Credentials invalid.\nYou will only be able to
        #     '\ + 'test experiments locally until you enter\nvalid '\ +
        #     'credentials in the AWS Access section of config.txt.'

    def update_credentials(self, aws_access_key_id, aws_secret_access_key):
        ''' Update credentials '''
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    def list_regions(self):
        ''' List regions '''
        regions = boto.rds.regions()
        return [reg.name for reg in regions]

    def get_region(self):
        ''' Get regions '''
        return self.region

    def set_region(self, region):
        ''' Set regions '''
        self.region = region

    def verify_aws_login(self):
        '''Verify AWS login '''
        if ((self.aws_access_key_id == 'YourAccessKeyId') or
                (self.aws_secret_access_key == 'YourSecretAccessKey')):
            return False
        else:
            # rdsparams = dict(
            #     aws_access_key_id=self.aws_access_key_id,
            #     aws_secret_access_key=self.aws_secret_access_key,
            #     region=self.region)
            # self.rdsc = RDSConnection(**rdsparams)
            self.rdsc = boto.rds.connect_to_region(
                self.region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            try:
                self.rdsc.get_all_dbinstances()
            except MTurkRequestError as exception:
                print exception.error_message
                return False
            except AttributeError:
                print "*** Unable to establish connection to AWS region %s "\
                    "using your access key/secret key", self.region
                return False
            except boto.exception.BotoServerError:
                print "***********************************************************"
                print "WARNING"
                print "Unable to establish connection to AWS."
                print "While your keys may be valid, your AWS account needs a "
                print "subscription to certain services.  If you haven't been asked"
                print "to provide a credit card and verified your account using your "
                print "phone, it means your keys are not completely set up yet."
                print "Please refer to "
                print "\thttp://psiturk.readthedocs.org/en/latest/amt_setup.html"
                print "***********************************************************"
                return False
            else:
                return True

    def connect_to_aws_rds(self):
        ''' Connec to aws rds '''
        if not self.valid_login:
            print 'Sorry, unable to connect to Amazon\'s RDS database server. "\
                "AWS credentials invalid.'
            return False
        # rdsparams = dict(
        #     aws_access_key_id = self.aws_access_key_id,
        #     aws_secret_access_key = self.aws_secret_access_key,
        #     region=self.region)
        # self.rdsc = RDSConnection(**rdsparams)
        self.rdsc = boto.rds.connect_to_region(
            self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        return True

    def get_db_instance_info(self, dbid):
        ''' Get DB instance info '''
        if not self.connect_to_aws_rds():
            return False
        try:
            instances = self.rdsc.get_all_dbinstances(dbid)
        except:
            return False
        else:
            myinstance = instances[0]
            return myinstance

    def allow_access_to_instance(self, _, ip_address):
        ''' Allow access to instance. '''
        if not self.connect_to_aws_rds():
            return False
        try:
            conn = boto.ec2.connect_to_region(
                self.region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            sgs = conn.get_all_security_groups('default')
            default_sg = sgs[0]
            default_sg.authorize(ip_protocol='tcp', from_port=3306,
                                 to_port=3306, cidr_ip=str(ip_address)+'/32')
        except EC2ResponseError, exception:
            if exception.error_code == "InvalidPermission.Duplicate":
                return True  # ok it already exists
            else:
                return False
        else:
            return True

    def get_db_instances(self):
        '''  DB instance '''
        if not self.connect_to_aws_rds():
            return False
        try:
            instances = self.rdsc.get_all_dbinstances()
        except:
            return False
        else:
            return instances

    def delete_db_instance(self, dbid):
        ''' Delete DB '''
        if not self.connect_to_aws_rds():
            return False
        try:
            database = self.rdsc.delete_dbinstance(dbid,
                                                   skip_final_snapshot=True)
            print database
        except:
            return False
        else:
            return True

    def validate_instance_id(self, instid):
        ''' Validate instance ID '''
        # 1-63 alphanumeric characters, first must be a letter.
        if re.match('[\w-]+$', instid) is not None:
            if len(instid) <= 63 and len(instid) >= 1:
                if instid[0].isalpha():
                    return True
        return "*** Error: Instance ids must be 1-63 alphanumeric characters, \
            first is a letter."

    def validate_instance_size(self, size):
        ''' integer between 5-1024 (inclusive) '''
        try:
            int(size)
        except ValueError:
            return '*** Error: size must be a whole number between 5 and 1024.'
        if int(size) < 5 or int(size) > 1024:
            return '*** Error: size must be between 5-1024 GB.'
        return True

    def validate_instance_username(self, username):
        ''' Validate instance username '''
        # 1-16 alphanumeric characters - first character must be a letter -
        # cannot be a reserved MySQL word
        if re.match('[\w-]+$', username) is not None:
            if len(username) <= 16 and len(username) >= 1:
                if username[0].isalpha():
                    if username not in MYSQL_RESERVED_WORDS:
                        return True
        return '*** Error: Usernames must be 1-16 alphanumeric chracters, \
            first a letter, cannot be reserved MySQL word.'

    def validate_instance_password(self, password):
        ''' Validate instance passwords '''
        # 1-16 alphanumeric characters - first character must be a letter -
        # cannot be a reserved MySQL word
        if re.match('[\w-]+$', password) is not None:
            if len(password) <= 41 and len(password) >= 8:
                return True
        return '*** Error: Passwords must be 8-41 alphanumeric characters'

    def validate_instance_dbname(self, dbname):
        ''' Validate instance database name '''
        # 1-64 alphanumeric characters, cannot be a reserved MySQL word
        if re.match('[\w-]+$', dbname) is not None:
            if len(dbname) <= 41 and len(dbname) >= 1:
                if dbname.lower() not in MYSQL_RESERVED_WORDS:
                    return True
        return '*** Error: Database names must be 1-64 alphanumeric characters,\
            cannot be a reserved MySQL word.'

    def create_db_instance(self, params):
        ''' Create db instance '''
        if not self.connect_to_aws_rds():
            return False
        try:
            database = self.rdsc.create_dbinstance(
                id=params['id'],
                allocated_storage=params['size'],
                instance_class='db.t1.micro',
                engine='MySQL',
                master_username=params['username'],
                master_password=params['password'],
                db_name=params['dbname'],
                multi_az=False
            )
        except:
            return False
        else:
            return True


class MTurkServices(object):
    ''' MTurk services '''
    def __init__(self, aws_access_key_id, aws_secret_access_key, is_sandbox):
        self.update_credentials(aws_access_key_id, aws_secret_access_key)
        self.set_sandbox(is_sandbox)
        self.valid_login = self.verify_aws_login()

        if not self.valid_login:
            print 'WARNING *****************************'
            print 'Sorry, AWS Credentials invalid.\nYou will only be able to '\
                  'test experiments locally until you enter\nvalid '\
                  'credentials in the AWS Access section of ~/.psiturkconfig\n'

    def update_credentials(self, aws_access_key_id, aws_secret_access_key):
        ''' Update credentials '''
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key

    def set_sandbox(self, is_sandbox):
        ''' Set sandbox '''
        self.is_sandbox = is_sandbox

    def get_reviewable_hits(self):
        ''' Get reviewable HITs '''
        if not self.connect_to_turk():
            return False
        try:
            hits = self.mtc.get_all_hits()
        except MTurkRequestError:
            return False
        reviewable_hits = [hit for hit in hits if hit.HITStatus == "Reviewable" \
                           or hit.HITStatus == "Reviewing"]
        hits_data = [MTurkHIT({
            'hitid': hit.HITId,
            'title': hit.Title,
            'status': hit.HITStatus,
            'max_assignments': hit.MaxAssignments,
            'number_assignments_completed': hit.NumberOfAssignmentsCompleted,
            'number_assignments_pending': hit.NumberOfAssignmentsPending,
            'number_assignments_available': hit.NumberOfAssignmentsAvailable,
            'creation_time': hit.CreationTime,
            'expiration': hit.Expiration
        }) for hit in reviewable_hits]
        return hits_data

    def get_all_hits(self):
        ''' Get all HITs '''
        if not self.connect_to_turk():
            return False
        try:
            hits = self.mtc.get_all_hits()
        except MTurkRequestError:
            return False
        hits_data = [MTurkHIT({
            'hitid': hit.HITId,
            'title': hit.Title,
            'status': hit.HITStatus,
            'max_assignments': hit.MaxAssignments,
            'number_assignments_completed': hit.NumberOfAssignmentsCompleted,
            'number_assignments_pending': hit.NumberOfAssignmentsPending,
            'number_assignments_available': hit.NumberOfAssignmentsAvailable,
            'creation_time': hit.CreationTime,
            'expiration': hit.Expiration,
            }) for hit in hits]
        return hits_data

    def get_active_hits(self):
        ''' Get active HITs '''
        if not self.connect_to_turk():
            return False
        # hits = self.mtc.search_hits()
        try:
            hits = self.mtc.get_all_hits()
        except MTurkRequestError:
            return False
        active_hits = [hit for hit in hits if not hit.expired]
        hits_data = [MTurkHIT({
            'hitid': hit.HITId,
            'title': hit.Title,
            'status': hit.HITStatus,
            'max_assignments': hit.MaxAssignments,
            'number_assignments_completed': hit.NumberOfAssignmentsCompleted,
            'number_assignments_pending': hit.NumberOfAssignmentsPending,
            'number_assignments_available': hit.NumberOfAssignmentsAvailable,
            'creation_time': hit.CreationTime,
            'expiration': hit.Expiration,
            }) for hit in active_hits]
        return hits_data

    def get_workers(self, assignment_status=None):
        ''' Get workers '''
        if not self.connect_to_turk():
            return False
        try:
            hits = self.mtc.search_hits(sort_direction='Descending',
                                        page_size=20)
            hit_ids = [hit.HITId for hit in hits]
            workers_nested = [
                self.mtc.get_assignments(
                    hit_id,
                    status=assignment_status,
                    sort_by='SubmitTime',
                    page_size=100
                ) for hit_id in hit_ids]

            workers = [val for subl in workers_nested for val in subl]  # Flatten nested lists
        except MTurkRequestError:
            return False
        worker_data = [{
            'hitId': worker.HITId,
            'assignmentId': worker.AssignmentId,
            'workerId': worker.WorkerId,
            'submit_time': worker.SubmitTime,
            'accept_time': worker.AcceptTime,
            'status': worker.AssignmentStatus
        } for worker in workers]
        return worker_data

    def bonus_worker(self, assignment_id, amount, reason=""):
        ''' Bonus worker '''
        if not self.connect_to_turk():
            return False
        try:
            bonus = MTurkConnection.get_price_as_price(amount)
            assignment = self.mtc.get_assignment(assignment_id)[0]
            worker_id = assignment.WorkerId
            self.mtc.grant_bonus(worker_id, assignment_id, bonus, reason)
            return True
        except MTurkRequestError as exception:
            print exception
            return False

    def approve_worker(self, assignment_id):
        ''' Approve worker '''
        if not self.connect_to_turk():
            return False
        try:
            self.mtc.approve_assignment(assignment_id, feedback=None)
            return True
        except MTurkRequestError:
            return False

    def reject_worker(self, assignment_id):
        ''' Reject worker '''
        if not self.connect_to_turk():
            return False
        try:
            self.mtc.reject_assignment(assignment_id, feedback=None)
            return True
        except MTurkRequestError:
            return False

    def unreject_worker(self, assignment_id):
        ''' Unreject worker '''
        if not self.connect_to_turk():
            return False
        try:
            self.mtc.approve_rejected_assignment(assignment_id)
            return True
        except MTurkRequestError:
            return False

    def verify_aws_login(self):
        ''' Verify AWS login '''
        if ((self.aws_access_key_id == 'YourAccessKeyId') or
                (self.aws_secret_access_key == 'YourSecretAccessKey')):
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
            except MTurkRequestError as exception:
                print exception.error_message
                return False
            else:
                return True

    def connect_to_turk(self):
        ''' Connect to turk '''
        if not self.valid_login:
            print 'Sorry, unable to connect to Amazon Mechanical Turk. AWS '\
                  'credentials invalid.'
            return False
        if self.is_sandbox:
            host = 'mechanicalturk.sandbox.amazonaws.com'
        else:
            host = 'mechanicalturk.amazonaws.com'

        mturkparams = dict(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            host=host)
        self.mtc = MTurkConnection(**mturkparams)
        return True

    def configure_hit(self, hit_config):
        ''' Configure HIT '''
        # configure question_url based on the id
        experiment_portal_url = hit_config['ad_location']
        frame_height = 600
        mturk_question = ExternalQuestion(experiment_portal_url, frame_height)

        # Qualification:
        quals = Qualifications()
        approve_requirement = hit_config['approve_requirement']
        quals.add(
            PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo",
                                                  approve_requirement))

        if hit_config['us_only']:
            quals.add(LocaleRequirement("EqualTo", "US"))

        # Specify all the HIT parameters
        self.param_dict = dict(
            hit_type=None,
            question=mturk_question,
            lifetime=hit_config['lifetime'],
            max_assignments=hit_config['max_assignments'],
            title=hit_config['title'],
            description=hit_config['description'],
            keywords=hit_config['keywords'],
            reward=hit_config['reward'],
            duration=hit_config['duration'],
            approval_delay=None,
            questions=None,
            qualifications=quals
        )

    def check_balance(self):
        ''' Check balance '''
        if not self.connect_to_turk():
            return '-'
        return self.mtc.get_account_balance()[0]

    # TODO (if valid AWS credentials haven't been provided then
    # connect_to_turk() will fail, not error checking here and elsewhere)
    def create_hit(self, hit_config):
        ''' Create HIT '''
        try:
            if not self.connect_to_turk():
                return False
            self.configure_hit(hit_config)
            myhit = self.mtc.create_hit(**self.param_dict)[0]
            self.hitid = myhit.HITId
        except:
            return False
        else:
            return self.hitid

    # TODO(Jay): Have a wrapper around functions that serializes them.
    # Default output should not be serialized.
    def expire_hit(self, hitid):
        ''' Expire HIT '''
        if not self.connect_to_turk():
            return False
        try:
            self.mtc.expire_hit(hitid)
            return True
        except MTurkRequestError:
            print "Failed to expire HIT. Please check the ID and try again."
            return False

    def dispose_hit(self, hitid):
        ''' Dispose HIT '''
        if not self.connect_to_turk():
            return False
        try:
            self.mtc.dispose_hit(hitid)
        except Exception, e:
            print 'Failed to dispose of HIT %s. Make sure there are no "\
                "assignments remaining to be reviewed' % hitid

    def extend_hit(self, hitid, assignments_increment=None,
                   expiration_increment=None):
        if not self.connect_to_turk():
            return False
        try:
            self.mtc.extend_hit(hitid,
                                assignments_increment=int(assignments_increment
                                                          or 0))
            self.mtc.extend_hit(hitid,
                                expiration_increment=int(expiration_increment
                                                         or 0)*60)
            return True
        except Exception, e:
            print "Failed to extend HIT %s. Please check the ID and try again." \
                % hitid
            return False

    def get_hit_status(self, hitid):
        ''' Get HIT status '''
        if not self.connect_to_turk():
            return False
        try:
            hitdata = self.mtc.get_hit(hitid)
        except:
            return False
        return hitdata[0].HITStatus

    def get_summary(self):
        ''' Get summary '''
        try:
            balance = self.check_balance()
            summary = jsonify(balance=str(balance))
            return summary
        except MTurkRequestError as exception:
            print exception.error_message
            return False
