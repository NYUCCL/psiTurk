from flask import Blueprint, render_template, request, jsonify, Response, abort, current_app, flash, session, g, redirect, url_for, make_response
from flask_login import UserMixin, login_user, logout_user, current_user
from jinja2 import TemplateNotFound
from functools import wraps
from sqlalchemy import or_

from psiturk.psiturk_config import PsiturkConfig
from psiturk.experiment_errors import ExperimentError, InvalidUsageError
from psiturk.user_utils import PsiTurkAuthorization, nocache
from psiturk.models import Participant
from psiturk.psiturk_exceptions import *

from psiturk.services_manager import psiturk_services_manager as services_manager

# # Database setup
from psiturk.db import db_session, init_db
from psiturk.models import Participant
from json import dumps, loads

# load the configuration options
config = PsiturkConfig()
config.load_config()
# if you want to add a password protect route use this
myauth = PsiTurkAuthorization(config)

# import the Blueprint
dashboard = Blueprint('dashboard', __name__,
                        template_folder='templates', static_folder='static', url_prefix='/dashboard')       

    
from flask_login import LoginManager, UserMixin
login_manager = LoginManager()
login_manager.login_view = 'dashboard.login'

def init_app(app):
    login_manager.init_app(app)

class DashboardUser(UserMixin):
    def __init__(self, username=''):
        self.id = username

@login_manager.user_loader
def load_user(username):
    return DashboardUser(username=username)

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if current_app.login_manager._login_disabled: # for unit testing
            return view(*args, **kwargs)
        is_logged_in = current_user.get_id() is not None
        is_static_resource_call = str(request.endpoint) == 'dashboard.static'
        is_login_route = str(request.url_rule) == '/dashboard/login'
        if not (is_static_resource_call or is_login_route or is_logged_in):
            return login_manager.unauthorized()
        return view(*args, **kwargs)
    return wrapped_view
    
def try_amt_services_wrapper(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        try:
            _ = services_manager.amt_services_wrapper
            return view(**kwargs)
        except Exception as e:
            message = e.message if hasattr(e, 'message') else str(e)
            flash(message, 'danger')
            return redirect(url_for('.index'))
    return wrapped_view

@dashboard.before_request
@login_required
def before_request():
    pass

@dashboard.route('/mode', methods=('GET','POST'))
@try_amt_services_wrapper
def mode():
    if request.method == 'POST':
        mode = request.form['mode']
        if mode not in ['live','sandbox']:
            flash('unrecognized mode: {}'.format(mode), 'danger')
        else:
            result = services_manager.amt_services_wrapper.set_mode(mode)
            if result.success:
                flash('mode successfully updated to {}'.format(mode), 'success')
            else:
                flash(str(result.exception), 'danger')
    mode = services_manager.amt_services_wrapper.get_mode().data
    return render_template('dashboard/mode.html', mode=mode)

@dashboard.route('/index')
@dashboard.route('/')
def index():
    current_codeversion = config['Task Parameters']['experiment_code_version']
    return render_template('dashboard/index.html', 
        current_codeversion=current_codeversion)
        
@dashboard.route('/hits')
@dashboard.route('/hits/')
@try_amt_services_wrapper
def hits_list():
    return render_template('dashboard/hits/list.html')
    
@dashboard.route('/assignments')
@dashboard.route('/assignments/')
@try_amt_services_wrapper
def assignments_list():
    return render_template('dashboard/assignments/list.html')

@dashboard.route('/campaigns')
@dashboard.route('/campaigns/')
def campaigns_list():
    completed_count = Participant.count_completed(
        codeversion=services_manager.codeversion, 
        mode=services_manager.mode)
        
    all_hits = services_manager.amt_services_wrapper.get_all_hits().data
    available_count = services_manager.amt_services_wrapper.count_available(hits=all_hits).data
    pending_count = services_manager.amt_services_wrapper.count_pending(hits=all_hits).data    
    maybe_will_complete_count = services_manager.amt_services_wrapper.count_maybe_will_complete(hits=all_hits).data
        
    return render_template('dashboard/campaigns/list.html', 
        completed_count=completed_count,
        pending_count=pending_count,
        maybe_will_complete_count=maybe_will_complete_count,
        available_count=available_count)
        
@dashboard.route('/tasks')
@dashboard.route('/tasks/')
def tasks_list():
    return render_template('dashboard/tasks/list.html')

@dashboard.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username= request.form['username']
        password= request.form['password']
        
        try:
            if 'example' in username or 'example' in password:
                raise Exception('Default username-password not permitted! Change them in your config file.')
            if not myauth.check_auth(username, password):
                raise Exception('Incorrect username or password')
                
            user = DashboardUser(username=username)
            login_user(user)
            flash("Logged in successfully.")
            next = request.args.get('next')
            return redirect(next or url_for('.index'))
        except Exception as e:
            flash(str(e), 'danger')
    
    return render_template('dashboard/login.html')            
    
@dashboard.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('.login'))