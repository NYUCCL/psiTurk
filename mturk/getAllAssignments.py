import os
from ConfigParser import ConfigParser
from boto.mturk.connection import MTurkConnection

framework_root = os.path.abspath( 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                 os.path.pardir))
configfilename = os.path.join(framework_root, 'config.txt')

config = ConfigParser()
config.read( configfilename )

host = 'mechanicalturk.amazonaws.com'
mturkparams = dict(
    aws_access_key_id = config.get( 'AWS Access', 'aws_access_key_id' ),
    aws_secret_access_key = config.get( 'AWS Access', 'aws_secret_access_key' ),
    host=host)
mtc = MTurkConnection( **mturkparams )

# Now let's get a list of all the assignment objects

page_size = 50
hitpages = []
newhits = True
#while newhits:
#    newhits = mtc.get_all_hits()
#    hitpages.append(newhits)
#    print dir(newhits)

hitpages = list( mtc.get_all_hits() )
hitpages.extend( list( mtc.get_reviewable_hits(page_size=100) ) )

total_pages = len(hitpages)

#pn = 1
#thehits = []
#while pn < total_pages:
#    print "Request hits page %i" % pn
#    temp_hits = mtc.get_reviewable_hits( page_size = page_size, page_number=pn )
#    thehits.extend( temp_hits )
#    pn += 1

hits = {}
assignments = {}
workers = {}
for hit in hitpages:
    hitid = hit.HITId
    these_assignments = mtc.get_assignments( hitid, page_size=100 )
    hits[hitid] = these_assignments
    for assign in these_assignments:
        assign.HitId = hitid
        assignments[assign.AssignmentId] = assign
        workers[assign.WorkerId] = assign

def viewApprovals( hitid ):
    return [ (x.WorkerId, x.AssignmentStatus) for x in hits[ hitid ] ]

def workerStatus( workerid ):
    return (workers[workerid].HitId, workers[workerid].AssignmentStatus)
