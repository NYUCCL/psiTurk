# -*- coding: utf-8 -*-
""" This module provides the backend Flask server used by psiTurk. """
from __future__ import generator_stop
import os
import sys
import datetime
import logging
from random import choice
import user_agents
import requests
import re
import json
from jinja2 import TemplateNotFound
from collections import Counter


# Setup flask
from flask import Flask, render_template, render_template_string, request, \
    jsonify, send_from_directory

# Setup database

from .db import db_session, init_db
from .models import Participant
from sqlalchemy import or_, exc

from .psiturk_statuses import *
from .psiturk_config import PsiturkConfig
from .experiment_errors import ExperimentError, ExperimentApiError
from .user_utils import nocache

# Setup config
CONFIG = PsiturkConfig()
CONFIG.load_config()

LOG_LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR,
logging.CRITICAL]
LOG_LEVEL = LOG_LEVELS[CONFIG.getint('Server Parameters', 'loglevel')]

logfile = CONFIG.get("Server Parameters", "errorlog")
if logfile != '-':
    file_path = os.path.join(os.getcwd(), logfile)
    logging.basicConfig(filename=file_path, format='%(asctime)s %(message)s',
                        level=LOG_LEVEL)

# Let's start
# ===========

app = Flask("Experiment_Server")
app.logger.setLevel(LOG_LEVEL)

# Set cache timeout to 10 seconds for static files
app.config.update(SEND_FILE_MAX_AGE_DEFAULT=10)
app.secret_key = CONFIG.get('Server Parameters', 'secret_key')


def check_templates_exist():
    # this checks for templates that are required if you are hosting your own ad.
    try:
        try_these = ['thanks-mturksubmit.html', 'closepopup.html']
        [app.jinja_env.get_template(try_this) for try_this in try_these]
    except TemplateNotFound as e:
        raise RuntimeError((
            f"Missing one of the following templates: {', '.join(try_these)}."
            f"Copy these over from a freshly-created psiturk example experiment."
            f"{type(e).__name__, str(e)}"
        ))


check_templates_exist()


# Serving warm, fresh, & sweet custom, user-provided routes
# ==========================================================

try:
    sys.path.append(os.getcwd())
    from custom import custom_code
except ModuleNotFoundError as e:
    app.logger.info("Hmm... it seems no custom code (custom.py) associated \
                    with this project.")
except ImportError as e:
    app.logger.error("There is custom code (custom.py) associated with this \
                      project but it doesn't import cleanly.  Raising exception,")
    raise
else:
    app.register_blueprint(custom_code)
    try:
        # noinspection PyUnresolvedReferences
        from custom import init_app as custom_init_app
    except ImportError as e:
        pass
    else:
        custom_init_app(app)

# scheduler

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from pytz import utc

from .db import engine
jobstores = {
    'default': SQLAlchemyJobStore(engine=engine)
}
if 'gunicorn' in os.environ.get('SERVER_SOFTWARE', ''):
    from apscheduler.schedulers.gevent import GeventScheduler as Scheduler
else:
    from apscheduler.schedulers.background import BackgroundScheduler as Scheduler
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
scheduler = Scheduler(jobstores=jobstores, timezone=utc)
app.apscheduler = scheduler
scheduler.app = app

if CONFIG.getboolean('Server Parameters', 'do_scheduler'):
    app.logger.info("Scheduler starting!")
    scheduler.start()
else:
    app.logger.info("Starting scheduler in 'paused' mode -- it will not run any tasks, but it can be used to create, modify, or delete tasks.")
    scheduler.start(paused=True)


#
# Dashboard
#
if CONFIG.getboolean('Server Parameters', 'enable_dashboard'):
    from .dashboard import dashboard, init_app as dashboard_init_app # management dashboard
    app.register_blueprint(dashboard)
    dashboard_init_app(app)

    from .api import api_blueprint
    app.register_blueprint(api_blueprint)

init_db()

# Read psiturk.js file into memory
PSITURK_JS_FILE = os.path.join(os.path.dirname(__file__),
                               "psiturk_js/psiturk.js")
app.logger.info(PSITURK_JS_FILE)

if os.path.exists(PSITURK_JS_FILE):
    PSITURK_JS_CODE = open(PSITURK_JS_FILE).read()
else:
    PSITURK_JS_CODE = "alert('psiturk.js file not found!');"


@app.errorhandler(ExperimentError)
def handle_exp_error(exception):
    """Handle errors by sending an error page."""
    app.logger.error(
        "%s (%s) %s", exception.value, exception.errornum, str(dict(request.args)))
    return exception.error_page(request, CONFIG.get('Task Parameters',
                                                    'contact_email_on_error'))


@app.errorhandler(ExperimentApiError)
def handle_experiment_api_error(error):
    # for use with API errors
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    app.logger.error(error.message)
    return response


@app.teardown_request
def shutdown_session(_=None):
    """ Shut down session route """
    db_session.remove()


# Experiment counterbalancing code
# ================================

def get_random_condcount(mode):
    """
    HITs can be in one of three states:
        - jobs that are finished
        - jobs that are started but not finished
        - jobs that are never going to finish (user decided not to do it)
    Our count should be based on the first two, so we count any tasks finished
    or any tasks not finished that were started in the last cutoff_time
    minutes, as specified in the cutoff_time variable in the config file.

    Returns a tuple: (cond, condition)
    """
    cutofftime = datetime.timedelta(minutes=-CONFIG.getint('Task Parameters',
                                                           'cutoff_time'))
    starttime = datetime.datetime.now(datetime.timezone.utc) + cutofftime

    try:
        conditions = json.load(
            open(os.path.join(app.root_path, 'conditions.json')))
        numconds = len(list(conditions.keys()))
        numcounts = 1
    except IOError:
        numconds = CONFIG.getint('Task Parameters', 'num_conds')
        numcounts = CONFIG.getint('Task Parameters', 'num_counters')

    participants = Participant.query.\
        filter(Participant.codeversion ==
               CONFIG.get('Task Parameters', 'experiment_code_version')).\
        filter(Participant.mode == mode).\
        filter(or_(Participant.status == COMPLETED,
                   Participant.status == CREDITED,
                   Participant.status == SUBMITTED,
                   Participant.status == BONUSED,
                   Participant.beginhit > starttime)).all()
    counts = Counter()
    for cond in range(numconds):
        for counter in range(numcounts):
            counts[(cond, counter)] = 0
    for participant in participants:
        condcount = (participant.cond, participant.counterbalance)
        if condcount in counts:
            counts[condcount] += 1
    mincount = min(counts.values())
    minima = [hsh for hsh, count in counts.items() if count == mincount]
    chosen = choice(minima)
    app.logger.info("given %(a)s chose %(b)s" % {'a': counts, 'b': chosen})

    return chosen


try:
    from custom import custom_get_condition as get_condition
except (ModuleNotFoundError, ImportError):
    get_condition = get_random_condcount

# Routes
# ======


@app.route('/')
@nocache
def index():
    """ Index route """
    return render_template('default.html')


@app.route('/favicon.ico')
def favicon():
    """ Serve favicon """
    return app.send_static_file('favicon.ico')


@app.route('/static/js/psiturk.js')
def psiturk_js():
    """ psiTurk js route """
    return render_template_string(PSITURK_JS_CODE)


@app.route('/check_worker_status', methods=['GET'])
def check_worker_status():
    """ Check worker status route """
    if 'workerId' not in request.args:
        resp = {"status": "bad request"}
        return jsonify(**resp)
    else:
        worker_id = request.args['workerId']
        assignment_id = request.args['assignmentId']
        allow_repeats = CONFIG.getboolean('Task Parameters', 'allow_repeats')
        if allow_repeats:  # if you allow repeats focus on current worker/assignment combo
            try:
                part = Participant.query.\
                    filter(Participant.workerid == worker_id).\
                    filter(Participant.assignmentid == assignment_id).one()
                status = part.status
            except exc.SQLAlchemyError:
                status = NOT_ACCEPTED
        else:  # if you disallow repeats search for highest status of anything by this worker
            try:
                matches = Participant.query.\
                    filter(Participant.workerid == worker_id).all()
                numrecs = len(matches)
                if numrecs == 0:  # this should be caught by exception, but just to be safe
                    status = NOT_ACCEPTED
                else:
                    status = max([record.status for record in matches])
            except exc.SQLAlchemyError:
                status = NOT_ACCEPTED
        resp = {"status": status}
        return jsonify(**resp)


@app.route('/ad', methods=['GET'])
@app.route('/pub', methods=['GET'])
@nocache
def advertisement():
    """
    This is the url we give for the ad for our 'external question'.  The ad has
    to display two different things: This page will be called from within
    mechanical turk, with url arguments hitId, assignmentId, and workerId.
    If the worker has not yet accepted the hit:
        These arguments will have null values, we should just show an ad for
        the experiment.
    If the worker has accepted the hit:
        These arguments will have appropriate values and we should enter the
        person in the database and provide a link to the experiment popup.
    """
    user_agent_string = request.user_agent.string
    user_agent_obj = user_agents.parse(user_agent_string)
    browser_ok = True
    browser_exclude_rule = CONFIG.get('Task Parameters', 'browser_exclude_rule')
    for rule in browser_exclude_rule.split(','):
        myrule = rule.strip()
        if myrule in ["mobile", "tablet", "touchcapable", "pc", "bot"]:
            if (myrule == "mobile" and user_agent_obj.is_mobile) or\
               (myrule == "tablet" and user_agent_obj.is_tablet) or\
               (myrule == "touchcapable" and user_agent_obj.is_touch_capable) or\
               (myrule == "pc" and user_agent_obj.is_pc) or\
               (myrule == "bot" and user_agent_obj.is_bot):
                browser_ok = False
        elif myrule == "Safari" or myrule == "safari":
            if "Chrome" in user_agent_string and "Safari" in user_agent_string:
                pass
            elif "Safari" in user_agent_string:
                browser_ok = False
        elif myrule in user_agent_string:
            browser_ok = False

    if not browser_ok:
        # Handler for IE users if IE is not supported.
        raise ExperimentError('browser_type_not_allowed')

    if not ('hitId' in request.args and 'assignmentId' in request.args):
        raise ExperimentError('hit_assign_worker_id_not_set_in_mturk')
    hit_id = request.args['hitId']
    assignment_id = request.args['assignmentId']
    mode = request.args['mode']
    if hit_id[:5] == "debug":
        debug_mode = True
    else:
        debug_mode = False
    already_in_db = False
    if 'workerId' in request.args:
        worker_id = request.args['workerId']
        # First check if this workerId has completed the task before (v1).
        nrecords = Participant.query.\
            filter(Participant.assignmentid != assignment_id).\
            filter(Participant.workerid == worker_id).\
            count()

        if nrecords > 0:  # Already completed task
            already_in_db = True
    else:  # If worker has not accepted the hit
        worker_id = None
    try:
        part = Participant.query.\
            filter(Participant.hitid == hit_id).\
            filter(Participant.assignmentid == assignment_id).\
            filter(Participant.workerid == worker_id).\
            one()
        status = part.status
    except exc.SQLAlchemyError:
        status = None

    allow_repeats = CONFIG.getboolean('Task Parameters', 'allow_repeats')
    if (status == STARTED or status == QUITEARLY) and not debug_mode:
        # Once participants have finished the instructions, we do not allow
        # them to start the task again.
        raise ExperimentError('already_started_exp_mturk')
    elif status == COMPLETED or (status == SUBMITTED and not already_in_db):
        # 'or status == SUBMITTED' because we suspect that sometimes the post
        # to mturk fails after we've set status to SUBMITTED, so really they
        # have not successfully submitted. This gives another chance for the
        # submit to work.

        # They've finished the experiment but haven't successfully submitted the HIT
        # yet.
        return render_template(
            'thanks-mturksubmit.html',
            using_sandbox=(mode == "sandbox"),
            hitid=hit_id,
            assignmentid=assignment_id,
            workerid=worker_id
        )
    elif already_in_db and not (debug_mode or allow_repeats):
        raise ExperimentError('already_did_exp_hit')
    elif status == ALLOCATED or not status or debug_mode:
        # Participant has not yet agreed to the consent. They might not
        # even have accepted the HIT.
        with open('templates/ad.html', 'r') as temp_file:
            ad_string = temp_file.read()
        ad_string = insert_mode(ad_string)
        return render_template_string(
            ad_string,
            mode=mode,
            hitid=hit_id,
            assignmentid=assignment_id,
            workerid=worker_id
        )
    else:
        raise ExperimentError('status_incorrectly_set')


@app.route('/consent', methods=['GET'])
@nocache
def give_consent():
    """
    Serves up the consent in the popup window.
    """
    if not ('hitId' in request.args and 'assignmentId' in request.args and
            'workerId' in request.args):
        raise ExperimentError('hit_assign_worker_id_not_set_in_consent')
    hit_id = request.args['hitId']
    assignment_id = request.args['assignmentId']
    worker_id = request.args['workerId']
    mode = request.args['mode']
    with open('templates/consent.html', 'r') as temp_file:
        consent_string = temp_file.read()
    consent_string = insert_mode(consent_string)
    return render_template_string(
        consent_string,
        mode=mode,
        hitid=hit_id,
        assignmentid=assignment_id,
        workerid=worker_id
    )


@app.route('/exp', methods=['GET'])
@nocache
def start_exp():
    """ Serves up the experiment applet. """
    if not (('hitId' in request.args) and ('assignmentId' in request.args) and
            ('workerId' in request.args) and ('mode' in request.args)):
        raise ExperimentError('hit_assign_worker_id_not_set_in_exp')
    hit_id = request.args['hitId']
    assignment_id = request.args['assignmentId']
    worker_id = request.args['workerId']
    mode = request.args['mode']
    app.logger.info("Accessing /exp: %(h)s %(a)s %(w)s " % {
        "h": hit_id,
        "a": assignment_id,
        "w": worker_id
    })
    if hit_id[:5] == "debug":
        debug_mode = True
    else:
        debug_mode = False

    # Check first to see if this hitId or assignmentId exists.  If so, check to
    # see if inExp is set
    allow_repeats = CONFIG.getboolean('Task Parameters', 'allow_repeats')
    if allow_repeats:
        matches = Participant.query.\
            filter(Participant.workerid == worker_id).\
            filter(Participant.assignmentid == assignment_id).\
            all()
    else:
        matches = Participant.query.\
            filter(Participant.workerid == worker_id).\
            all()

    numrecs = len(matches)
    if numrecs == 0:
        # Choose condition and counterbalance
        subj_cond, subj_counter = get_condition(mode)

        worker_ip = "UNKNOWN" if not request.remote_addr else \
            request.remote_addr
        browser = "UNKNOWN" if not request.user_agent.browser else \
            request.user_agent.browser
        platform = "UNKNOWN" if not request.user_agent.platform else \
            request.user_agent.platform
        language = "UNKNOWN" if not request.accept_languages else \
            request.accept_languages.best

        # Set condition here and insert into database.
        participant_attributes = dict(
            assignmentid=assignment_id,
            workerid=worker_id,
            hitid=hit_id,
            cond=subj_cond,
            counterbalance=subj_counter,
            ipaddress=worker_ip,
            browser=browser,
            platform=platform,
            language=language,
            mode=mode
        )
        part = Participant(**participant_attributes)
        db_session.add(part)
        db_session.commit()

    else:
        # A couple possible problems here:
        # 1: They've already done an assignment, then we should tell them they
        #    can't do another one
        # 2: They've already worked on this assignment, and got too far to
        #    start over.
        # 3: They're in the database twice for the same assignment, that should
        #    never happen.
        # 4: They're returning and all is well.
        nrecords = 0
        for record in matches:
            other_assignment = False
            if record.assignmentid != assignment_id:
                other_assignment = True
            else:
                nrecords += 1
        if nrecords <= 1 and not other_assignment:
            part = matches[0]
            # In experiment (or later) can't restart at this point
            if part.status >= STARTED and not debug_mode:
                raise ExperimentError('already_started_exp')
        else:
            if nrecords > 1:
                app.logger.error("Error, hit/assignment appears in database \
                                 more than once (serious problem)")
                raise ExperimentError(
                    'hit_assign_appears_in_database_more_than_once'
                )
            if other_assignment:
                raise ExperimentError('already_did_exp_hit')

    ad_server_location = '/complete'

    return render_template(
        'exp.html', uniqueId=part.uniqueid,
        condition=part.cond,
        counterbalance=part.counterbalance,
        adServerLoc=ad_server_location,
        mode=mode,
        contact_address=CONFIG.get(
            'Task Parameters', 'contact_email_on_error'),
        codeversion=CONFIG.get(
            'Task Parameters', 'experiment_code_version')
    )


@app.route('/inexp', methods=['POST'])
def enterexp():
    """
    AJAX listener that listens for a signal from the user's script when they
    leave the instructions and enter the real experiment. After the server
    receives this signal, it will no longer allow them to re-access the
    experiment applet (meaning they can't do part of the experiment and
    referesh to start over).
    """
    app.logger.info("Accessing /inexp")
    if 'uniqueId' not in request.form:
        raise ExperimentError('improper_inputs')
    unique_id = request.form['uniqueId']

    try:
        user = Participant.query.\
            filter(Participant.uniqueid == unique_id).one()
        user.status = STARTED
        user.beginexp = datetime.datetime.now(datetime.timezone.utc)
        db_session.add(user)
        db_session.commit()
        resp = {"status": "success"}
    except exc.SQLAlchemyError:
        app.logger.error("DB error: Unique user not found.")
        resp = {"status": "error, uniqueId not found"}
    return jsonify(**resp)

# TODD SAYS: This the only route in the whole thing that uses <id> like this
# where everything else uses POST!  This could be confusing but is forced
# somewhat by Backbone?  Take heed!
@app.route('/sync/<uid>', methods=['GET'])
def load(uid=None):
    """
    Load experiment data, which should be a JSON object and will be stored
    after converting to string.
    """
    app.logger.info("GET /sync route with id: %s" % uid)

    try:
        user = Participant.query.\
            filter(Participant.uniqueid == uid).\
            one()
    except exc.SQLAlchemyError:
        app.logger.error("DB error: Unique user not found.")
    else:
        try:
            resp = json.loads(user.datastring)
        except (ValueError, TypeError, json.JSONDecodeError):
            resp = {
                "condition": user.cond,
                "counterbalance": user.counterbalance,
                "assignmentId": user.assignmentid,
                "workerId": user.workerid,
                "hitId": user.hitid,
                "bonus": user.bonus
            }
        return jsonify(**resp)


@app.route('/sync/<uid>', methods=['PUT'])
def update(uid=None):
    """
    Save experiment data, which should be a JSON object and will be stored
    after converting to string.
    """
    app.logger.info("PUT /sync route with id: %s" % uid)

    try:
        user = Participant.query.\
            filter(Participant.uniqueid == uid).\
            one()
    except exc.SQLAlchemyError:
        raise ExperimentApiError("DB error: Unique user not found.")

    user.datastring = json.dumps(request.json)
    db_session.add(user)
    db_session.commit()

    try:
        data = json.loads(user.datastring)
    except Exception as e:
        raise ExperimentApiError('failed to load json datastring back from database as object! Error was {}: {}'.format(type(e), str(e)))

    trial = data.get("currenttrial", None)
    app.logger.info("saved data for %s (current trial: %s)", uid, trial)
    resp = {"status": "user data saved"}
    return jsonify(**resp)


@app.route('/quitter', methods=['POST'])
def quitter():
    """
    Mark quitter as such.
    """
    unique_id = request.form['uniqueId']
    if unique_id[:5] == "debug":
        debug_mode = True
    else:
        debug_mode = False

    if debug_mode:
        resp = {"status": "didn't mark as quitter since this is debugging"}
        return jsonify(**resp)
    else:
        try:
            unique_id = request.form['uniqueId']
            app.logger.info("Marking quitter %s" % unique_id)
            user = Participant.query.\
                filter(Participant.uniqueid == unique_id).\
                one()
            user.status = QUITEARLY
            db_session.add(user)
            db_session.commit()
        except exc.SQLAlchemyError:
            raise ExperimentError('tried_to_quit')
        else:
            resp = {"status": "marked as quitter"}
            return jsonify(**resp)

# Note: This route should only used when debugging
# or when not using the psiturk adserver
@app.route('/complete', methods=['GET'])
@nocache
def debug_complete():
    """ Debugging route for complete. """
    if 'uniqueId' not in request.args:
        raise ExperimentError('improper_inputs')
    else:
        unique_id = request.args['uniqueId']
        mode = request.args['mode']
        try:
            user = Participant.query.\
                filter(Participant.uniqueid == unique_id).one()
            user.status = COMPLETED
            user.endhit = datetime.datetime.now(datetime.timezone.utc)
            db_session.add(user)
            db_session.commit()
        except exc.SQLAlchemyError:
            raise ExperimentError('error_setting_worker_complete')
        else:
            # send them back to mturk.
            if mode == 'sandbox' or mode == 'live':
                return render_template('closepopup.html')
            else:
                allow_repeats = CONFIG.getboolean('Task Parameters', 'allow_repeats')
                return render_template('complete.html',
                                       allow_repeats=allow_repeats,
                                       worker_id=user.workerid)


@app.route('/worker_complete', methods=['GET'])
def worker_complete():
    """ Complete worker. """
    if 'uniqueId' not in request.args:
        resp = {"status": "bad request"}
        return jsonify(**resp)
    else:
        unique_id = request.args['uniqueId']
        app.logger.info("Completed experiment %s" % unique_id)
        try:
            user = Participant.query.\
                filter(Participant.uniqueid == unique_id).one()
            user.status = COMPLETED
            user.endhit = datetime.datetime.now(datetime.timezone.utc)
            db_session.add(user)
            db_session.commit()
            status = "success"
        except exc.SQLAlchemyError:
            status = "database error"
        resp = {"status": status}
        return jsonify(**resp)


@app.route('/worker_submitted', methods=['GET'])
def worker_submitted():
    """ Submit worker """
    if 'uniqueId' not in request.args:
        resp = {"status": "bad request"}
        return jsonify(**resp)
    else:
        unique_id = request.args['uniqueId']
        app.logger.info("Submitted experiment for %s" % unique_id)
        try:
            user = Participant.query.\
                filter(Participant.uniqueid == unique_id).one()
            user.status = SUBMITTED
            db_session.add(user)
            db_session.commit()
            status = "success"
        except exc.SQLAlchemyError:
            status = "database error"
        resp = {"status": status}
        return jsonify(**resp)

# Is this a security risk?
@app.route("/ppid")
def ppid():
    """ Get ppid """
    proc_id = os.getppid()
    return str(proc_id)

# Insert "mode" into pages so it's carried from page to page done server-side
# to avoid breaking backwards compatibility with old templates.


def insert_mode(page_html):
    """ Insert mode """
    page_html = page_html
    match_found = False
    matches = re.finditer('workerId={{ workerid }}', page_html)
    match = None
    for match in matches:
        match_found = True
    if match_found:
        new_html = page_html[:match.end()] + '&mode={{ mode }}' +\
            page_html[match.end():]
        return new_html
    else:
        raise ExperimentError("insert_mode_failed")


# Generic route
# =============

@app.route('/<path:path>')
def regularpage(path):
    """
    Route not found by the other routes above. May point to a static template.
    """
    return send_from_directory('templates', path)


def run_webserver():
    """ Run web server """
    host = CONFIG.get('Server Parameters', 'host')
    port = CONFIG.getint('Server Parameters', 'port')
    print(f"Serving on http://{host}:{port}")
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.run(debug=True, host=host, port=port)


if __name__ == '__main__':
    run_webserver()
