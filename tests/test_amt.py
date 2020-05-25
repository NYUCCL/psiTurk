from builtins import range
from builtins import object
import pytest
from unittest import mock
from unittest.mock import patch, PropertyMock
import pickle
import os
import boto3
from botocore.stub import ANY
from importlib import reload


import datetime
import ciso8601
from psiturk import psiturk_statuses
from psiturk.psiturk_exceptions import *

SANDBOX_ENDPOINT_URL = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
LIVE_ENDPOINT_URL = 'https://mturk-requester.us-east-1.amazonaws.com'

# pytest_plugins = ['pytest_profiling']

# TODO: make it easier to import these quals which psiturk adds
psiturk_standard_quals = [
    {'Comparator': 'GreaterThanOrEqualTo',
        'IntegerValues': [95],
        'QualificationTypeId': '000000000000000000L0'},
    {'Comparator': 'GreaterThanOrEqualTo',
        'IntegerValues': [0],
        'QualificationTypeId': '00000000000000000040'},
    {'Comparator': 'EqualTo',
        'LocaleValues': [{'Country': 'US'}],
        'QualificationTypeId': '00000000000000000071'}
]

class TestAmtServices(object):

    def test_wrapper_hit_create(self, amt_services_wrapper, helpers, create_dummy_hit, stubber_prepare_create_hit):

        create_dummy_hit('3XJOUITW8URHJMX7F00H20LGRIAQTX')
        create_dummy_hit('ABCDUITW8URHJMX7F00H20LGRIAQTX')

        from psiturk.models import Hit
        # confirm that it's in the local db...
        assert Hit.query.get('3XJOUITW8URHJMX7F00H20LGRIAQTX') is not None
        # confirm that it's in the local db...
        assert Hit.query.get('ABCDUITW8URHJMX7F00H20LGRIAQTX') is not None


    def test_wrapper_hit_create_with_whitelist_qualification(self, stubber, amt_services_wrapper):
        '''
        makes sure that whitelist_qualid finds its way into the qual list as EXISTS
        '''

        WHITELIST_QUAL_ID = 'WHITELISTQUAL_123'
        quals = psiturk_standard_quals + [
            {
                'Comparator': 'Exists',
                'QualificationTypeId': WHITELIST_QUAL_ID
            }]

        stubber.add_response('create_hit_type', {'HITTypeId': 'HITTypeId_123'}, {
            'Title': ANY,
            'Description': ANY,
            'Reward': ANY,
            'AssignmentDurationInSeconds': ANY,
            'Keywords': ANY,
            'QualificationRequirements': quals
        })
        stubber.add_response('create_hit_with_hit_type', {
            'HIT': {
                'HITId': 'ABC123'
            }
        })
        # import pytest; pytest.set_trace()
        response = amt_services_wrapper.create_hit(1, 0.01, 1, whitelist_qualification_ids=[WHITELIST_QUAL_ID])
        if not response.success:
            raise response.exception

    def test_wrapper_hit_create_with_multiple_whitelist_qualifications(self, stubber, amt_services_wrapper):
        '''
        makes sure that whitelist_qualid finds its way into the qual list as EXISTS
        '''

        WHITELIST_QUAL_IDS = 'WHITELISTQUAL_123, WHITELISTQUAL_123'
        quals = psiturk_standard_quals + [
            {
                'Comparator': 'Exists',
                'QualificationTypeId': qual_id
            } for qual_id in WHITELIST_QUAL_IDS]

        stubber.add_response('create_hit_type', {'HITTypeId': 'HITTypeId_123'}, {
            'Title': ANY,
            'Description': ANY,
            'Reward': ANY,
            'AssignmentDurationInSeconds': ANY,
            'Keywords': ANY,
            'QualificationRequirements': quals
        })
        stubber.add_response('create_hit_with_hit_type', {
            'HIT': {
                'HITId': 'ABC123'
            }
        })
        # import pytest; pytest.set_trace()
        response = amt_services_wrapper.create_hit(1, 0.01, 1, whitelist_qualification_ids=WHITELIST_QUAL_IDS)
        if not response.success:
            raise response.exception

    def test_wrapper_generate_hit_config_reads_qualifications_from_config_file(self, edit_config_file, stubber, amt_services_wrapper):
        '''
        makes sure that whitelist_qualid finds its way into the qual list as EXISTS
        '''

        whitelist_config_file_qual_ids = ['whitelist_config_123','whitelist_config_456']
        blacklist_config_file_qual_ids = ['blacklist_config_123','blacklist_config_456']

        edit_config_file('require_quals =','require_quals = {}'.format(','.join(whitelist_config_file_qual_ids)))
        edit_config_file('block_quals =','block_quals = {}'.format(','.join(blacklist_config_file_qual_ids)))

        whitelist_qualification_ids_passed = ['white_passed_123', 'white_passed_456']
        blacklist_qualification_ids_passed = ['black_passed_123', 'black_passed_456']

        # need to reset the amt_services_wrapper config after editing config file above.
        from psiturk.psiturk_config import PsiturkConfig
        config = PsiturkConfig()
        config.load_config()
        amt_services_wrapper.config = config

        hit_config = amt_services_wrapper._generate_hit_config(
            'loc_123', 1, '1.00', 1,
            whitelist_qualification_ids=whitelist_qualification_ids_passed,
            blacklist_qualification_ids=blacklist_qualification_ids_passed)

        whitelist_qual_ids = whitelist_config_file_qual_ids + whitelist_qualification_ids_passed
        blacklist_qual_ids = blacklist_config_file_qual_ids + blacklist_qualification_ids_passed

        for qual in whitelist_qual_ids:
            assert qual in hit_config['whitelist_qualification_ids']

        for qual in blacklist_qual_ids:
            assert qual in hit_config['blacklist_qualification_ids']





    def test_wrapper_hit_create_with_blacklist_qualification(self, stubber, amt_services_wrapper):
        '''
        makes sure that whitelist_qualid finds its way into the qual list as EXISTS
        '''

        BLACKLIST_QUAL_ID = 'QUAL_123'
        quals = psiturk_standard_quals + [
            {
                'Comparator': 'DoesNotExist',
                'QualificationTypeId': BLACKLIST_QUAL_ID
            }]

        stubber.add_response('create_hit_type', {'HITTypeId': 'HITTypeId_123'}, {
            'Title': ANY,
            'Description': ANY,
            'Reward': ANY,
            'AssignmentDurationInSeconds': ANY,
            'Keywords': ANY,
            'QualificationRequirements': quals
        })
        stubber.add_response('create_hit_with_hit_type', {
            'HIT': {
                'HITId': 'ABC123'
            }
        })
        # import pytest; pytest.set_trace()
        response = amt_services_wrapper.create_hit(1, 0.01, 1, blacklist_qualification_ids=[BLACKLIST_QUAL_ID])
        if not response.success:
            raise response.exception

    def test_wrapper_hit_create_with_whitelist_and_blacklist_qualifications(self, stubber, amt_services_wrapper):
        '''
        makes sure that whitelist_qualid finds its way into the qual list as EXISTS
        '''

        WHITELIST_QUAL_ID = 'WHITELISTQUAL_123'
        BLACKLIST_QUAL_ID = 'BLACKLISTQUAL_123'
        quals = psiturk_standard_quals + [
            {
                'Comparator': 'Exists',
                'QualificationTypeId': WHITELIST_QUAL_ID
            },
            {
                'Comparator': 'DoesNotExist',
                'QualificationTypeId': BLACKLIST_QUAL_ID
            }]

        stubber.add_response('create_hit_type', {'HITTypeId': 'HITTypeId_123'}, {
            'Title': ANY,
            'Description': ANY,
            'Reward': ANY,
            'AssignmentDurationInSeconds': ANY,
            'Keywords': ANY,
            'QualificationRequirements': quals
        })
        stubber.add_response('create_hit_with_hit_type', {
            'HIT': {
                'HITId': 'ABC123'
            }
        })
        # import pytest; pytest.set_trace()
        response = amt_services_wrapper.create_hit(1, 0.01, 1, whitelist_qualification_ids=[WHITELIST_QUAL_ID], blacklist_qualification_ids=[BLACKLIST_QUAL_ID])
        if not response.success:
            raise response.exception

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
        response = amt_services_wrapper.extend_hit(
            '3BFNCI9LYKQ2ENUY4MLKKW0NSU437W', assignments=10)
        if not response.success:
            raise response.exception

        stubber.add_response(
            'get_hit', helpers.get_boto3_return('get_hit.json'))
        stubber.add_response('update_expiration_for_hit', {})
        response = amt_services_wrapper.extend_hit(
            '3BFNCI9LYKQ2ENUY4MLKKW0NSU437W', minutes=10)
        if not response.success:
            raise response.exception

        stubber.add_response('create_additional_assignments_for_hit', {})
        stubber.add_response(
            'get_hit', helpers.get_boto3_return('get_hit.json'))
        stubber.add_response('update_expiration_for_hit', {})
        response = amt_services_wrapper.extend_hit(
            '3BFNCI9LYKQ2ENUY4MLKKW0NSU437W', assignments=10, minutes=10)
        if not response.success:
            raise response.exception

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

    def test_wrapper_approve_single_assignment(self, stubber, create_dummy_assignment, amt_services_wrapper):
        create_dummy_assignment({
                'hitid': '123',
                'beginhit': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=-2),
                'assignmentid': 'ABC',
                'status': psiturk_statuses.SUBMITTED,
                'mode': 'sandbox'})
        create_dummy_assignment({'hitid': '123',
            'beginhit': datetime.datetime.now(datetime.timezone.utc),
            'assignmentid': 'DEF',
            'status': psiturk_statuses.SUBMITTED,
            'mode': 'sandbox'
        })
        stubber.add_response('approve_assignment', {}, {'AssignmentId':'ABC', 'OverrideRejection': False})
        response = amt_services_wrapper.approve_assignment_by_assignment_id('ABC')
        assert response.success

    def test_wrapper_approve_all_assignments(self, stubber, activate_a_hit, helpers, create_dummy_assignment, create_dummy_hit, amt_services_wrapper):
        hits_json = helpers.get_boto3_return('list_hits.json')
        index_of_hit_to_be_active = 0
        hits_json = activate_a_hit(
            hits_json, index_of_hit_to_be_active=index_of_hit_to_be_active)

        active_hit_id = hits_json['HITs'][index_of_hit_to_be_active]['HITId']

        assignment_1 = create_dummy_assignment(
            {'hitid': active_hit_id, 'status': psiturk_statuses.SUBMITTED})
        # do not create dummy hit

        assignment_2 = create_dummy_assignment(
            {'hitid': active_hit_id, 'status': psiturk_statuses.SUBMITTED})
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

    def test_wrapper_approve_all_for_hit(self, stubber, activate_a_hit, helpers, create_dummy_assignment, create_dummy_hit, amt_services_wrapper):
        hits_json = helpers.get_boto3_return('list_hits.json')
        [activate_a_hit(hits_json, i) for (i, hit) in enumerate(hits_json['HITs'])]

        first_hitid = hits_json['HITs'][0]['HITId']
        second_hitid = hits_json['HITs'][1]['HITId']

        # set two to be for the first hit
        mode = 'sandbox'
        a_1 = create_dummy_assignment(
            {'hitid': first_hitid, 'status': psiturk_statuses.SUBMITTED})
        a_2 = create_dummy_assignment(
            {'hitid': first_hitid, 'status': psiturk_statuses.SUBMITTED})
        a_3 = create_dummy_assignment(
            {'hitid': second_hitid, 'status': psiturk_statuses.SUBMITTED})


        #set up stubber to expect two 'approve_hit' calls
        stubber.add_response('approve_assignment', {})
        stubber.add_response('approve_assignment', {})

        response = amt_services_wrapper.approve_assignments_for_hit(first_hitid)
        for r in response.data['results']:
            assert r.success
        assert len(response.data['results']) == 2

    def test_wrapper_reject_unreject_assignments(self, stubber, amt_services_wrapper, create_dummy_assignment, helpers):

        # reject all for a given hit, local only...
        assignment_1 = create_dummy_assignment({'hitid': 'abc', 'status': 4, 'mode': 'sandbox'})
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
        assignment_2 = create_dummy_assignment({'hitid': hit_id})
        edit_assignment(assignment_1, {'status': psiturk_statuses.BONUSED})
        edit_assignment(assignment_2, {'status': psiturk_statuses.BONUSED})
        results = amt_services_wrapper.bonus_assignments_for_hit(
            hit_id, amount, reason, override_bonused_status)
        results = results.data['results']
        assert isinstance(results[0].exception,
                          AssignmentAlreadyBonusedError)

        edit_assignment(
            assignment_1, {'status': psiturk_statuses.CREDITED, 'bonus': 0.00})
        results = (amt_services_wrapper.bonus_assignments_for_hit(
            '123', amount, reason)).data['results']
        assert isinstance(results[0].exception, (BadBonusAmountError, NoAutoBonusAmountSetError))

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
        results = [amt_services_wrapper.bonus_assignment_for_assignment_id(
            assignment_id, amount, reason) for assignment_id in [assignment_id, '123']]
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
        results = [amt_services_wrapper.bonus_assignment_for_assignment_id(
            assignment_id, amount=amount, reason='') for assignment_id in ['1bc', '2bc']]
        for result in results:
            assert isinstance(
                result.exception, BonusReasonMissingError)

    @pytest.mark.skip(reason='todo')
    def test_wrapper_list_qualification_types(self):
        pass
