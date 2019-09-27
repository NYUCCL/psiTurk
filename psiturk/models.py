from __future__ import print_function
from __future__ import absolute_import

import datetime
import io
import csv
import json
from sqlalchemy import Column, Integer, String, DateTime, Float, Text

from .db import Base
from .psiturk_config import PsiturkConfig

config = PsiturkConfig()
config.load_config()

TABLENAME = config.get('Database Parameters', 'table_name')
CODE_VERSION = config.get('Task Parameters', 'experiment_code_version')

import six

class Participant(Base):
    """
    Object representation of a participant in the database.
    """
    __tablename__ = TABLENAME

    uniqueid = Column(String(128), primary_key=True)
    assignmentid = Column(String(128), nullable=False)
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
    bonus = Column(Float, default=0)
    status = Column(Integer, default=1)
    mode = Column(String(128))
    if 'postgres://' in config.get('Database Parameters', 'database_url').lower():
        datastring = Column(Text)
    else:
        datastring = Column(Text(4294967295))

    def __init__(self, **kwargs):
        self.uniqueid = "{workerid}:{assignmentid}".format(**kwargs)
        self.status = 1
        self.codeversion = CODE_VERSION
        self.beginhit = datetime.datetime.now()
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __repr__(self):
        return "Subject(uniqueid|%s, condition|%s, status|%s, codeversion|%s)" % (
            self.uniqueid,
            self.cond,
            self.status,
            self.codeversion)

    def get_trial_data(self):
        try:
            trialdata = json.loads(self.datastring)["data"]
        except (TypeError, ValueError):
            # There was no data to return.
            print(("No trial data found in record:", self))
            return("")
        
        my_io = io.StringIO
        if six.PY2:
            my_io = io.BytesIO

        try:
            ret = []
            with my_io() as outstring:
                csvwriter = csv.writer(outstring)
                for trial in trialdata:
                    csvwriter.writerow((
                        self.uniqueid,
                        trial["current_trial"],
                        trial["dateTime"],
                        json.dumps(trial["trialdata"])))
                ret = outstring.getvalue()
            return ret
        except:
            print(("Error reading record:", self))
            return("")

    def get_event_data(self):
        try:
            eventdata = json.loads(self.datastring)["eventdata"]
        except (ValueError, TypeError):
            # There was no data to return.
            print(("No event data found in record:", self))
            return("")

        my_io = io.StringIO
        if six.PY2:
            my_io = io.BytesIO

        try:
            ret = []
            with my_io() as outstring:
                csvwriter = csv.writer(outstring)
                for event in eventdata:
                    csvwriter.writerow(
                        (self.uniqueid, event["eventtype"], event["interval"], event["value"], event["timestamp"]))
                ret = outstring.getvalue()
            return ret
        except:
            print(("Error reading record:", self))
            return("")

    def get_question_data(self):
        try:
            questiondata = json.loads(self.datastring)["questiondata"]
        except (TypeError, ValueError):
            # There was no data to return.
            print(("No question data found in record:", self))
            return("")

        my_io = io.StringIO
        if six.PY2:
            my_io = io.BytesIO

        try:
            ret = []
            with my_io() as outstring:
                csvwriter = csv.writer(outstring)
                for question in questiondata:
                    csvwriter.writerow(
                        (self.uniqueid, question, questiondata[question]))
                ret = outstring.getvalue()
            return ret
        except:
            print(("Error reading record:", self))
            return("")


class Hit(Base):
    '''
    '''
    __tablename__ = 'amt_hit'
    hitid = Column(String(128), primary_key=True)
