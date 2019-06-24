from builtins import range
from builtins import object
import pytest
from faker import Faker
try:
    import mock
    from mock import patch, PropertyMock
except ImportError:
    from unittest import mock
    from unittest.mock import patch, PropertyMock
import pickle
import os
import boto3
from botocore.stub import Stubber
import datetime
import ciso8601
from psiturk import psiturk_statuses
from psiturk.psiturk_exceptions import *

SANDBOX_ENDPOINT_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
LIVE_ENDPOINT_URL = 'https://mturk-requester.us-east-1.amazonaws.com'


@pytest.fixture(scope='function')
def client():
    client = boto3.client('mturk')
    return client


@pytest.fixture(scope='function')
def stubber(client):
    stubber = Stubber(client)
    stubber.activate()
    yield stubber
    stubber.deactivate()


@pytest.fixture(scope='session')
def faker():
    faker = Faker()
    return faker


class TestAmtServices(object):

    @pytest.fixture(scope='function')
    def patch_aws_services(self, client, mocker):
        import psiturk.amt_services_wrapper
        import psiturk.amt_services

        def setup_mturk_connection(self):
            self.mtc = client
            return True

        mocker.patch.object(psiturk.amt_services.MTurkServices,
                            'verify_aws_login', lambda *args, **kwargs: True)
        mocker.patch.object(psiturk.amt_services.MTurkServices,
                            'setup_mturk_connection', setup_mturk_connection)

        my_amt_services = psiturk.amt_services.MTurkServices(
            '', '', is_sandbox=True)
        mocker.patch.object(
            psiturk.amt_services_wrapper.MTurkServicesWrapper, 'amt_services', my_amt_services)

    @pytest.fixture()
    def amt_services_wrapper(self, patch_aws_services):
        import psiturk.amt_services_wrapper
        amt_services_wrapper = psiturk.amt_services_wrapper.MTurkServicesWrapper()
        return amt_services_wrapper

    @pytest.fixture()
    def stubber_prepare_create_hit(self, stubber, helpers, faker):
        def do_it(with_hit_id=None):
            if not with_hit_id:
                with_hit_id = faker.md5(raw_output=False)

            stubber.add_response(
                'create_hit_type', helpers.get_boto3_return('create_hit_type.json'))

            boto_return_create_hit_with_hit_type = helpers.get_boto3_return(
                'create_hit_with_hit_type.json')

            boto_return_create_hit_with_hit_type['HIT']['HITId'] = with_hit_id
            # used to always return a hit with id: 3XJOUITW8URHJMX7F00H20LGRIAQTX

            stubber.add_response('create_hit_with_hit_type',
                                 boto_return_create_hit_with_hit_type)
        return do_it

    @pytest.fixture()
    def create_dummy_hit(self, stubber_prepare_create_hit, amt_services_wrapper):

        def do_it(with_hit_id=None):
            stubber_prepare_create_hit(with_hit_id)
            result = amt_services_wrapper.create_hit(1, 0.01, 1)

        return do_it

    @pytest.fixture()
    def list_hits(self, stubber, helpers, amt_services_wrapper):
        '''
        Returns two hit_ids:
            3BFNCI9LYKQ2ENUY4MLKKW0NSU437W
            3XJOUITW8URHJMX7F00H20LGRIAQTX
        '''
        def do_it(hits_json=None, all_studies=False, active=False):
            if not hits_json:
                hits_json = helpers.get_boto3_return('list_hits.json')

            stubber.add_response('list_hits', hits_json)
            if active:
                results = (amt_services_wrapper.get_active_hits(
                    all_studies=all_studies)).data['active_hits']
            else:
                results = (amt_services_wrapper.get_all_hits(
                    all_studies=all_studies)).data['hits']
            return results

        return do_it

    @pytest.fixture()
    def expire_a_hit(self):
        def do_it(hits_json, index_of_hit_to_expire=0):
            expired_time = datetime.datetime.now() - datetime.timedelta(hours=10)
            hits_json['HITs'][index_of_hit_to_expire]['Expiration'] = expired_time
            return hits_json
        return do_it

    @pytest.fixture()
    def activate_a_hit(self):
        def do_it(hits_json, index_of_hit_to_be_active=1):
            active_time = datetime.datetime.now() + datetime.timedelta(hours=10)
            hits_json['HITs'][index_of_hit_to_be_active]['Expiration'] = active_time
            return hits_json
        return do_it

    def test_wrapper_hit_create(self, amt_services_wrapper, helpers, create_dummy_hit, stubber_prepare_create_hit, run_in_psiturk_shell):

        create_dummy_hit('3XJOUITW8URHJMX7F00H20LGRIAQTX')
        create_dummy_hit('ABCDUITW8URHJMX7F00H20LGRIAQTX')

        from psiturk.models import Hit
        # confirm that it's in the local db...
        assert Hit.query.get('3XJOUITW8URHJMX7F00H20LGRIAQTX') is not None
        # confirm that it's in the local db...
        assert Hit.query.get('ABCDUITW8URHJMX7F00H20LGRIAQTX') is not None

        stubber_prepare_create_hit()
        run_in_psiturk_shell('hit create 1 ye 1')

    def test_wrapper_get_all_hits(self, amt_services_wrapper, create_dummy_hit, list_hits, helpers):

        create_dummy_hit('3XJOUITW8URHJMX7F00H20LGRIAQTX')
        hits = list_hits()

        hit_ids = [hit.options['hitid'] for hit in hits]

        assert '3XJOUITW8URHJMX7F00H20LGRIAQTX' in hit_ids

    def test_wrapper_get_all_hits_all_studies(self, amt_services_wrapper, create_dummy_hit, list_hits, helpers):
        create_dummy_hit('3XJOUITW8URHJMX7F00H20LGRIAQTX')
        create_dummy_hit('3BFNCI9LYKQ2ENUY4MLKKW0NSU437W')

        from psiturk.db import db_session
        from psiturk.models import Hit
        Hit.query.filter_by(hitid='3BFNCI9LYKQ2ENUY4MLKKW0NSU437W').delete()
        db_session.commit()

        hits = list_hits(all_studies=False)
        assert '3BFNCI9LYKQ2ENUY4MLKKW0NSU437W' not in [
            hit.options['hitid'] for hit in hits]

        hits = list_hits(all_studies=True)
        assert '3BFNCI9LYKQ2ENUY4MLKKW0NSU437W' in [
            hit.options['hitid'] for hit in hits]

    def test_wrapper_get_active_hits(self, activate_a_hit, expire_a_hit, amt_services_wrapper, create_dummy_hit, list_hits, helpers):
        hits_json = helpers.get_boto3_return('list_hits.json')

        index_of_hit_to_expire = 0
        id_of_hit_to_expire = hits_json['HITs'][index_of_hit_to_expire]['HITId']

        index_of_hit_to_be_active = 1
        id_of_hit_to_be_active = hits_json['HITs'][index_of_hit_to_be_active]['HITId']

        hits_json = activate_a_hit(hits_json)
        hits_json = expire_a_hit(hits_json)

        create_dummy_hit(id_of_hit_to_expire)
        create_dummy_hit(id_of_hit_to_be_active)

        active_hits = list_hits(hits_json=hits_json,
                                all_studies=False, active=True)
        active_hit_ids = [hit.options['hitid'] for hit in active_hits]

        assert id_of_hit_to_expire not in active_hit_ids
        assert id_of_hit_to_be_active in active_hit_ids

    def test_wrapper_extend_hit(self, stubber, helpers, amt_services_wrapper):
        # uh, just test that boto doesn't throw an error...
        stubber.add_response('create_additional_assignments_for_hit', {})
        amt_services_wrapper.extend_hit(
            '3BFNCI9LYKQ2ENUY4MLKKW0NSU437W', assignments=10)

        stubber.add_response(
            'get_hit', helpers.get_boto3_return('get_hit.json'))
        amt_services_wrapper.extend_hit(
            '3BFNCI9LYKQ2ENUY4MLKKW0NSU437W', minutes=10)

        stubber.add_response('create_additional_assignments_for_hit', {})
        stubber.add_response(
            'get_hit', helpers.get_boto3_return('get_hit.json'))
        amt_services_wrapper.extend_hit(
            '3BFNCI9LYKQ2ENUY4MLKKW0NSU437W', assignments=10, minutes=10)

    def test_wrapper_expire_hit(self, stubber, amt_services_wrapper, helpers):
        # a list of ids...
        hit_ids = ['123', 'abc']
        for hit_id in hit_ids:
            stubber.add_response('update_expiration_for_hit', {})
            amt_services_wrapper.expire_hit(hit_id)

    def test_wrapper_expire_all_hits(self, stubber, amt_services_wrapper, helpers):
        # expire all...
        # This would ideally test that only hits for the current study are being expired...
        hits_json = helpers.get_boto3_return('list_hits.json')
        stubber.add_response('list_hits', hits_json)

        for i in hits_json['HITs']:
            stubber.add_response('update_expiration_for_hit', {})
        amt_services_wrapper.expire_all_hits()
        pass

    def test_wrapper_delete_hit(self, stubber, amt_services_wrapper):
        hit_ids = ['123', 'abc']
        for hit_id in hit_ids:
            stubber.add_response('delete_hit', {})
            amt_services_wrapper.delete_hit(hit_id)

    def test_wrapper_delete_all_hits(self, stubber, amt_services_wrapper, helpers):
        hits_json = helpers.get_boto3_return('list_hits.json')
        stubber.add_response('list_hits', hits_json)

        for hit in hits_json['HITs']:
            stubber.add_response('delete_hit', {})
        amt_services_wrapper.delete_all_hits()

    def test_wrapper_tally_hits(self, stubber, activate_a_hit, create_dummy_hit, helpers, amt_services_wrapper):
        hits_json = helpers.get_boto3_return('list_hits.json')
        hits_json = activate_a_hit(hits_json)
        hit_ids = [hit['HITId'] for hit in hits_json['HITs']]
        for hit_id in hit_ids:
            create_dummy_hit(hit_id)
        stubber.add_response('list_hits', hits_json)
        count = amt_services_wrapper.tally_hits()

    @pytest.fixture()
    def get_assignment_json(self, helpers):
        def do_it():
            assignment = helpers.get_boto3_return('get_assignment.json')
            return assignment
        return do_it

    @pytest.fixture()
    def get_submitted_assignment_json(self, get_assignment_json):
        def do_it(assignment=None):
            if not assignment:
                assignment = get_assignment_json()
            assignment['Assignment']['AssignmentStatus'] = 'Submitted'
            return assignment
        return do_it

    @pytest.fixture()
    def get_rejected_assignment_json(self, get_assignment_json):
        def do_it(assignment=None):
            if not assignment:
                assignment = get_assignment_json()
            assignment['Assignment']['AssignmentStatus'] = 'Rejected'
            return assignment
        return do_it

    @pytest.fixture()
    def get_approved_assignment_json(self, get_assignment_json):
        def do_it(assignment=None):
            if not assignment:
                assignment = get_assignment_json()
            assignment['Assignment']['AssignmentStatus'] = 'Approved'
            return assignment
        return do_it

    def test_wrapper_get_assignments_for_hits(self, stubber, amt_services_wrapper, helpers, create_dummy_hit, get_submitted_assignment_json):
        assignments_data = helpers.get_boto3_return(
            'list_assignments_for_hit.json')
        hit_ids = list(set([assignment['HITId']
                            for assignment in assignments_data['Assignments']]))
        [create_dummy_hit(hit_id) for hit_id in hit_ids]
        [stubber.add_response('list_assignments_for_hit',
                              assignments_data) for hit_id in hit_ids]
        assignments = amt_services_wrapper.get_assignments(hit_ids=hit_ids)

    @pytest.fixture()
    def create_dummy_assignment(self, faker):
        from psiturk.db import db_session, init_db
        from psiturk.models import Participant

        def do_it(participant_attributes={}):

            participant_attribute_defaults = {
                'workerid': faker.md5(raw_output=False),
                'hitid': faker.md5(raw_output=False),
                'assignmentid': faker.md5(raw_output=False),
            }

            participant_attributes = dict(list(
                participant_attribute_defaults.items()) + list(participant_attributes.items()))
            init_db()

            participant = Participant(**participant_attributes)
            db_session.add(participant)
            db_session.commit()

            return participant

        return do_it

    def test_wrapper_approve_all_assignments(self, stubber, activate_a_hit, helpers, create_dummy_assignment, create_dummy_hit, amt_services_wrapper):
        hits_json = helpers.get_boto3_return('list_hits.json')
        index_of_hit_to_be_active = 0
        hits_json = activate_a_hit(
            hits_json, index_of_hit_to_be_active=index_of_hit_to_be_active)

        active_hit_id = hits_json['HITs'][index_of_hit_to_be_active]['HITId']

        assignment_1 = create_dummy_assignment(
            {'hitid': active_hit_id, 'status': psiturk_statuses.COMPLETED})
        # do not create dummy hit

        assignment_2 = create_dummy_assignment(
            {'hitid': active_hit_id, 'status': psiturk_statuses.COMPLETED})
        # create_dummy_hit(assignment_2.hitid)

        assignments = [assignment_1, assignment_2]

        [stubber.add_response('approve_assignment', {})
         for assignment in assignments]
        results = (amt_services_wrapper.approve_all_assignments(
            all_studies=False)).data['results']
        assert len(
            [result for result in results if result.status == 'success']) == 2

        stubber.add_response('list_hits', hits_json)

        assignments_data = helpers.get_boto3_return(
            'list_assignments_for_hit.json')

        number_approved = 0

        for i in range(len(hits_json['HITs'])):
            stubber.add_response('list_assignments_for_hit', assignments_data)

        for i in range(len(hits_json['HITs'])):
            for j in range(len(assignments_data['Assignments'])):
                stubber.add_response('approve_assignment', {})
                number_approved += 1

        results = (amt_services_wrapper.approve_all_assignments(
            all_studies=True)).data['results']
        assert len([result for result in results if result.status ==
                    'success']) == number_approved

    def test_wrapper_reject_unreject_assignments(self, stubber, amt_services_wrapper, create_dummy_assignment, helpers):

        # reject all for a given hit, local only...
        assignment_1 = create_dummy_assignment({'hitid': 'abc', 'status': 4})
        stubber.add_response('reject_assignment', {})
        results = (amt_services_wrapper.reject_assignments_for_hit(
            'abc', all_studies=False)).data['results']
        assert len(results) == 1

        hits_data = helpers.get_boto3_return('list_hits.json')
        assignments_data = helpers.get_boto3_return(
            'list_assignments_for_hit.json')

        def prep_list_hits():
            stubber.add_response('list_hits', hits_data)
            for i in range(len(hits_data['HITs'])):
                stubber.add_response(
                    'list_assignments_for_hit', assignments_data)

        # reject all for a given hit,, all studies...
        prep_list_hits()

        def prep_operation_all_for_hit(operation=None):
            number_to_be_operated_on = 0
            for i in range(len(hits_data['HITs'])):
                for j in range(len(assignments_data['Assignments'])):
                    stubber.add_response(operation, {})
                    number_to_be_operated_on += 1
            return number_to_be_operated_on

        number_to_be_approved = prep_operation_all_for_hit('reject_assignment')

        results = (amt_services_wrapper.reject_assignments_for_hit(
            'abc', all_studies=True)).data['results']
        assert len(results) == number_to_be_approved
        for result in results:
            assert result.status == 'success'

        # reject one at a time
        reject_these = ['abc', '123']
        [stubber.add_response('reject_assignment', {}) for i in reject_these]
        result = amt_services_wrapper.reject_assignments(reject_these)

        # unreject one at a time
        [stubber.add_response('approve_assignment', {}) for i in reject_these]
        results = (amt_services_wrapper.unreject_assignments(
            reject_these)).data['results']
        assert len(results) == len(reject_these)

        # unreject all for a given hit for local study only
        results = (amt_services_wrapper.unreject_assignments_for_hit(
            ['abc'], all_studies=False)).data['results']
        assert len(results) == 1

        # unreject all for a given hit across all studies
        prep_list_hits()
        number_to_be_unrejected = prep_operation_all_for_hit(
            'approve_assignment')
        results = (amt_services_wrapper.unreject_assignments_for_hit(
            'abc', all_studies=True)).data['results']
        assert len(results) == number_to_be_unrejected
        for result in results:
            assert result.status == 'success'

    def test_wrapper_bonus_assignment(self, create_dummy_assignment, amt_services_wrapper, stubber):

        from psiturk.db import db_session

        # ## filters
        # with hit_id
        hit_id = '123'
        # amount = 0.01
        amount = 'auto'
        reason = 'yee'
        override_bonused_status = False

        def edit_assignment(assignment, new_config):
            for k, v in list(new_config.items()):
                setattr(assignment, k, v)
            db_session.add(assignment)
            db_session.commit()

        assignment_1 = create_dummy_assignment({'hitid': hit_id})
        edit_assignment(assignment_1, {'status': psiturk_statuses.BONUSED})
        results = (amt_services_wrapper.bonus_assignments_for_hit(
            '123', amount, reason, override_bonused_status)).data['results']
        assert isinstance(results[0].data['exception'],
                          AssignmentAlreadyBonusedError)

        edit_assignment(
            assignment_1, {'status': psiturk_statuses.CREDITED, 'bonus': 0.00})
        results = (amt_services_wrapper.bonus_assignments_for_hit(
            '123', amount, reason)).data['results']
        assert isinstance(results[0].data['exception'], BadBonusAmountError)

        stubber.add_response('send_bonus', {})
        edit_assignment(
            assignment_1, {'status': psiturk_statuses.BONUSED, 'bonus': 0.50})
        results = (amt_services_wrapper.bonus_assignments_for_hit(
            '123', amount, reason, override_bonused_status=True)).data['results']
        assert results[0].status == 'success'

        assignment_id = 'abc'
        amount = 0.50
        reason = 'yee'
        assignment_2 = create_dummy_assignment({
            'hitid': hit_id,
            'assignmentid': assignment_id,
            'status': psiturk_statuses.CREDITED
        })
        stubber.add_response('send_bonus', {})
        stubber.add_response('send_bonus', {})
        results = (amt_services_wrapper.bonus_assignments_for_assignment_ids(
            [assignment_id, '123'], amount, reason)).data['results']
        assert len(
            [result for result in results if result.status == 'success']) == 1

        for assignment in [assignment_1, assignment_2]:
            edit_assignment(assignment, {
                            'status': psiturk_statuses.CREDITED, 'mode': 'sandbox', 'bonus': 0.50})
            stubber.add_response('send_bonus', {})
        amount = 'auto'
        reason = 'yee'
        results = (amt_services_wrapper.bonus_all_local_assignments(
            amount, reason)).data['results']
        assert len(
            [result for result in results if result.status == 'success']) == 2

        for i, assignment in enumerate([assignment_1, assignment_2]):
            edit_assignment(assignment, {
                'assignmentid': '{}bc'.format(i+1),
                'status': psiturk_statuses.CREDITED,
                'mode': 'sandbox',
                'bonus': 0.50
            })
            stubber.add_response('send_bonus', {})
        results = (amt_services_wrapper.bonus_assignments_for_assignment_ids(
            ['1bc', '2bc'], amount=amount, reason='')).data['results']
        for result in results:
            assert isinstance(
                result.data['exception'], BonusReasonMissingError)
