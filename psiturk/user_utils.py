from functools import wraps
from flask import Flask, render_template, request, Response, jsonify


#----------------------------------------------
# class for adding for authentication decorator
#----------------------------------------------
class PsiTurkAuthorization():

    def __init__(self, config):
        self.queryname = config.get('Server Parameters', 'login_username')
        self.querypw = config.get('Server Parameters', 'login_pw')

    def wrapper(func, args):
        return func(*args)

    def check_auth(self, username, password):
        """This function is called to check if a username /
        password combination is valid.
        """
        return username == self.queryname and password == self.querypw

    def authenticate(self):
        """Sends a 401 response that enables basic auth"""
        return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

    def requires_auth(self, f):
        """
        Decorator to prompt for user name and password. Useful for data dumps, etc.
        that you don't want to be public.
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth or not self.check_auth(auth.username, auth.password):
                return self.authenticate()
            return f(*args, **kwargs)
        return decorated