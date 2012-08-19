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

framework_root = os.path.abspath( 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                 os.path.pardir))
configfilename = os.path.join(framework_root, 'config.txt')

config = ConfigParser()
config.read( configfilename )

SANDBOX = config.getboolean('HIT Configuration', 'using_sandbox')


class TurkConnect:
    def __init__(self, host, n=10):
        mturkparams = dict(
            aws_access_key_id = config.get( 'AWS Access', 'aws_access_key_id' ),
            aws_secret_access_key = config.get( 'AWS Access', 'aws_secret_access_key' ),
            host=host)
        self.mtc = MTurkConnection( **mturkparams )
        
        # Configure portal
        experimentPortalURL = config.get( 'HIT Configuration', 'question_url' )
        frameheight = 600
        mturkQuestion = ExternalQuestion( experimentPortalURL, frameheight )
        
        # Qualification:
        quals = Qualifications();
        approve_requirement = config.getint('HIT Configuration',
                                            'Approve_Requirement')
        quals.add(
            PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo",
                                                  approve_requirement))
        if config.getboolean('HIT Configuration', 'US_only'):
            quals.add( LocaleRequirement("EqualTo", "US") )
        
        # Specify all the HIT parameters
        self.paramdict = dict(
            hit_type = None,
            question = mturkQuestion,
            lifetime = datetime.timedelta(hours=config.getfloat('HIT Configuration', 'HIT_lifetime')),
            max_assignments = config.getint('HIT Configuration', 'max_assignments'),
            title = config.get('HIT Configuration', 'title'),
            description = config.get('HIT Configuration', 'description'),
            keywords = config.get('HIT Configuration', 'keywords'),
            reward = config.getfloat('HIT Configuration', 'reward'),
            duration = datetime.timedelta(
                hours=config.getfloat('HIT Configuration', 'duration')),
            approval_delay = None,
            questions = None,
            qualifications = quals
        )
    
    def checkbalance(self):
        return self.mtc.get_account_balance()  # Tests the connection
    
    def createhit(self):
        myhit = self.mtc.create_hit( **self.paramdict )[0]
        hitid = myhit.HITId


def printusage():
    print "Usage:"
    print "python createHIT.py [# of assignments] -- create a real HIT with [# of assignments] assignment"

###########################################################
# let's start
###########################################################
if __name__ == '__main__':
    if SANDBOX:
        host = 'mechanicalturk.sandbox.amazonaws.com'
    else:
        host = 'mechanicalturk.amazonaws.com'
    connection = TurkConnect( host )
    print connection.checkbalance()
    connection.createhit()
