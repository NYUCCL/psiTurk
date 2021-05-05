# coding: utf-8
"""
The initial motivation for this wrapper is to abstract away
the mturk functionality from the shell
"""
from __future__ import generator_stop
from functools import wraps
from .models import Participant, Hit
from .db import db_session, init_db
from .psiturk_exceptions import *
from .psiturk_statuses import *
from .psiturk_config import PsiturkConfig
from .amt_services import MTurkServices
import sqlalchemy as sa
import datetime
import random
import string
import json
from builtins import object
from builtins import range
from builtins import str

try:
    import gnureadline as readline
except ImportError:
    import readline


class WrapperResponse(object):
    def __init__(self, status=None, message='', data: dict = None,
                 operation='', **kwargs):
        self.dict_keys = ['status', 'success', 'message', 'data', 'operation']
        self.status = status
        self.message = message
        self.data = data if data is not None else {}
        self.operation = operation
        self.mode = None
        self.sandbox = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        details = []
        if self.operation:
            details.append(('Operation', self.operation))
        if self.status:
            details.append(('Status', self.status))
        if self.message:
            details.append(('Message', self.message))
        if hasattr(self, 'exception'):
            details.append(('Exception', self.exception))

        details = ' | '.join(['{}: {}'.format(key, value)
                              for key, value in details])

        return 'Response({})'.format(details)

    def to_dict(self):
        _dict = {}
        for key in self.dict_keys:
            _dict[key] = getattr(self, key)
        return _dict


class WrapperResponseSuccess(WrapperResponse):
    def __init__(self, *args, **kwargs):
        super(WrapperResponseSuccess, self).__init__(
            *args, status='success', success=True, **kwargs)


class WrapperResponseError(WrapperResponse):
    def __init__(self, *args, **kwargs):
        super(WrapperResponseError, self).__init__(
            *args, status='error', success=False, **kwargs)

        self.dict_keys.append('exception')
        self.exception = kwargs.pop('exception', None)


def amt_services_wrapper_response(func):
    """Return amt_services_wrapper_response decorator."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            response = func(self, *args, **kwargs)
            if isinstance(response, WrapperResponse):
                return response
            if isinstance(response, dict) and 'exception' in response:
                return WrapperResponseError(
                    operation=func.__name__,
                    exception=response.pop('exception'), data=response)
            return WrapperResponseSuccess(
                operation=func.__name__,
                data=response)
        except Exception as e:
            return WrapperResponseError(operation=func.__name__, exception=e)

    return wrapper


class MTurkServicesWrapper(object):
    """class MTurkServicesWrapper."""

    _cached_dbs_services = None
    _cached_amt_services = None
    mode = None

    @property
    def amt_services(self):
        """Get amt_services."""
        if not self._cached_amt_services:
            try:
                self._cached_amt_services = MTurkServices(mode=self.mode,
                                                          config=self.config)
            except PsiturkException:
                raise
        return self._cached_amt_services

    def __init__(self, config=None, web_services=None, mode='sandbox'):
        """__init__."""
        init_db()

        if not config:
            config = PsiturkConfig()
            config.load_config()
        self.config = config

        self.set_mode(mode)

        if web_services:
            self._cached_web_services = web_services

        _ = self.amt_services  # may throw an exception. Let it throw!

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   Miscellaneous
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    @amt_services_wrapper_response
    def get_mode(self):
        """Get mode."""
        return self.mode

    @amt_services_wrapper_response
    def set_mode(self, mode):
        """set_mode."""
        if mode not in ['sandbox', 'live']:
            raise PsiturkException(f'mode not recognized: {mode}')

        self.mode = mode
        self.amt_services.set_mode(mode)

        return {'success': True}

    def random_id_generator(self, size=6, chars=string.ascii_uppercase +
                            string.digits):
        """ Generate random id numbers """
        return ''.join(random.choice(chars) for x in range(size))

    @amt_services_wrapper_response
    def amt_balance(self):
        """ Get MTurk balance """
        return self.amt_services.check_balance().data

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   worker management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    @staticmethod
    def add_bonus_info(assignment_dict):
        """ Adds DB-logged worker bonus to worker list data """
        try:
            unique_id = f"{assignment_dict['workerId']}:{assignment_dict['assignmentId']}"
            worker = Participant.query.filter(
                Participant.uniqueid == unique_id).one()
            assignment_dict['bonus'] = worker.bonus
        except sa.exc.InvalidRequestError:
            # assignment is found on mturk but not in local database.
            assignment_dict['bonus'] = 'not-found-in-study-database'
        return assignment_dict

    @amt_services_wrapper_response
    def count_workers(self, codeversion='latest', mode='live', status='completed'):
        """
        Counts the number of participants in the database who have made it through
        the experiment.
        """
        if codeversion == 'latest':
            codeversion = self.config.get(
                'Task Parameters', 'experiment_code_version')

        if status == 'completed':
            status = [3, 4, 5, 7]
        query = Participant.query
        if mode:
            query = query.filter(Participant.mode == mode)
        if codeversion:
            if not isinstance(codeversion, list):
                codeversion = [codeversion]
            query = query.filter(Participant.codeversion.in_(codeversion))
        if status:
            if not isinstance(status, list):
                status = [status]
            query = query.filter(Participant.status.in_(status))
        worker_count = Participant.count_workers(query=query, group_bys=[])
        return worker_count

    @amt_services_wrapper_response
    def count_available(self, hits=None):
        if not hits:
            hits = self.get_all_hits().data
        return sum([hit.options['number_assignments_available'] for hit in hits if
                    hit.options['status'] == 'Assignable'])

    @amt_services_wrapper_response
    def count_pending(self, hits=None):
        if not hits:
            hits = self.get_all_hits().data
        return sum([hit.options['number_assignments_pending'] for hit in hits if
                    hit.options['status'] in ['Assignable', 'Unassignable']])

    @amt_services_wrapper_response
    def count_maybe_will_complete(self, hits=None):
        maybe_will_complete_count = 0
        if not hits:
            hits = self.get_all_hits().data
        for hit in hits:
            status = hit.options['status']
            if status == 'Assignable':
                maybe_will_complete_count += hit.options['number_assignments_pending'] + \
                                             hit.options['number_assignments_available']
            elif status == 'Unassignable':
                maybe_will_complete_count += hit.options['number_assignments_pending']
        return maybe_will_complete_count

    @amt_services_wrapper_response
    def get_assignments(self, hit_ids=None, assignment_status=None, all_studies=False):
        """
        assignment_status, if set, can be one of `Submitted`, `Approved`, or `Rejected`
        """
        if not all_studies and assignment_status != 'Rejected':
            p_query = Participant.query
            p_query = p_query.filter(~Participant.uniqueid.contains('debug'))
            if assignment_status:
                mturk_status_to_local_status = {
                    'Submitted': SUBMITTED,
                    'Approved': CREDITED,
                }
                local_status = mturk_status_to_local_status[assignment_status]
                p_query = p_query.filter(Participant.status == local_status)
            if hit_ids:
                p_query = p_query.filter(Participant.hitid.in_(hit_ids))
            assignments = p_query.all()
        else:
            assignments = self.amt_services.get_assignments(
                assignment_status=assignment_status, hit_ids=hit_ids).data
            if assignments:
                assignments = [self.add_bonus_info(
                    assignment) for assignment in assignments]
        return {'assignments': assignments}

    def _filter_assignments_for_current_study(self, assignments):
        my_hitids = self._get_local_hitids()
        assignments_filtered = [
            assignment for assignment in assignments if assignment['hitId'] in my_hitids]
        return assignments_filtered

    def _try_fetch_local_credited_assignments(self, try_these):
        attempts_were_made = []
        for try_this in try_these:
            attempt_was_made = self._try_fetch_local_credited_assignment(
                try_this)
            attempts_were_made.append(attempt_was_made)
        return attempts_were_made

    def _try_fetch_local_assignment(self, try_this, with_psiturk_status=None):
        """
        Can accept either an assignment_id or the return of a mturk boto grab...
        """
        query = Participant.query.order_by(Participant.beginhit.desc())

        if with_psiturk_status:
            query = query.filter(Participant.status == with_psiturk_status)

        if isinstance(try_this, str):  # then assume that it's an assignment_id
            assignment_id = try_this
            query = query.filter(Participant.assignmentid == assignment_id)

        elif isinstance(try_this, dict):  # then assume that it's a return from mturk
            assignment = try_this
            assignment_id = assignment['assignmentId']
            query = query.filter(Participant.workerid == assignment['workerId']) \
                .filter(Participant.assignmentid == assignment_id)
        else:
            raise PsiturkException('Unrecognized `try_this` value-type: {}'.format(type(try_this)))

        local_assignment = query.first()
        if local_assignment:
            return local_assignment
        else:
            return try_this

    def _try_fetch_local_submitted_assignment(self, try_this):
        return self._try_fetch_local_assignment(try_this, with_psiturk_status=SUBMITTED)

    def _try_fetch_local_credited_assignment(self, try_this):
        return self._try_fetch_local_assignment(try_this, with_psiturk_status=CREDITED)

    @amt_services_wrapper_response
    def approve_all_assignments(self, all_studies=False):
        if all_studies:
            results = self._approve_all_assignments_from_mturk(ignore_local_not_found=all_studies)
        else:
            results = self._approve_all_assignments_from_local_records()
        return {'results': results}

    @amt_services_wrapper_response
    def approve_assignment_by_assignment_id(self, assignment_id, all_studies=False):
        tried_this = self._try_fetch_local_submitted_assignment(assignment_id)
        if isinstance(tried_this, Participant):
            result = self.approve_local_assignment(tried_this)
            return result
        else:
            if not all_studies:
                raise AssignmentIdNotFoundInLocalDBError(assignment_id=assignment_id)
            else:
                response = self.amt_services.approve_assignment(assignment_id)
                if response.success:
                    return {'success': True}
                else:
                    raise response.exception

    @amt_services_wrapper_response
    def approve_assignments_for_hit(self, hit_id, all_studies=False):
        if all_studies:
            assignments = self.amt_services.get_assignments(
                assignment_status='Submitted', hit_ids=[hit_id]).data
            results = []
            for assignment in assignments:
                results.append(
                    self.approve_mturk_assignment(assignment, ignore_local_not_found=all_studies))
        else:
            assignments = self._get_local_submitted_assignments(hit_id=hit_id)
            results = []
            for assignment in assignments:
                results.append(self.approve_local_assignment(assignment))
        return {'results': results, 'hit_id': hit_id}

    def _get_local_submitted_assignments(self, hit_id=None):
        query = Participant.query.filter(Participant.status == SUBMITTED)
        if hit_id:
            query = query.filter(Participant.hitid == hit_id)
        assignments = query.all()
        return assignments

    def _approve_all_assignments_from_local_records(self):
        assignments = self._get_local_submitted_assignments()
        results = []
        for assignment in assignments:
            results.append(self.approve_local_assignment(assignment))
        return results

    def _approve_all_assignments_from_mturk(self, ignore_local_not_found=False):
        assignments = self.amt_services.get_assignments(
            assignment_status="Submitted").data
        results = []
        for assignment in assignments:
            results.append(self.approve_mturk_assignment(assignment,
                                                         ignore_local_not_found=ignore_local_not_found))
        return results

    @amt_services_wrapper_response
    def approve_local_assignment(self, assignment):
        try:
            assignment_id = assignment.assignmentid
            response = self.amt_services.approve_assignment(assignment_id)
            if not response.success:
                raise response.exception
            assignment.status = CREDITED
            db_session.add(assignment)
            db_session.commit()
            return {'assignment_id': assignment_id}
        except Exception as e:
            return {'exception': e, 'assignment': assignment}

    @amt_services_wrapper_response
    def approve_mturk_assignment(self, assignment, ignore_local_not_found=False):
        """ Approve assignment """
        assignment_id = assignment['assignmentId']

        found_assignment = False
        parts = Participant.query. \
            filter(Participant.assignmentid == assignment_id). \
            filter(Participant.status.in_([3, 4])). \
            all()
        # Iterate through all the people who completed this assignment.
        # This should be one person, and it should match the person who
        # submitted the HIT, but that doesn't always hold.
        status_report = ''
        for part in parts:
            if part.workerid == assignment['workerId']:
                found_assignment = True
                response = self.amt_services.approve_assignment(assignment_id)
                if not response.success:
                    raise response.exception
                else:
                    part.status = CREDITED
                    db_session.add(part)
                    db_session.commit()
                break
        if not found_assignment:
            # approve assignments not found in DB if the assignment id has been specified
            if ignore_local_not_found:
                response = self.amt_services.approve_assignment(assignment_id)
                if response.success:
                    pass  # yay
                else:
                    raise response.exception
            else:
                raise WorkerIdNotFoundInLocalDBError()
        return {'assignment_id': assignment_id}

    @amt_services_wrapper_response
    def reject_assignments_for_hit(self, hit_id, all_studies=False):
        if all_studies:
            assignments = self.amt_services.get_assignments("Submitted").data
            assignment_ids = [assignment['assignmentId'] for assignment in assignments if
                              assignment['hitId'] == hit_id]
        else:
            assignments = self._get_local_submitted_assignments()
            assignment_ids = [
                assignment.assignmentid for assignment in assignments]
        response = self.reject_assignments(assignment_ids)
        return response.data

    @amt_services_wrapper_response
    def reject_assignments(self, assignment_ids, all_studies=False):
        results = []
        for assignment_id in assignment_ids:
            result = self.reject_assignment(assignment_id)
            results.append(result)
        return {'results': results}

    @amt_services_wrapper_response
    def reject_assignment(self, assignment_id, all_studies=False):
        response = self.amt_services.reject_assignment(assignment_id)
        if not response.success:
            raise response.exception
        else:
            return {'success': True}

    @amt_services_wrapper_response
    def unreject_assignments_for_hit(self, hit_id, all_studies=False):
        if all_studies:
            assignments = self.amt_services.get_assignments("Rejected").data
            assignment_ids = [assignment['assignmentId'] for assignment in assignments if
                              assignment['hitId'] == hit_id]
        else:
            assignments = self._get_local_submitted_assignments()
            assignment_ids = [
                assignment.assignmentid for assignment in assignments]
        response = self.unreject_assignments(assignment_ids)
        return response.data

    @amt_services_wrapper_response
    def unreject_assignments(self, assignment_ids, all_studies=False):
        results = []
        for assignment_id in assignment_ids:
            result = self.unreject_assignment(assignment_id)
            results.append(result)
        return {'results': results}

    @amt_services_wrapper_response
    def unreject_assignment(self, assignment_id, all_studies=False):
        """ Unreject assignment """
        response = self.amt_services.unreject_assignment(assignment_id)
        result = {}
        if not response.success:
            raise response.exception
        else:
            message = 'unrejected {}'.format(assignment_id)
            try:
                participant = Participant.query \
                    .filter(Participant.assignmentid == assignment_id) \
                    .order_by(Participant.beginhit.desc()).first()
                participant.status = CREDITED
                db_session.add(participant)
                db_session.commit()
            except:
                message = '{} but failed to update local db'.format(
                    message)
        return message

    @amt_services_wrapper_response
    def bonus_all_local_assignments(self, amount, reason, override_bonused_status=False):
        assignments = Participant.query.filter(Participant.status == CREDITED)\
            .filter(Participant.mode == self.mode)\
            .all()
        results = []
        for assignment in assignments:
            result = self.bonus_local_assignment(
                assignment, amount, reason, override_bonused_status)
            results.append(result)
        return {'results': results}

    @amt_services_wrapper_response
    def bonus_local_assignment(self, local_assignment, amount, reason,
                               override_bonused_status=False):
        assignment_id = local_assignment.assignmentid
        if local_assignment.status == BONUSED and not override_bonused_status:
            message = 'Participant with assignment_id {} already bonused, and override not set. Not bonusing.'.format(
                local_assignment.assignmentid)
            raise AssignmentAlreadyBonusedError(message=message)
        if amount == 'auto':
            if not local_assignment.bonus:
                return {'exception': NoAutoBonusAmountSetError(), 'assignment_id': assignment_id}
            amount = local_assignment.bonus

        response = self.bonus_nonlocal_assignment(
            assignment_id, amount, reason, worker_id=local_assignment.workerid)
        if response.status == 'success':
            # result['message'] = "gave bonus of ${} for assignment {}".format(str(amount), local_assignment.assignmentid)

            local_assignment.status = BONUSED
            db_session.add(local_assignment)
            db_session.commit()
        return response

    @amt_services_wrapper_response
    def bonus_assignments_for_hit(self, hit_id, amount, reason, all_studies=False,
                                  override_bonused_status=False):
        """
        Fetch assignments for local hit.
        * If all_studies, try to map them to a local_assignment.
        * If not all_studies, just pull from local db. Already a Participant.

        For each, if isinstance Participant, assignment, then send to `bonus_local_assignment`.
        Otherwise, send directly to bonus_assignment. Record the result either way.
        """
        if all_studies:
            mturk_assignments = self.amt_services.get_assignments(
                assignment_status="Approved", hit_ids=[hit_id]).data
            assignments = self._try_fetch_local_credited_assignments(
                mturk_assignments)
        else:
            assignments = Participant.query \
                .filter(Participant.status.in_([CREDITED, BONUSED])) \
                .filter(Participant.hitid == hit_id) \
                .all()
        results = self._bonus_list(
            assignments, amount, reason, override_bonused_status)
        return {'results': results}

    def _bonus_list(self, bonus_these, amount, reason, override_bonused_status=False):
        results = []
        for bonus_this in bonus_these:
            if isinstance(bonus_this, Participant):
                result = self.bonus_local_assignment(
                    bonus_this, amount, reason, override_bonused_status)
                results.append(result)
            elif isinstance(bonus_this, str):
                # assume that the str is just an assignment_id
                assignment_id = bonus_this
                result = self.bonus_nonlocal_assignment(
                    assignment_id=bonus_this, amount=amount, reason=reason, worker_id=None)
                results.append(result)
        return results

    @amt_services_wrapper_response
    def bonus_assignment_for_assignment_id(self, assignment_id, amount, reason, all_studies=False):
        tried_this = self._try_fetch_local_credited_assignment(
            assignment_id)
        if isinstance(tried_this, Participant):
            result = self.bonus_local_assignment(tried_this, amount, reason,
                                                 override_bonused_status=True)
            return result
        else:
            if not all_studies:
                raise AssignmentIdNotFoundInLocalDBError(assignment_id=assignment_id)
            else:
                response = self.bonus_nonlocal_assignment(assignment_id, amount, reason,
                                                          worker_id=None)
                if response.success:
                    return {'success': True}
                else:
                    raise response.exception

    @amt_services_wrapper_response
    def bonus_nonlocal_assignment(self, assignment_id, amount, reason, worker_id=None):
        """ Bonus assignment """

        '''
        If this is supposed to bonus a local_assignment, then call `bonus_local_assignment`,
        passing the local assignment.

        Try to match up local_assignments with whatever arguments are passed (assignment_ids, hit_id)
        before coming into this function.
        `amount` has to be greater than 0

        Otherwise, just give at least an assignment_id. Worker_id is nice if you have it, but if
        you don't, amt_services will look it up.
        '''

        result = {}
        try:
            float(amount)
        except ValueError as e:
            raise e
        if amount <= 0:
            raise BadBonusAmountError(amount, assignment_id=assignment_id)
        if not reason:
            raise BonusReasonMissingError()
        response = self.amt_services.bonus_assignment(
            assignment_id, worker_id, amount, reason)
        if not response.success:
            raise response.exception
        message = "gave bonus of ${} for assignment {}".format(
            str(amount), assignment_id)
        return {'message': message}

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   hit management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.

    @amt_services_wrapper_response
    def tally_hits(self):
        hits = self.get_active_hits(all_studies=False).data
        num_hits = 0
        if hits:
            num_hits = len(hits)
        return {'hit_tally': num_hits}

    def _get_local_hitids(self):
        return [hit.hitid for hit in Hit.query.distinct(Hit.hitid)]

    @amt_services_wrapper_response
    def get_active_hits(self, all_studies=False):
        hits = self._get_hits(all_studies)
        active_hits = self._filter_active(hits)
        return active_hits

    def _filter_active(self, hits):
        return [hit for hit in hits if not hit.options['is_expired']]

    @amt_services_wrapper_response
    def get_reviewable_hits(self, all_studies=False):
        hits = self._get_hits(all_studies)
        reviewable_hits = self._filter_reviewable(hits)
        return reviewable_hits

    def _filter_reviewable(self, hits):
        return [hit for hit in hits if hit.options['status'] in ['Reviewable', 'Reviewing']]

    @amt_services_wrapper_response
    def get_all_hits(self, all_studies=False):
        hits = self._get_hits(all_studies)
        return hits

    @amt_services_wrapper_response
    def get_hit(self, hit_id):
        hit = self.amt_services.get_hit(hit_id).data
        return hit

    def _get_hits(self, all_studies=False):
        # get all hits from amt
        # then filter to just the ones that have an id that appears in the local Hit table
        response = self.amt_services.get_all_hits()
        if not response.success:
            raise response.exception
        hits = response.data

        my_hitids = self._get_local_hitids()
        if not all_studies:
            hits = [hit for hit in hits if hit.options['hitid'] in my_hitids]
        return hits

    @amt_services_wrapper_response
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

        response = self.amt_services.extend_hit(hit_id, assignments_increment=assignments,
                                                expiration_increment=minutes)
        if not response.success:
            raise response.exception

        return {'success': True}

    @amt_services_wrapper_response
    def delete_all_hits(self, all_studies=False):
        """
        Deletes all reviewable hits
        """
        response = self.get_all_hits(all_studies=all_studies)
        if not response.success:
            raise response.exception
        hits = response.data
        hit_ids = [hit.options['hitid'] for hit in hits if
                   hit.options['status'] == "Reviewable" and
                   hit.options['number_submissions_needing_action'] == 0]
        results = []
        for hit_id in hit_ids:
            _result = self.delete_hit(hit_id)
            results.append(_result)
        return {'results': results}

    @amt_services_wrapper_response
    def delete_hit(self, hit_id):
        """
        Deletes a single hit if it is reviewable
        """
        # Check that the HIT is reviewable

        response = self.amt_services.delete_hit(hit_id)
        # self.web_services.delete_ad(hit)  # also delete the ad
        if not response.success:
            return {'exception': response.exception, 'hit_id': hit_id}
        else:
            success_message = f"deleted {self.mode} HIT {hit_id}"
            return {'hit_id': hit_id, 'success': True, 'message': success_message}

    @amt_services_wrapper_response
    def expire_hit(self, hit_id):
        response = self.amt_services.expire_hit(hit_id)
        if not response.success:
            raise AmtServicesWrapperError(
                'Error expiring hit {}'.format(hit_id)) from response.exception
        else:
            return {'hit_id': hit_id, 'success': True}

    @amt_services_wrapper_response
    def expire_all_hits(self):
        hits_data = self.get_active_hits().data
        hit_ids = [hit.options['hitid'] for hit in hits_data]
        results = []
        for hit_id in hit_ids:
            results.append(self.expire_hit(hit_id))
        return {'results': results}

    @amt_services_wrapper_response
    def create_hit(self, num_workers, reward, duration, require_qualification_ids=None,
                   block_qualification_ids=None, **kwargs):
        """
        Create a HIT

        `require_qualification_ids` and `block_qualification_ids` get extended
        with any values set in the config
        """
        # backwards compatibility
        if 'whitelist_qualification_ids' in kwargs and not require_qualification_ids:
            require_qualification_ids = kwargs['whitelist_qualification_ids']
        if 'blacklist_qualification_ids' in kwargs and not block_qualification_ids:
            block_qualification_ids = kwargs['blacklist_qualification_ids']

        if require_qualification_ids is None:
            require_qualification_ids = []
        if block_qualification_ids is None:
            block_qualification_ids = []

        server_loc = str(self.config.get('Server Parameters', 'host'))

        if not self.amt_services.verify_aws_login():
            raise InvalidAWSCredentialsError()

        ad_url = self.config.get_ad_url()
        ad_url = f"{ad_url}?mode={self.mode}"
        hit_config = self._generate_hit_config(
            ad_url, num_workers, reward, duration, require_qualification_ids, block_qualification_ids)
        response = self.amt_services.create_hit(hit_config)
        if not response.success:
            raise response.exception
        else:
            hit_id = response.data['HITId']

        # stash hit id in psiturk database
        hit = Hit(hitid=hit_id)
        db_session.add(hit)
        db_session.commit()

        return {'hit_id': hit_id}

    @amt_services_wrapper_response
    def list_qualification_types(self, *args, **kwargs):
        """
        client.list_qualification_types(
            Query='string',
            MustBeRequestable=True|False,
            MustBeOwnedByCaller=True|False,
            NextToken='string',
            MaxResults=123
        )

        To just get the ones created by le user, call:

            list_qualification_types(MustBeOwnedByCaller=True)
        """
        response = self.amt_services.list_qualification_types(*args, **kwargs)
        if not response.success:
            raise response.exception
        else:
            qualification_types = response.data
            return {'qualification_types': qualification_types}

    def _generate_hit_config(self, ad_url, num_workers, reward, duration, require_qualification_ids=None, block_qualification_ids=None):
        if require_qualification_ids is None:
            require_qualification_ids = []

        if block_qualification_ids is None:
            block_qualification_ids = []

        require_quals = self.config.get('HIT Configuration', 'require_quals', fallback=None)
        if require_quals:
            require_qualification_ids.extend(require_quals.split(','))

        block_quals = self.config.get('HIT Configuration', 'block_quals', fallback=None)
        if block_quals:
            block_qualification_ids.extend(block_quals.split(','))
        
        advanced_quals_path = self.config.get('HIT Configuration', 'advanced_quals_path', fallback=None)
        advanced_qualifications = []
        if advanced_quals_path:
            with open(advanced_quals_path) as f:
                advanced_qualifications = json.load(f)
                if not isinstance(advanced_qualifications, list):
                    raise PsiturkException(message=f'JSON file "{advanced_quals_path}" must be a list of dicts')
                else:
                    for el in advanced_qualifications:
                        if not isinstance(el, dict):
                            raise PsiturkException(message=f'JSON file "{advanced_quals_path}" must be a list of dicts')

        hit_config = {
            "ad_location": ad_url,
            "approve_requirement": self.config.getint('HIT Configuration', 'Approve_Requirement'),
            "us_only": self.config.getboolean('HIT Configuration', 'US_only'),
            "lifetime": datetime.timedelta(
                hours=self.config.getfloat('HIT Configuration', 'lifetime')),
            "max_assignments": num_workers,
            "title": self.config.get('HIT Configuration', 'title', raw=True),
            "description": self.config.get('HIT Configuration', 'description', raw=True),
            "keywords": self.config.get('HIT Configuration', 'keywords'),
            "reward": reward,
            "duration": datetime.timedelta(hours=duration),
            "number_hits_approved": self.config.getint('HIT Configuration', 'number_hits_approved'),
            "require_master_workers": self.config.getboolean('HIT Configuration',
                                                             'require_master_workers'),
            "require_qualification_ids": require_qualification_ids,
            "block_qualification_ids": block_qualification_ids,
            "advanced_qualifications": advanced_qualifications
        }
        return hit_config
