# -*- coding: utf-8 -*-
""" This module tests the psiTurk suite.  """

from builtins import str
from builtins import object
import os
import unittest
import psiturk
import json
from faker import Faker
import pytest
from importlib import reload  # Python 3.4+

fake = Faker()  # Fake data generator


class FlaskTestClientProxy(object):
    """Spoof user agent (Chrome)"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', fake.ipv4())
        environ['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X\
            10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0\
            Safari/537.36'
        return self.app(environ, start_response)


class BadFlaskTestClientProxy(object):
    """Spoof user agent (iPad)"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', fake.ipv4())
        environ['HTTP_USER_AGENT'] = 'Mozilla/5.0 (iPad; U; CPU OS 3_2 like \
            Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) \
            Version/4.0.4 Mobile/7B334b Safari/531.21.10'
        return self.app(environ, start_response)


class PsiturkUnitTest(unittest.TestCase):

    def setUp(self, case=None):
        """Build up fixtures"""
        import psiturk.experiment
        reload(psiturk.experiment)

        psiturk.experiment.app.wsgi_app = FlaskTestClientProxy(
            psiturk.experiment.app.wsgi_app)
        self.app = psiturk.experiment.app.test_client()
        self.config = psiturk.experiment.CONFIG

        # Fake MTurk data
        self.worker_id = fake.md5(raw_output=False)
        self.hit_id = fake.md5(raw_output=False)
        self.assignment_id = fake.md5(raw_output=False)

    def tearDown(self):
        """Tear down fixtures"""
        self.app = None

    def set_config(self, section, field, value):
        self.config.parent.set(self.config, section, field, str(value))


@pytest.fixture()
def remove_file(tmpdir):
    def do_it(filename):
        import shutil
        shutil.move(filename, './{}.xyz'.format(filename))

    return do_it


@pytest.fixture()
def remove_template(remove_file):
    def do_it(template_name):
        remove_file('templates/{}'.format(template_name))

    return do_it


@pytest.fixture()
def psiturk_test_client():
    def do_it():
        import psiturk.experiment
        reload(psiturk.experiment)
        psiturk.experiment.app.wsgi_app = FlaskTestClientProxy(
            psiturk.experiment.app.wsgi_app)
        return psiturk.experiment.app

    yield do_it


def test_custom_get_condition_can_import(mocker, psiturk_test_client):
    # pytest.set_trace()
    # import psiturk.experiment
    import sys
    sys.path.append(os.getcwd())
    import custom
    reload(custom)
    mocker.patch.object(custom, 'custom_get_condition', lambda mode: (9, 9), create=True)
    app = psiturk_test_client()

    from psiturk.experiment import get_condition
    assert get_condition('') == (9, 9)


def test_custom_get_condition_not_necessary(tmpdir, mocker, psiturk_test_client):
    import sys
    sys.path.append(os.getcwd())
    import custom
    reload(custom)
    app = psiturk_test_client()

    from psiturk.experiment import get_condition
    assert get_condition('') == (0, 0)


def test_missing_template_exception(edit_config_file, remove_template, psiturk_test_client):
    remove_template('closepopup.html')
    with pytest.raises(RuntimeError):
        app = psiturk_test_client()


def test_notmissing_template(edit_config_file, remove_template, psiturk_test_client):
    psiturk_test_client()


def test_does_not_die_if_no_custompy(remove_file, psiturk_test_client):
    remove_file('custom.py')
    psiturk_test_client()


def test_insert_mode(psiturk_test_client):
    with open('templates/ad.html', 'r') as temp_file:
        ad_string = temp_file.read()

    from psiturk.experiment import insert_mode
    insert_mode(ad_string)


class PsiTurkStandardTests(PsiturkUnitTest):

    # Test experiment.py
    # ==================

    def test_default_page(self):
        """Test that root page works."""
        rv = self.app.get('/')
        response = rv.get_data(as_text=True)
        # print(os.getcwd())
        # with open('server.log','r') as infile:
        # print(file.read())
        assert ('Welcome to psiTurk!' in response)

    def test_exp_debug_no_url_vars(self):
        """Test that exp page throws Error #1003 with no url vars."""
        rv = self.app.get('/exp')
        assert u'<b>Error</b>: 1003' in rv.get_data(as_text=True)

    def test_ad_no_url_vars(self):
        """Test that ad page throws Error #1001 with no url vars."""
        rv = self.app.get('/ad')
        assert u'<b>Error</b>: 1001' in rv.get_data(as_text=True)

    def test_ad_with_all_urls(self):
        """Test that ad page throws Error #1003 with no url vars."""
        args = '&'.join([
            'assignmentId=debug%s' % self.assignment_id,
            'workerId=debug%s' % self.worker_id,
            'hitId=debug%s' % self.hit_id,
            'mode=sandbox'])
        rv = self.app.get('/ad?%s' % args)
        assert 'Thank you for accepting this HIT!' in rv.get_data(as_text=True)

    @pytest.mark.skip('psiturk api server is slow for this test')
    def test_exp_with_all_url_vars_not_registered_on_ad_server(self):
        """Test that exp page throws Error #1018 with all url vars but not registered."""
        self.set_config('Shell Parameters', 'use_psiturk_ad_server', 'true')
        args = '&'.join([
            'assignmentId=debug%s' % self.assignment_id,
            'workerId=debug%s' % self.worker_id,
            'hitId=debug%s' % self.hit_id,
            'mode=sandbox'])
        rv = self.app.get('/exp?%s' % args)
        assert '<b>Error</b>: 1018' in rv.get_data(as_text=True)

    def test_sync_put(self):
        request = "&".join([
            "assignmentId=debug%s" % self.assignment_id,
            "workerId=debug%s" % self.worker_id,
            "hitId=debug%s" % self.hit_id,
            "mode=debug"])

        # put the user in the database
        rv = self.app.get("/exp?%s" % request)

        # try putting the sync, simulating a Backbone PUT payload
        uniqueid = "debug%s:debug%s" % (self.worker_id, self.assignment_id)
        payload = {
            "condition": 5,
            "counterbalance": 0,
            "assignmentId": self.assignment_id,
            "workerId": self.worker_id,
            "hitId": self.hit_id,
            "currenttrial": 2,
            "bonus": 0,
            "data": [
                {
                    "uniqueid": uniqueid,
                    "current_trial": 0,
                    "dateTime": 1564425799481,
                    "trialdata": {
                        "phase": "postquestionnaire",
                        "status": "begin"
                    }
                }, {
                    "uniqueid": uniqueid,
                    "current_trial": 1,
                    "dateTime": 1564425802158,
                    "trialdata": {
                        "phase": "postquestionnaire",
                        "status": "submit"
                    }
                }
            ],
            "questiondata": {
                "engagement": "5",
                "difficulty": "5"
            },
            "eventdata": [
                {
                    "eventtype": "initialized",
                    "value": '',
                    "timestamp": 1564425799139,
                    "interval": 0
                }, {
                    "eventtype": "window_resize",
                    "value": [933, 708],
                    "timestamp": 1564425799139,
                    "interval": 0
                }
            ],
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            "mode": "debug"
        }
        rv = self.app.put('/sync/%s' % uniqueid, json=payload)
        status = json.loads(rv.get_data(as_text=True)).get("status", "")
        assert status == "user data saved"

    def test_sync_get(self):
        self.assignment_id = "debug%s" % self.assignment_id
        self.worker_id = "debug%s" % self.worker_id
        self.hit_id = "debug%s" % self.hit_id

        request = "&".join([
            "assignmentId=%s" % self.assignment_id,
            "workerId=%s" % self.worker_id,
            "hitId=%s" % self.hit_id,
            "mode="])

        # put the user in the database
        rv = self.app.get("/exp?%s" % request)

        # save data with sync PUT
        uniqueid = "%s:%s" % (self.worker_id, self.assignment_id)
        condition = 0
        counterbalance = 0
        bonus = 0.0
        payload = {
            "condition": condition,
            "counterbalance": counterbalance,
            "assignmentId": self.assignment_id,
            "workerId": self.worker_id,
            "hitId": self.hit_id,
            "currenttrial": 2,
            "bonus": bonus,
            "data": [
                {
                    "uniqueid": uniqueid,
                    "current_trial": 0,
                    "dateTime": 1564425799481,
                    "trialdata": {
                        "phase": "postquestionnaire",
                        "status": "begin"
                    }
                },
                {
                    "uniqueid": uniqueid,
                    "current_trial": 1,
                    "dateTime": 1564425802158,
                    "trialdata": {
                        "phase": "postquestionnaire",
                        "status": "submit"
                    }
                }
            ],
            "questiondata": {
                "engagement": "5",
                "difficulty": "5"
            },
            "eventdata": [
                {
                    "eventtype": "initialized",
                    "value": '',
                    "timestamp": 1564425799139,
                    "interval": 0
                },
                {
                    "eventtype": "window_resize",
                    "value": [933, 708],
                    "timestamp": 1564425799139,
                    "interval": 0
                }
            ],
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            "mode": "debug"
        }
        rv = self.app.put('/sync/%s' % uniqueid, json=payload)

        # get data with sync GET
        uniqueid = "%s:%s" % (self.worker_id, self.assignment_id)
        rv = self.app.get('/sync/%s' % uniqueid)

        response = json.loads(rv.get_data(as_text=True))
        assert response.get("assignmentId", "") == "%s" % self.assignment_id
        assert response.get("workerId", "") == "%s" % self.worker_id
        assert response.get("hitId", "") == "%s" % self.hit_id
        assert response.get("condition", None) == condition
        assert response.get("counterbalance", None) == counterbalance
        assert response.get("bonus", None) == bonus

    def test_favicon(self):
        """Test that favicon loads."""
        rv = self.app.get('/favicon.ico')
        assert rv.status_code == 200

    def test_complete_experiment(self):
        """Test that a participant can start and finish the experiment."""
        request = "&".join([
            "assignmentId=debug%s" % self.assignment_id,
            "workerId=debug%s" % self.worker_id,
            "hitId=debug%s" % self.hit_id,
            "mode=debug"])

        # put the user in the database
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200

        # complete experiment
        uniqueid = "debug%s:debug%s" % (self.worker_id, self.assignment_id)
        mode = 'debug'
        rv = self.app.get('/complete?uniqueId=%s&mode=%s' % (uniqueid, mode))
        assert rv.status_code == 200

    def test_repeat_experiment_fail(self):
        """Test that a participant cannot repeat the experiment."""
        request = "&".join([
            "assignmentId=%s" % self.assignment_id,
            "workerId=%s" % self.worker_id,
            "hitId=%s" % self.hit_id,
            "mode=debug"])

        # put the user in the database
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200

        # save data with sync PUT
        uniqueid = "%s:%s" % (self.worker_id, self.assignment_id)
        payload = {
            "condition": 5, "counterbalance": 0,
            "assignmentId": self.assignment_id,
            "workerId": self.worker_id,
            "hitId": self.hit_id,
            "currenttrial": 2,
            "bonus": 0,
            "data": [
                {
                    "uniqueid": uniqueid,
                    "current_trial": 0,
                    "dateTime": 1564425799481,
                    "trialdata": {
                        "phase": "postquestionnaire",
                        "status": "begin"
                    }
                },
                {
                    "uniqueid": uniqueid,
                    "current_trial": 1,
                    "dateTime": 1564425802158,
                    "trialdata": {
                        "phase": "postquestionnaire",
                        "status": "submit"
                    }
                }
            ],
            "questiondata": {
                "engagement": "5",
                "difficulty": "5"
            },
            "eventdata": [
                {
                    "eventtype": "initialized",
                    "value": '',
                    "timestamp": 1564425799139,
                    "interval": 0
                },
                {
                    "eventtype": "window_resize",
                    "value": [933, 708],
                    "timestamp": 1564425799139,
                    "interval": 0
                }
            ],
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            "mode": "debug"
        }
        rv = self.app.put('/sync/%s' % uniqueid, json={
            "condition": 5,
            "counterbalance": 0,
            "assignmentId": self.assignment_id,
            "workerId": self.worker_id,
            "hitId": self.hit_id,
            "currenttrial": 2,
            "bonus": 0, "data": [
                {
                    "uniqueid": uniqueid,
                    "current_trial": 0,
                    "dateTime": 1564425799481,
                    "trialdata": {
                        "phase": "postquestionnaire",
                        "status": "begin"
                    }
                },
                {
                    "uniqueid": uniqueid,
                    "current_trial": 1,
                    "dateTime": 1564425802158,
                    "trialdata": {
                        "phase": "postquestionnaire",
                        "status": "submit"
                    }
                }
            ],
            "questiondata": {
                "engagement": "5",
                "difficulty": "5"
            },
            "eventdata": [
                {
                    "eventtype": "initialized", "value": '',
                    "timestamp": 1564425799139,
                    "interval": 0
                },
                {
                    "eventtype": "window_resize",
                    "value": [933, 708],
                    "timestamp": 1564425799139,
                    "interval": 0
                }
            ],
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            "mode": "debug"
        })
        assert rv.status_code == 200

        # complete experiment
        mode = 'debug'
        rv = self.app.get('/complete?uniqueId=%s&mode=%s' % (uniqueid, mode))
        assert rv.status_code == 200

        # choose new assignment and hit ids
        self.assignment_id = fake.md5(raw_output=False)
        self.hit_id = fake.md5(raw_output=False)
        request = "&".join([
            "assignmentId=%s" % self.assignment_id,
            "workerId=%s" % self.worker_id,
            "hitId=%s" % self.hit_id,
            "mode=debug"])

        # make sure they are blocked on the ad page
        rv = self.app.get('/ad?%s' % request)
        assert ': 1010' in rv.get_data(as_text=True)

        # make sure they are blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert ': 1010' in rv.get_data(as_text=True)

    def test_repeat_experiment_success(self):
        """Test that a participant can repeat the experiment."""
        self.set_config(u'Task Parameters', u'allow_repeats', u'true')
        request = "&".join([
            "assignmentId=%s" % self.assignment_id,
            "workerId=%s" % self.worker_id,
            "hitId=%s" % self.hit_id,
            "mode=debug"])

        # put the user in the database
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200

        # save data with sync PUT
        uniqueid = "%s:%s" % (self.worker_id, self.assignment_id)
        payload = {
            "condition": 5, "counterbalance": 0,
            "assignmentId": self.assignment_id, "workerId": self.worker_id,
            "hitId": self.hit_id, "currenttrial": 2, "bonus": 0, "data": [
                {"uniqueid": uniqueid, "current_trial": 0, "dateTime": 1564425799481,
                 "trialdata": {"phase": "postquestionnaire", "status": "begin"}},
                {"uniqueid": uniqueid, "current_trial": 1, "dateTime": 1564425802158,
                 "trialdata": {"phase": "postquestionnaire", "status": "submit"}}],
            "questiondata": {"engagement": "5", "difficulty": "5"}, "eventdata": [
                {"eventtype": "initialized", "value": '', "timestamp": 1564425799139,
                 "interval": 0},
                {"eventtype": "window_resize", "value": [933, 708], "timestamp": 1564425799139,
                 "interval": 0}],
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            "mode": "debug"}
        rv = self.app.put('/sync/%s' % uniqueid, json=payload)
        assert rv.status_code == 200

        # complete experiment
        mode = 'debug'
        rv = self.app.get('/complete?uniqueId=%s&mode=%s' % (uniqueid, mode))
        assert rv.status_code == 200

        # choose new assignment and hit ids
        self.assignment_id = fake.md5(raw_output=False)
        self.hit_id = fake.md5(raw_output=False)
        request = "&".join([
            "assignmentId=%s" % self.assignment_id,
            "workerId=%s" % self.worker_id,
            "hitId=%s" % self.hit_id,
            "mode=debug"])

        # make sure they are not blocked on the ad page
        rv = self.app.get('/ad?%s' % request)
        assert rv.status_code == 200
        assert ': 1010' not in rv.get_data(as_text=True)

        # make sure they are not blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200
        assert ': 1010' not in rv.get_data(as_text=True)

        # save data with sync PUT
        uniqueid = "%s:%s" % (self.worker_id, self.assignment_id)
        payload = payload = {
            "condition": 5, "counterbalance": 0,
            "assignmentId": self.assignment_id, "workerId": self.worker_id,
            "hitId": self.hit_id, "currenttrial": 2, "bonus": 0, "data": [
                {"uniqueid": uniqueid, "current_trial": 0, "dateTime": 1564425799481,
                 "trialdata": {"phase": "postquestionnaire", "status": "begin"}},
                {"uniqueid": uniqueid, "current_trial": 1, "dateTime": 1564425802158,
                 "trialdata": {"phase": "postquestionnaire", "status": "submit"}}],
            "questiondata": {"engagement": "5", "difficulty": "5"}, "eventdata": [
                {"eventtype": "initialized", "value": '', "timestamp": 1564425799139,
                 "interval": 0},
                {"eventtype": "window_resize", "value": [933, 708], "timestamp": 1564425799139,
                 "interval": 0}],
            "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            "mode": "debug"}
        rv = self.app.put('/sync/%s' % uniqueid, json=payload)
        assert rv.status_code == 200

        # complete experiment
        mode = 'debug'
        rv = self.app.get('/complete?uniqueId=%s&mode=%s' % (uniqueid, mode))
        assert rv.status_code == 200

    def test_repeat_experiment_quit(self):
        """Test that a participant cannot restart the experiment."""
        request = "&".join([
            "assignmentId=%s" % self.assignment_id,
            "workerId=%s" % self.worker_id,
            "hitId=%s" % self.hit_id,
            "mode=debug"])

        # put the user in the database
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200

        # put the in the experiment
        uniqueid = "%s:%s" % (self.worker_id, self.assignment_id)
        rv = self.app.post("/inexp", data=dict(uniqueId=uniqueid))
        assert rv.status_code == 200

        # make sure they are blocked on the ad page
        rv = self.app.get('/ad?%s' % request)
        assert rv.status_code == 200
        assert ': 1009' in rv.get_data(as_text=True)

        # make sure they are blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200
        assert ': 1008' in rv.get_data(as_text=True)

        # have them quit the experiment
        rv = self.app.post("/quitter", data=dict(uniqueId=uniqueid))
        assert rv.status_code == 200

        # make sure they are blocked on the ad page
        rv = self.app.get('/ad?%s' % request)
        assert rv.status_code == 200
        assert ': 1009' in rv.get_data(as_text=True)

        # make sure they are blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200
        assert ': 1008' in rv.get_data(as_text=True)

    def test_repeat_experiment_quit_allow_repeats(self):
        """Test that a participant cannot restart the experiment, even when repeats are allowed."""
        self.set_config(u'Task Parameters', u'allow_repeats', u'true')
        request = "&".join([
            "assignmentId=%s" % self.assignment_id,
            "workerId=%s" % self.worker_id,
            "hitId=%s" % self.hit_id,
            "mode=debug"])

        # put the user in the database
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200

        # put the in the experiment
        uniqueid = "%s:%s" % (self.worker_id, self.assignment_id)
        rv = self.app.post("/inexp", data=dict(uniqueId=uniqueid))
        assert rv.status_code == 200

        # make sure they are blocked on the ad page
        rv = self.app.get('/ad?%s' % request)
        assert rv.status_code == 200
        assert ': 1009' in rv.get_data(as_text=True)

        # make sure they are blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200
        assert ': 1008' in rv.get_data(as_text=True)

        # have them quit the experiment
        rv = self.app.post("/quitter", data=dict(uniqueId=uniqueid))
        assert rv.status_code == 200

        # make sure they are blocked on the ad page
        rv = self.app.get('/ad?%s' % request)
        assert rv.status_code == 200
        assert ': 1009' in rv.get_data(as_text=True)

        # make sure they are blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200
        assert ': 1008' in rv.get_data(as_text=True)


class BadUserAgent(PsiturkUnitTest):
    """Setup test blocked user agent (iPad/tablets)"""

    def setUp(self):
        """Build up fixtures"""
        import psiturk.experiment
        reload(psiturk.experiment)

        psiturk.experiment.app.wsgi_app = BadFlaskTestClientProxy(
            psiturk.experiment.app.wsgi_app)
        self.app = psiturk.experiment.app.test_client()

        # Fake MTurk data
        self.worker_id = fake.md5(raw_output=False)
        self.hit_id = fake.md5(raw_output=False)
        self.assignment_id = fake.md5(raw_output=False)

    def test_ad_with_bad_user_agent(self):
        """Test that ad page throws Error when user agent is blocked."""
        rv = self.app.get(
            '/ad' + '?assignmentId=debug' + self.assignment_id + '&workerId=debug' +
            self.worker_id + '&hitId=debug' + self.hit_id + '&mode=sandbox'
        )
        assert '<b>Error</b>: 1014' in rv.get_data(as_text=True)


class PsiTurkTestPsiturkJS(PsiturkUnitTest):
    """ Setup test for missing psiturk.js file. """

    def setUp(self):
        """Build up fixtures"""
        self.PSITURK_JS_FILE = '../psiturk/psiturk_js/psiturk.js'
        os.rename(self.PSITURK_JS_FILE, self.PSITURK_JS_FILE + '.bup')
        import psiturk.experiment
        reload(psiturk.experiment)

        psiturk.experiment.app.wsgi_app = FlaskTestClientProxy(
            psiturk.experiment.app.wsgi_app)
        self.app = psiturk.experiment.app.test_client()

    @pytest.mark.skip('soemthing about the testing env is making this not work well')
    def test_psiturk_js_is_missing(self):
        """ Test for missing psiturk.js """
        rv = self.app.get('static/js/psiturk.js')
        assert 'file not found' in rv.get_data(as_text=True)

    def tearDown(self):
        """Tear down fixtures"""
        super(PsiTurkTestPsiturkJS, self).tearDown()
        os.rename(self.PSITURK_JS_FILE + '.bup', self.PSITURK_JS_FILE)


class ExperimentErrorsTest(PsiturkUnitTest):

    def test_experiment_errors(self):
        """Make sure every error has a description"""
        error_cls = psiturk.experiment_errors.ExperimentError

        for error_name in error_cls.experiment_errors:
            assert error_name in error_cls.error_descriptions

        for error_name in error_cls.error_descriptions:
            assert error_name in error_cls.experiment_errors


if __name__ == '__main__':
    unittest.main()
