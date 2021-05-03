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
import boto3
from botocore.stub import Stubber
import shutil
from distutils import dir_util, file_util
from faker import Faker
from importlib import reload


@pytest.fixture(autouse=True)
def bork_aws_environ():
    os.environ['AWS_ACCESS_KEY_ID'] = 'foo'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'bar'
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    os.environ.pop('AWS_PROFILE', None)
    yield


@pytest.fixture()
def edit_config_file():
    def do_it(find, replace):
        with open('config.txt', 'r') as file:
            config_file = file.read()

        config_file = config_file.replace(find, replace)

        with open('config.txt', 'w') as file:
            file.write(config_file)
    yield do_it


@pytest.fixture(scope='function', autouse=True)
def experiment_dir(tmpdir, bork_aws_environ, edit_config_file):
    os.chdir(tmpdir)
    import psiturk.setup_example as se
    se.setup_example()
    os.environ['PSITURK_AD_URL_DOMAIN'] = 'example.com'
    os.environ['PSITURK_LOGIN_USERNAME'] = 'foo'
    os.environ['PSITURK_LOGIN_PW'] = 'bar'
    os.environ['PSITURK_SECRET_KEY'] = 'baz'

    # the setup script already chdirs into here,
    # although I don't like that it does that
    # os.chdir('psiturk-example')
    yield

    os.chdir('..')
    shutil.rmtree('psiturk-example')


@pytest.fixture(autouse=True)
def db_setup(mocker, experiment_dir, tmpdir, request):
    import psiturk.db
    reload(psiturk.db)

    import psiturk.models
    psiturk.models.Base.metadata.clear()
    reload(psiturk.models)

    from psiturk.db import init_db
    init_db()

    yield


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


@pytest.fixture()
def amt_services_wrapper(patch_aws_services):
    import psiturk.amt_services_wrapper
    reload(psiturk.amt_services_wrapper)
    amt_services_wrapper = psiturk.amt_services_wrapper.MTurkServicesWrapper()
    return amt_services_wrapper


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

    my_amt_services = psiturk.amt_services.MTurkServices(mode='sandbox')
    mocker.patch.object(
        psiturk.amt_services_wrapper.MTurkServicesWrapper, 'amt_services', my_amt_services)


@pytest.fixture(scope='session')
def faker():
    faker = Faker()
    return faker


@pytest.fixture()
def stubber_prepare_create_hit(stubber, helpers, faker):
    def do_it(with_hit_id=None):
        if not with_hit_id:
            with_hit_id = faker.md5(raw_output=False)

        stubber.add_response(
            'create_hit_type', helpers.get_boto3_return('create_hit_type.json'))

        boto_return_create_hit_with_hit_type = helpers.get_boto3_return(
            'create_hit_with_hit_type.json')

        boto_return_create_hit_with_hit_type['HIT']['HITId'] = with_hit_id
        # used to always return a hit with id: 3XJOUITW8URHJMX7F00H20LGRIAQTX

        stubber.add_response('create_hit_with_hit_type',
                             boto_return_create_hit_with_hit_type)
    return do_it


@pytest.fixture()
def create_dummy_hit(stubber_prepare_create_hit, amt_services_wrapper):

    def do_it(with_hit_id=None, **kwargs):
        stubber_prepare_create_hit(with_hit_id)
        result = amt_services_wrapper.create_hit(1, 0.01, 1, **kwargs)
        if not result.success:
            raise result.exception

    return do_it


@pytest.fixture()
def create_dummy_assignment(faker):
    from psiturk.db import db_session, init_db
    from psiturk.models import Participant

    def do_it(participant_attributes=None):
        if not participant_attributes:
            participant_attributes = {}
        participant_attribute_defaults = {
            'workerid': faker.md5(raw_output=False),
            'hitid': faker.md5(raw_output=False),
            'assignmentid': faker.md5(raw_output=False),
        }

        participant_attributes = dict(
            list(participant_attribute_defaults.items()) +
            list(participant_attributes.items())
        )
        init_db()

        participant = Participant(**participant_attributes)
        db_session.add(participant)
        db_session.commit()

        return participant

    return do_it


@pytest.fixture()
def list_hits(stubber, helpers, amt_services_wrapper):
    """
    Returns two hit_ids:
        3BFNCI9LYKQ2ENUY4MLKKW0NSU437W
        3XJOUITW8URHJMX7F00H20LGRIAQTX
    """
    def do_it(hits_json=None, all_studies=False, active=False):
        if not hits_json:
            hits_json = helpers.get_boto3_return('list_hits.json')

        stubber.add_response('list_hits', hits_json)
        if active:
            results = (amt_services_wrapper.get_active_hits(
                all_studies=all_studies)).data
        else:
            results = (amt_services_wrapper.get_all_hits(
                all_studies=all_studies)).data
        return results

    return do_it


@pytest.fixture()
def expire_a_hit():
    def do_it(hits_json, index_of_hit_to_expire=0):
        expired_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=10)
        hits_json['HITs'][index_of_hit_to_expire]['Expiration'] = expired_time
        return hits_json
    return do_it


@pytest.fixture()
def activate_a_hit():
    def do_it(hits_json, index_of_hit_to_be_active=1):
        active_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=10)
        hits_json['HITs'][index_of_hit_to_be_active]['Expiration'] = active_time
        return hits_json
    return do_it


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
                return pickle.load(infile, encoding='latin1')
            elif filepath.endswith('.json'):
                data = json.load(infile, object_hook=date_hook)
                # print(data['HITs'][0])
                return data


@pytest.fixture(scope='session')
def helpers():
    return Helpers
