# -*- coding: utf-8 -*-
""" This module provides additional tools for psiTurk users. """
from __future__ import generator_stop
from functools import wraps, update_wrapper
from flask import request, Response, make_response, current_app
from .psiturk_exceptions import PsiturkException

# provides easy way to print to log in custom.py
# =========================================


def print_to_log(stuff_to_print):
    current_app.logger.info(stuff_to_print)


# Decorator for turning off browser caching
# =========================================

def nocache(func):
    """Stop caching for pages wrapped in nocache decorator."""
    def new_func(*args, **kwargs):
        """ No cache Wrapper """
        resp = make_response(func(*args, **kwargs))
        resp.cache_control.no_cache = True
        return resp
    return update_wrapper(new_func, func)


# Authentication decorator
# ========================

class PsiTurkAuthorization(object):
    """ Authorize route """

    def __init__(self, config):
        username = config.get('Server Parameters', 'login_username')
        password = config.get('Server Parameters', 'login_pw')
        if not username or not password:
            raise PsiturkException(message='login_username or login_pw not set! Set them in config.txt')
        self.queryname = username
        self.querypw = password

    @classmethod
    def wrapper(cls, func, args):
        """ Auth wrapper """
        return func(*args)

    def check_auth(self, username, password):
        """ This function is called to check if a username password combination
            is valid. """
        return username == self.queryname and password == self.querypw

    @classmethod
    def authenticate(cls):
        """Sends a 401 response that enables basic auth"""
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )

    def requires_auth(self, func):
        """
        Decorator to prompt for user name and password. Useful for data dumps,
        etc.  That you don't want to be public.
        """
        @wraps(func)
        def decorated(*args, **kwargs):
            """ Wrapper """
            auth = request.authorization
            if not auth or not self.check_auth(auth.username, auth.password):
                return self.authenticate()
            return func(*args, **kwargs)
        return decorated
