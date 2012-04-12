
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text

from db import Base
from config import config

TABLENAME = config.get('Database Parameters', 'table_name')
CODE_VERSION = config.get('Task Parameters', 'code_version')

class Participant(Base):
    """
    Object representation of a participant in the database.
    """
    __tablename__ = TABLENAME
    
    subjid = Column( Integer, primary_key = True )
    ipaddress = Column(String(128))
    hitid = Column(String(128))
    assignmentid =Column(String(128))
    workerid = Column(String(128))
    cond = Column(Integer)
    counterbalance = Column(Integer)
    codeversion = Column(String(128))
    beginhit = Column(DateTime, nullable=True)
    beginexp = Column(DateTime, nullable=True)
    endhit = Column(DateTime, nullable=True)
    status = Column(Integer, default = 1)
    debriefed = Column(Boolean)
    datastring = Column(Text, nullable=True)
    
    def __init__(self, hitid, ipaddress, assignmentid, workerid, cond, counterbalance):
        self.hitid = hitid
        self.ipaddress = ipaddress
        self.assignmentid = assignmentid
        self.workerid = workerid
        self.cond = cond
        self.counterbalance = counterbalance
        self.status = 1
        self.codeversion = CODE_VERSION
        self.debriefed = False
        self.beginhit = datetime.datetime.now()
    
    def __repr__( self ):
        return "Subject(%r, %s, %r, %r, %s)" % ( 
            self.subjid, 
            self.workerid, 
            self.cond, 
            self.status,
            self.codeversion )
