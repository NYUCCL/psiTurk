from __future__ import generator_stop
from flask import Blueprint, render_template, request, current_app as app, \
    flash, session, g, redirect, url_for
from flask_login import login_user, logout_user, current_user
from functools import wraps
from psiturk.psiturk_config import PsiturkConfig
from psiturk.user_utils import PsiTurkAuthorization, nocache
from psiturk.psiturk_exceptions import *

from psiturk.services_manager import SESSION_SERVICES_MANAGER_MODE_KEY, \
    psiturk_services_manager as services_manager
from flask_login import LoginManager, UserMixin

# # Database setup
from psiturk.models import Participant

# load the configuration options
config = PsiturkConfig()
config.load_config()

# if you want to add a password protect route use this
myauth = PsiTurkAuthorization(config)

# import the Blueprint
dashboard = Blueprint('dashboard', __name__,
                      template_folder='templates',
                      static_folder='static', url_prefix='/dashboard')


login_manager = LoginManager()
login_manager.login_view = 'dashboard.login'


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


class DashboardUser(UserMixin):
    def __init__(self, username=''):
        self.id = username


@login_manager.user_loader
def load_user(username):
    return DashboardUser(username=username)

def is_static_resource_call():
    return str(request.endpoint) == 'dashboard.static'

def is_login_route():
    return str(request.url_rule) == '/dashboard/login'

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if current_user.is_authenticated:
            pass
        elif app.config.get('LOGIN_DISABLED'):  # for unit testing
            pass
        elif is_static_resource_call() or is_login_route():
            pass
        else:
            return login_manager.unauthorized()
        return view(*args, **kwargs)

    return wrapped_view


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

def warn_if_scheduler_not_running(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        app.logger.debug('checking if scheduler is running...')
        do_scheduler = config.getboolean('Server Parameters', 'do_scheduler')
        app.logger.debug(f'do_scheduler was {do_scheduler}')
        if not do_scheduler:
            flash((
                'Warning: `do_scheduler` is set to False. '
                'Tasks (such as campaigns) can be created, modified, or deleted, '
                'but they will not be run by this psiturk instance.'
            ), 'warning')
        return view(**kwargs)

    return wrapped_view

@dashboard.before_request
@login_required
@try_amt_services_wrapper
def before_request():
    pass


@dashboard.route('/mode', methods=('GET', 'POST'))
def mode():
    if request.method == 'POST':
        mode = request.form['mode']
        if mode not in ['live', 'sandbox']:
            flash('unrecognized mode: {}'.format(mode), 'danger')
        else:
            try:
                services_manager.mode = mode
                session[SESSION_SERVICES_MANAGER_MODE_KEY] = mode
                flash('mode successfully updated to {}'.format(mode), 'success')
            except Exception as e:
                flash(str(e), 'danger')
    mode = services_manager.mode
    return render_template('dashboard/mode.html', mode=mode)


@dashboard.route('/index')
@dashboard.route('/')
def index():
    current_codeversion = config['Task Parameters']['experiment_code_version']
    return render_template('dashboard/index.html',
                           current_codeversion=current_codeversion)


@dashboard.route('/hits')
@dashboard.route('/hits/')
def hits_list():
    return render_template('dashboard/hits/list.html')


@dashboard.route('/assignments')
@dashboard.route('/assignments/')
def assignments_list():
    return render_template('dashboard/assignments/list.html')

@dashboard.route('/campaigns')
@dashboard.route('/campaigns/')
@warn_if_scheduler_not_running
def campaigns_list():
    completed_count = Participant.count_completed(
        codeversion=services_manager.codeversion,
        mode=services_manager.mode)

    all_hits = services_manager.amt_services_wrapper.get_all_hits().data
    available_count = services_manager.amt_services_wrapper.count_available(hits=all_hits).data
    pending_count = services_manager.amt_services_wrapper.count_pending(hits=all_hits).data
    maybe_will_complete_count = services_manager.amt_services_wrapper.count_maybe_will_complete(
        hits=all_hits).data

    return render_template('dashboard/campaigns/list.html',
                           completed_count=completed_count,
                           pending_count=pending_count,
                           maybe_will_complete_count=maybe_will_complete_count,
                           available_count=available_count)


@dashboard.route('/tasks')
@dashboard.route('/tasks/')
@warn_if_scheduler_not_running
def tasks_list():
    return render_template('dashboard/tasks/list.html')


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
