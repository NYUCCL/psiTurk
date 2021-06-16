# Flask imports
from flask import Blueprint, render_template, request, current_app as app, \
    flash, session, redirect, url_for, jsonify
from flask_login import login_user, logout_user, current_user, LoginManager, UserMixin

# PsiTurk imports
from psiturk.psiturk_config import PsiturkConfig
from psiturk.user_utils import PsiTurkAuthorization
from psiturk.services_manager import SESSION_SERVICES_MANAGER_MODE_KEY, \
    psiturk_services_manager as services_manager
from psiturk.psiturk_exceptions import *
from psiturk.models import Participant, Hit

# Misc. imports
from functools import wraps

# TEMP IMPORT UNTIL ADVANCED QUASLS FIXED UP
import json

## Database setup

# Load configuration options
config = PsiturkConfig()
config.load_config()

# For password protected routes
myauth = PsiTurkAuthorization(config)

# Import the blueprint
dashboard = Blueprint('dashboard', __name__, template_folder='templates',
    static_folder='static', url_prefix='/dashboard')

# ---------------------------------------------------------------------------- #
#                                   CONSTANTS                                  #
# ---------------------------------------------------------------------------- #

# Get the advanced qualifications for info dumping
advanced_quals_path = config.get('HIT Configuration', 'advanced_quals_path', fallback=None)
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

# Load the local HIT data from the config
HIT_INFO = {
    "title": config.get('HIT Configuration', 'title'),
    "description": config.get('HIT Configuration', 'description'),
    "lifetime": config.get('HIT Configuration', 'lifetime'),
    "approve_requirement": config.get('HIT Configuration', 'approve_requirement'),
    "number_hits_approved": config.get('HIT Configuration', 'number_hits_approved'),
    "require_master_workers": config.get('HIT Configuration', 'require_master_workers'),
    "advanced_qualifications": advanced_qualifications
}

MAX_RESULTS = 100

# ---------------------------------------------------------------------------- #
#                                  FLASK LOGIN                                 #
# ---------------------------------------------------------------------------- #

# Login page for the dashboard
login_manager = LoginManager()
login_manager.login_view = 'dashboard.login'

# Flask custom user class must import UserMixin
class DashboardUser(UserMixin):
    def __init__(self, username=''):
        self.id = username

@login_manager.user_loader
def load_user(username):
    return DashboardUser(username=username)

# Ignore case 1 for login-required endpoints
def is_static_resource_call():
    return str(request.endpoint) == 'dashboard.static'

# Ignore case 2 for login-required endpoints
def is_login_route():
    return str(request.url_rule) == '/dashboard/login'

# Login-required user wrapper, ignores static / login routes
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if current_user.is_authenticated:
            pass
        elif app.config.get('LOGIN_DISABLED'):
            pass
        elif is_static_resource_call() or is_login_route():
            pass
        else:
            return login_manager.unauthorized()
        return view(*args, **kwargs)
    return wrapped_view

# ---------------------------------------------------------------------------- #
#                          AMT SERVICES INITIALIZATION                         #
# ---------------------------------------------------------------------------- #

# Initializes app with dashboard and amt services
def init_app(app):
    if not app.config.get('LOGIN_DISABLED'):
        # this dashboard requires a valid mturk connection -- try for one here
        try:
            _ = services_manager.amt_services_wrapper  # may throw error if aws keys not set
        except NoMturkConnectionError:
            raise Exception((
                'Dashboard requested, but no valid mturk credentials found. '
                'Either disable the dashboard in config, or set valid mturk credentials -- '
                'see https://psiturk.readthedocs.io/en/latest/amt_setup.html#aws-credentials . '
                '\nRefusing to start.'
                ))
    login_manager.init_app(app)

# Ensures AMT services exist for a view
def try_amt_services_wrapper(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        try:
            _ = services_manager.amt_services_wrapper  # may throw error if aws keys not set
            if SESSION_SERVICES_MANAGER_MODE_KEY not in session:
                app.logger.debug('setting session mode to {}'.format(services_manager.mode))
                session[SESSION_SERVICES_MANAGER_MODE_KEY] = services_manager.mode
            else:
                app.logger.debug(
                    'found session mode: {}'.format(session[SESSION_SERVICES_MANAGER_MODE_KEY]))
                services_manager.mode = session[SESSION_SERVICES_MANAGER_MODE_KEY]
                app.logger.debug('I set services manager mode to {}'.format(services_manager.mode))
            return view(**kwargs)
        except Exception as e:
            if not is_login_route() and not is_static_resource_call():
                message = e.message if hasattr(e, 'message') else str(e)
                flash(message, 'danger')
                return redirect(url_for('.login'))
    return wrapped_view

# ---------------------------------------------------------------------------- #
#                              SEMI-STATIC-ROUTES                              #
# ---------------------------------------------------------------------------- #
# Routes which have minimal Python logic behind them in the dashboard

# All dashboard requests must be logged in and have an AMT Services object
@dashboard.before_request
@login_required
@try_amt_services_wrapper
def before_request():
    pass

# Main page, also serves the experiment code version
@dashboard.route('/index')
@dashboard.route('/')
def index():
    current_codeversion = config['Task Parameters']['experiment_code_version']
    return render_template('dashboard/index.html',
                           current_codeversion=current_codeversion)

# Database of local HITs with management controls
@dashboard.route('/hits')
@dashboard.route('/hits/')
@dashboard.route('/hits/<hit_id>')
@dashboard.route('/hits/<hit_id>/')
def hits_list(hit_id=None):
    return render_template('dashboard/hits.html', hit_id=hit_id, hit_info=HIT_INFO)

# Database of assignments for a given HIT
@dashboard.route('/hits/<hit_id>/assignments')
@dashboard.route('/hits/<hit_id>/assignments/')
def assignments_list(hit_id):
    my_hitids = list(set([hit.hitid for hit in Hit.query.distinct(Hit.hitid)]))
    return render_template('dashboard/assignments.html', hit_id=hit_id, hit_local=hit_id in my_hitids)

# ---------------------------------------------------------------------------- #
#                                  FORM ROUTES                                 #
# ---------------------------------------------------------------------------- #
# Routes which double as forms for posting

# Login page for logging in a user
@dashboard.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            if not myauth.check_auth(username, password):
                raise Exception('Incorrect username or password')
            user = DashboardUser(username=username)
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('.index'))
        except Exception as e:
            pass
    return render_template('dashboard/login.html')

# Logout endpoint logs out a user and sends back to login
@dashboard.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('.login'))

# Get/set mode of the current AMT Services Wrapper 
@dashboard.route('/mode', methods=['POST'])
def mode():
    mode = request.json['mode']
    try:
        services_manager.mode = mode
        session[SESSION_SERVICES_MANAGER_MODE_KEY] = mode
        return jsonify({"success": True, "data": {"mode": mode}}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# ---------------------------------------------------------------------------- #
#                                  API ROUTES                                  #
# ---------------------------------------------------------------------------- #

# Retrieves all HITs associated with this account
@dashboard.route('/api/hits', methods=['POST'])
def API_list_hits():
    try:
        response = services_manager.amt_services_wrapper.amt_services.mtc.list_hits(MaxResults=MAX_RESULTS)['HITs']
        my_hitids = list(set([hit.hitid for hit in Hit.query.distinct(Hit.hitid)]))
        response = map(lambda hit: dict(hit, local_hit=hit['HITId'] in my_hitids), response)
        if 'only_local' in request.json and request.json['only_local']:
            response = [hit for hit in response if hit['local']]
        if 'statuses' in request.json and len(request.json['statuses']) > 0:
            response = list(filter(lambda hit: hit['HITStatus'] in request.json['statuses'], response))
        return jsonify({"success": True, "data": response}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# Retrieves a list of assignments for a hit id
@dashboard.route('/api/assignments', methods=['POST'])
def API_list_assignments():
    try:
        hitids = request.json['hit_ids']
        local = request.json['local']
        if local:
            response = [p.toAPIData() for p in Participant.query.filter(Participant.hitid.in_(hitids)).all()]
        else:
            response = services_manager.amt_services_wrapper.amt_services.get_assignments(hit_ids=hitids)
            if not response.success:
                raise response.exception
            else:
                response = response.data
        return jsonify({"success": True, "data": response}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# Creates a local HIT
@dashboard.route('/api/hits/create', methods=['POST'])
def API_create_hit():
    try:
        num_workers = request.json['num_workers']
        reward = request.json['reward']
        duration = request.json['duration']
        response = services_manager.amt_services_wrapper.create_hit(
            num_workers=num_workers,
            reward=reward,
            duration=duration)
        if not response.success:
            raise response.exception
        return jsonify({"success": True, "data": response.data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
