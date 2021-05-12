# -*- coding: utf-8 -*-
from __future__ import generator_stop
from functools import wraps
from builtins import str
from builtins import object
import boto3
import boto3.session
import datetime
from flask import jsonify
from psiturk.psiturk_config import PsiturkConfig
from .psiturk_exceptions import *

PERCENT_ASSIGNMENTS_APPROVED_QUAL_ID = '000000000000000000L0'
NUMBER_HITS_APPROVED_QUAL_ID = '00000000000000000040'
LOCALE_QUAL_ID = '00000000000000000071'
MASTERS_QUAL_ID = '2F1QJWKUDD8XADTFD2Q0G6UTO95ALH'
MASTERS_SANDBOX_QUAL_ID = '2ARFPLSP75KLA8M8DH1HTEQVJT3SY6'

NOTIFICATION_VERSION = '2006-05-05'


class AmtServicesResponse(object):
    """class AmtServicesResponse."""

    def __init__(self, status=None, success=None, operation='', message='',
                 data: dict = None, **kwargs):
        """Init."""
        self.success = success
        self.status = status
        self.operation = operation,
        self.message = message,
        self.data = data if data is not None else {}
        for k, v in kwargs.items():
            setattr(self, k, v)


class AmtServicesSuccessResponse(AmtServicesResponse):
    """class AmtServicesSuccessResponse."""

    def __init__(self, *args, **kwargs):
        """__init__."""
        super(AmtServicesSuccessResponse, self).__init__(
            *args, status='success', success=True, **kwargs)


class AmtServicesErrorResponse(AmtServicesResponse):
    """class AmtServicesErrorResponse."""

    def __init__(self, *args, **kwargs):
        """__init__."""
        exception = kwargs.pop('exception', None)
        super(AmtServicesErrorResponse, self).__init__(
            *args, status='error', success=False, exception=exception,
            **kwargs)


class NoHitDataError(AmtServicesException):
    """class NoHitDataError."""
    pass


def check_mturk_connection(func):
    """Return check_mturk_connection decorator."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.connect_to_turk():
            raise NoMturkConnectionError()
        return func(self, *args, **kwargs)

    return wrapper


def amt_service_response(func):
    """Return amt_service_response decorator."""
    @check_mturk_connection
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            return AmtServicesSuccessResponse(operation=func.__name__, data=response)
        except Exception as e:
            # print(e)
            return AmtServicesErrorResponse(operation=func.__name__, exception=e)

    return wrapper


class MTurkHIT(object):
    """Structure for dealing with MTurk HITs."""

    def __init__(self, options):
        """__init__."""
        self.options = options

    def __repr__(self):
        """__repr__."""
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


class MTurkServices(object):
    """MTurk services."""

    def __init__(self, config=None, mode='sandbox'):
        """__init__."""
        if config:
            self.config = config
        else:
            config = PsiturkConfig()
            config.load_config()
            self.config = config
        self.mode = None
        self.mtc = None
        self.session = None
        self.param_dict = None
        self.set_mode(mode)
        self.valid_login = self.verify_aws_login()

        if not self.valid_login:
            raise NoMturkConnectionError()

    def set_mode(self, mode):
        """Set mode."""
        self.mode = mode
        self.setup_mturk_connection()

    @staticmethod
    def _hit_xml_to_object(hits):
        if not isinstance(hits, list):
            hits = [hits]
        hits_data = [MTurkHIT({
            'hitid': hit['HITId'],
            'title': hit['Title'],
            'status': hit['HITStatus'],
            'max_assignments': hit['MaxAssignments'],
            'number_assignments_completed':
                hit['NumberOfAssignmentsCompleted'],
            'number_assignments_pending':
                hit['NumberOfAssignmentsPending'],
            'number_assignments_available':
                hit['NumberOfAssignmentsAvailable'],
            'creation_time': hit['CreationTime'],
            'expiration': hit['Expiration'],
            'is_expired': datetime.datetime.now(
                hit['Expiration'].tzinfo) >= hit['Expiration'],
            'duration_in_seconds': hit['AssignmentDurationInSeconds'],
            'reward': hit['Reward'],
            'description': hit['Description'],
            'number_submissions_needing_action':
                hit['MaxAssignments'] -
                hit['NumberOfAssignmentsCompleted'] -
                hit['NumberOfAssignmentsPending'] -
                hit['NumberOfAssignmentsAvailable']
        }) for hit in hits]
        return hits_data

    @amt_service_response
    def get_all_hits(self):
        """Get all HITs."""
        hits = []
        paginator = self.mtc.get_paginator('list_hits')
        for page in paginator.paginate():
            hits.extend(page['HITs'])
        hits_data = self._hit_xml_to_object(hits)
        return hits_data

    @amt_service_response
    def get_assignments(self, assignment_status=None, hit_ids=None):
        """Get workers."""
        if not hit_ids:
            hits = self.get_all_hits().data
            hit_ids = [hit.options['hitid'] for hit in hits]
        elif not isinstance(hit_ids, list):
            hit_ids = [hit_ids]

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
        workers = [{
            'hitId': assignment['HITId'],
            'assignmentId': assignment['AssignmentId'],
            'workerId': assignment['WorkerId'],
            'submit_time': assignment['SubmitTime'],
            'accept_time': assignment['AcceptTime'],
            'status': assignment['AssignmentStatus'],
        } for assignment in assignments]
        return workers

    @amt_service_response
    def get_assignment(self, assignment_id):
        """Get assignment."""
        assignment = self.mtc.get_assignment(
            AssignmentId=assignment_id)['Assignment']
        worker_data = {
            'hitId': assignment['HITId'],
            'assignmentId': assignment['AssignmentId'],
            'workerId': assignment['WorkerId'],
            'submit_time': assignment['SubmitTime'],
            'accept_time': assignment['AcceptTime'],
            'status': assignment['AssignmentStatus'],
        }
        return worker_data

    @amt_service_response
    def bonus_assignment(self, assignment_id, worker_id, amount, reason=""):
        """Bonus worker."""
        if not worker_id:
            assignment = self.mtc.get_assignment(
                AssignmentId=assignment_id)['Assignment']
            worker_id = assignment['WorkerId']
        self.mtc.send_bonus(WorkerId=worker_id, AssignmentId=assignment_id,
                            BonusAmount=str(amount), Reason=reason)
        return True

    @amt_service_response
    def approve_assignment(self, assignment_id, override_rejection=False):
        """Approve worker."""
        self.mtc.approve_assignment(AssignmentId=assignment_id,
                                    OverrideRejection=override_rejection)
        return True

    @amt_service_response
    def reject_assignment(self, assignment_id):
        """Reject worker."""
        self.mtc.reject_assignment(
            AssignmentId=assignment_id, RequesterFeedback='')
        return True

    @amt_service_response
    def unreject_assignment(self, assignment_id):
        """Unreject worker."""
        return self.approve_assignment(assignment_id, override_rejection=True)

    def setup_mturk_connection(self):
        """Connect to turk."""
        if self.mode == 'sandbox':
            endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
        else:
            endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

        client_kwargs = {
            'endpoint_url': endpoint_url
        }

        session_kwargs = {
            'region_name': 'us-east-1',
        }
        aws_access_key_id = self.config.get('AWS Access', 'aws_access_key_id')
        aws_secret_access_key = self.config.get('AWS Access',
                                                'aws_secret_access_key')

        if aws_access_key_id and aws_secret_access_key:
            session_kwargs['aws_access_key_id'] = aws_access_key_id
            session_kwargs['aws_secret_access_key'] = aws_secret_access_key

        self.session = boto3.session.Session(**session_kwargs)
        self.mtc = self.session.client('mturk', **client_kwargs)


        # aws access key might have been set via env var -- fetch it and
        # set it to the psiturk config for dashboard use
        credentials = self.session.get_credentials()
        if credentials:
            self.config.set('AWS Access', 'aws_access_key_id',
                            credentials.access_key)
            self.config.set('AWS Access', 'aws_secret_access_key',
                            credentials.secret_key)

        return True

    def verify_aws_login(self):
        """Verify AWS login."""
        if not self.mtc:
            return False

        try:
            self.mtc.get_account_balance()
            return True
        except Exception:
            return False

    def connect_to_turk(self):
        """Connect to turk."""
        if not self.valid_login or not self.mtc:
            return False
        return True

    def configure_hit(self, hit_config):
        """Configure HIT."""
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
            master_qualId = (MASTERS_SANDBOX_QUAL_ID if self.mode == 'sandbox'
                             else MASTERS_QUAL_ID)
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

        for qual_id in hit_config['require_qualification_ids']:
            quals.append(dict(QualificationTypeId=qual_id,
                              Comparator='Exists'))

        for qual_id in hit_config['block_qualification_ids']:
            quals.append(dict(QualificationTypeId=qual_id,
                              Comparator='DoesNotExist'))

        for advanced_qual in hit_config['advanced_qualifications']:
            quals.append(dict(advanced_qual))

        # Create a HIT type for this HIT.
        hit_type = self.mtc.create_hit_type(
            Title=hit_config['title'],
            Description=hit_config['description'],
            Reward=str(hit_config['reward']),
            AssignmentDurationInSeconds=int(
                hit_config['duration'].total_seconds()),
            Keywords=hit_config['keywords'],
            QualificationRequirements=quals)

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

    @amt_service_response
    def list_qualification_types(self, Query='', MustBeRequestable=False,
                                 MustBeOwnedByCaller=True):
        """list_qualification_types."""
        paginator = self.mtc.get_paginator('list_qualification_types')
        qualification_types = []
        kwargs = {
            'MustBeRequestable': MustBeRequestable,
            'MustBeOwnedByCaller': MustBeOwnedByCaller
        }
        if Query:
            kwargs['Query'] = Query

        for page in paginator.paginate(**kwargs):
            qualification_types.extend(page['QualificationTypes'])

        return qualification_types

    @amt_service_response
    def check_balance(self):
        """Check balance."""
        response = self.mtc.get_account_balance()
        return response['AvailableBalance']

    @amt_service_response
    def create_hit(self, hit_config):
        """Create HIT."""
        self.configure_hit(hit_config)
        myhit = self.mtc.create_hit_with_hit_type(**self.param_dict)['HIT']
        return myhit

    @amt_service_response
    def expire_hit(self, hitid):
        """Expire HIT."""
        time_in_past = (datetime.datetime.now(datetime.timezone.utc) +
                        datetime.timedelta(-30))
        self.mtc.update_expiration_for_hit(
            HITId=hitid,
            ExpireAt=time_in_past
        )
        return True

    @amt_service_response
    def delete_hit(self, hitid):
        """Delete HIT."""
        self.mtc.delete_hit(HITId=hitid)
        return True

    @amt_service_response
    def extend_hit(self, hitid, assignments_increment=None,
                   expiration_increment=None):
        """extend_hit."""
        if assignments_increment:
            self.mtc.create_additional_assignments_for_hit(
                HITId=hitid,
                NumberOfAdditionalAssignments=int(assignments_increment))
        if expiration_increment:
            hit = self.get_hit(hitid).data
            expiration = hit.options['expiration'] + datetime.timedelta(
                minutes=int(expiration_increment))
            self.mtc.update_expiration_for_hit(
                HITId=hitid, ExpireAt=expiration)

        return True

    @amt_service_response
    def get_hit(self, hitid):
        """Get HIT."""
        hitdata = self.mtc.get_hit(HITId=hitid)
        return self._hit_xml_to_object(hitdata['HIT'])[0]

    @amt_service_response
    def get_hit_status(self, hitid):
        """Get HIT status."""
        response = self.get_hit(hitid)
        if not response.success:
            raise response.exception
        hitdata = response.data
        return hitdata['HITStatus']

    @amt_service_response
    def get_summary(self):
        """Get summary."""
        balance = self.check_balance()
        summary = jsonify(balance=str(balance))
        return summary
