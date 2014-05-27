import os, sys
import urllib2
import json
import datetime
import requests
from flask import jsonify
from version import version_number
import git

class PsiturkOrgServices:
    """
        PsiturkOrgServices
        this class provides an interface to the API provided
        by the psiturk_org website.  the two main features
        of this API are registering secure ads
        see: https://github.com/NYUCCL/api-psiturk-org
    """
    def __init__(self, key, secret):
        self.apiServer = 'https://api.psiturk.org' # 'https://api.psiturk.org' # by default for now
        self.adServer = 'https://ad.psiturk.org'
        self.sandboxAdServer = 'https://sandbox.ad.psiturk.org'
        self.update_credentials(key,secret)
        if not self.check_credentials():
            print 'WARNING *****************************'
            print 'Sorry, psiTurk Credentials invalid.\nYou will only be able to '\
                  + 'test experiments locally until you enter\nvalid '\
                  + 'credentials in the psiTurk Access section of ~/.psiturkconfig.\nGet your ' \
                  + 'credentials at https://www.psiturk.org/login.\n'

    def check_credentials(self):
        r = requests.get(self.apiServer + '/api/ad', auth=(self.access_key,self.secret_key))
        if r.status_code in [401, 403, 500]:  # not sure 500 server error should be included here
            return False
        else:
            return True

    def update_credentials(self, key, secret):
        self.access_key = key
        self.secret_key = secret 

    def connect(self, server):
        """
            connect:
            "connects to server"  since the is a fairly
            basic API, just allows overriding of which Ad server
            you are talking to
        """
        self.apiServer = server

    def get_system_status(self):
        """
            get_system_status:
        """
        try:
            api_server_status_link = self.apiServer + '/status_msg?version=' + version_number
            response=urllib2.urlopen(api_server_status_link,timeout=1)
            status_msg = json.load(response)['status']
        except:
            status_msg = "Sorry, can't connect to psiturk.org, please check your internet connection.\nYou will not be able to create new hits, but testing locally should work.\n"
        return status_msg
        
    def get_my_ip(self):
        """
            get_my_ip:
            asks and external server what your ip appears to be
            (useful is running from behind a NAT/wifi router).
            Of course, incoming port to the router must be
            forwarded correctly.
        """
        if 'OPENSHIFT_SECRET_TOKEN' in os.environ:
            ip = os.environ['OPENSHIFT_APP_DNS']
        else:
            ip = json.load(urllib2.urlopen('http://httpbin.org/ip'))['origin']
        return ip

    def create_record(self, name, content, username, password):
        #headers = {'key': username, 'secret': password}
        r = requests.post(self.apiServer + '/api/' + name, data=json.dumps(content), auth=(username,password))
        return r

    def update_record(self, name, recordid, content, username, password):
        #headers = {'key': username, 'secret': password}
        r = requests.put(self.apiServer + '/api/' + name + '/' + str(recordid), data=json.dumps(content), auth=(username,password))
        return r

    def delete_record(self, name, recordid, username, password):
        #headers = {'key': username, 'secret': password}
        r = requests.delete(self.apiServer + '/api/' + name + '/' + str(recordid), auth=(username,password))
        return r

    def query_records(self, name, username, password, query=''):
        #headers = {'key': username, 'secret': password}
        r = requests.get(self.apiServer + '/api/' + name + "/" + query, auth=(username,password))
        return r


    def get_ad_url(self, adId, sandbox):
        """
            get_ad_url:
            gets ad server thing
        """
        if sandbox:
            return self.sandboxAdServer + '/view/' + str(adId)
        else:
            return self.adServer + '/view/' + str(adId)

    def set_ad_hitid(self, adId, hitId, sandbox):
        """
            get_ad_hitid:
            updates the ad with the corresponding hitid
        """
        if sandbox:
            r = self.update_record('sandboxad', adId, {'amt_hit_id':hitId}, self.access_key, self.secret_key)
        else:    
            r = self.update_record('ad', adId, {'amt_hit_id':hitId}, self.access_key, self.secret_key)
        if r.status_code == 201:
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
                r = self.create_record('sandboxad', ad_content, self.access_key, self.secret_key)
            else:
                r = self.create_record('ad', ad_content, self.access_key, self.secret_key)
            if r.status_code == 201:
                return r.json()['ad_id']
            else:
                return False    

    def download_experiment(self, experiment_id):
        """
            download_experiment:
        """
        r = self.query_records('experiment', self.access_key, self.secret_key, query='download/'+experiment_id)
        print r.text
        return


class ExperimentExchangeServices:
    """
        ExperimentExchangeServices
        this class provides a non-authenticated interface to the API provided
        by the psiturk_org website.  the feature is
        interfacing with the experiment exchange
        see: https://github.com/NYUCCL/api-psiturk-org
    """
    def __init__(self):
        self.apiServer = 'https://api.psiturk.org' # 'https://api.psiturk.org' # by default for now

    def query_records_no_auth(self, name, query=''):
        #headers = {'key': username, 'secret': password}
        r = requests.get(self.apiServer + '/api/' + name + "/" + query)
        return r

    def download_experiment(self, experiment_id):
        """
            download_experiment:
        """
        r = self.query_records_no_auth('experiment', query='download/'+experiment_id)
        if r.status_code == 404:
            print "Sorry, no experiment matching id # " + experiment_id
            print "Please double check the code you obtained on the http://psiturk.org/ee"
        else:
            # check if folder with same name already exists.
            expinfo = r.json()
            gitr = requests.get(expinfo['git_url']).json()
            if os.path.exists('./'+gitr['name']):
                print "*"*20
                print "Sorry, you already have a file or folder named "+gitr['name']+". Please rename or delete it before trying to download this experiment.  You can do this by typing `rm -rf " + gitr['name'] + "`" 
                print "*"*20
                return
            if "clone_url" in gitr:
                git.Git().clone(gitr["clone_url"])
                print "="*20
                print "Downloading..."
                print "Name: " + expinfo['name']
                print "Downloads: " + str(expinfo['downloads'])
                print "Keywords: " + expinfo['keywords']
                print "psiTurk Version: " + str(expinfo['psiturk_version_string'])
                print "URL: http://psiturk.org/ee/"+experiment_id
                print "\n"
                print "Experiment downloaded into the `" + gitr['name'] + "` folder of the current directory"
                print "Type 'cd " + gitr['name'] + "` then run the `psiturk` command."
                print "="*20
            else:
                print "Sorry, experiment not located on github.  You might contact the author of this experiment.  Experiment NOT downloaded."
            return