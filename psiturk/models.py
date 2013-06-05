
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
    
    uniqueid =Column(String(128), primary_key=True)
    assignmentid =Column(String(128), nullable=False)
    workerid = Column(String(128), nullable=False)
    hitid = Column(String(128), nullable=False)
    ipaddress = Column(String(128))
    browser = Column(String(128))
    platform = Column(String(128))
    language = Column(String(128))
    cond = Column(Integer)
    counterbalance = Column(Integer)
    codeversion = Column(String(128))
    beginhit = Column(DateTime)
    beginexp = Column(DateTime)
    endhit = Column(DateTime)
    status = Column(Integer, default = 1)
    debriefed = Column(Boolean)
    datastring = Column(Text)
    
    def __init__(self, **kwargs):
        self.uniqueid = "{workerid}:{assignmentid}".format(**kwargs)
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.status = 1
        self.codeversion = CODE_VERSION
        self.debriefed = False
        self.beginhit = datetime.datetime.now()
    
    def __repr__( self ):
        return "Subject(%s, %s, %r, %r, %s)" % ( 
            self.uniqueid, 
            self.cond, 
            self.status,
            self.codeversion)

