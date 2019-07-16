from flask import Blueprint, jsonify, make_response, request
from flask.json import JSONEncoder
from flask_restful import Api, Resource
from psiturk.dashboard import login_required
from psiturk.services_manager import psiturk_services_manager as services_manager
from psiturk.models import Participant
from psiturk.experiment import app
from psiturk.psiturk_exceptions import *
from psiturk.amt_services_wrapper import WrapperResponse
from functools import wraps

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api()

@api_blueprint.errorhandler(Exception)
def handle_psiturk_exception(exception):
    message = exception.message if (hasattr(exception, 'message') and exception.message) else str(exception)
    return jsonify({
        'exception': type(exception).__name__,
        'message': message
        }), 400

class PsiturkJsonEncoder(JSONEncoder): # flask's jsonencoder class
    def default(self, obj):
        if isinstance(obj, (PsiturkException, WrapperResponse)):
            return obj.to_dict()
        elif isinstance(obj, Exception):
            return str(obj)
        return JSONEncoder.default(self, obj)

api_blueprint.json_encoder = PsiturkJsonEncoder

@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(jsonify(data), code)
    resp.headers.extend(headers or {})
    return resp
    
@api_blueprint.before_request
@login_required
def before_request():
    pass
    
class ServicesManager(Resource):
    def get(self):
        try:
            mode = services_manager.amt_services_wrapper.get_mode().data
        except PsiturkException:
            mode = 'unavailable'
        return {'mode':mode}

class Workers(Resource):
    def get(self, worker_id=None):
        all_workers = [worker.object_as_dict(filter_these=['datastring']) for worker in Participant.query.filter(Participant.mode != 'debug').all()]
        return all_workers

class Hit(Resource):
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
        return services_manager.amt_services_wrapper.get_hit(hit_id).data.__dict__, 201
        
    def delete(self, hit_id):
        response = services_manager.amt_services_wrapper.delete_hit(hit_id)
        if not response.success:
            raise response.exception
        return '', 204
        
class Hits(Resource):
    def get(self, status=None):
        if status == 'active':
            hits = services_manager.amt_services_wrapper.get_active_hits().data
        else:
            hits = services_manager.amt_services_wrapper.get_all_hits().data
        hits = [hit.__dict__ for hit in hits]
        return hits
            
class HitsAction(Resource):
    def get(self, action=None):
        if action == 'expire_all':
            response = services_manager.amt_services_wrapper.expire_all_hits()
            if response.success:
                _return = []
                for hit_response in response.data['results']:
                    _return.append(hit_response.to_dict())
                return _return, 201
            else:
                raise response.exception
        elif action == 'delete_all':
            response = services_manager.amt_services_wrapper.delete_all_hits()
            if response.success:
                _return = []
                for hit_response in response.data['results']:
                    _return.append(hit_response.to_dict())
                return _return, 201
            else:
                raise response.exception
        elif action == 'approve_all':
            hits = services_manager.amt_services_wrapper.get_all_hits().data
            
            _return = []
            for hit in hits:
                hit_response = services_manager.amt_services_wrapper.approve_assignments_for_hit(hit.options['hitid'], all_studies=True)
                _return.append(hit_response.to_dict())
            return _return, 201
                
        else:
            raise APIException(message='action `{}` not recognized!'.format(action))

        
api.add_resource(ServicesManager, '/services_manager','/services_manager/')
api.add_resource(Workers, '/workers/', '/workers/<worker_id>')
api.add_resource(Hits, '/hits/', '/hits/<status>')
api.add_resource(HitsAction, '/hits/action/<action>')
api.add_resource(Hit, '/hit/<hit_id>')
api.init_app(api_blueprint)