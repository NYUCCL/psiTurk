
import sys, os

# GUI stuff:
import wx # This will be an adventure.
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

# Boto is the wrapper library for the mturk API
from boto.mturk.connection import MTurkConnection
from ConfigParser import ConfigParser

# Our database stuff.
from models import Participant

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

framework_root = os.path.dirname(os.path.abspath(__file__))
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

def getHits():
    awaiting = Participant.query.\
                           filter(Participant.status == 4).\
                           all()
    return awaiting

    hitids = set([ p.hitid for p in awaiting ])

    assignmentdict = {}
    for hitid in hitids:
        assignments = mtc.get_assignments( hitid )
        for assign in assignments:
            print "Adding ", assign.AssignmentId 
            assignmentdict[ assign.AssignmentId ] = assign

    for part in awaiting:
        try:
            assign = assignmentdict[part.assignmentid]
            print assign.WorkerId
            print "\t",  assign.AssignmentStatus
        except KeyError:
            print "Key error."
            print "\tAssignment ID:", part.assignmentid
            print "\tHit ID:       ", part.hitid
            print "\tWorker ID:    ", part.workerid
            print "Assignments in that hit:"
            for assign in mtc.get_assignments( part.hitid ):
                print "\t", assign.WorkerId

#print "HITs:"
#for hit in mtc.get_all_hits():
#    print "\tHitID:", hit.HITId
#    print "\tAssignments:"
#    for assignment in mtc.get_assignments(hit.HITId):
#        print "\t\tWorker ID:", assignment.WorkerId
#        print "\t\tAssignment ID:", assignment.AssignmentId
#        print "\t\tSubmit URL:", "https://www.mturk.com/mturk/externalSubmit?assignmentId=%s&hitId=%s&workerId=%s" % (assignment.AssignmentId, hit.HITId, assignment.WorkerId)
#        import urllib2, urllib
#        values = {'assignmentId':assignment.AssignmentId, 'hitId':hit.HITId, 'workerId':assignment.WorkerId}
#        req = urllib2.Request("https://www.mturk.com/mturk/externalSubmit", urllib.urlencode( values ))
#        response = urllib2.urlopen(req)
#        result = response.read()
#        print result

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin): 
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

class AssignmentListWindow(wx.Frame):
    def __init__(self, parent, id, title):
        self.dataFromDB = getHits()
        
        wx.Frame.__init__(self, parent, id, title, size=(450, 600))
        
        splitter = wx.SplitterWindow(self, -1)
        panel1 = wx.Panel(splitter, -1)
        panel2 = wx.Panel(splitter, -1)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        bottombox = wx.BoxSizer(wx.VERTICAL)
        
        leftPanel = wx.Panel(panel1, -1)
        rightPanel = wx.Panel(panel1, -1)
        
        self.databox = wx.TextCtrl(panel2, -1, style=wx.TE_MULTILINE, size=(-1, 1200))
        
        self.list = CheckListCtrl(rightPanel)
        self.list.InsertColumn(0, "Assignement ID", width=320)
        self.list.InsertColumn(1, "Worker ID", width=180)
        self.list.InsertColumn(2, "Hit ID", width=320)
        self.list.InsertColumn(3, "DB Status")
        
        for entry in self.dataFromDB:
            index = self.list.InsertStringItem(sys.maxint, entry.assignmentid)
            self.list.SetStringItem(index, 1, entry.workerid)
            self.list.SetStringItem(index, 2, entry.hitid)
            self.list.SetStringItem(index, 3, str(entry.status))
        
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        
        sel = wx.Button(leftPanel, -1, 'Select All', size=(100, -1))
        des = wx.Button(leftPanel, -1, 'Deselect All', size=(100, -1))
        givecredit = wx.Button(leftPanel, -1, 'Give Credit', size=(100, -1))
        reject = wx.Button(leftPanel, -1, 'Reject', size=(100, -1))
        
        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, id=sel.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, id=des.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnGiveCredit, id=givecredit.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnReject, id=reject.GetId())
        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect, self.list)
        
        vbox2.Add(sel, 0, wx.TOP, 5)
        vbox2.Add(des)
        vbox2.Add(givecredit)
        vbox2.Add(reject)
        
        sel = wx.Button
        leftPanel.SetSizer(vbox2)
        
        vbox.Add(self.list, 1, wx.EXPAND | wx.TOP, 3)
        
        rightPanel.SetSizer(vbox)
        
        bottombox.Add(self.databox, 0.5, wx.EXPAND)
        panel2.SetSizer(bottombox)
        
        splitter.SplitHorizontally(panel1, panel2)
        
        hbox.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(rightPanel, 1, wx.EXPAND)
        hbox.Add((3, -1))
        
        panel1.SetSizer(hbox)
        
        self.Centre()
        self.Show(True)

    def OnSelect(self, event):
        # Show the data in the box below.
        num = event.m_itemIndex
        self.databox.Clear()
        self.databox.AppendText(self.dataFromDB[num].datastring )
        
    def OnSelectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i);
    
    def OnDeselectAll(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i, False);
    
    def OnGiveCredit(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            if i==0:
                self.databox.Clear()
            if self.list.IsChecked(i):
                self.databox.AppendText(self.list.GetItemText(i) + '\n')
    
    def OnReject(self, event):
        num = self.list.GetItemCount()
        for i in range(num):
            if i==0:
                self.databox.Clear()
            if self.list.IsChecked(i):
                self.databox.AppendText(self.list.GetItemText(i) + '\n')


app = wx.App()
AssignmentListWindow(None, -1, u"AssignmentListWindow")
#window.Show(True)

app.MainLoop()
