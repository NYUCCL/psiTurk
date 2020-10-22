from __future__ import generator_stop

class PsiturkException(Exception):
    def __init__(self, *args, **kwargs):
        super(PsiturkException, self).__init__(*args)
        self.message = kwargs['message'] if 'message' in kwargs else ''
        
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, self.message)
        
    def to_dict(self):
        return {
            'exception': type(self).__name__,
            'message': self.message
        }

####################################################
# AMT Services Exceptions
####################################################


class AmtServicesException(PsiturkException):
    
    def __init__(self, **kwargs):
        super(AmtServicesException, self).__init__(**kwargs)


class AWSAccessKeysNotSetError(AmtServicesException):
    def __init__(self, **kwargs):
        message = 'AWS access keys not set in ~/.psiturkconfig; please enter valid credentials.'
        super(AWSAccessKeysNotSetError, self).__init__(message=message, **kwargs)


class NoMturkConnectionError(AmtServicesException):
    def __init__(self, **kwargs):
        message = 'Sorry, unable to connect to Amazon Mechanical Turk. AWS credentials invalid.'
        super(NoMturkConnectionError, self).__init__(message=message, **kwargs)

####################################################
# AMT Service Wrapper Exceptions
####################################################


class AmtServicesWrapperError(PsiturkException):
    pass


class DoBonusError(AmtServicesWrapperError):
    def __init__(self, assignment_id='', **kwargs):
        super(DoBonusError, self).__init__(**kwargs)
        self.assignment_id = assignment_id


class AssignmentAlreadyBonusedError(DoBonusError):
    pass


class BadBonusAmountError(DoBonusError):
    def __init__(self, amount, **kwargs):
        super(BadBonusAmountError, self).__init__(**kwargs)
        self.message = 'Bonus must be a number greater than 0. You gave: {}'.format(
            amount)


class BonusReasonMissingError(DoBonusError):
    pass


class NoAutoBonusAmountSetError(DoBonusError):
    pass


class AssignmentIdNotFoundInLocalDBError(AmtServicesWrapperError):
    def __init__(self, assignment_id='', **kwargs):
        super(AssignmentIdNotFoundInLocalDBError, self).__init__(**kwargs)
        self.assignment_id = assignment_id


class WorkerIdNotFoundInLocalDBError(AmtServicesWrapperError):
    pass


class MissingArgumentsError(AmtServicesWrapperError):
    pass


class InvalidPsiturkCredentialsError(AmtServicesWrapperError):
    def __init__(self, *args, **kwargs):
        super(InvalidPsiturkCredentialsError, self).__init__(*args, **kwargs)
        self.message = '\n'.join([
            '*****************************',
            '  Sorry, your psiTurk Credentials are invalid.\n ',
            '  You cannot create ads and hits until you enter valid credentials in ',
            '  the \'psiTurk Access\' section of ~/.psiturkconfig.  You can obtain your',
            '  credentials or sign up at https://www.psiturk.org/login.\n'])


class InvalidAWSCredentialsError(AmtServicesWrapperError):
    def __init__(self, *args, **kwargs):
        super(InvalidAWSCredentialsError, self).__init__(*args, **kwargs)
        self.message = '\n'.join([
            '*****************************',
            '  Sorry, your AWS Credentials are invalid.\n ',
            '  You cannot create ads and hits until you enter valid credentials in ',
            '  the \'AWS Access\' section of ~/.psiturkconfig.  You can obtain your ',
            '  credentials via the Amazon AMT requester website.\n'])


class AdPsiturkOrgError(AmtServicesWrapperError):
    pass


class AdHtmlNotFoundError(AmtServicesWrapperError):
    def __init__(self, *args, **kwargs):
        super(AdHtmlNotFoundError, self).__init__(*args, **kwargs)
        self.message = '\n'.join([
            '*****************************',
            '  Sorry, there was an error registering ad.',
            '  The file ad.html is required to be in the templates folder',
            '  of your project so that the ad can be served.'])


class AdHtmlTooLarge(AmtServicesWrapperError):
    def __init__(self, size_of_ad, *args, **kwargs):
        super(AdHtmlTooLarge, self).__init__(*args, **kwargs)
        self.message = '\n'.join([
            '*****************************',
            '  Sorry, there was an error registering the ad.',
            '  Your local ad.html is {} bytes, but the maximum'.format(size_of_ad),
            '  template size uploadable to the ad server is',
            '  1048576 bytes.'])
                                 
#################
# API Exceptions
#################


class APIException(PsiturkException):
    pass


class EphemeralContainerDBError(PsiturkException):
    def __init__(self, db_address, *args, **kwargs):
        super(EphemeralContainerDBError, self).__init__(**kwargs)
        self.message = '\n'.join([
            f'The database URL you gave is {db_address}. This is unlikely to work ',
            'in an ephemeral container like Heroku either because it is run on a localhost or because it uses SQLite ',
            '(see https://devcenter.heroku.com/articles/sqlite3 for why that might not be a good idea). One better '
            'option might be to use a Heroku PostGRES table. Instructions to do that can be found here: ',
            'https://psiturk.readthedocs.io/en/latest/heroku.html'])


class HerokuCmdNotFound(PsiturkException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = 'command `heroku` command not found. Please first install the heroku cmd cli.'


class HerokuNotLoggedIn(PsiturkException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = 'Heroku cli not logged in. Please run `heroku auth:login` first.'


class HerokuNotAGitRepo(PsiturkException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = 'Current directory is not a git repository. See https://devcenter.heroku.com/articles/git for help.'


class HerokuAppNotSet(PsiturkException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = 'Heroku app not known. '
