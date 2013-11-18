
import datetime
import io, csv, json
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text

from db import Base
from psiturk_config import PsiturkConfig

config = PsiturkConfig()
config.load_config()

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
    
    def __repr__(self):
        return "Subject(%s, %s, %s, %s)" % ( 
            self.uniqueid, 
            self.cond, 
            self.status,
            self.codeversion)
    
    def get_trial_data(self):
        try:
            return(json.loads(self.datastring)["data"])
        except:
            # There was no data to return.
            print("No trial data found in record:", self)
            return("")
    
    def get_event_data(self):
        try:
            eventdata = json.loads(self.datastring)["eventdata"]
        except ValueError:
            # There was no data to return.
            print("No event data found in record:", self)
            return("")
        
        try:
            ret = []
            with io.BytesIO() as outstring:
                csvwriter = csv.writer(outstring)
                for event in eventdata:
                    csvwriter.writerow((self.uniqueid, event["eventtype"], event["interval"], event["value"], event["timestamp"]))
                ret = outstring.getvalue()
            return ret
        except:
            print("Error reading record:", self)
            return("")
    
    def get_question_data(self):
        try:
            questiondata = json.loads(self.datastring)["questiondata"]
        except ValueError:
            # There was no data to return.
            print("No question data found in record:", self)
            return("")
        
        try:
            ret = []
            with io.BytesIO() as outstring:
                csvwriter = csv.writer(outstring)
                for question in questiondata:
                    csvwriter.writerow((self.uniqueid, question, questiondata[question]))
                ret = outstring.getvalue()
            return ret
        except:
            print("Error reading record:", self)
            return("")

    def add_data(self, data):
        # see if there is existing saved data
        try:
            olddata = json.loads(self.datastring)
        # TypeError means no, because nothing has been saved yet
        except TypeError:
            olddata = ""
        # ValueError means it's invalid JSON
        except ValueError:
            olddata = ""

        # handle unicode characcters
        d = data.decode('utf-8').encode('ascii', 'xmlcharrefreplace')

        # try to load the given json
        try:
            newdata = json.loads(d)
        except ValueError:
            newdata = ""

        # nothing has been saved yet, and nothing has been given to be
        # saved
        if olddata == "" and newdata == "":
            self.datastring = ""
        # nothing has been saved yet, so just save the new stuff
        elif olddata == "":
            self.datastring = d
        # nothing new to be saved
        elif newdata == "":
            pass
        # concatenate the old data with the new data
        else:
            olddata["questiondata"].update(newdata["questiondata"])
            olddata["eventdata"].extend(newdata["eventdata"])
            olddata["data"] += newdata["data"]
            self.datastring = json.dumps(olddata)
