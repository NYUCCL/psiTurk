from __future__ import generator_stop
from flask import Blueprint, jsonify, make_response, request, session, current_app as app, send_file
from flask.json import JSONEncoder
from flask_restful import Api, Resource
from psiturk.dashboard import login_required
from psiturk.services_manager import SESSION_SERVICES_MANAGER_MODE_KEY, \
    psiturk_services_manager as services_manager
from psiturk.models import Participant, Campaign, Hit
from psiturk.experiment import app
from psiturk.psiturk_exceptions import *
from psiturk.amt_services_wrapper import WrapperResponse
from psiturk.amt_services import MTurkHIT
from psiturk.db import db_session
from psiturk.models import Base as DBModel
from apscheduler.job import Job
from apscheduler.triggers.base import BaseTrigger
import datetime
import pytz
import json
from io import BytesIO
import zipfile
from pytz.tzinfo import BaseTzInfo

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

class CustomApi(Api):
    """
    For custom error handling
    """
    def handle_error(self, exception):

        message = exception.message if (hasattr(exception, 'message') and
                                        exception.message) else str(exception)
        return jsonify({
            'exception': type(exception).__name__,
            'message': message
        }), 400

api = CustomApi()


@api_blueprint.errorhandler(Exception)
def handle_exception(exception):
    message = exception.message if (hasattr(exception, 'message') and
                                    exception.message) else str(exception)
    # raise exception
    return jsonify({
        'exception': type(exception).__name__,
        'message': message
    }), 400


class PsiturkJSONEncoder(JSONEncoder):  # flask's jsonencoder class
    def default(self, obj):
        if isinstance(obj, (PsiturkException, WrapperResponse)):
            return obj.to_dict()

        if isinstance(obj, Exception):
            return {
                'exception': type(obj).__name__,
                'message': str(obj)
            }

        if isinstance(obj, datetime.timedelta):
            return str(obj)

        if isinstance(obj, MTurkHIT):
            return obj.__dict__

        if isinstance(obj, DBModel):
            return obj.object_as_dict()

        if isinstance(obj, (Job, BaseTrigger)):
            return obj.__getstate__()

        if isinstance(obj, BaseTzInfo):
            return str(obj)

        return JSONEncoder.default(self, obj)


api_blueprint.json_encoder = PsiturkJSONEncoder


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(jsonify(data), code)
    resp.headers.extend(headers or {})
    return resp


@api_blueprint.before_request
@login_required
def before_request():
    pass

class AssignmentsAction(Resource):
    def post(self, action=None):
        data = request.json
        if action == 'approve_all':
            response = services_manager.amt_services_wrapper.approve_all_assignments()
            if not response.success:
                raise response.exception
            return response.data['results']
        elif action == 'bonus_all':
            if 'reason' not in data or not data['reason']:
                raise APIException(message='bonus reason is missing!')

            response = services_manager.amt_services_wrapper.bonus_all_local_assignments(
                amount='auto', reason=data['reason'])
            if not response.success:
                raise response.exception
            return response.data['results'], 201
        else:
            raise APIException(message='action `{}` not recognized!'.format(action))


class Hits(Resource):
    def patch(self, hit_id):
        data = request.json
        if 'is_expired' in data and data['is_expired']:
            response = services_manager.amt_services_wrapper.expire_hit(hit_id)
            if not response.success:
                raise response.exception
        if 'action' in data:
            if data['action'] == 'approve_all':
                response = services_manager.amt_services_wrapper.approve_assignments_for_hit(hit_id)
                if not response.success:
                    raise response.exception
        return services_manager.amt_services_wrapper.get_hit(hit_id).data, 201

    def delete(self, hit_id):
        response = services_manager.amt_services_wrapper.delete_hit(hit_id)
        if not response.success:
            raise response.exception
        return '', 204

class Campaigns(Resource):
    def get(self, campaign_id):
        campaign = Campaign.query.filter(Campaign.id == campaign_id).one()
        return campaign

    def patch(self, campaign_id):
        campaign = Campaign.query.filter(Campaign.id == campaign_id).one()
        data = request.json
        did_something = False
        if 'is_active' in data and campaign.is_active and not data['is_active']:
            campaign.end()
        elif 'goal' in data:
            goal = data['goal']

            completed_count = Participant.count_completed(
                codeversion=services_manager.codeversion,
                mode=services_manager.mode)

            assert goal > completed_count, 'Goal {} must be greater than current completed {}.'.format(
                goal, completed_count)

            campaign.set_new_goal(goal)

        return campaign

class Tasks(Resource):
    def delete(self, task_id):
        app.apscheduler.remove_job(str(task_id))
        return '', 204


class TaskList(Resource):
    def get(self):
        tasks = app.apscheduler.get_jobs()
        return tasks

    def post(self):
        data = request.json
        mode = services_manager.mode
        if data['name'] == 'approve_all':
            # check if we already have an 'approve_all'
            if app.apscheduler.get_job('approve_all'):
                raise APIException(message='`approve_all` job already exists')

            from psiturk.tasks import do_approve_all

            job = app.apscheduler.add_job(
                id='approve_all',
                args=[mode],
                func=do_approve_all,
                trigger='interval',
                minutes=max(int(float(data['interval']) * 60), 30),
                next_run_time=datetime.datetime.now(pytz.utc)
            )
            return job, 201

        raise APIException(message='task name `{}` not recognized!'.format(data['name']))

# -------------------------- DASHBOARD v2 RESOURCES -------------------------- #

class WorkersList(Resource):

    # POST: Returns the full list of workers from the local database
    #  codeversion: the codeversion for which to retrieve workers for
    def post(self):
        worker_ids = request.json['worker_ids']
        codeversion = request.json['codeversion']
        query = Participant.query
        if len(worker_ids) > 0:
            query = query.filter(Participant.workerid.in_(worker_ids))
        if codeversion:
            query = query.filter(Participant.codeversion == codeversion)
        _return = query.all()
        return [p.toAPIData() for p in _return]

class CampaignsList(Resource):

    # POST: Returns a list of campaigns from the local database
    #  codeversion: the codeversion for which to retrieve campaigns for
    def post(self):
        codeversion = request.json['codeversion']
        query = Campaign.query.filter(Campaign.mode == services_manager.mode)
        if codeversion:
            query = query.filter(Campaign.codeversion == services_manager.codeversion)
        _return = query.all()
        return _return

class CampaignsAction(Resource):

    # POST: Actions for campaigns
    def post(self, action=None):

        # ACTION: Create a campaign
        #  goal: the target number of participants to hit
        #  minutes_between_rounds: how many minutes to wait between rounds
        #  assignments_between_rounds: how many assignments per round (9)
        #  hit_reward: the reward for the HIT
        #  hit_duration_hours: how long the HIT lasts before a user is unable to submit
        if action == 'create':
            goal = request.json['goal']
            minutes_between_rounds = request.json['minutes_between_rounds']
            assignments_per_round = request.json['assignments_per_round']
            hit_reward = request.json['hit_reward']
            hit_duration_hours = request.json['hit_duration_hours']
            # check if one already exists that is active...
            if Campaign.active_campaign_exists():
                raise APIException(
                    message='Active campaign already exists. Cancel that campaign first in order to create a new one.')
            codeversion = services_manager.codeversion
            mode = services_manager.mode
            _return = Campaign.launch_new_campaign(
                codeversion=codeversion, 
                mode=mode, 
                goal=goal, 
                minutes_between_rounds=minutes_between_rounds,
                assignments_per_round=assignments_per_round, 
                hit_reward=hit_reward,
                hit_duration_hours=hit_duration_hours)
            return _return, 201



class ServicesManager(Resource):

    # POST: Set the services manager mode
    #  mode: live or sandbox, the desired mode
    def post(self):
        mode = request.json['mode']
        services_manager.mode = mode
        session[SESSION_SERVICES_MANAGER_MODE_KEY] = mode
    
    # GET: Retrieves information from the services manager
    def get(self):
        _return = {
            'mode': 'unavailable',
            'codeversion': 'unavailable',
            'amt_balance': 'unavailable',
            'aws_access_key_id': 'unavailable'
        }
        try:
            _return['mode'] = services_manager.mode
            _return['codeversion'] = services_manager.codeversion
            _return['amt_balance'] = services_manager.amt_balance
            _return['aws_access_key_id'] = services_manager.config.get('AWS Access',
                                                                       'aws_access_key_id')
        except PsiturkException:
            pass
        return _return


# A constant used in amt service queries to expand pages
MAX_RESULTS = 100
class HitsList(Resource):

    # POST: Returns a list of HITs from MTurk
    #  only_local: Only return local HITs
    #  statuses: Filter for these HIT statuses
    def post(self):
        only_local = request.json['only_local']
        statuses = request.json['statuses']
        _return = services_manager.amt_services_wrapper.amt_services.mtc.list_hits(MaxResults=MAX_RESULTS)['HITs']
        my_hitids = list(set([hit.hitid for hit in Hit.query.distinct(Hit.hitid)]))
        _return = list(map(lambda hit: dict(hit, 
            local_hit=hit['HITId'] in my_hitids,
            ToDoAssignments=hit['MaxAssignments'] - hit['NumberOfAssignmentsAvailable'] - hit['NumberOfAssignmentsCompleted'] - hit['NumberOfAssignmentsPending']), _return))
        if only_local:
            _return = [hit for hit in _return if hit['local']]
        if len(statuses) > 0:
            _return = list(filter(lambda hit: hit['HITStatus'] in request.json['statuses'], _return))
        return _return

class HitsAction(Resource):

    # GET: Batch download HIT data
    def get(self, action):

        # ACTION: Download data
        #  assignment: the assignment id for which to download data
        if action == 'datadownload':
            hitid = request.args.get('hitid')
            fields = ['question_data', 'trial_data', 'event_data']
            participants = Participant.query.filter(Participant.hitid == hitid).all()
            mem_file = BytesIO()
            with zipfile.ZipFile(mem_file, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                for participant in participants:
                    write_data_to_zip(participant, fields, zf, prefix=participant.workerid + '_data/')
            mem_file.seek(0)
            return send_file(mem_file, attachment_filename=hitid + '_hitdata.zip', as_attachment=True)

    # POST: Perform an HIT action 
    def post(self, action=None):

        # ACTION: Create
        #  num_workers: the number of workers for the assignment
        #  reward: the reward for the hit
        #  duration: the duration of the hit
        if action == 'create':
            num_workers = request.json['num_workers']
            reward = request.json['reward']
            duration = request.json['duration']
            _return = services_manager.amt_services_wrapper.create_hit(
                num_workers=num_workers,
                reward=reward,
                duration=duration)
            return _return

class AssignmentsList(Resource):

    # POST: Returns a list of Assignments for a HIT from MTurk
    #  hit_ids: a list of hit ids for which to get assignments
    #  assignment_ids: a list of assignment_ids for which to get assignments
    #  local: when true, queries local data instead of just MTurk
    def post(self):
        hitids = request.json['hit_ids'] if 'hit_ids' in request.json else None
        assignmentids = request.json['assignment_ids'] if 'assignment_ids' in request.json else None
        local = request.json['local']
        if local:
            if hitids:
                _return = [p.toAPIData() for p in Participant.query.filter(Participant.hitid.in_(hitids)).all()]
            else:
                _return = [p.toAPIData() for p in Participant.query.filter(Participant.assignmentid.in_(assignmentids)).all()]
        else:
            if hitids:
                _return = services_manager.amt_services_wrapper.amt_services.get_assignments(hit_ids=hitids).data
            else:
                _return = []
                for assignment_id in assignmentids:
                    _return.append(services_manager.amt_services_wrapper.amt_services \
                        .get_assignment(assignment_id).data)
        return _return


class AssignmentsAction(Resource):

    # GET: For downloading data
    def get(self, action):

        # ACTION: Download data
        #  assignment: the assignment id for which to download data
        if action == 'datadownload':
            assignmentid = request.args.get('assignmentid')
            fields = ['question_data', 'trial_data', 'event_data']
            participant = Participant.query.filter(Participant.assignmentid == assignmentid).one_or_none()
            if not participant:
                return {'success': False, 'message': 'Assignment id not found.'}, 404
            mem_file = BytesIO()
            with zipfile.ZipFile(mem_file, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                write_data_to_zip(participant, fields, zf)
            mem_file.seek(0)
            return send_file(mem_file, attachment_filename=participant.workerid + '_data.zip', as_attachment=True)


    # POST: Perform an assignment action 
    def post(self, action):

        # ACTION: Approve
        #  assignments: a list of assignment ids to approve
        #  all_studies: approve in mturk even if not in local db?
        if action == 'approve':
            assignments = request.json['assignments']
            all_studies = request.json['all_studies']
            _return = []
            for assignment in assignments:
                try:
                    response = services_manager.amt_services_wrapper \
                        .approve_assignment_by_assignment_id(assignment, all_studies)
                    _return.append({
                        "assignment": assignment,
                        "success": response.status == "success",
                        "message": str(response)})
                except Exception as e:
                    _return.append({
                        "assignment": assignment, 
                        "success": False, 
                        "message": str(e)})
            return _return

        # ACTION: Reject
        #  assignments: a list of assignment ids to reject
        #  all_studies: reject in mturk even if not in local db?
        elif action == 'reject':
            assignments = request.json['assignments']
            all_studies = request.json['all_studies']
            _return = []
            for assignment in assignments:
                try:
                    response = services_manager.amt_services_wrapper \
                        .reject_assignment(assignment, all_studies)
                    _return.append({
                        "assignment": assignment, 
                        "success": response.status == 'success', 
                        "message": str(response)})
                except Exception as e:
                    _return.append({
                        "assignment": assignment, 
                        "success": False, 
                        "message": str(e)})
            return _return

        # ACTION: Bonus
        #  assignments: a list of assignment ids to bonus
        #  all_studies: bonus in mturk even if not in local db?
        #  amount: a float value to bonus, or "auto" for auto-bonusing from local
        #  reason: a string reason to send to the worker
        elif action == 'bonus':
            assignments = request.json['assignments']
            all_studies = request.json['all_studies']
            amount = request.json['amount']
            reason = request.json['reason']
            _return = []
            for assignment in assignments:
                try:
                    resp = services_manager.amt_services_wrapper \
                        .bonus_assignment_for_assignment_id(
                            assignment, amount, reason, all_studies)
                    _return.append({
                        "assignment": assignment, 
                        "success": resp.status == 'success', 
                        "message": str(resp)})
                except Exception as e:
                    _return.append({
                        "assignment": assignment, 
                        "success": False, 
                        "message": str(e)})
            return _return

        # ACTION: Data
        #  assignments: a list of assignment ids to retrieve data for
        elif action == 'data':
            assignments = request.json['assignments']
            _return = {}
            for assignment_id in assignments:
                p = Participant.query.filter_by(assignmentid=assignment_id).first()
                q_data = json.loads(p.datastring)["questiondata"]
                e_data = json.loads(p.datastring)["eventdata"]
                t_data = json.loads(p.datastring)["data"]
                jsonData = {
                    'question_data': [{
                        'questionname': q,
                        'response': json.dumps(q_data[q])} for q in q_data],
                    'event_data': [{
                        'eventtype': e['eventtype'],
                        'interval': e['interval'],
                        'value': e['value'],
                        'timestamp': e['timestamp']} for e in e_data],
                    'trial_data': [{
                        'current_trial': t['current_trial'],
                        'dateTime': t['dateTime'],
                        'trialdata': json.dumps(t['trialdata'])} for t in t_data]
                }
                _return[assignment_id] = jsonData
            return _return


class BonusList(Resource):

    # POST: Returns a list of bonuses for a HIT from MTurk
    #  hit_id: a specific hit to get all bonuses for (priority)
    #  assignment_ids: list of assignment ids to get bonuses for
    def post(self):
        hit_id = request.json['hit_id'] if 'hit_id' in request.json else None
        assignment_ids = request.json['assignment_ids'] if 'assignment_ids' in request.json else None
        _return = services_manager.amt_services_wrapper.get_bonuses(
            hit_id=hit_id, assignment_ids=assignment_ids)
        return _return.data


# --------------------------- DATA WRITING HELPERS --------------------------- #

# Writes data to an open zipfile
def write_data_to_zip(participant, fields, zf, prefix=''):
    for field in fields:
        output = get_datafile(participant, field)
        if output:
            zf.writestr(prefix + field + '.csv', output)

def get_datafile(participant, datatype):
    if not participant.datastring:
        return None
    contents = {
        "trial_data": {
            "function": lambda p: p.get_trial_data(),
            "headerline": "uniqueid,currenttrial,time,trialData\n"        
        }, 
        "event_data": {
            "function": lambda p: p.get_event_data(),
            "headerline": "uniqueid,eventtype,interval,value,time\n"        
        }, 
        "question_data": {
            "function": lambda p: p.get_question_data(),
            "headerline": "uniqueid,questionname,response\n"
        },
        }
    ret = contents[datatype]["headerline"] + contents[datatype]["function"](participant)
    return ret


# ------------------------------ RESOURCE ADDING ----------------------------- #


api.add_resource(TaskList, '/tasks', '/tasks/')
api.add_resource(Tasks, '/tasks/<task_id>')

# Dashboard API endpoints

# Workers
api.add_resource(WorkersList, '/workers', '/workers/')

# Campaigns
api.add_resource(CampaignsList, '/campaigns', '/campaigns/')
api.add_resource(CampaignsAction, '/campaigns/action/<action>')

# Service Manager
api.add_resource(ServicesManager, '/services_manager', '/services_manager/')

# HITs
api.add_resource(HitsList, '/hits', '/hits/')
api.add_resource(HitsAction, '/hits/action/<action>')

# Bonuses
api.add_resource(BonusList, '/bonuses', '/bonuses/')

# Assignments
api.add_resource(AssignmentsList, '/assignments', '/assignments/')
api.add_resource(AssignmentsAction, '/assignments/action/<action>')

api.init_app(api_blueprint)