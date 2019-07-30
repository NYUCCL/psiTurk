from __future__ import print_function
# https://docs.pytest.org/en/latest/fixture.html#using-fixtures-from-classes-modules-or-projects
from builtins import object
import pytest
import os
import sys
import pickle
import json
import datetime
import dateutil.parser
import ciso8601
import six
import boto3
from botocore.stub import Stubber
from distutils import dir_util, file_util


@pytest.fixture(scope='session', autouse=True)
def experiment_dir():
    import shutil
    try:
        dir_util.remove_tree('psiturk-example')
    except FileNotFoundError:
        pass
    import psiturk.setup_example as se
    # import pytest; pytest.set_trace()
    se.setup_example()
    
    # os.chdir('psiturk-example') # the setup script already chdirs into here, although I don't like that it does that
    os.environ['AWS_ACCESS_KEY_ID'] = 'foo'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'bar'
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    os.environ.pop('AWS_PROFILE', None)
    
    yield
    os.chdir('..')
    dir_util.remove_tree('psiturk-example')

@pytest.fixture(autouse=True)
def reset_experiment_dir(pytestconfig, db_setup, reset_config_file):
    dir_util.copy_tree(os.path.join(pytestconfig.rootdir,'psiturk','example'),'')
    reset_config_file()
    db_setup()
    
@pytest.fixture()
def reset_config_file():
    def do_it():
        from psiturk.setup_example import DEFAULT_CONFIG_FILE
        file_util.copy_file(DEFAULT_CONFIG_FILE, 'config.txt')
        # change config file...
        with open('config.txt', 'r') as file:
            config_file = file.read()

        config_file = config_file.replace(
            'use_psiturk_ad_server = true', 'use_psiturk_ad_server = false')

        with open('config.txt', 'w') as file:
            file.write(config_file)
    yield do_it

@pytest.fixture()
def db_setup():
    def do_it():
        from psiturk import db
        db.init_db()
        db.truncate_tables()
    yield do_it

@pytest.fixture(scope='session')
def run_in_psiturk_shell():
    import psiturk.psiturk_shell as ps

    def do_it(execute_string):
        ps.run(cabinmode=False, execute=execute_string, quiet=True)
    return do_it



#############
# amt-related fixtures
##############
@pytest.fixture(scope='function')
def client():
    client = boto3.client('mturk')
    return client


@pytest.fixture(scope='function')
def stubber(client):
    stubber = Stubber(client)
    stubber.activate()
    yield stubber
    stubber.deactivate()

@pytest.fixture(scope='function')
def patch_aws_services(client, mocker):
    import psiturk.amt_services_wrapper
    import psiturk.amt_services

    def setup_mturk_connection(self):
        self.mtc = client
        return True

    mocker.patch.object(psiturk.amt_services.MTurkServices,
                        'verify_aws_login', lambda *args, **kwargs: True)
    mocker.patch.object(psiturk.amt_services.MTurkServices,
                        'setup_mturk_connection', setup_mturk_connection)

    my_amt_services = psiturk.amt_services.MTurkServices(
        '', '', is_sandbox=True)
    mocker.patch.object(
        psiturk.amt_services_wrapper.MTurkServicesWrapper, 'amt_services', my_amt_services)




class Helpers(object):

    @staticmethod
    def get_boto3_return(name):

        # https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
        def date_hook(json_dict):
            for (key, value) in list(json_dict.items()):
                try:
                    # json_dict[key] = dateutil.parser.parse(value)
                    # json_dict[key] = datetime.datetime.fromisoformat(value)
                    # json_dict[key] = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S%Z")
                    json_dict[key] = ciso8601.parse_datetime(value)
                except:
                    if key == 'Expiration':
                        print(key)
                        raise
                    pass
            return json_dict

        filepath = os.path.join(
            *[os.path.dirname(os.path.realpath(__file__)), 'boto3-returns', name])
        with open(filepath, 'rb') as infile:
            if filepath.endswith('.pickle'):
                if six.PY2:
                    return pickle.load(infile)
                else:
                    return pickle.load(infile, encoding='latin1')
            elif filepath.endswith('.json'):
                data = json.load(infile, object_hook=date_hook)
                # print(data['HITs'][0])
                return data


@pytest.fixture(scope='session')
def helpers():
    return Helpers

