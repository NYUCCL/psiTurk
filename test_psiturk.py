import os
import sh
import shutil
import unittest
import tempfile
import psiturk
from faker import Faker


fake = Faker()  # Fake data generator

class FlaskTestClientProxy(object):
   '''Spoof user agent'''
   def __init__(self, app):
       self.app = app

   def __call__(self, environ, start_response):
       environ['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', fake.ipv4())
       environ['HTTP_USER_AGENT'] = environ.get('HTTP_USER_AGENT', fake.user_agent())
       return self.app(environ, start_response)


class PsiTurkTestCase(unittest.TestCase):

    def setUp(self):
        '''Build up fixtures'''
        initialize_psiturk = sh.Command('psiturk-setup-example')  # Initialize psiTurk
        initialize_psiturk()
        os.chdir('psiturk-example')
        import psiturk.db
        import psiturk.experiment
        self.db_fd, psiturk.experiment.app.config['DATABASE'] = tempfile.mkstemp()
        psiturk.experiment.app.wsgi_app = FlaskTestClientProxy(psiturk.experiment.app.wsgi_app)
        self.app = psiturk.experiment.app.test_client()
        psiturk.db.init_db()

        # Fake MTurk data
        self.worker_id = fake.md5(raw_output=False)
        self.hit_id = fake.md5(raw_output=False)
        self.assignment_id = fake.md5(raw_output=False)

    def test_default_page(self):
        '''Test that root page works.'''
        rv = self.app.get('/')
        assert 'Welcome to psiTurk!' in rv.data

    def test_exp_debug_no_url_vars(self):
        '''Test that exp page throws Error #1003 with no url vars.'''
        rv = self.app.get('/exp')
        assert 'Error: #1003' in rv.data

    def test_exp_with_all_url_vars_not_registered_on_ad_server(self):
        '''Test that exp page throws Error #1018 with all url vars but not registered.'''
        rv = self.app.get('/exp' + '?assignmentId=' + self.assignment_id + '&workerId=' + self.worker_id + '&hitId=' + self.hit_id)
        assert 'Error: #1018' in rv.data

    def tearDown(self):
        '''Tear down fixtures'''
        os.close(self.db_fd)
        os.chdir('..')
        shutil.rmtree('psiturk-example')
        os.unlink(psiturk.experiment.app.config['DATABASE'])


if __name__ == '__main__':
    unittest.main()
