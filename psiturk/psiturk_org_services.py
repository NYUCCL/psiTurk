# -*- coding: utf-8 -*-
""" This module """
from __future__ import print_function

try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError
    
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
    

import git
from psiturk.version import version_number
import requests
import json
import os
from builtins import object
from builtins import str
from future import standard_library
standard_library.install_aliases()


class PsiturkOrgServices(object):
    """
        PsiturkOrgServices this class provides an interface to the API provided
        by the psiturk_org website. The main feature of this API is
        registering secure ads. See:
        https://github.com/NYUCCL/api-psiturk-org
    """

    def __init__(self, key, secret):

        # 'https://api.psiturk.org' # by default for now
        self.api_server = 'https://api.psiturk.org'
        self.ad_server = 'https://ad.psiturk.org'
        self.sandbox_ad_server = 'https://sandbox.ad.psiturk.org'
        self.update_credentials(key, secret)
        if not self.check_credentials():
            print('WARNING *****************************')
            print('Sorry, psiTurk Credentials invalid.\nYou will only be able '
                  + 'to test experiments locally until you enter\nvalid '
                  + 'credentials in the psiTurk Access section of '
                  + '~/.psiturkconfig.\n  Get your credentials at '
                  + 'https://www.psiturk.org/login.\n')

    def check_credentials(self):
        ''' Check credentials '''
        req = requests.get(self.api_server + '/api/ad',
                           auth=(self.access_key, self.secret_key))
        # Not sure 500 server error should be included here
        if req.status_code in [401, 403, 500]:
            return False
        else:
            return True

    def update_credentials(self, key, secret):
        ''' Update credentials '''
        self.access_key = key
        self.secret_key = secret

    def connect(self, server):
        """
            connect:
                "connects to server"  since the is a fairly
            basic API, just allows overriding of which Ad server
            you are talking to
        """
        self.api_server = server

    def get_system_status(self):
        """
            get_system_status:
        """
        try:
            api_server_status_link = self.api_server + '/status_msg?version=' +\
                version_number
            response = urlopen(
                api_server_status_link, timeout=1)
            status_msg = json.load(response)['status']
        except HTTPError:
            status_msg = "Sorry, can't connect to psiturk.org, please check\
                your internet connection.\nYou will not be able to create new\
                hits, but testing locally should work.\n"
        return status_msg

    def create_record(self, name, content, username, password):
        ''' Create record '''
        #headers = {'key': username, 'secret': password}
        req = requests.post(self.api_server + '/api/' + name,
                            data=json.dumps(content), auth=(username, password))
        return req

    def update_record(self, name, recordid, content, username, password):
        ''' Update record '''
        # headers = {'key': username, 'secret': password}
        req = requests.put(self.api_server + '/api/' + name + '/' +
                           str(recordid), data=json.dumps(content),
                           auth=(username, password))
        return req

    def delete_record(self, name, recordid, username, password):
        ''' Delete record '''
        #headers = {'key': username, 'secret': password}
        req = requests.delete(self.api_server + '/api/' + name + '/' +
                              str(recordid), auth=(username, password))
        return req

    def query_records(self, name, username, password, query=''):
        ''' Query records '''
        #headers = {'key': username, 'secret': password}
        req = requests.get(self.api_server + '/api/' + name + "/" + query,
                           auth=(username, password))
        return req

    def get_ad_url(self, ad_id, sandbox):
        """
            get_ad_url:
            gets ad server thing
        """
        if sandbox:
            return self.sandbox_ad_server + '/view/' + str(ad_id)
        else:
            return self.ad_server + '/view/' + str(ad_id)

    def set_ad_hitid(self, ad_id, hit_id, sandbox):
        """
            get_ad_hitid:
            updates the ad with the corresponding hitid
        """
        if sandbox:
            req = self.update_record('sandboxad', ad_id, {'amt_hit_id': hit_id},
                                     self.access_key, self.secret_key)
        else:
            req = self.update_record('ad', ad_id, {'amt_hit_id': hit_id},
                                     self.access_key, self.secret_key)
        if req.status_code == 201:
            return True
        else:
            return False

    def create_ad(self, ad_content):
        """
            create_ad:
        """
        if not 'is_sandbox' in ad_content:
            return False
        else:
            if ad_content['is_sandbox']:
                req = self.create_record(
                    'sandboxad', ad_content, self.access_key, self.secret_key
                )
            else:
                req = self.create_record(
                    'ad', ad_content, self.access_key, self.secret_key
                )
            if req.status_code == 201:
                return req.json()['ad_id']
            else:
                return False

    def download_experiment(self, experiment_id):
        """
            download_experiment:
        """
        req = self.query_records('experiment', self.access_key,
                                 self.secret_key,
                                 query='download/'+experiment_id)
        print(req.text)
        return


class ExperimentExchangeServices(object):
    """
        ExperimentExchangeServices
        this class provides a non-authenticated interface to the API provided
        by the psiturk_org website.  the feature is interfacing with the
        experiment exchange see: https://github.com/NYUCCL/api-psiturk-org
    """

    def __init__(self):
        # 'https://api.psiturk.org' # by default for now
        self.api_server = 'https://api.psiturk.org'

    def query_records_no_auth(self, name, query=''):
        ''' Query records without authorization '''
        #headers = {'key': username, 'secret': password}
        req = requests.get(self.api_server + '/api/' + name + "/" + query)
        return req

    def download_experiment(self, experiment_id):
        """
            download_experiment:
        """
        req = self.query_records_no_auth('experiment',
                                         query='download/'+experiment_id)
        if req.status_code == 404:
            print("Sorry, no experiment matching id # " + experiment_id)
            print("Please double check the code you obtained on the\
                http://psiturk.org/ee")
        else:
            # Check if folder with same name already exists.
            expinfo = req.json()
            gitr = requests.get(expinfo['git_url']).json()
            if os.path.exists('./'+gitr['name']):
                print("*"*20)
                print("Sorry, you already have a file or folder named\
                    "+gitr['name']+". Please rename or delete it before trying\
                    to download this experiment.  You can do this by typing `rm\
                    -rf " + gitr['name'] + "`")
                print("*"*20)
                return
            if "clone_url" in gitr:
                git.Git().clone(gitr["clone_url"])
                print("="*20)
                print("Downloading...")
                print("Name: " + expinfo['name'])
                print("Downloads: " + str(expinfo['downloads']))
                print("Keywords: " + expinfo['keywords'])
                print("psiTurk Version: " +
                      str(expinfo['psiturk_version_string']))
                print("URL: http://psiturk.org/ee/"+experiment_id)
                print("\n")
                print("Experiment downloaded into the `" + gitr['name'] + "`\
                    folder of the current directory")
                print("Type 'cd " + gitr['name'] + "` then run the `psiturk`\
                    command.")
                print("="*20)
            else:
                print("Sorry, experiment not located on github.  You might\
                    contact the author of this experiment.  Experiment NOT\
                    downloaded.")
            return
