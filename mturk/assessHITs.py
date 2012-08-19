
import os

from boto.mturk.connection import MTurkConnection
from ConfigParser import ConfigParser



#print mtc.get_account_balance()  # Tests the connection

def get_all_reviewable_hits( mtc ):
    page_size = 50;
    hits = mtc.get_reviewable_hits( page_size=page_size )
    print "Total results to fetch %s" % hits.TotalNumResults
    print "Request hits page %i" % 1
    total_pages = float( hits.TotalNumResults )/page_size
    int_total = int(total_pages)
    if total_pages - int_total > 0:
        total_pages = int_total+1
    else:
        total_pages = int_total
    pn = 1
    while pn < total_pages:
        pn += 1
        print "Request hits page %i" % pn
        temp_hits = mtc.get_reviewable_hits( page_size = page_size, page_number=pn )
        hits.extend( temp_hits )
    return hits


framework_root = os.path.abspath(os.path.join(os.getcwd(), os.path.pardir))
configfilename = os.path.join(framework_root, 'config.txt')

config = ConfigParser()
config.read( configfilename )

hostname = 'mechanicalturk.amazonaws.com'

mturkparams =  dict(
    aws_access_key_id = config.get( 'AWS Access', 'aws_access_key_id' ),
    aws_secret_access_key = config.get( 'AWS Access', 'aws_secret_access_key' ),
    host = hostname
)

mtc = MTurkConnection( **mturkparams )

print "Reviewable:"
for hit in get_all_reviewable_hits( mtc ):
    print hit

print "HITs:"
for hit in mtc.get_all_hits():
    print "\tHitID:", hit.HITId
    print "\tAssignments:"
    for assignment in mtc.get_assignments(hit.HITId):
        print "\t\tWorker ID:", assignment.WorkerId
        print "\t\tAssignment ID:", assignment.AssignmentId
        print "\t\tSubmit URL:", "https://www.mturk.com/mturk/externalSubmit?assignmentId=%s&hitId=%s&workerId=%s" % (assignment.AssignmentId, hit.HITId, assignment.WorkerId)
        import urllib2, urllib
        values = {'assignmentId':assignment.AssignmentId, 'hitId':hit.HITId, 'workerId':assignment.WorkerId}
        req = urllib2.Request("https://www.mturk.com/mturk/externalSubmit", urllib.urlencode( values ))
        response = urllib2.urlopen(req)
        result = response.read()
        print result


