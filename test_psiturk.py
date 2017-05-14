# -*- coding: utf-8 -*-
""" This module tests the psiTurk suite.  """

import os
import unittest
import tempfile
import psiturk
import json
from faker import Faker


fake = Faker()  # Fake data generator


class FlaskTestClientProxy(object):
    '''Spoof user agent (Chrome)'''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', fake.ipv4())
        environ['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X\
            10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0\
            Safari/537.36'
        return self.app(environ, start_response)


class BadFlaskTestClientProxy(object):
    '''Spoof user agent (iPad)'''
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
        '''Build up fixtures'''
        os.chdir('psiturk-example')
        import psiturk.db
        import psiturk.experiment
        reload(psiturk.experiment)

        fd, db_path = tempfile.mkstemp()
        self.db_fd = fd
        psiturk.experiment.app.config['DATABASE'] = db_path
        psiturk.experiment.app.wsgi_app = FlaskTestClientProxy(
            psiturk.experiment.app.wsgi_app)
        self.app = psiturk.experiment.app.test_client()
        self.config = psiturk.experiment.CONFIG
        psiturk.db.init_db()

        # Fake MTurk data
        self.worker_id = fake.md5(raw_output=False)
        self.hit_id = fake.md5(raw_output=False)
        self.assignment_id = fake.md5(raw_output=False)

    def tearDown(self):
        '''Tear down fixtures'''
        os.close(self.db_fd)
        os.chdir('..')
        os.unlink(psiturk.experiment.app.config['DATABASE'])
        self.app = None

    def set_config(self, section, field, value):
        self.config.parent.set(self.config, section, field, str(value))


class PsiTurkStandardTests(PsiturkUnitTest):

    # Test experiment.py
    # ==================

    def test_default_page(self):
        '''Test that root page works.'''
        rv = self.app.get('/')
        assert 'Welcome to psiTurk!' in rv.data

    def test_exp_debug_no_url_vars(self):
        '''Test that exp page throws Error #1003 with no url vars.'''
        rv = self.app.get('/exp')
        assert '<b>Error</b>: 1003' in rv.data

    def test_ad_no_url_vars(self):
        '''Test that ad page throws Error #1001 with no url vars.'''
        rv = self.app.get('/ad')
        assert '<b>Error</b>: 1001' in rv.data

    def test_ad_with_all_urls(self):
        '''Test that ad page throws Error #1003 with no url vars.'''
        args = '&'.join([
            'assignmentId=debug%s' % self.assignment_id,
            'workerId=debug%s' % self.worker_id,
            'hitId=debug%s' % self.hit_id,
            'mode=sandbox'])
        rv = self.app.get('/ad?%s' % args)
        assert 'Thank you for accepting this HIT!' in rv.data

    def test_exp_with_all_url_vars_not_registered_on_ad_server(self):
        '''Test that exp page throws Error #1018 with all url vars but not registered.'''
        args = '&'.join([
            'assignmentId=debug%s' % self.assignment_id,
            'workerId=debug%s' % self.worker_id,
            'hitId=debug%s' % self.hit_id,
            'mode=sandbox'])
        rv = self.app.get('/exp?%s' % args)
        assert '<b>Error</b>: 1018' in rv.data

    def test_sync_put(self):
        request = "&".join([
           "assignmentId=debug%s" % self.assignment_id,
           "workerId=debug%s" % self.worker_id,
           "hitId=debug%s" % self.hit_id,
           "mode=debug"])

        # put the user in the database
        rv = self.app.get("/exp?%s" % request)

        # try putting the sync
        uniqueid = "debug%s:debug%s" % (self.worker_id, self.assignment_id)
        rv = self.app.put('/sync/%s' % uniqueid)
        status = json.loads(rv.data).get("status", "")
        assert status == "user data saved"

    def test_sync_get(self):
        request = "&".join([
           "assignmentId=debug%s" % self.assignment_id,
           "workerId=debug%s" % self.worker_id,
           "hitId=debug%s" % self.hit_id,
           "mode=debug"])

        # put the user in the database
        rv = self.app.get("/exp?%s" % request)

        # save data with sync PUT
        uniqueid = "debug%s:debug%s" % (self.worker_id, self.assignment_id)
        rv = self.app.put('/sync/%s' % uniqueid)

        # get data with sync GET
        uniqueid = "debug%s:debug%s" % (self.worker_id, self.assignment_id)
        rv = self.app.get('/sync/%s' % uniqueid)

        response = json.loads(rv.data)
        assert response.get("assignmentId", "") == "debug%s" % self.assignment_id
        assert response.get("workerId", "") == "debug%s" % self.worker_id
        assert response.get("hitId", "") == "debug%s" % self.hit_id
        assert response.get("condition", None) == 0
        assert response.get("counterbalance", None) == 0
        assert response.get("bonus", None) == 0.0

    def test_favicon(self):
        '''Test that favicon loads.'''
        rv = self.app.get('/favicon.ico')
        assert rv.status_code == 200

    def test_complete_experiment(self):
        '''Test that a participant can start and finish the experiment.'''
        request = "&".join([
            "assignmentId=debug%s" % self.assignment_id,
            "workerId=debug%s" % self.worker_id,
            "hitId=debug%s" % self.hit_id,
            "mode=debug"])

        # put the user in the database
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200

        # save data with sync PUT
        uniqueid = "debug%s:debug%s" % (self.worker_id, self.assignment_id)
        rv = self.app.put('/sync/%s' % uniqueid)
        assert rv.status_code == 200

        # complete experiment
        mode = 'debug'
        rv = self.app.get('/complete?uniqueId=%s&mode=%s' % (uniqueid, mode))
        assert rv.status_code == 200

    def test_repeat_experiment_fail(self):
        '''Test that a participant cannot repeat the experiment.'''
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
        rv = self.app.put('/sync/%s' % uniqueid)
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
        assert ': 1010' in rv.data

        # make sure they are blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert ': 1010' in rv.data

    def test_repeat_experiment_success(self):
        '''Test that a participant can repeat the experiment.'''
        self.set_config('HIT Configuration', 'allow_repeats', 'true')
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
        rv = self.app.put('/sync/%s' % uniqueid)
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
        assert ': 1010' not in rv.data

        # make sure they are not blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200
        assert ': 1010' not in rv.data

        # save data with sync PUT
        uniqueid = "%s:%s" % (self.worker_id, self.assignment_id)
        rv = self.app.put('/sync/%s' % uniqueid)
        assert rv.status_code == 200

        # complete experiment
        mode = 'debug'
        rv = self.app.get('/complete?uniqueId=%s&mode=%s' % (uniqueid, mode))
        assert rv.status_code == 200

    def test_repeat_experiment_quit(self):
        '''Test that a participant cannot restart the experiment.'''
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
        assert ': 1009' in rv.data

        # make sure they are blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200
        assert ': 1008' in rv.data

        # have them quit the experiment
        rv = self.app.post("/quitter", data=dict(uniqueId=uniqueid))
        assert rv.status_code == 200

        # make sure they are blocked on the ad page
        rv = self.app.get('/ad?%s' % request)
        assert rv.status_code == 200
        assert ': 1009' in rv.data

        # make sure they are blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200
        assert ': 1008' in rv.data

    def test_repeat_experiment_quit_allow_repeats(self):
        '''Test that a participant cannot restart the experiment, even when repeats are allowed.'''
        self.set_config('HIT Configuration', 'allow_repeats', 'true')
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
        assert ': 1009' in rv.data

        # make sure they are blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200
        assert ': 1008' in rv.data

        # have them quit the experiment
        rv = self.app.post("/quitter", data=dict(uniqueId=uniqueid))
        assert rv.status_code == 200

        # make sure they are blocked on the ad page
        rv = self.app.get('/ad?%s' % request)
        assert rv.status_code == 200
        assert ': 1009' in rv.data

        # make sure they are blocked on the experiment page
        rv = self.app.get("/exp?%s" % request)
        assert rv.status_code == 200
        assert ': 1008' in rv.data


class BadUserAgent(PsiturkUnitTest):
    '''Setup test blocked user agent (iPad/tablets)'''

    def setUp(self):
        '''Build up fixtures'''
        os.chdir('psiturk-example')
        import psiturk.db
        import psiturk.experiment
        reload(psiturk.experiment)

        fd, db_path = tempfile.mkstemp()
        self.db_fd = fd
        psiturk.experiment.app.config['DATABASE'] = db_path
        psiturk.experiment.app.wsgi_app = BadFlaskTestClientProxy(
            psiturk.experiment.app.wsgi_app)
        self.app = psiturk.experiment.app.test_client()
        psiturk.db.init_db()

        # Fake MTurk data
        self.worker_id = fake.md5(raw_output=False)
        self.hit_id = fake.md5(raw_output=False)
        self.assignment_id = fake.md5(raw_output=False)

    def test_ad_with_bad_user_agent(self):
        '''Test that ad page throws Error when user agent is blocked.'''
        rv = self.app.get(
            '/ad' + '?assignmentId=debug' + self.assignment_id + '&workerId=debug' +
            self.worker_id + '&hitId=debug' + self.hit_id + '&mode=sandbox'
        )
        assert '<b>Error</b>: 1014' in rv.data


class PsiTurkTestPsiturkJS(PsiturkUnitTest):
    ''' Setup test for missing psiturk.js file. '''

    def setUp(self):
        '''Build up fixtures'''
        self.PSITURK_JS_FILE = '../psiturk/psiturk_js/psiturk.js'
        os.chdir('psiturk-example')
        os.rename(self.PSITURK_JS_FILE, self.PSITURK_JS_FILE + '.bup')
        import psiturk.db
        import psiturk.experiment
        reload(psiturk.experiment)

        fd, db_path = tempfile.mkstemp()
        self.db_fd = fd
        psiturk.experiment.app.config['DATABASE'] = db_path
        psiturk.experiment.app.wsgi_app = FlaskTestClientProxy(
            psiturk.experiment.app.wsgi_app)
        self.app = psiturk.experiment.app.test_client()
        psiturk.db.init_db()

    def test_psiturk_js_is_missing(self):
        ''' Test for missing psiturk.js '''
        rv = self.app.get('static/js/psiturk.js')
        assert 'file not found' in rv.data

    def tearDown(self):
        '''Tear down fixtures'''
        super(PsiTurkTestPsiturkJS, self).tearDown()
        os.chdir('psiturk-example')
        os.rename(self.PSITURK_JS_FILE + '.bup', self.PSITURK_JS_FILE)
        os.chdir('..')


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
