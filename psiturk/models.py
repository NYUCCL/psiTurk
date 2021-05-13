from __future__ import generator_stop
import datetime
import io
import csv
import json
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, func, inspect
from sqlalchemy.orm import validates, deferred
from sqlalchemy.ext.declarative import declarative_base
from psiturk.db import db_session
from .psiturk_config import PsiturkConfig
from typing import List
from itertools import groupby
from .tasks import do_campaign_round
from apscheduler.jobstores.base import JobLookupError

config = PsiturkConfig()
config.load_config()


TABLENAME = config.get('Database Parameters', 'table_name')
CODE_VERSION = config.get('Task Parameters', 'experiment_code_version')

# Base class

Base = declarative_base()
Base.query = db_session.query_property()


def object_as_dict(self, filter_these: list = None):
    if filter_these is None:
        filter_these = []
    return {c.key: getattr(self, c.key) for c in
            inspect(self).mapper.column_attrs if c.key not in filter_these}


Base.object_as_dict = object_as_dict


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
        datastring = deferred(Column(Text))
    else:
        datastring = deferred(Column(Text(4294967295)))

    def __init__(self, **kwargs):
        self.uniqueid = "{workerid}:{assignmentid}".format(**kwargs)
        self.status = 1
        self.codeversion = CODE_VERSION
        self.beginhit = datetime.datetime.now(datetime.timezone.utc)
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
            return ""

        try:
            with io.StringIO() as outstring:
                csvwriter = csv.writer(outstring)
                for trial in trialdata:
                    csvwriter.writerow(
                        (
                            self.uniqueid,
                            trial["current_trial"],
                            trial["dateTime"],
                            json.dumps(trial["trialdata"])
                         )
                    )
                return outstring.getvalue()
        except:
            print(("Error reading record:", self))
            return ""

    def get_event_data(self):
        try:
            eventdata = json.loads(self.datastring)["eventdata"]
        except (ValueError, TypeError):
            # There was no data to return.
            print(("No event data found in record:", self))
            return ""

        try:
            with io.StringIO() as outstring:
                csvwriter = csv.writer(outstring)
                for event in eventdata:
                    csvwriter.writerow(
                        (
                            self.uniqueid,
                            event["eventtype"],
                            event["interval"],
                            event["value"],
                            event["timestamp"]
                         )
                    )
                return outstring.getvalue()
        except:
            print(("Error reading record:", self))
            return ""

    def get_question_data(self):
        try:
            questiondata = json.loads(self.datastring)["questiondata"]
        except (TypeError, ValueError):
            # There was no data to return.
            print(("No question data found in record:", self))
            return ""

        try:
            with io.StringIO() as outstring:
                csvwriter = csv.writer(outstring)
                for question in questiondata:
                    csvwriter.writerow(
                        (
                            self.uniqueid,
                            question,
                            questiondata[question]
                         )
                    )
                return outstring.getvalue()
        except:
            print(("Error reading record:", self))

            return ""
            
    @classmethod
    def count_completed(cls, codeversion, mode):
        completed_statuses = [3, 4, 5, 7]
        return cls.query.with_entities(func.count()).filter(
                cls.status.in_(completed_statuses),
                cls.codeversion == codeversion,
                cls.mode == mode
            ).scalar()

    @classmethod
    def count_workers_grouped(cls, query=None, group_bys: List[str] = None):
        if group_bys is None:
            group_bys = ['codeversion', 'mode', 'status']
        group_by_labels = group_bys + ['count']
        group_bys = [getattr(cls, group_by) for group_by in group_bys]
        if not query:
            query = cls.query
        for group_by in group_bys:
            query = query.group_by(group_by).order_by(group_by.desc())
        entities = group_bys + [func.count()]

        query = query.with_entities(*entities)
        results = query.all()

        def list_to_grouped_dicts(results):
            parsed_results = {}
            for k, group in groupby(results, lambda row: row[0]):  # k will be codeversion
                group = list(group)
                if len(group[0]) > 2:
                    parsed_results[k] = list_to_grouped_dicts([row[1:] for row in group])
                else:
                    parsed_results.update({k: v for k, v in group})
            return parsed_results

        # TODO: Is this call actually doing anything? Looks like it is ignored.
        parsed_results = list_to_grouped_dicts(results)

        zipped_results = [dict(zip(group_by_labels, row)) for row in results]
        return zipped_results

    @classmethod
    def all_but_datastring(cls):
        query = cls.query
        query = query.with_entities(*[c for c in cls.__table__.c if c.name != 'datastring'])
        return query.all()


class Hit(Base):
    """
    """
    __tablename__ = 'amt_hit'
    hitid = Column(String(128), primary_key=True)


class Campaign(Base):
    """
    """
    __tablename__ = 'campaign'
    id = Column(Integer, primary_key=True)
    codeversion = Column(String(128), nullable=False)
    mode = Column(String(128), nullable=False)
    goal = Column(Integer, nullable=False)
    minutes_between_rounds = Column(Integer, nullable=False)
    assignments_per_round = Column(Integer, nullable=False)
    hit_reward = Column(Float, nullable=False)
    hit_duration_hours = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    ended = Column(DateTime, default=None)

    @validates('goal', 'minutes_between_rounds', 'assignments_per_round',
               'hit_duration_hours')
    def validate_greater_than_zero(self, key, value):
        if key == 'goal':
            self._validate_greater_than_already_completed(value)
        assert value > 0, 'Property `{}` must be greater than 0'.format(key)
        return value

    @validates('hit_reward')
    def validate_hit_reward(self, key, hit_reward):
        assert hit_reward >= 0, \
            f'Hit reward must be greater than or equal to zero, got {hit_reward}'
        return hit_reward

    def _validate_greater_than_already_completed(self, goal):
        count_completed = Participant.count_completed(
            codeversion=self.codeversion, mode=self.mode)
        assert goal > count_completed, \
            f'Goal ({goal}) must be greater than the count of '\
            f'already-completed {count_completed}).'
    
    @validates('mode')
    def validate_mode(self, key, mode):
        assert mode in ['sandbox', 'live'], 'Mode {} not recognized.'.format(mode)
        return mode

    @validates('is_active')
    def validate_is_active(self, key, is_active):
        if is_active:
            assert not self.active_campaign_exists(), 'No no, there can be only one active campaign.'
        return is_active

    def __init__(self, **kwargs):
        self.codeversion = CODE_VERSION
        for key in kwargs:
            setattr(self, key, kwargs[key])

    @property
    def campaign_job_id(self):
        return 'campaign-{}'.format(self.id)

    def end(self):
        self.is_active = False
        self.ended = datetime.datetime.now(datetime.timezone.utc)
        from .experiment import app
        try:
            app.apscheduler.remove_job(self.campaign_job_id)
        except JobLookupError:
            pass

        db_session.add(self)
        db_session.commit()
        return self

    def set_new_goal(self, goal):
        self.goal = goal
        db_session.add(self)
        db_session.commit()

        from .experiment import app
        job = app.apscheduler.get_job(self.campaign_job_id)
        kwargs = job.kwargs
        kwargs['campaign'] = self
        job.modify(kwargs=kwargs)

        return self

    @classmethod
    def active_campaign_exists(cls):
        subquery = cls.query.filter(cls.is_active.is_(True)).exists()
        query = db_session.query(subquery)
        _return = query.scalar()
        return _return

    @classmethod
    def launch_new_campaign(cls, **kwargs):
        kwargs['is_active'] = True
        new_campaign = cls(**kwargs)
        db_session.add(new_campaign)
        db_session.commit()

        _kwargs = {
            'campaign': new_campaign,
            'job_id': new_campaign.campaign_job_id
        }
        from .experiment import app
        app.apscheduler.add_job(
            id=new_campaign.campaign_job_id,
            func=do_campaign_round,
            kwargs=_kwargs,
            trigger='interval',
            minutes=new_campaign.minutes_between_rounds,
            next_run_time=datetime.datetime.now(datetime.timezone.utc)
        )

        return new_campaign
