import datetime
import os, sys
from ConfigParser import ConfigParser
try:
    import argparse
    USINGPY27 = True
except:
    USINGPY27 = False

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import LocaleRequirement, PercentAssignmentsApprovedRequirement, Qualifications

framework_root = os.path.abspath(os.path.join(os.getcwd(), os.path.pardir))
configfilename = os.path.join(framework_root, 'config')

config = ConfigParser()
config.read( configfilename )


defaultN = 1

class TurkConnect:
    def __init__(self, host, n=10):
        mturkparams = dict(
            aws_access_key_id = config.get( 'AWS Access', 'aws_access_key_id' ),
            aws_secret_access_key = config.get( 'AWS Access', 'aws_secret_access_key' ),
            host=host)
        self.mtc = MTurkConnection( **mturkparams )
        
        # Configure portal
        experimentPortalURL = "http://localhost:5001/mturk"
        frameheight = 600
        mturkQuestion = ExternalQuestion( experimentPortalURL, 600 )
        
        # Qualification:
        quals = Qualifications();
        quals.add( PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo", "95") )
        quals.add( LocaleRequirement("EqualTo", "US") )
        
        # Specify all the HIT parameters
        self.paramdict = dict(
            hit_type = None,
            question = mturkQuestion,
            lifetime = datetime.timedelta(1),  # How long the HIT will be available
            max_assignments = None, # will be assigned later.
            title = "Perceptual Reaction Time",
            description = "Make a series of perceptual judgments.",
            keywords = "Perception, Psychology",
            reward = .1,
            duration = datetime.timedelta(hours=2),
            approval_delay = None,
            annotation = None,  # Do we need this? Not clear on what it is.
            questions = None,
            qualifications = quals
        )
    
    def checkbalance(self):
        return self.mtc.get_account_balance()  # Tests the connection
    
    def createhit(self, n):
        self.paramdict[ 'max_assignments' ] = n
        myhit = self.mtc.create_hit( **self.paramdict )[0]
        hitid = myhit.HITId


def printusage():
    print "Usage:"
    print "python createHIT.py sandbox -- create a HIT with 10 assignments in the sandbox"
    print "python createHIT.py [# of assignments] -- create a real HIT with [# of assignments] assignment"

###########################################################
# let's start
###########################################################
if __name__ == '__main__':
    if USINGPY27:
        parser = argparse.ArgumentParser(
            description = "Start a new HIT", 
            epilog="""
            Be careful with this! It is very easy to accidentally post a lot of
            paid slots live to MTurk using this function. Start out in the
            sandbox and make sure you understand how it works.
            """
        )
        parser.add_argument('--sandbox', 
                            dest='usingSandbox',
                            action='store_const', 
                            const=True, 
                            default=False,
                            help='Use the Mechanical Turk sandbox.')
        parser.add_argument('maxAssignments', 
                            metavar='maxassign', 
                            type=int,
                            default=1, 
                            help='Number of times the job will be assigned.')
        args = parser.parse_args()
        sandbox = args.usingSandbox
        maxAssign = args.maxAssignments
    else:
        try:
            print "Warning, using python < 2.7, falling back on manual command line parsing."
            if sys.argv[1]:
                sandbox =  sys.argv[1] == 'sandbox'
                if not sandbox:
                    n = int( sys.argv[1] )
                else:
                    n = defaultN
            else:
                sandbox = False
                n = defaultN
        except:
            printusage();
    
    if sandbox:
        host = 'mechanicalturk.sandbox.amazonaws.com'
    else:
        host = 'mechanicalturk.amazonaws.com'
    connection = TurkConnect( host )
    print connection.checkbalance()
    connection.createhit()
