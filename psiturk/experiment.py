import os
import sys
import datetime
import logging
from functools import wraps
from random import choice
try:
    from collections import Counter
except ImportError:
    from counter import Counter

# Importing flask
from flask import Flask, render_template, request, Response, jsonify

# Database setup
from db import db_session, init_db
from models import Participant
from sqlalchemy import or_

from psiturk_config import PsiturkConfig
from experiment_errors import ExperimentError

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
DEBRIEFED = 4
CREDITED = 5
QUITEARLY = 6

###########################################################
# let's start
###########################################################
app = Flask("Experiment_Server")
init_db()  

#----------------------------------------------
# function for authentication
#----------------------------------------------
queryname = config.get('Server Parameters', 'login_username')
querypw = config.get('Server Parameters', 'login_pw')

def wrapper(func, args):
    return func(*args)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == queryname and password == querypw

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    """
    Decorator to prompt for user name and password. Useful for data dumps, etc.
    that you don't want to be public.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

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
    return e.error_page( request )

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
                   filter(or_(Participant.status == 4, 
                              Participant.status == 5, 
                              Participant.beginhit > starttime)).\
                   all()
    counts = Counter()
    for cond in range(numconds):
        for counter in range(numcounts):
            counts[(cond, counter)] = 0
    for p in participants:
        counts[(p.cond, p.counterbalance)] += 1
    mincount = min( counts.values() )
    minima = [hash for hash, count in counts.iteritems() if count == mincount]
    chosen = choice(minima)
    #conds += [ 0 for _ in range(1000) ]
    #conds += [ 1 for _ in range(1000) ]
    app.logger.info( "given %(a)s chose %(b)s" % {'a': counts, 'b': chosen})
    
    return chosen

#----------------------------------------------
# routes
#----------------------------------------------
@app.route('/')
def index():
    return render_template('default.html')

@app.route('/check_worker_status', methods=['GET'])
def check_worker_status():
    if not (request.args.has_key('hitId') and \
            request.args.has_key('assignmentId') and \
            request.args.has_key('workerId')):
        resp = {"status": "bad request"}
        return jsonify(**resp)
    else:
        workerId = request.args['workerId']
        assignmentId = request.args['assignmentId']
        hitId = request.args['hitId']
        try:
            part = Participant.query.\
                   filter(Participant.hitid == hitId).\
                   filter(Participant.assignmentid == assignmentId).\
                   filter(Participant.workerid == workerId).\
                   one()
            status = part.status
        except:
            status = NOT_ACCEPTED
        resp = {"status" : status}
        return jsonify(**resp)


@app.route('/ad', methods=['GET'])
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
    if (not config.getboolean('Task Parameters', 'support_ie')) and request.user_agent.browser == 'msie':
        # Handler for IE users if IE is not supported.
        raise ExperimentError('ie_not_allowed')
    if not (request.args.has_key('hitId') and request.args.has_key('assignmentId')):
        raise ExperimentError('hit_assign_worker_id_not_set_in_mturk')
    hitId = request.args['hitId']
    assignmentId = request.args['assignmentId'] 
    already_in_db = False
    if request.args.has_key('workerId'):
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
    
    if status == STARTED:
        # Once participants have finished the instructions, we do not allow
        # them to start the task again.
        raise ExperimentError('already_started_exp_mturk')
    elif status == COMPLETED:
        # They've done the whole task, but haven't signed the debriefing yet.
        return render_template('debriefing.html', 
                               workerId = workerId,
                               assignmentId = assignmentId)
    elif status == DEBRIEFED:
        # They've done the debriefing but perhaps haven't submitted the HIT yet..
        # Turn asignmentId into original assignment id before sending it back to AMT
        return render_template('thanks.html', 
                               is_sandbox=config.getboolean('HIT Configuration', 'using_sandbox'), 
                               hitid = hitId, 
                               assignmentid = assignmentId, 
                               workerid = workerId)
    elif already_in_db:
        raise ExperimentError('already_did_exp_hit')
    elif status == ALLOCATED or not status:
        # Participant has not yet agreed to the consent. They might not
        # even have accepted the HIT. 
        return render_template('ad.html', 
                               hitid = hitId, 
                               assignmentid = assignmentId, 
                               workerid = workerId)
    else:
        raise ExperimentError('STATUS_INCORRECTLY_SET')

@app.route('/consent', methods=['GET'])
def give_consent():
    """
    Serves up the consent in the popup window.
    """
    if not (request.args.has_key('hitId') and request.args.has_key('assignmentId') and request.args.has_key('workerId')):
        raise ExperimentError('hit_assign_worker_id_not_set_in_consent')
    hitId = request.args['hitId']
    assignmentId = request.args['assignmentId']
    workerId = request.args['workerId']
    return render_template('consent.html', hitid = hitId, assignmentid=assignmentId, workerid=workerId)

@app.route('/exp', methods=['GET'])
def start_exp():
    """
    Serves up the experiment applet.
    """
    if not (request.args.has_key('hitId') and request.args.has_key('assignmentId') and request.args.has_key('workerId')):
        raise ExperimentError( 'hit_assign_worker_id_not_set_in_exp' )
    hitId = request.args['hitId']
    assignmentId = request.args['assignmentId']
    workerId = request.args['workerId']
    app.logger.info( "Accessing /exp: %(h)s %(a)s %(w)s " % {"h" : hitId, "a": assignmentId, "w": workerId})
    
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
        already_entered = False
        nrecords = 0
        for record in matches:
            other_assignment = False
            if record.assignmentid != assignmentId:
                other_assignment = True
            else:
                nrecords += 1
        if nrecords <= 1 and not other_assignment:
            part = matches[0]
            if part.status>=STARTED: # in experiment (or later) can't restart at this point
                raise ExperimentError('already_started_exp')
        else:
            if nrecords > 1:
                app.logger.error( "Error, hit/assignment appears in database more than once (serious problem)")
                raise ExperimentError('hit_assign_appears_in_database_more_than_once')
            if other_assignment:
                raise ExperimentError('already_did_exp_hit')
    
    return render_template('exp.html', uniqueId=part.uniqueid, condition=part.cond, counterbalance=part.counterbalance)

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
    if not request.form.has_key('uniqueId'):
        raise ExperimentError('improper_inputs')
    uniqueId = request.form['uniqueId']

    user = Participant.query.\
            filter(Participant.uniqueid == uniqueId).\
            one()
    user.status = STARTED
    user.beginexp = datetime.datetime.now()
    db_session.add(user)
    db_session.commit()
    return "Success"

# TODD SAYS: this the only route in the whole thing that uses <id> like this
# where everything else uses POST!  This could be confusing but is forced
# somewhat by Backbone?  take heed!
@app.route('/sync/<id>', methods=['GET', 'PUT'])  
def update(id=None):
    """
    Save experiment data, which should be a JSON object and will be stored
    after converting to string.
    """
    app.logger.info("accessing the /sync route with id: %s" % id)
    
    try:
        user = Participant.query.\
                filter(Participant.uniqueid == id).\
                one()
    except:
        app.logger.error( "DB error: Unique user not found.")
    
    if hasattr(request, 'json'):
        user.datastring = request.data
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

@app.route('/debrief', methods=['GET'])
def savedata():
    """
    User has finished the experiment and is posting their data in the form of a
    (long) string. They will receive a debreifing back.
    """
    app.logger.info( request.args.keys())
    if not request.args.has_key('uniqueId'):
        raise ExperimentError('improper_inputs')
    else:
        uniqueId = request.args['uniqueId']
    app.logger.info( "/debrief called with %s" % uniqueId)

    user = Participant.query.\
           filter(Participant.uniqueid == uniqueId).\
           one()

    if config.getboolean('Task Parameters', 'use_debriefing'):
        user.status = COMPLETED
        user.endhit = datetime.datetime.now()
        db_session.add(user)
        db_session.commit()
    
        return render_template('debriefing.html', uniqueId=user.uniqueid)

    else:
        user.status = DEBRIEFED
        user.endhit = datetime.datetime.now()
        db_session.add(user)
        db_session.commit()

        return render_template('closepopup.html')

@app.route('/complete', methods=['POST'])
def completed():
    """
    This is sent in when the participant completes the debriefing. The
    participant can accept the debriefing or declare that they were not
    adequately debriefed, and that response is logged in the database.
    """
    app.logger.info( "accessing the /complete route")
    if not (request.form.has_key('uniqueId') and request.form.has_key('agree')):
        raise ExperimentError('improper_inputs')
    uniqueId = request.form['uniqueId']
    agreed = request.form['agree']
    app.logger.info( uniqueId +  agreed)
    
    user = Participant.query.\
            filter(Participant.uniqueid == uniqueId).\
            one()
    user.status = DEBRIEFED
    user.debriefed = agreed == 'true'
    db_session.add(user)
    db_session.commit()
    return render_template('closepopup.html')

# Is this a security risk?
@app.route("/ppid")
def ppid():
    ppid = os.getppid()
    return str(ppid)

#----------------------------------------------
# generic route
#----------------------------------------------
@app.route('/<pagename>')
def regularpage(pagename=None):
    """
    Route not found by the other routes above. May point to a static template.
    """
    if pagename==None:
        raise ExperimentError('page_not_found')
    return render_template(pagename)



# # Initialize database if necessary
def run_webserver():
    host = "0.0.0.0"
    port = config.getint('Server Parameters', 'port')
    print "Serving on ", "http://" +  host + ":" + str(port)
    app.run(debug=True, host=host, port=port)

if __name__ == '__main__':
    run_webserver()

