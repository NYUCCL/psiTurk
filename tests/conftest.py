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

@pytest.fixture(scope='session')
def experiment_dir():
    import shutil
    shutil.rmtree('psiturk-example', ignore_errors=True)
    import psiturk.setup_example as se
    se.setup_example()
    
    # change config file...
    with open('config.txt', 'r') as file:
        config_file = file.read()
        
    config_file = config_file.replace('use_psiturk_ad_server = true', 'use_psiturk_ad_server = false')
        
    with open('config.txt', 'w') as file:
        file.write(config_file)
    
    # os.chdir('psiturk-example') # the setup script already chdirs into here, although I don't like that it does that
    os.environ['AWS_ACCESS_KEY_ID'] = 'foo'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'bar'
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    os.environ.pop('AWS_PROFILE', None)
    
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
        
        filepath = os.path.join(*[os.path.dirname(os.path.realpath(__file__)), 'boto3-returns', name])
        with open(filepath, 'rb') as infile:
            if filepath.endswith('.pickle'):
                return pickle.load(infile)
            elif filepath.endswith('.json'):
                data = json.load(infile, object_hook=date_hook)
                # print(data['HITs'][0])
                return data
            
@pytest.fixture(scope='session')    
def helpers():
    return Helpers
    
@pytest.fixture()
def db_setup():
    import psiturk.models
    from psiturk import db
    db.init_db()
    db.truncate_tables()
    yield
    db.truncate_tables()
    
@pytest.fixture(scope='session')
def run_in_psiturk_shell():
    import psiturk.psiturk_shell as ps
    def do_it(execute_string):
        ps.run(cabinmode=False, execute=execute_string, quiet=True)
    return do_it
    