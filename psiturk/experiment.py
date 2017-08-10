# -*- coding: utf-8 -*-
""" This module provides the backend Flask server used by psiTurk. """

import os
import sys
import datetime
import logging
from random import choice
import user_agents
import string
import requests
import re
import json

try:
    from collections import Counter
except ImportError:
    from counter import Counter

# Setup flask
from flask import Flask, render_template, render_template_string, request, \
    jsonify

# Setup database
from db import db_session, init_db
from models import Participant
from sqlalchemy import or_, exc

from psiturk_config import PsiturkConfig
from experiment_errors import ExperimentError, InvalidUsage
from psiturk.user_utils import nocache

# Setup config
CONFIG = PsiturkConfig()
CONFIG.load_config()

# Setup logging
if 'ON_HEROKU' in os.environ:
    LOG_FILE_PATH = None
else:
    LOG_FILE_PATH = os.path.join(os.getcwd(), CONFIG.get("Server Parameters", \
    "logfile"))

LOG_LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR,
              logging.CRITICAL]
LOG_LEVEL = LOG_LEVELS[CONFIG.getint('Server Parameters', 'loglevel')]
logging.basicConfig(filename=LOG_FILE_PATH, format='%(asctime)s %(message)s',
                    level=LOG_LEVEL)

# Status codes
NOT_ACCEPTED = 0
ALLOCATED = 1
STARTED = 2
COMPLETED = 3
SUBMITTED = 4
CREDITED = 5
QUITEARLY = 6
BONUSED = 7


# Let's start
# ===========

app = Flask("Experiment_Server")
# Set cache timeout to 10 seconds for static files
app.config.update(SEND_FILE_MAX_AGE_DEFAULT=10)
app.secret_key = CONFIG.get('Server Parameters', 'secret_key')
app.logger.info("Secret key: " + app.secret_key)



# Serving warm, fresh, & sweet custom, user-provided routes
# ==========================================================

try:
    sys.path.append(os.getcwd())
    from custom import custom_code
except ImportError as e:
    if str(e) == 'No module named custom':
        app.logger.info("Hmm... it seems no custom code (custom.py) associated \
                        with this project.")
    else:
        app.logger.error("There is custom code (custom.py) associated with this \
                          project but it doesn't import cleanly.  Raising exception,")
        raise
else:
    app.register_blueprint(custom_code)

init_db()


# Read psiturk.js file into memory
PSITURK_JS_FILE = os.path.join(os.path.dirname(__file__), \
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
    return exception.error_page(request, CONFIG.get('HIT Configuration',
                                                    'contact_email_on_error'))

# for use with API errors
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    app.logger.error(error.message)
    return response

@app.teardown_request
def shutdown_session(_=None):
    ''' Shut down session route '''
    db_session.remove()


# Experiment counterbalancing code
# ================================

def get_random_condcount():
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
    cutofftime = datetime.timedelta(minutes=-CONFIG.getint('Server Parameters',
                                                           'cutoff_time'))
    starttime = datetime.datetime.now() + cutofftime

    numconds = CONFIG.getint('Task Parameters', 'num_conds')
    numcounts = CONFIG.getint('Task Parameters', 'num_counters')

    participants = Participant.query.\
        filter(Participant.codeversion == \
               CONFIG.get('Task Parameters', 'experiment_code_version')).\
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
    minima = [hsh for hsh, count in counts.iteritems() if count == mincount]
    chosen = choice(minima)
    #conds += [ 0 for _ in range(1000) ]
    #conds += [ 1 for _ in range(1000) ]
    app.logger.info("given %(a)s chose %(b)s" % {'a': counts, 'b': chosen})

    return chosen


# Routes
# ======

@app.route('/')
@nocache
def index():
    ''' Index route '''
    return render_template('default.html')


@app.route('/favicon.ico')
def favicon():
    ''' Serve favicon '''
    return app.send_static_file('favicon.ico')

@app.route('/static/js/psiturk.js')
def psiturk_js():
    ''' psiTurk js route '''
    return render_template_string(PSITURK_JS_CODE)

@app.route('/check_worker_status', methods=['GET'])
def check_worker_status():
    ''' Check worker status route '''
    if 'workerId' not in request.args:
        resp = {"status": "bad request"}
        return jsonify(**resp)
    else:
        worker_id = request.args['workerId']
        assignment_id = request.args['assignmentId']
        allow_repeats = CONFIG.getboolean('HIT Configuration', 'allow_repeats')
        if allow_repeats: # if you allow repeats focus on current worker/assignment combo
            try:
                part = Participant.query.\
                    filter(Participant.workerid == worker_id).\
                    filter(Participant.assignmentid == assignment_id).one()
                status = part.status
            except exc.SQLAlchemyError:
                status = NOT_ACCEPTED
        else: # if you disallow repeats search for highest status of anything by this worker
            try:
                matches = Participant.query.\
                    filter(Participant.workerid == worker_id).all()
                numrecs = len(matches)
                if numrecs==0: # this should be caught by exception, but just to be safe
                    status = NOT_ACCEPTED
                else:
                    status = max([record.status for record in matches])
            except exc.SQLAlchemyError:
                status = NOT_ACCEPTED
        resp = {"status" : status}
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
    for rule in string.split(
            CONFIG.get('HIT Configuration', 'browser_exclude_rule'), ','):
        myrule = rule.strip()
        if myrule in ["mobile", "tablet", "touchcapable", "pc", "bot"]:
            if (myrule == "mobile" and user_agent_obj.is_mobile) or\
               (myrule == "tablet" and user_agent_obj.is_tablet) or\
               (myrule == "touchcapable" and user_agent_obj.is_touch_capable) or\
               (myrule == "pc" and user_agent_obj.is_pc) or\
               (myrule == "bot" and user_agent_obj.is_bot):
                browser_ok = False
        elif (myrule == "Safari" or myrule == "safari"):
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

    allow_repeats = CONFIG.getboolean('HIT Configuration', 'allow_repeats')
    if (status == STARTED or status == QUITEARLY) and not debug_mode:
        # Once participants have finished the instructions, we do not allow
        # them to start the task again.
        raise ExperimentError('already_started_exp_mturk')
    elif status == COMPLETED or (status == SUBMITTED and not already_in_db):
        # 'or status == SUBMITTED' because we suspect that sometimes the post
        # to mturk fails after we've set status to SUBMITTED, so really they
        # have not successfully submitted. This gives another chance for the
        # submit to work when not using the psiturk ad server.
        use_psiturk_ad_server = CONFIG.getboolean('Shell Parameters', 'use_psiturk_ad_server')
        if not use_psiturk_ad_server:
            # They've finished the experiment but haven't successfully submitted the HIT
            # yet.
            return render_template(
                'thanks-mturksubmit.html',
                using_sandbox=(mode == "sandbox"),
                hitid=hit_id,
                assignmentid=assignment_id,
                workerid=worker_id
            )
        else: 
            # Show them a thanks message and tell them to go away.
            return render_template( 'thanks.html' )
    elif already_in_db and not (debug_mode or allow_repeats):
        raise ExperimentError('already_did_exp_hit')
    elif status == ALLOCATED or not status or debug_mode:
        # Participant has not yet agreed to the consent. They might not
        # even have accepted the HIT.
        with open('templates/ad.html', 'r') as temp_file:
            ad_string = temp_file.read()
        ad_string = insert_mode(ad_string, mode)
        return render_template_string(
            ad_string,
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
    consent_string = insert_mode(consent_string, mode)
    return render_template_string(
        consent_string,
        hitid=hit_id,
        assignmentid=assignment_id,
        workerid=worker_id
    )

def get_ad_via_hitid(hit_id):
    ''' Get ad via HIT id '''
    username = CONFIG.get('psiTurk Access', 'psiturk_access_key_id')
    password = CONFIG.get('psiTurk Access', 'psiturk_secret_access_id')
    try:
        req = requests.get('https://api.psiturk.org/api/ad/lookup/' + hit_id,
                           auth=(username, password))
    except:
        raise ExperimentError('api_server_not_reachable')
    else:
        if req.status_code == 200:
            return req.json()['ad_id']
        else:
            return "error"

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
        "h" : hit_id,
        "a": assignment_id,
        "w": worker_id
    })
    if hit_id[:5] == "debug":
        debug_mode = True
    else:
        debug_mode = False

    # Check first to see if this hitId or assignmentId exists.  If so, check to
    # see if inExp is set
    allow_repeats = CONFIG.getboolean('HIT Configuration', 'allow_repeats')
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
        subj_cond, subj_counter = get_random_condcount()

        worker_ip = "UNKNOWN" if not request.remote_addr else \
            request.remote_addr
        browser = "UNKNOWN" if not request.user_agent.browser else \
            request.user_agent.browser
        platform = "UNKNOWN" if not request.user_agent.platform else \
            request.user_agent.platform
        language = "UNKNOWN" if not request.user_agent.language else \
            request.user_agent.language

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

    use_psiturk_ad_server = CONFIG.getboolean('Shell Parameters', 'use_psiturk_ad_server')
    if use_psiturk_ad_server and (mode == 'sandbox' or mode == 'live'):
        # If everything goes ok here relatively safe to assume we can lookup
        # the ad.
        ad_id = get_ad_via_hitid(hit_id)
        if ad_id != "error":
            if mode == "sandbox":
                ad_server_location = 'https://sandbox.ad.psiturk.org/complete/'\
                    + str(ad_id)
            elif mode == "live":
                ad_server_location = 'https://ad.psiturk.org/complete/' +\
                str(ad_id)
        else:
            raise ExperimentError('hit_not_registered_with_ad_server')
    else:
        ad_server_location = '/complete'

    return render_template(
        'exp.html', uniqueId=part.uniqueid,
        condition=part.cond,
        counterbalance=part.counterbalance,
        adServerLoc=ad_server_location,
        mode = mode,
        contact_address=CONFIG.get('HIT Configuration', 'contact_email_on_error')
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
    if not 'uniqueId' in request.form:
        raise ExperimentError('improper_inputs')
    unique_id = request.form['uniqueId']

    try:
        user = Participant.query.\
            filter(Participant.uniqueid == unique_id).one()
        user.status = STARTED
        user.beginexp = datetime.datetime.now()
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

    try:
        resp = json.loads(user.datastring)
    except:
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
        app.logger.error("DB error: Unique user not found.")

    if hasattr(request, 'json'):
        user.datastring = request.data.decode('utf-8').encode(
            'ascii', 'xmlcharrefreplace'
        )
        db_session.add(user)
        db_session.commit()

    try:
        data = json.loads(user.datastring)
    except:
        data = {}

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
    ''' Debugging route for complete. '''
    if not 'uniqueId' in request.args:
        raise ExperimentError('improper_inputs')
    else:
        unique_id = request.args['uniqueId']
        mode = request.args['mode']
        try:
            user = Participant.query.\
                filter(Participant.uniqueid == unique_id).one()
            user.status = COMPLETED
            user.endhit = datetime.datetime.now()
            db_session.add(user)
            db_session.commit()
        except:
            raise ExperimentError('error_setting_worker_complete')
        else:
            if (mode == 'sandbox' or mode == 'live'): # send them back to mturk.
                return render_template('closepopup.html')
            else:
                return render_template('complete.html')

@app.route('/worker_complete', methods=['GET'])
def worker_complete():
    ''' Complete worker. '''
    if not 'uniqueId' in request.args:
        resp = {"status": "bad request"}
        return jsonify(**resp)
    else:
        unique_id = request.args['uniqueId']
        app.logger.info("Completed experiment %s" % unique_id)
        try:
            user = Participant.query.\
                filter(Participant.uniqueid == unique_id).one()
            user.status = COMPLETED
            user.endhit = datetime.datetime.now()
            db_session.add(user)
            db_session.commit()
            status = "success"
        except exc.SQLAlchemyError:
            status = "database error"
        resp = {"status" : status}
        return jsonify(**resp)

@app.route('/worker_submitted', methods=['GET'])
def worker_submitted():
    ''' Submit worker '''
    if not 'uniqueId' in request.args:
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
        resp = {"status" : status}
        return jsonify(**resp)

# Is this a security risk?
@app.route("/ppid")
def ppid():
    ''' Get ppid '''
    proc_id = os.getppid()
    return str(proc_id)

# Insert "mode" into pages so it's carried from page to page done server-side
# to avoid breaking backwards compatibility with old templates.
def insert_mode(page_html, mode):
    ''' Insert mode '''
    page_html = page_html.decode("utf-8")
    match_found = False
    matches = re.finditer('workerId={{ workerid }}', page_html)
    match = None
    for match in matches:
        match_found = True
    if match_found:
        new_html = page_html[:match.end()] + "&mode=" + mode +\
            page_html[match.end():]
        return new_html
    else:
        raise ExperimentError("insert_mode_failed")


# Generic route
# =============

@app.route('/<pagename>')
@app.route('/<foldername>/<pagename>')
def regularpage(foldername=None, pagename=None):
    """
    Route not found by the other routes above. May point to a static template.
    """
    if foldername is None and pagename is None:
        raise ExperimentError('page_not_found')
    if foldername is None and pagename is not None:
        return render_template(pagename)
    else:
        return render_template(foldername+"/"+pagename)

def run_webserver():
    ''' Run web server '''
    host = "0.0.0.0"
    port = CONFIG.getint('Server Parameters', 'port')
    print "Serving on ", "http://" +  host + ":" + str(port)
    app.run(debug=True, host=host, port=port)

if __name__ == '__main__':
    run_webserver()
