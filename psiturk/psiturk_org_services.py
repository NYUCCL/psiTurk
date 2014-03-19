import os, sys
import urllib2
import json
import datetime
import requests
from flask import jsonify
from version import version_number

class PsiturkOrgServices:
    """
        PsiturkOrgServices
        this class provides an interface to the API provided
        by the psiturk_org website.  the two main features
        of this API are registering secure ads and
        interfacing with the experiment exchange
        see: https://github.com/NYUCCL/psiTurk_website
    """
    def __init__(self, key, secret):
        self.apiServer = 'https://api.psiturk.org' # 'https://api.psiturk.org' # by default for now
        self.adServer = 'https://ad.psiturk.org'
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
        return json.load(urllib2.urlopen('http://httpbin.org/ip'))['origin']

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


    def get_ad_url(self, adId):
        """
            get_ad_url:
            gets ad server thing
        """
        return self.adServer + '/view/' + str(adId)

    def set_ad_hitid(self, adId, hitId):
        """
            get_ad_hitid:
            updates the ad with the corresponding hitid
        """
        r = self.update_record('ad', adId, {'amt_hit_id':hitId}, self.access_key, self.secret_key)
        if r.status_code == 201:
            return True
        else:
            return False        

    def create_ad(self, ad_content):
        """
            create_ad:
        """
        r = self.create_record('ad', ad_content, self.access_key, self.secret_key)
        if r.status_code == 201:
            return r.json()['ad_id']
        else:
            return False        
