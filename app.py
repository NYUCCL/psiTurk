from flask import Flask, render_template, request, Response
from string import split
import datetime
from random import choice, shuffle, seed, getstate, setstate
import sys
from sqlalchemy import *
from functools import wraps



# constants
DEPLOYMENT_ENV = 'sandbox'  # 'sandbox' or 'deploy' (the real thing)
CODE_VERSION = '1'

#DATABASE = 'mysql://user:password@domain:port/dbname'
DATABASE = 'sqlite://'
TABLENAME = 'turkdemo'
SUPPORTIE = True
NUMCONDS = 1
NUMCOUNTERS = 2
ALLOCATED = 1
STARTED = 2
COMPLETED = 3
DEBRIEFED = 4
CREDITED = 5
QUITEARLY = 6

# For easy debugging
if DEPLOYMENT_ENV == 'sandbox':
    MAXBLOCKS = 2
else:
    MAXBLOCKS = 15

TESTINGPROBLEMSIX = False

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
# based counterbalancing code
#----------------------------------------------
seed(500)  # use the same order each time the program is launched
counterbalanceconds = []
dimorders = range(24)
dimvals = range(16)
shuffle(dimorders)
shuffle(dimvals)
for i in dimorders:
    for j in dimvals:
        counterbalanceconds.append((i,j))


#----------------------------------------------
# function for authentication
#----------------------------------------------
validuname = "examplename"
validpw = "examplepass"

def wrapper(func, args):
    return func(*args)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == validuname and password == validpw


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
def get_people(conn, s):
    people={}
    i=0
    for row in conn.execute(s):
        person = {}
        for field in ['subjid', 'ipaddress', 'hitid', 'assignmentid', 'workerid',
                        'cond', 'counterbalance', 'beginhit','beginexp', 'endhit',
                        'status', 'datafile']:
            if field=='datafile':
                if row[field] == None:
                    person[field] = "Nothing yet"
                else:
                    person[field] = row[field][:10]
            else:
                person[field] = row[field]
        people[i] = person
        i+=1
    return [people, i]


#----------------------------------------------
# Experiment counterbalancing code.
#----------------------------------------------
def get_random_condition(conn):
    """
    HITs can be in one of three states:
        - jobs that are finished
        - jobs that are started but not finished
        - jobs that are never going to finish (user decided not to do it)
    Our count should be based on the first two, so we count any tasks finished
    or any tasks not finished that were started in the last 30 minutes.
    """
    starttime = datetime.datetime.now() + datetime.timedelta(minutes=-30)
    s = select([participantsdb.c.cond], and_(participantsdb.c.codeversion==CODE_VERSION, or_(participantsdb.c.endhit!=null, participantsdb.c.beginhit>starttime)), from_obj=[participantsdb])
    result = conn.execute(s)
    counts = [0]*NUMCONDS
    for row in result:
        counts[row[0]]+=1
    
    # choose randomly from the ones that have the least in them (so will tend to fill in evenly)
    indicies = [i for i, x in enumerate(counts) if x == min(counts)]
    rstate = getstate()
    seed()
    subj_cond = choice(indicies)
    setstate(rstate)
    return subj_cond

def get_random_counterbalance(conn):
    starttime = datetime.datetime.now() + datetime.timedelta(minutes=-30)
    s = select([participantsdb.c.counterbalance], 
               and_(
                   participantsdb.c.codeversion==CODE_VERSION, 
                   or_(
                       participantsdb.c.endhit!=null, 
                       participantsdb.c.beginhit>starttime)), 
               from_obj=[participantsdb])    
    result = conn.execute(s)
    counts = [0]*NUMCOUNTERS
    for row in result:
        counts[row[0]]+=1
    
    # choose randomly from the ones that have the least in them (so will tend to fill in evenly)
    indicies = [i for i, x in enumerate(counts) if x == min(counts)]
    rstate = getstate()
    seed()
    subj_counter = choice(indicies)
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
        conn = engine.connect()
        hitID = request.args['hitId']
        assignmentID = request.args['assignmentId']
        if request.args.has_key('workerId'):
            workerID = request.args['workerId']
            # first check if this workerId has completed the task before (v1)
            s = select([participantsdb.c.subjid])
            s = s.where(and_(participantsdb.c.hitid!=hitID, participantsdb.c.workerid==workerID))
            result = conn.execute(s)
            matches = [row for row in result]
            numrecs = len(matches)
            
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
        s = select([participantsdb.c.status, participantsdb.c.subjid])
        s = s.where(and_(participantsdb.c.hitid==hitID, participantsdb.c.assignmentid==assignmentID, participantsdb.c.workerid==workerID))
        
        status = None
        for row in conn.execute(s):
            status = row[0]
            subj_id = row[1]
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
        
        conn = engine.connect()
        
        # check first to see if this hitID or assignmentID exists.  if so check to see if inExp is set
        s = select([participantsdb.c.subjid, participantsdb.c.cond, participantsdb.c.counterbalance, participantsdb.c.status], from_obj=[participantsdb])
        s = s.where(and_(participantsdb.c.hitid==hitID,participantsdb.c.assignmentid==assignmentID,participantsdb.c.workerid==workerID))
        result = conn.execute(s)
        matches = [row for row in result]
        numrecs = len(matches)
        if numrecs == 0:
            
            # doesn't exist, get a histogram of completed conditions and choose an under-used condition
            subj_cond = get_random_condition(conn)
            
            # doesn't exist, get a histogram of completed counterbalanced, and choose an under-used one
            subj_counter = get_random_counterbalance(conn)
            
            if not request.remote_addr:
                myip = "UKNOWNIP"
            else:
                myip = request.remote_addr
            
            # set condition here and insert into database
            result = conn.execute(participantsdb.insert(),
                hitid = hitID,
                ipaddress = myip,
                assignmentid = assignmentID,
                workerid = workerID,
                cond = subj_cond,
                counterbalance = subj_counter,
                status = ALLOCATED,
                codeversion = CODE_VERSION,
                debriefed=False,
                beginhit = datetime.datetime.now()
            )
            myid = result.inserted_primary_key[0]
        
        elif numrecs==1:
            myid, subj_cond, subj_counter, status = matches[0]
            if status>=STARTED: # in experiment (or later) can't restart at this point
                return render_template('error.html', errornum=ALREADY_STARTED_EXP, hitid=request.args['hitId'], assignid=request.args['assignmentId'], workerid=request.args['workerId'])
        else:
            print "Error, hit/assignment appears in database more than once (serious problem)"
            return render_template('error.html', errornum=HIT_ASSIGN_APPEARS_IN_DATABASE_MORE_THAN_ONCE, hitid=request.args['hitId'], assignid=request.args['assignmentId'], workerid=request.args['workerId'])
        
        conn.close()
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
            subid = request.form['subjId']
            conn = engine.connect()
            results = conn.execute(
                participantsdb.update().where(
                    participantsdb.c.subjid==subid
                ).values(
                    status=STARTED, 
                    beginexp = datetime.datetime.now()))
            conn.close()
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
            conn = engine.connect()
            conn.execute(participantsdb.update().where(participantsdb.c.subjid==subj_id).values(datafile=datastring, status=STARTED))
            conn.close()
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
            subj_id = request.form['subjId']
            datastring = request.form['dataString']  
            print "getting the save data", subj_id, datastring
            conn = engine.connect()
            conn.execute(participantsdb.update().where(participantsdb.c.subjid==subj_id).values(datafile=datastring, status=QUITEARLY))
            conn.close()
    return render_template('error.html', errornum=TRIED_TO_QUIT)

@app.route('/debrief', methods=['POST', 'GET'])
def savedata():
    """
    User has finished the experiment and is posting their data in the form of a
    (long) string. They will receive a debreifing back.
    """
    print request.form.keys()
    if request.form.has_key('subjid') and request.form.has_key('data'):
        conn = engine.connect()
        subj_id = int(request.form['subjid'])
        datafile = request.form['data']
        print subj_id, datafile
        s = participantsdb.update()
        s = s.where(participantsdb.c.subjid==subj_id)
        s = s.values(status=COMPLETED, datafile=datafile, endhit=datetime.datetime.now())
        conn.execute(s)
        return render_template('debriefing.html', subjid=subj_id)

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
            subj_id = request.form['subjid']
            agreed = request.form['agree']  
            print subj_id, agreed
            conn = engine.connect()
            if agreed=="true":
                conn.execute(participantsdb.update().where(participantsdb.c.subjid==subj_id).values(debriefed=True, status=DEBRIEFED))
            else:
                conn.execute(participantsdb.update().where(participantsdb.c.subjid==subj_id).values(debriefed=False, status=DEBRIEFED))
            conn.close()
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
    s = select([participantsdb], use_labels=False)
    s = s.order_by(participantsdb.c.subjid.asc())
    conn = engine.connect()
    [people, i] = get_people(conn, s)
    conn.close()
    return render_template('simplelist.html', records=people, nrecords=i)


@app.route('/updatestatus', methods=['POST'])
@app.route('/updatestatus/', methods=['POST'])
def updatestatus():
    """
    Allows subject status to be updated from the web interface.
    """
    if request.method == 'POST':
        conn = engine.connect()
        field = request.form['id']
        value = request.form['value']
        print field, value
        [tmp, field, id] = split(field,'_')
        id = int(id)
        s = participantsdb.update()
        s = s.where(participantsdb.c.subjid==id)
        if field=='status':
            s = s.values(status=value)
        conn.execute(s)
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

#----------------------------------------------
# database management
#----------------------------------------------
def createdatabase(engine, metadata):
    # try to load tables from a file, if that fails create new tables
    try:
        participants = Table(TABLENAME, metadata, autoload=True)
        print "Participant table already seems to exist."
    except: # can you put in the specific exception here?
        # ok will create the database
        print "Initializing the database."
        participants = Table(TABLENAME, metadata,
            Column('subjid', Integer, primary_key=True),
            Column('ipaddress', String(128)),
            Column('hitid', String(128)),
            Column('assignmentid', String(128)),
            Column('workerid', String(128)),
            Column('cond', Integer),
            Column('counterbalance', Integer),
            Column('codeversion',String(128)),
            Column('beginhit', DateTime(), nullable=True),
            Column('beginexp', DateTime(), nullable=True),
            Column('endhit', DateTime(), nullable=True),
            Column('status', Integer, default = ALLOCATED),
            Column('debriefed', Boolean),
            Column('datafile', Text, nullable=True),  #the data from the exp
        )
        participants.create()
    return participants


def loaddatabase(engine, metadata):
    # try to load tables from a file, if that fails create new tables
    try:
        participants = Table(TABLENAME, metadata, autoload=True)
    except: # can you put in the specific exception here?
        print "Error, participants table doesn't exist"
        exit()
    return participants


###########################################################
# let's start
###########################################################
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Useage: python webapp.py [initdb/server]"
    elif len(sys.argv)>1:
        engine = create_engine(DATABASE, echo=False) 
        metadata = MetaData()
        metadata.bind = engine
        if 'initdb' in sys.argv:
            print "initializing database"
            createdatabase(engine, metadata)
        if 'server' in sys.argv:
            print "starting webserver"
            participantsdb = loaddatabase(engine, metadata)
            # by default just launch webserver
            app.run(debug=True, host='0.0.0.0', port=5001)

