from flask import Flask, render_template, request, Response
from string import split
import datetime
from random import choice, shuffle, seed, getstate, setstate
import sys
from functools import wraps



# constants
DEPLOYMENT_ENV = 'sandbox'  # 'sandbox' or 'deploy' (the real thing)  MOVE TO CONFIG
CODE_VERSION = '1'          # MOVE TO CONFIG
CUTOFFTIME = 30  # Minutes after starting when a participnat is assumed to have timed out.  MOVE TO CONFIG


# For easy debugging
if DEPLOYMENT_ENV == 'sandbox':
    MAXBLOCKS = 2
else:
    MAXBLOCKS = 15

TESTINGPROBLEMSIX = False

# Database configuration and constants
#DATABASE = 'mysql://user:password@domain:port/dbname'
DATABASE = 'sqlite://'  # MOVE TO CONFIG
TABLENAME = 'turkdemo'  # MOVE TO CONFIG
SUPPORTIE = True        # MOVE TO CONFIG

NUMCONDS = 1
NUMCOUNTERS = 2
ALLOCATED = 1
STARTED = 2
COMPLETED = 3
DEBRIEFED = 4
CREDITED = 5
QUITEARLY = 6

# error codes
STATUS_INCORRECTLY_SET = 1000
HIT_ASSIGN_WORKER_ID_NOT_SET_IN_MTURK = 1001
HIT_ASSIGN_WORKER_ID_NOT_SET_IN_CONSENT = 1002
HIT_ASSIGN_WORKER_ID_NOT_SET_IN_EXP = 1003
HIT_ASSIGN_APPEARS_IN_DATABASE_MORE_THAN_ONCE = 1004
IN_EXP_ACCESSED_WITHOUT_POST = 1005
DEBRIEF_ACCESSED_WITHOUT_POST = 1006
COMPLETE_ACCESSED_WITHOUT_POST = 1007
ALREADY_STARTED_EXP = 1008
ALREADY_STARTED_EXP_MTURK = 1009
ALREADY_DID_EXP_HIT = 1010
TRIED_TO_QUIT= 1011
INTERMEDIATE_SAVE = 1012
PAGE_NOT_FOUND = 404

IN_DEBUG = 2005

app = Flask(__name__)


#----------------------------------------------
# function for authentication
#----------------------------------------------
queryname = "examplename"   # MOVE TO CONFIG
querypw = "examplepass"     # MOVE TO CONFIG

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
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


#----------------------------------------------
# general utilities
#----------------------------------------------
def get_people(people):
    people=[]
    for record in people:
        person = {}
        for field in ['subjid', 'ipaddress', 'hitid', 'assignmentid',
                      'workerid', 'cond', 'counterbalance',
                      'beginhit','beginexp', 'endhit', 'status', 'datafile']:
            if field=='datafile':
                if record[field] == None:
                    person[field] = "Nothing yet"
                else:
                    person[field] = record[field][:10]
            else:
                person[field] = record[field]
        people.append( person )
    return people

#----------------------------------------------
# Define database class
#----------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy import or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
Base = declarative_base()

class Participant(Base):
    __tablename__ = TABLENAME
    
    subjid = Column( Integer, primary_key = True )
    ipaddress = Column(String),
    hitid = Column(String),
    assignmentid =Column(String),
    workerid = Column(String),
    cond = Column(Integer),
    counterbalance = Column(Integer),
    codeversion = Column(String),
    beginhit = Column(DateTime, nullable=True),
    beginexp = Column(DateTime, nullable=True),
    endhit = Column(DateTime, nullable=True),
    status = Column(Integer, default = ALLOCATED),
    debriefed = Column(Boolean),
    datafile = Column(Text, nullable=True),  #the data from the exp
    
    def __init__(self, hitid, ipaddress, assignmentid, workerid, cond, counterbalance):
        self.hitid = hitid
        self.ipaddress = ipaddress
        self.assignmentid = assignmentid
        self.workerid = workerid
        self.cond = cond
        self.counterbalance = counterbalance
        self.status = ALLOCATED
        self.codeversion = CODE_VERSION
        self.debriefed = False
        self.beginhit = datetime.datetime.now()
    
    def __repr__( self ):
        return "Subject(%r, %r)" % ( self.subjid, self.status )

#----------------------------------------------
# Experiment counterbalancing code.
#----------------------------------------------
def get_random_condition(session):
    """
    HITs can be in one of three states:
        - jobs that are finished
        - jobs that are started but not finished
        - jobs that are never going to finish (user decided not to do it)
    Our count should be based on the first two, so we count any tasks finished
    or any tasks not finished that were started in the last 30 minutes.
    """
    starttime = datetime.datetime.now() + datetime.timedelta(minutes=-CUTOFFTIME)
    counts = [0]*NUMCONDS
    for partcond in session.query(Participant.cond).\
                    filter(Participant.codeversion == CODE_VERSION).\
                    filter(or_(Participant.endhit != None, Participant.beginhit > starttime)):
        counts[partcond] += 1
    
    # choose randomly from the ones that have the least in them (so will tend to fill in evenly)
    indices = [i for i, x in enumerate(counts) if x == min(counts)]
    rstate = getstate()
    seed()
    subj_cond = choice(indices)
    setstate(rstate)
    return subj_cond

def get_random_counterbalance(session):
    starttime = datetime.datetime.now() + datetime.timedelta(minutes=-30)
    session = Session()
    counts = [0]*NUMCOUNTERS
    for partcount in session.query(Participant.counterbalance).\
                     filter(Participant.codeversion == CODE_VERSION).\
                     filter(or_(Participant.endhit != None, Participant.beginhit > starttime)):
        counts[partcount] += 1
    
    # choose randomly from the ones that have the least in them (so will tend to fill in evenly)
    indices = [i for i, x in enumerate(counts) if x == min(counts)]
    rstate = getstate()
    seed()
    subj_counter = choice(indices)
    setstate(rstate)
    return subj_counter

#----------------------------------------------
# routes
#----------------------------------------------

@app.route('/debug', methods=['GET'])
def start_exp_debug():
    # this serves up the experiment applet in debug mode
    if "cond" in request.args.keys():
        subj_cond = int( request.args['cond'] );
    else:
        import random
        subj_cond = random.randrange(12);
    if "subjid" in request.args.keys():
        counterbalance = int( request.args['counterbalance'] );
    else:
        import random
        counterbalance = random.randrange(384);
    return render_template('exp.html', 
                           subj_num = -1, 
                           traintype = 0 if subj_cond<6 else 1, 
                           rule = subj_cond%6, 
                           dimorder = counterbalance%24, 
                           dimvals = counterbalance//24,
                           skipto = request.args['skipto'] if 'skipto' in request.args else ''
                          )

@app.route('/mturk', methods=['GET'])
def mturkroute():
    """
    This is the url we give for our 'external question'.
    This page will be called from within mechanical turk, with url arguments
    hitId, assignmentId, and workerId. 
    If the worker has not yet accepted the hit:
      These arguments will have null values, we should just show an ad for the
      experiment.
    If the worker has accepted the hit:
      These arguments will have appropriate values and we should enter the person
      in the database and provide a link to the experiment popup.
    """
    if not SUPPORTIE:
        # Handler for IE users if IE is not supported.
        if request.user_agent.browser == "msie":
            return render_template( 'ie.html' )
    
    if request.args.has_key('hitId') and request.args.has_key('assignmentId'):
        # Person has accepted the HIT, entering them into the database.
        session = Session()
        hitID = request.args['hitId']
        assignmentID = request.args['assignmentId']
        if request.args.has_key('workerId'):
            workerID = request.args['workerId']
            # first check if this workerId has completed the task before (v1)
            numrecs = session.query(Participant.subjid).\
                       filter(Participant.workerid == workerID).\
                       matches()
            
            # Note about old code: Referencing the hitId is actually
            # problematic here, the same experiment could be posted on
            # different HITs
            #s = s.where(and_(participantsdb.c.hitid!=hitID, participantsdb.c.workerid==workerID))
            
            if numrecs != 0:
                # already completed task
                return render_template('error.html', 
                                       errornum=ALREADY_DID_EXP_HIT, 
                                       hitid=request.args['hitId'], 
                                       assignid=request.args['assignmentId'], 
                                       workerid=request.args['workerId'])
        else:
            # If worker has not accepted the hit:
            workerID = None # WARNING was '-1', should be fine but if this crashes on the home screen could be my fault here.
        print hitID, assignmentID, workerID
        status, subj_id = session.query(Participant.status, Participant.subjid).\
                            filter(Participant.hitid == hitID).\
                            filter(Participant.assignmentid == assignmentID).\
                            filter(Participant.workerid == workerID).one()
        
        if status == ALLOCATED or not status:
            # Participant has not yet agreed to the consent. They might not
            # even have accepted the HIT. The mturkindex template will treat
            # them appropriately regardless.
            return render_template('mturkindex.html', 
                                   hitid = hitID, 
                                   assignmentid = assignmentID, 
                                   workerid = workerID)
        elif status == STARTED:
            # Once participants have finished the instructions, we do not allow
            # them to start the task again.
            return render_template('error.html', 
                                   errornum=ALREADY_STARTED_EXP_MTURK, 
                                   hitid=request.args['hitId'], 
                                   assignid=request.args['assignmentId'], 
                                   workerid=request.args['workerId'])
        elif status == COMPLETED:
            # They've done the whole task, but haven't signed the debriefing yet.
            return render_template('debriefing.html', 
                                   subjid = subj_id)
        elif status == DEBRIEFED:
            # They've done the debriefing but perhaps haven't submitted the HIT yet..
            return render_template('thanks.html', 
                                   target_env=DEPLOYMENT_ENV, 
                                   hitid = hitID, 
                                   assignmentid = assignmentID, 
                                   workerid = workerID)
        else:
            # Hopefully this won't happen.
            return render_template('error.html', 
                                   errornum=STATUS_INCORRECTLY_SET, 
                                   hitid=request.args['hitId'], 
                                   assignid=request.args['assignmentId'], 
                                   workerid=request.args['workerId'])
    else:
        return render_template('error.html', errornum=HIT_ASSIGN_WORKER_ID_NOT_SET_IN_MTURK)

@app.route('/consent', methods=['GET'])
def give_consent():
    """
    Serves up the consent in the popup window.
    """
    if request.args.has_key('hitId') and request.args.has_key('assignmentId') and request.args.has_key('workerId'):
        hitID = request.args['hitId']
        assignmentID = request.args['assignmentId']
        workerID = request.args['workerId']
        print hitID, assignmentID, workerID
        return render_template('consent.html', hitid = hitID, assignmentid=assignmentID, workerid=workerID)
    else:
        return render_template('error.html', errornum=HIT_ASSIGN_WORKER_ID_NOT_SET_IN_CONSENT)

@app.route('/exp', methods=['GET'])
def start_exp():
    """
    Serves up the experiment applet.
    """
    if request.args.has_key('hitId') and request.args.has_key('assignmentId') and request.args.has_key('workerId'):
        hitID = request.args['hitId']
        assignmentID = request.args['assignmentId']
        workerID = request.args['workerId']
        print hitID, assignmentID, workerID
        
        
        # check first to see if this hitID or assignmentID exists.  if so check to see if inExp is set
        session = Session()
        matches = session.query(Participant.subjid, Participant.cond, Participant.counterbalance, Participant.status).\
                            filter(Participant.hitid == hitID).\
                            filter(Participant.assignmentid == assignmentID).\
                            filter(Participant.workerid == workerID).all()
        numrecs = len(matches)
        if numrecs == 0:
            
            # doesn't exist, get a histogram of completed conditions and choose an under-used condition
            subj_cond = get_random_condition(session)
            
            # doesn't exist, get a histogram of completed counterbalanced, and choose an under-used one
            subj_counter = get_random_counterbalance(session)
            
            if not request.remote_addr:
                myip = "UKNOWNIP"
            else:
                myip = request.remote_addr
            
            # set condition here and insert into database
            newpart = Participant( hitID, myip, assignmentID, workerID, subj_cond, subj_counter)
            session.add( newpart )
            session.commit()
            myid = newpart.subjid
        
        elif numrecs==1:
            myid, subj_cond, subj_counter, status = matches[0]
            if status>=STARTED: # in experiment (or later) can't restart at this point
                return render_template('error.html', errornum=ALREADY_STARTED_EXP, hitid=request.args['hitId'], assignid=request.args['assignmentId'], workerid=request.args['workerId'])
        else:
            print "Error, hit/assignment appears in database more than once (serious problem)"
            return render_template('error.html', errornum=HIT_ASSIGN_APPEARS_IN_DATABASE_MORE_THAN_ONCE, hitid=request.args['hitId'], assignid=request.args['assignmentId'], workerid=request.args['workerId'])
        
        dimo, dimv = counterbalanceconds[subj_counter]
        return render_template('exp.html', subj_num = myid, order=subj_counter )
    else:
        return render_template('error.html', errornum=HIT_ASSIGN_WORKER_ID_NOT_SET_IN_EXP)

@app.route('/inexp', methods=['POST'])
def enterexp():
    """
    AJAX listener that listens for a signal from the user's script when they
    leave the instructions and enter the real experiment. After the server
    receives this signal, it will no longer allow them to re-access the
    experiment applet (meaning they can't do part of the experiment and
    referesh to start over).
    """
    print "accessing /inexp"
    if request.method == 'POST':
        if request.form.has_key('subjId'):
            subjid = request.form['subjId']
            session = Session()
            user = session.query(Participant).\
                    filter(Participant.subjid == subjid).\
                    one()
            user.status = STARTED
            user.beginexp = datetime.datetime.now()
            session.commit()
    else:
        return render_template('error.html', errornum=IN_EXP_ACCESSED_WITHOUT_POST)

@app.route('/inexpsave', methods=['POST'])
def inexpsave():
    """
    The experiments script updates the server periodically on subjects'
    progress. This lets us better understand attrition.
    """
    print "accessing the /inexpsave route"
    if request.method == 'POST':
        print request.form.keys()
        if request.form.has_key('subjId') and request.form.has_key('dataString'):
            subj_id = request.form['subjId']
            datastring = request.form['dataString']  
            print "getting the save data", subj_id, datastring
            session = Session()
            user = session.query(Participant).\
                    filter(Participant.subjid == subjid).\
                    one()
            user.datafile = datastring
            user.status = STARTED
            session.commit()
    return render_template('error.html', errornum=INTERMEDIATE_SAVE)

@app.route('/quitter', methods=['POST'])
def quitter():
    """
    Subjects post data as they quit, to help us better understand the quitters.
    """
    print "accessing the /quitter route"
    if request.method == 'POST':
        print request.form.keys()
        if request.form.has_key('subjId') and request.form.has_key('dataString'):
            subjid = request.form['subjId']
            datastring = request.form['dataString']  
            print "getting the save data", subjid, datastring
            session = Session()
            user = session.query(Participant).\
                    filter(Participant.subjid == subjid).\
                    one()
            user.datafile = datastring
            user.status = QUITEARLY
            session.commit()
    return render_template('error.html', errornum=TRIED_TO_QUIT)

@app.route('/debrief', methods=['POST', 'GET'])
def savedata():
    """
    User has finished the experiment and is posting their data in the form of a
    (long) string. They will receive a debreifing back.
    """
    print request.form.keys()
    if request.form.has_key('subjid') and request.form.has_key('data'):
        subjid = int(request.form['subjid'])
        datastring = request.form['data']
        print subjid, datastring
        
        session = Session()
        user = session.query(Participant).\
                filter(Participant.subjid == subjid).\
                one()
        user.status = COMPLETED
        user.datafile = datastring
        user.endhit = datetime.datetime.now()
        session.commit()
        
        return render_template('debriefing.html', subjid=subjid)

@app.route('/complete', methods=['POST'])
def completed():
    """
    This is sent in when the participant completes the debriefing. The
    participant can accept the debriefing or declare that they were not
    adequately debriefed, and that response is logged in the database.
    """
    print "accessing the /complete route"
    if request.method == 'POST':
        print request.form.keys()
        if request.form.has_key('subjid') and request.form.has_key('agree'):
            subjid = request.form['subjid']
            agreed = request.form['agree']  
            print subjid, agreed
            
            session = Session()
            user = session.query(Participant).\
                    filter(Participant.subjid == subjid).\
                    one()
            user.status = DEBRIEFED
            user.debriefed = agreed
            
            return render_template('closepopup.html')
    return render_template('error.html', errornum=COMPLETE_ACCESSED_WITHOUT_POST)


#------------------------------------------------------
# routes for displaying the database/editing it in html
#------------------------------------------------------
@app.route('/list')
@requires_auth
def viewdata():
    """
    Gives a page providing a readout of the database. Requires password
    authentication.
    """
    session = Session()
    people = session.query(Participant).\
            order_by(Participant.subjid_).\
            all()
    people = get_people(people)
    return render_template('simplelist.html', records=people)


@app.route('/updatestatus', methods=['POST'])
@app.route('/updatestatus/', methods=['POST'])
def updatestatus():
    """
    Allows subject status to be updated from the web interface.
    """
    if request.method == 'POST':
        field = request.form['id']
        value = request.form['value']
        print field, value
        [tmp, field, subjid] = split(field, '_')
        id = int(id)
        
        session = Session()
        user = session.query(Participant).\
                filter(Participant.subjid == subjid).\
                one()
        if field=='status':
            user.status = value
        session.commit()
        
        return value


#----------------------------------------------
# generic route
#----------------------------------------------
@app.route('/<pagename>')
#@requires_auth
def regularpage(pagename=None):
    """
    Route not found by the other routes above. May point to a static template.
    """
    if pagename==None:
        # This will probably never happen.
        print "error"
        return render_template('error.html', errornum=PAGE_NOT_FOUND)
    else:
        return render_template(pagename)


###########################################################
# let's start
###########################################################
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Useage: python webapp.py [initdb/server]"
    elif len(sys.argv)>1:
        # Some basic server config
        engine = create_engine(DATABASE, echo=False) 
        Session = sessionmaker( bind=engine )
        Session.configure( bind=engine )
        
        if 'initdb' in sys.argv:
            print "initializing database"
            Base.metadata.create_all( engine )
        if 'server' in sys.argv:
            print "starting webserver"
            app.run(debug=True, host='0.0.0.0', port=5001)

