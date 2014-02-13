import os, sys
import urllib2
import json
import datetime
from flask import jsonify

class PsiturkOrgServices:
    """
        PsiturkOrgServices
        this class provides an interface to the API provided
        by the psiturk_org website.  the two main features
        of this API are registering secure ads and
        interfacing with the experiment exchange
        see: https://github.com/NYUCCL/psiTurk_website
    """
    def __init__(self, ad_server_location, contact_email):
        self.adServer = ad_server_location # by default for now
        if self.adServer[-1]=='/':
            self.adServer = self.adServer[:-1]
        self.contactEmail = contact_email

    def connect(self, server):
        """
            connect:
            "connects to server"  since the is a fairly
            basic API, just allows overriding of which Ad server
            you are talking to
        """
        self.adServer = server

    def get_system_status(self):
        """
            get_system_status:
        """
        try:
            ad_server_status_link= 'http://api.psiturk.org/get_status_msg'
            response=urllib2.urlopen(ad_server_status_link,timeout=1)
            status_msg = json.load(response)['status']
        except urllib2.URLError as err:
            status_msg = "Sorry, can't connect to psiturk.org, please check your internet connection.\n You will not be able to create new hits, but testing locally should work."  
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

    def get_ad_url(self, adId):
        """
            get_ad_url:
            gets ad server thing
        """
        return self.adServer + '/ad/' + str(adId)

    def set_ad_hitid(self, adId, hitId):
        """
            get_ad_hitid:
            updates the ad with the corresponding hitid
        """
        ad_server_update_link = self.adServer + '/ad/' + str(adId) + '/link?hitid=' + hitId
        response = urllib2.urlopen(ad_server_update_link)
        if json.load(response)['status']=="we're good!":
            return True
        else:
            return False

    def delete_ad(self, hitId):
        """
            delete_ad:
        """
        ad_server_expire_link = self.adServer + '/ad/delete?hitid=' + hitId
        response = urllib2.urlopen(ad_server_expire_link)
        status_msg = json.load(response)['status']
        if status_msg=="we're good!" or status_msg=="add not found":
            return True
        else:
            return False

    def create_ad(self, ad_content):
        """
            create_ad:
        """
        ad_server_register_url = self.adServer + '/ad/register'
        #ad_server_register_url = 'http://0.0.0.0:5004/ad/register'
        req = urllib2.Request(ad_server_register_url)
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req, json.dumps(ad_content))
        
        # 2. get id in response
        data = json.load(response) 
        if isinstance(data['id'], int):
            return data['id']
        else:
            if data['id'] == "correct parameters not provided":
                print "Error: registering Ad with server, you didn't provide all the required parameters (server, port, support_ie)"
                return False
            elif data['id'] == "localhost not allowed":
                print "Error: attempting to localhost or 127.0.0.1 as your server location to the Ad server, but this is not allowed.  Check the 'host' parameter in config.txt and make it a publically accessible hostname/ip."
                return False
            elif data['id'][:25] == "The maximum template size":
                print data['id']  # print out the message about template size
                return False
