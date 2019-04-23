# -*- coding: utf-8 -*-
""" This module is a facade for AMT (Boto) services. """

import boto3
import botocore
import datetime
import dateutil.tz

from flask import jsonify
import re as re
from psiturk.psiturk_config import PsiturkConfig

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

PERCENT_ASSIGNMENTS_APPROVED_QUAL_ID = '000000000000000000L0'
NUMBER_HITS_APPROVED_QUAL_ID = '00000000000000000040'
LOCALE_QUAL_ID = '00000000000000000071'
MASTERS_QUAL_ID = '2F1QJWKUDD8XADTFD2Q0G6UTO95ALH'
MASTERS_SANDBOX_QUAL_ID = '2ARFPLSP75KLA8M8DH1HTEQVJT3SY6'

NOTIFICATION_VERSION = '2006-05-05'

class MTurkHIT(object):
    ''' Structure for dealing with MTurk HITs '''

    def __init__(self, options):
        self.options = options

    def __repr__(self):
        return "%s \n\tStatus: %s \n\tHITid: %s \
            \n\tmax:%s/pending:%s/complete:%s/remain:%s \n\tCreated:%s \
            \n\tExpires:%s\n\tIs Expired:%s\n" % (
                self.options['title'],
                self.options['status'],
                self.options['hitid'],
                self.options['max_assignments'],
                self.options['number_assignments_pending'],
                self.options['number_assignments_completed'],
                self.options['number_assignments_available'],
                self.options['creation_time'],
                self.options['expiration'],
                self.options['is_expired']
            )

class RDSServices(object):
    ''' Relational database services via AWS '''

    def __init__(self, aws_access_key_id, aws_secret_access_key,
                 region='us-east-1', quiet=False):
        self.update_credentials(aws_access_key_id, aws_secret_access_key)
        self.set_region(region)

        self.rdsc = boto3.client(
            'rds',
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )
        if not quiet:
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
        regions = boto3.session.Session().get_available_regions('s3')
        return regions

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
            try:
                self.rdsc.describe_db_instances()
            except botocore.exceptions.ClientError as exception:
                print exception
                return False
            except AttributeError as e:
                print e
                print "*** Unable to establish connection to AWS region %s "\
                    "using your access key/secret key", self.region
                return False
            except boto.exception.BotoServerError as e:
                print "***********************************************************"
                print "WARNING"
                print "Unable to establish connection to AWS RDS (Amazon relational database services)."
                print "See relevant psiturk docs here:"
                print "\thttp://psiturk.readthedocs.io/en/latest/configure_databases.html#obtaining-a-low-cost-or-free-mysql-database-on-amazon-s-web-services-cloud"
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

        return True

    def get_db_instance_info(self, dbid):
        ''' Get DB instance info '''
        if not self.connect_to_aws_rds():
            return False
        try:
            instances = self.rdsc.describe_db_instances(dbid).get('DBInstances')
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
            instances = self.rdsc.describe_db_instances().get('DBInstances')
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
        self.setup_mturk_connection()
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

    @staticmethod
    def _hit_xml_to_object(hits):
        hits_data = [MTurkHIT({
            'hitid': hit['HITId'],
            'title': hit['Title'],
            'status': hit['HITStatus'],
            'max_assignments': hit['MaxAssignments'],
            'number_assignments_completed': hit['NumberOfAssignmentsCompleted'],
            'number_assignments_pending': hit['NumberOfAssignmentsPending'],
            'number_assignments_available': hit['NumberOfAssignmentsAvailable'],
            'creation_time': hit['CreationTime'],
            'expiration': hit['Expiration'],
            'is_expired': datetime.datetime.now(hit['Expiration'].tzinfo) >= hit['Expiration']
        }) for hit in hits]
        return hits_data

    def get_all_hits(self):
        ''' Get all HITs '''
        if not self.connect_to_turk():
            return False
        try:
            hits = []
            paginator = self.mtc.get_paginator('list_hits')
            for page in paginator.paginate():
                hits.extend(page['HITs'])
        except Exception as e:
            print e
            return False
        hits_data = self._hit_xml_to_object(hits)
        return hits_data

    def get_workers(self, assignment_status=None, chosen_hits=None):
        ''' Get workers '''
        if not self.connect_to_turk():
            return False
        try:
            if chosen_hits:
                hit_ids = chosen_hits
            else:
                hits = self.get_all_hits()
                hit_ids = [hit.options['hitid'] for hit in hits]

            assignments = []
            for hit_id in hit_ids:
                paginator = self.mtc.get_paginator('list_assignments_for_hit')
                args = dict(
                    HITId=hit_id
                )
                if assignment_status:
                    args['AssignmentStatuses'] = [assignment_status]

                for page in paginator.paginate(**args):
                    assignments.extend(page['Assignments'])

        except Exception as e:
            print e
            return False
        workers = [{
            'hitId': assignment['HITId'],
            'assignmentId': assignment['AssignmentId'],
            'workerId': assignment['WorkerId'],
            'submit_time': assignment['SubmitTime'],
            'accept_time': assignment['AcceptTime'],
            'status': assignment['AssignmentStatus'],
        } for assignment in assignments]
        return workers

    def get_worker(self, assignment_id):
        if not self.connect_to_turk():
            return False
        try:
            assignment = self.mtc.get_assignment(AssignmentId=assignment_id)['Assignment']
        except Exception as e:
            return False
        worker_data = {
            'hitId': assignment['HITId'],
            'assignmentId': assignment['AssignmentId'],
            'workerId': assignment['WorkerId'],
            'submit_time': assignment['SubmitTime'],
            'accept_time': assignment['AcceptTime'],
            'status': assignment['AssignmentStatus'],
        }
        return worker_data

    def bonus_worker(self, assignment_id, amount, reason=""):
        ''' Bonus worker '''
        if not self.connect_to_turk():
            return False
        try:
            assignment = self.mtc.get_assignment(AssignmentId=assignment_id)['Assignment']
            worker_id = assignment['WorkerId']
            self.mtc.send_bonus(WorkerId=worker_id, AssignmentId=assignment_id, BonusAmount=amount, Reason=reason)
            return True
        except Exception as exception:
            print exception
            return False

    def approve_worker(self, assignment_id, override_rejection = False):
        ''' Approve worker '''
        if not self.connect_to_turk():
            return False
        try:
            self.mtc.approve_assignment(AssignmentId=assignment_id,
                OverrideRejection=override_rejection)
        except Exception as e:
            return False

    def reject_worker(self, assignment_id):
        ''' Reject worker '''
        if not self.connect_to_turk():
            return False
        try:
            self.mtc.reject_assignment(AssignmentId=assignment_id)
            return True
        except Exception:
            return False

    def unreject_worker(self, assignment_id):
        ''' Unreject worker '''
        return self.approve_worker(assignment_id, True)

    def setup_mturk_connection(self):
        ''' Connect to turk '''
        if ((self.aws_access_key_id == 'YourAccessKeyId') or
                (self.aws_secret_access_key == 'YourSecretAccessKey')):
            return False

        if self.is_sandbox:
            endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
        else:
            endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

        self.mtc = boto3.client('mturk',
                region_name='us-east-1',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                endpoint_url=endpoint_url)
        return True

    def verify_aws_login(self):
        ''' Verify AWS login '''
        if not self.mtc:
            return False

        try:
            self.mtc.get_account_balance()
        except Exception as exception:
            print exception
            return False
        else:
            return True

    def connect_to_turk(self):
        ''' Connect to turk '''
        if not self.valid_login or not self.mtc:
            print 'Sorry, unable to connect to Amazon Mechanical Turk. AWS '\
                  'credentials invalid.'
            return False

        return True

    def configure_hit(self, hit_config):
        ''' Configure HIT '''

        # Qualification:
        quals = []
        quals.append(dict(
            QualificationTypeId=PERCENT_ASSIGNMENTS_APPROVED_QUAL_ID,
            Comparator='GreaterThanOrEqualTo',
            IntegerValues=[int(hit_config['approve_requirement'])]
        ))

        quals.append(dict(
            QualificationTypeId=NUMBER_HITS_APPROVED_QUAL_ID,
            Comparator='GreaterThanOrEqualTo',
            IntegerValues=[int(hit_config['number_hits_approved'])]
        ))

        if hit_config['require_master_workers']:
            master_qualId = MASTERS_SANDBOX_QUAL_ID if self.is_sandbox else MASTERS_QUAL_ID
            quals.append(dict(
                QualificationTypeId=master_qualId,
                Comparator='Exists'
            ))

        if hit_config['us_only']:
            quals.append(dict(
                QualificationTypeId=LOCALE_QUAL_ID,
                Comparator='EqualTo',
                LocaleValues=[{'Country': 'US'}]
            ))

        # Create a HIT type for this HIT.
        hit_type = self.mtc.create_hit_type(
            Title=hit_config['title'],
            Description=hit_config['description'],
            Reward=str(hit_config['reward']),
            AssignmentDurationInSeconds=int(hit_config['duration'].total_seconds()),
            Keywords=hit_config['keywords'],
            QualificationRequirements=quals)

        # Check the config file to see if notifications are wanted.
        config = PsiturkConfig()
        config.load_config()

        try:
            url = config.get('Server Parameters', 'notification_url')

            all_event_types = [
                "AssignmentAccepted",
                "AssignmentAbandoned",
                "AssignmentReturned",
                "AssignmentSubmitted",
                "HITReviewable",
                "HITExpired",
            ]

            # TODO: not sure if this works. Can't find documentation in PsiTurk or MTurk
            self.mtc.update_notification_settings(
                HitTypeId=hit_type['HITTypeId'],
                Notification=dict(
                    Destination=url,
                    Transport='REST',
                    Version=NOTIFICATION_VERSION,
                    EventTypes=all_event_types,
                ),
            )

        except Exception as e:
            pass

        schema_url = "http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"
        template = '<ExternalQuestion xmlns="%(schema_url)s"><ExternalURL>%%(external_url)s</ExternalURL><FrameHeight>%%(frame_height)s</FrameHeight></ExternalQuestion>' % vars()
        question = template % dict(
            external_url=hit_config['ad_location'],
            frame_height=600,
        )


        # Specify all the HIT parameters
        self.param_dict = dict(
            HITTypeId=hit_type['HITTypeId'],
            Question=question,
            LifetimeInSeconds=int(hit_config['lifetime'].total_seconds()),
            MaxAssignments=hit_config['max_assignments'],
            # TODO
            # ResponseGroups=[
            #     'Minimal',
            #     'HITDetail',
            #     'HITQuestion',
            #     'HITAssignmentSummary'
            # ]
            )

    def check_balance(self):
        ''' Check balance '''
        if not self.connect_to_turk():
            return '-'
        return self.mtc.get_account_balance()['AvailableBalance']

    # TODO (if valid AWS credentials haven't been provided then
    # connect_to_turk() will fail, not error checking here and elsewhere)
    def create_hit(self, hit_config):
        ''' Create HIT '''
        try:
            if not self.connect_to_turk():
                return False
            self.configure_hit(hit_config)
            myhit = self.mtc.create_hit_with_hit_type(**self.param_dict)['HIT']
            self.hitid = myhit['HITId']
        except Exception as e:
            print e
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
            self.mtc.update_expiration_for_hit(
                HITId=hitid,
                ExpireAt=datetime.datetime.now()
            )
            return True
        except Exception as e:
            print "Failed to expire HIT. Please check the ID and try again."
            print e
            return False

    def delete_hit(self, hitid):
        ''' Delete HIT '''
        if not self.connect_to_turk():
            return False
        try:
            self.mtc.delete_hit(HITId=hitid)
        except Exception, e:
            print "Failed to delete of HIT %s. Make sure there are no "\
                "assignments remaining to be reviewed." % hitid

    def extend_hit(self, hitid, assignments_increment=None,
                   expiration_increment=None):
        if not self.connect_to_turk():
            return False
        try:
            if assignments_increment:
                self.mtc.create_additional_assignments_for_hit(HITId=hitid,
                    NumberOfAdditionalAssignments=int(assignments_increment))

            if expiration_increment:
                hit = self.get_hit(hitid)
                print 'got hit', hit
                expiration = hit['Expiration'] + datetime.timedelta(minutes=int(expiration_increment))
                self.mtc.update_expiration_for_hit(HITId=hitid, ExpireAt=expiration)

            return True
        except Exception, e:
            print e
            print "Failed to extend HIT %s. Please check the ID and try again." \
                % hitid
            return False

    def get_hit(self, hitid):
        ''' Get HIT '''
        if not self.connect_to_turk():
            return False
        try:
            hitdata = self.mtc.get_hit(HITId=hitid)
        except Exception as e:
            print e
            return False
        return hitdata['HIT']

    def get_hit_status(self, hitid):
        ''' Get HIT status '''
        hit = self.get_hit(hitid)
        if not hit:
            return False

        return hitdata['HITStatus']

    def get_summary(self):
        ''' Get summary '''
        try:
            balance = self.check_balance()
            summary = jsonify(balance=str(balance))
            return summary
        except MTurkRequestError as exception:
            print exception.error_message
            return False

