from flask import Blueprint, render_template, request, jsonify, Response, abort, current_app, flash, session, g, redirect, url_for
from jinja2 import TemplateNotFound
from functools import wraps
from sqlalchemy import or_

from psiturk.psiturk_config import PsiturkConfig
from psiturk.experiment_errors import ExperimentError, InvalidUsage
from psiturk.user_utils import PsiTurkAuthorization, nocache

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
                        template_folder='dashboard/templates', static_folder='static', url_prefix='/dashboard')
           
def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        print(request.url_rule)
        if 'username' not in g and str(request.url_rule) != '/dashboard/login':
            return redirect(url_for('.login'))
        return view(**kwargs)
    return wrapped_view
    
@dashboard.before_request
@login_required
def before_request():
    pass

    
@dashboard.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username= request.form['username']
        password= request.form['password']
        success = myauth.check_auth(username, password)
        
        if not success:
            error = 'Incorrect username or password'
            flash(error)
        else:
            session.clear()
            session['username'] = username
            return redirect(url_for('.index'))
    return render_template('login.html')
    
@dashboard.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('.login'))
    
        