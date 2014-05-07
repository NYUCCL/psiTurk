import os
import sys
import datetime
import logging
from random import choice
import user_agents
import string
import requests
try:
    from collections import Counter
except ImportError:
    from counter import Counter

# Importing flask
from flask import Flask, render_template, render_template_string, request, jsonify

# Database setup
from db import db_session, init_db
from models import Participant
from sqlalchemy import or_

from psiturk_config import PsiturkConfig
from experiment_errors import ExperimentError
from psiturk.user_utils import nocache

config = PsiturkConfig()
config.load_config()

# Set up logging
logfilepath = os.path.join(os.getcwd(),
                           config.get("Server Parameters", "logfile"))

loglevels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
loglevel = loglevels[config.getint('Server Parameters', 'loglevel')]
logging.basicConfig( filename=logfilepath, format='%(asctime)s %(message)s', level=loglevel )


# Status codes
NOT_ACCEPTED = 0
ALLOCATED = 1
STARTED = 2
COMPLETED = 3
SUBMITTED = 4
CREDITED = 5
QUITEARLY = 6
BONUSED = 7

###########################################################
# let's start
###########################################################
app = Flask("Experiment_Server")
def start_app(sandbox):
    global sandbox_bool
    sandbox_bool = sandbox
    return app
app.config.update(SEND_FILE_MAX_AGE_DEFAULT=10) # set cache timeout to 10ms for static files

###########################################################
#  serving warm, fresh, & sweet custom, user-provided routes
###########################################################

try:
    sys.path.append(os.getcwd())
    from custom import custom_code
except ImportError:
    app.logger.info( "Hmm... it seems no custom code (custom.py) assocated with this project.")
else:
    app.register_blueprint(custom_code)

try:
    sys.path.append(os.getcwd())
    from custom_models import *
except ImportError:
    app.logger.info( "Hmm... it seems no custom model code (custom_models.py) assocated with this project.")

init_db()

# read psiturk.js file into memory
psiturk_js_file = os.path.join(os.path.dirname(__file__), "psiturk_js/psiturk.js")
app.logger.error( psiturk_js_file )

if os.path.exists(psiturk_js_file):
    psiturk_js_code = open(psiturk_js_file).read()
else:
    psiturk_js_code = "alert('psiturk.js file not found!');"

#----------------------------------------------
# favicon
#----------------------------------------------
@app.route('/favicon.ico')
def favicon():
    """
    Serving a favicon
    """
    return app.send_static_file('favicon.ico')

@app.errorhandler(ExperimentError)
def handleExpError(e):
    """Handle errors by sending an error page."""
    return e.error_page( request, config.get('HIT Configuration', 'contact_email_on_error') )

@app.route('/static/js/psiturk.js')
def psiturk_js():
    return render_template_string(psiturk_js_code)

#----------------------------------------------
# DB setup
#----------------------------------------------
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

#----------------------------------------------
# Experiment counterbalancing code.
#----------------------------------------------
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
    cutofftime = datetime.timedelta(minutes=-config.getint('Server Parameters', 'cutoff_time'))
    starttime = datetime.datetime.now() + cutofftime

    numconds = config.getint('Task Parameters', 'num_conds')
    numcounts = config.getint('Task Parameters', 'num_counters')

    participants = Participant.query.\
                   filter(Participant.codeversion == config.get('Task Parameters', 'experiment_code_version')).\
                   filter(or_(Participant.status == COMPLETED,
                              Participant.status == CREDITED,
                              Participant.status == SUBMITTED,
                              Participant.status == BONUSED,
                              Participant.beginhit > starttime)).\
                   all()
    counts = Counter()
    for cond in range(numconds):
        for counter in range(numcounts):
            counts[(cond, counter)] = 0
    for p in participants:
        counts[(p.cond, p.counterbalance)] += 1
    mincount = min( counts.values() )
    minima = [hsh for hsh, count in counts.iteritems() if count == mincount]
    chosen = choice(minima)
    #conds += [ 0 for _ in range(1000) ]
    #conds += [ 1 for _ in range(1000) ]
    app.logger.info( "given %(a)s chose %(b)s" % {'a': counts, 'b': chosen})

    return chosen

#----------------------------------------------
# routes
#----------------------------------------------
@app.route('/')
@nocache
def index():
    return render_template('default.html')

@app.route('/check_worker_status', methods=['GET'])
def check_worker_status():
    if 'workerId' not in request.args:
        resp = {"status": "bad request"}
        return jsonify(**resp)
    else:
        workerId = request.args['workerId']
        try:
            part = Participant.query.\
                   filter(Participant.workerid == workerId).\
                   one()
            status = part.status
        except:
            status = NOT_ACCEPTED
        resp = {"status" : status}
        return jsonify(**resp)


@app.route('/ad', methods=['GET'])
@nocache
def advertisement():
    """
    This is the url we give for the ad for our 'external question'.
    The ad has to display two different things:
    This page will be called from within mechanical turk, with url arguments
    hitId, assignmentId, and workerId.
    If the worker has not yet accepted the hit:
      These arguments will have null values, we should just show an ad for the
      experiment.
    If the worker has accepted the hit:
      These arguments will have appropriate values and we should enter the person
      in the database and provide a link to the experiment popup.
    """
    user_agent_string = request.user_agent.string
    user_agent_obj = user_agents.parse(user_agent_string)
    browser_ok = True
    for rule in string.split(config.get('HIT Configuration', 'browser_exclude_rule'),','):
        myrule = rule.strip()
        if myrule in ["mobile","tablet","touchcapable","pc","bot"]:
            if (myrule == "mobile" and user_agent_obj.is_mobile) or \
               (myrule == "tablet" and user_agent_obj.is_tablet) or \
               (myrule == "touchcapable" and user_agent_obj.is_touch_capable) or \
               (myrule == "pc" and user_agent_obj.is_pc) or \
               (myrule == "bot" and user_agent_obj.is_bot):
                browser_ok = False
        elif myrule in user_agent_string:
            browser_ok = False

    if not browser_ok:
        # Handler for IE users if IE is not supported.
        raise ExperimentError('browser_type_not_allowed')

    if not ('hitId' in request.args and 'assignmentId' in request.args):
        raise ExperimentError('hit_assign_worker_id_not_set_in_mturk')
    hitId = request.args['hitId']
    assignmentId = request.args['assignmentId']
    if hitId[:5] == "debug":
        debug_mode = True
    else:
        debug_mode = False
    already_in_db = False
    if 'workerId' in request.args:
        workerId = request.args['workerId']
        # first check if this workerId has completed the task before (v1)
        nrecords = Participant.query.\
                   filter(Participant.assignmentid != assignmentId).\
                   filter(Participant.workerid == workerId).\
                   count()

        if nrecords > 0:
            # already completed task
            already_in_db = True
    else:
        # If worker has not accepted the hit:
        workerId = None
    try:
        part = Participant.query.\
                           filter(Participant.hitid == hitId).\
                           filter(Participant.assignmentid == assignmentId).\
                           filter(Participant.workerid == workerId).\
                           one()
        status = part.status
    except:
        status = None

    if status == STARTED and not debug_mode:
        # Once participants have finished the instructions, we do not allow
        # them to start the task again.
        raise ExperimentError('already_started_exp_mturk')
    elif status == COMPLETED:
        # They've done the debriefing but perhaps haven't submitted the HIT yet..
        # Turn asignmentId into original assignment id before sending it back to AMT
        return render_template('thanks.html',
                               is_sandbox = sandbox_bool,
                               hitid = hitId,
                               assignmentid = assignmentId,
                               workerid = workerId)
    elif already_in_db and not debug_mode:
        raise ExperimentError('already_did_exp_hit')
    elif status == ALLOCATED or not status or debug_mode:
        # Participant has not yet agreed to the consent. They might not
        # even have accepted the HIT.
        return render_template('ad.html',
                               hitid = hitId,
                               assignmentid = assignmentId,
                               workerid = workerId)
    else:
        raise ExperimentError('status_incorrectly_set')

@app.route('/consent', methods=['GET'])
@nocache
def give_consent():
    """
    Serves up the consent in the popup window.
    """
    if not ('hitId' in request.args and 'assignmentId' in request.args and 'workerId' in request.args):
        raise ExperimentError( 'hit_assign_worker_id_not_set_in_consent')
    hitId = request.args['hitId']
    assignmentId = request.args['assignmentId']
    workerId = request.args['workerId']
    return render_template('consent.html', hitid = hitId, assignmentid=assignmentId, workerid=workerId)

def get_ad_via_hitid(hitId):
    username = config.get('psiTurk Access', 'psiturk_access_key_id')
    password = config.get('psiTurk Access', 'psiturk_secret_access_id')
    try:
        r = requests.get('https://api.psiturk.org/api/ad/lookup/' + hitId, auth=(username,password))
    except:
        raise ExperimentError('api_server_not_reachable')
    else:
        if r.status_code == 200:
            return r.json()['ad_id']
        else:
            return "error"

@app.route('/exp', methods=['GET'])
@nocache
def start_exp():
    """
    Serves up the experiment applet.
    """
    if not ('hitId' in request.args and 'assignmentId' in request.args and 'workerId' in request.args):
        raise ExperimentError( 'hit_assign_worker_id_not_set_in_exp')
    hitId = request.args['hitId']
    assignmentId = request.args['assignmentId']
    workerId = request.args['workerId']
    app.logger.info( "Accessing /exp: %(h)s %(a)s %(w)s " % {"h" : hitId, "a": assignmentId, "w": workerId})
    if hitId[:5] == "debug":
        debug_mode = True
    else:
        debug_mode = False

    # check first to see if this hitId or assignmentId exists.  if so check to see if inExp is set
    matches = Participant.query.\
                        filter(Participant.workerid == workerId).\
                        all()
    numrecs = len(matches)
    if numrecs == 0:
        # Choose condition and counterbalance
        subj_cond, subj_counter = get_random_condcount()

        ip = "UNKNOWN" if not request.remote_addr else request.remote_addr
        browser = "UNKNOWN" if not request.user_agent.browser else request.user_agent.browser
        platform = "UNKNOWN" if not request.user_agent.platform else request.user_agent.platform
        language = "UNKNOWN" if not request.user_agent.language else request.user_agent.language

        # set condition here and insert into database
        participant_attributes = dict(
            assignmentid = assignmentId,
            workerid = workerId,
            hitid = hitId,
            cond = subj_cond,
            counterbalance = subj_counter,
            ipaddress = ip,
            browser = browser,
            platform = platform,
            language = language)
        part = Participant(**participant_attributes)
        db_session.add(part)
        db_session.commit()

    else:
        # A couple possible problems here:
        # 1: They've already done an assignment, then we should tell them they can't do another one
        # 2: They've already worked on this assignment, and got too far to start over.
        # 3: They're in the database twice for the same assignment, that should never happen.
        # 4: They're returning and all is well.
        nrecords = 0
        for record in matches:
            other_assignment = False
            if record.assignmentid != assignmentId:
                other_assignment = True
            else:
                nrecords += 1
        if nrecords <= 1 and not other_assignment:
            part = matches[0]
            if part.status>=STARTED and not debug_mode: # in experiment (or later) can't restart at this point
                raise ExperimentError('already_started_exp')
        else:
            if nrecords > 1:
                app.logger.error( "Error, hit/assignment appears in database more than once (serious problem)")
                raise ExperimentError('hit_assign_appears_in_database_more_than_once')
            if other_assignment:
                raise ExperimentError('already_did_exp_hit')

    if debug_mode:
        ad_server_location = '/complete'
    else:
        # if everything goes ok here relatively safe to assume we can lookup the ad
        ad_id = get_ad_via_hitid(hitId)
        if ad_id != "error":
            if sandbox_bool:
                ad_server_location = 'https://sandbox.ad.psiturk.org/complete/' + str(ad_id)
            else:
                ad_server_location = 'https://ad.psiturk.org/complete/' + str(ad_id)
        else:
            raise ExperimentError('hit_not_registered_with_ad_server')

    return render_template('exp.html', uniqueId=part.uniqueid, condition=part.cond, counterbalance=part.counterbalance, adServerLoc=ad_server_location)

@app.route('/inexp', methods=['POST'])
def enterexp():
    """
    AJAX listener that listens for a signal from the user's script when they
    leave the instructions and enter the real experiment. After the server
    receives this signal, it will no longer allow them to re-access the
    experiment applet (meaning they can't do part of the experiment and
    referesh to start over).
    """
    app.logger.info( "Accessing /inexp")
    if not 'uniqueId' in request.form:
        raise ExperimentError('improper_inputs')
    uniqueId = request.form['uniqueId']

    try:
        user = Participant.query.\
                filter(Participant.uniqueid == uniqueId).\
                one()
        user.status = STARTED
        user.beginexp = datetime.datetime.now()
        db_session.add(user)
        db_session.commit()
        resp = {"status": "success"}
    except:
        app.logger.error( "DB error: Unique user not found.")
        resp = {"status": "error, uniqueId not found"}
    return jsonify(**resp)

# TODD SAYS: this the only route in the whole thing that uses <id> like this
# where everything else uses POST!  This could be confusing but is forced
# somewhat by Backbone?  take heed!
@app.route('/sync/<uid>', methods=['GET', 'PUT'])
def update(uid=None):
    """
    Save experiment data, which should be a JSON object and will be stored
    after converting to string.
    """
    app.logger.info("accessing the /sync route with id: %s" % uid)

    try:
        user = Participant.query.\
                filter(Participant.uniqueid == uid).\
                one()
    except:
        app.logger.error( "DB error: Unique user not found.")

    if hasattr(request, 'json'):
        user.datastring = request.data.decode('utf-8').encode('ascii', 'xmlcharrefreplace')
        db_session.add(user)
        db_session.commit()

    resp = {"condition": user.cond,
            "counterbalance": user.counterbalance,
            "assignmentId": user.assignmentid,
            "workerId": user.workerid,
            "hitId": user.hitid}

    return jsonify(**resp)

@app.route('/quitter', methods=['POST'])
def quitter():
    """
    Mark quitter as such.
    """
    uniqueId = request.form['uniqueId']
    if uniqueId[:5] == "debug":
        debug_mode = True
    else:
        debug_mode = False

    if debug_mode:
        resp = {"status": "didn't mark as quitter since this is debugging"}
        return jsonify(**resp)
    else:
        try:
            uniqueId = request.form['uniqueId']
            app.logger.info( "Marking quitter %s" % uniqueId)
            user = Participant.query.\
                    filter(Participant.uniqueid == uniqueId).\
                    one()
            user.status = QUITEARLY
            db_session.add(user)
            db_session.commit()
        except:
            raise ExperimentError('tried_to_quit')
        else:
            resp = {"status": "marked as quitter"}
            return jsonify(**resp)

# this route should only used when debugging
@app.route('/complete', methods=['GET'])
@nocache
def debug_complete():
    if not 'uniqueId' in request.args:
        raise ExperimentError('improper_inputs')
    else:
        uniqueId = request.args['uniqueId']
        try:
            user = Participant.query.\
                        filter(Participant.uniqueid == uniqueId).\
                        one()
            user.status = COMPLETED
            user.endhit = datetime.datetime.now()
            db_session.add(user)
            db_session.commit()
        except:
            raise ExperimentError('error_setting_worker_complete')
        else:
            return render_template('complete.html')

@app.route('/worker_complete', methods=['GET'])
def worker_complete():
    if not 'uniqueId' in request.args:
        resp = {"status": "bad request"}
        return jsonify(**resp)
    else:
        uniqueId = request.args['uniqueId']
        app.logger.info( "Completed experiment %s" % uniqueId)
        try:
            user = Participant.query.\
                        filter(Participant.uniqueid == uniqueId).\
                        one()
            user.status = COMPLETED
            user.endhit = datetime.datetime.now()
            db_session.add(user)
            db_session.commit()
            status = "success"
        except:
            status = "database error"
        resp = {"status" : status}
        return jsonify(**resp)

@app.route('/worker_submitted', methods=['GET'])
def worker_submitted():
    if not 'uniqueId' in request.args:
        resp = {"status": "bad request"}
        return jsonify(**resp)
    else:
        uniqueId = request.args['uniqueId']
        app.logger.info( "Submitted experiment for %s" % uniqueId)
        try:
            user = Participant.query.\
                        filter(Participant.uniqueid == uniqueId).\
                        one()
            user.status = SUBMITTED
            db_session.add(user)
            db_session.commit()
            status = "success"
        except:
            status = "database error"
        resp = {"status" : status}
        return jsonify(**resp)

# Is this a security risk?
@app.route("/ppid")
def ppid():
    ppid = os.getppid()
    return str(ppid)

#----------------------------------------------
# generic route
#----------------------------------------------
@app.route('/<pagename>')
@app.route('/<foldername>/<pagename>')
def regularpage(foldername=None,pagename=None):
    """
    Route not found by the other routes above. May point to a static template.
    """
    if foldername is None and pagename is None:
        raise ExperimentError('page_not_found')
    if foldername is None and pagename is not None:
        return render_template(pagename)
    else:
        return render_template(foldername+"/"+pagename)

# # Initialize database if necessary
def run_webserver():
    host = "0.0.0.0"
    port = config.getint('Server Parameters', 'port')
    print "Serving on ", "http://" +  host + ":" + str(port)
    app.run(debug=True, host=host, port=port)

if __name__ == '__main__':
    run_webserver()
