class PsiturkException(Exception):
    def __str__(self):
        return '{}: {}'.format(type(self).__name__, self.message)
    
class DoBonusError(PsiturkException):
    def __init__(self, assignment_id=''):
        self.assignment_id = assignment_id
    
class AssignmentAlreadyBonusedError(DoBonusError):
    pass
    
class BadBonusAmountError(DoBonusError):
    def __init__(self, amount, **kwargs):
        super(BadBonusAmountError, self).__init__(**kwargs)
        self.message = 'Bonus must be a number greater than 0. You gave: {}'.format(amount)
        
class BonusReasonMissingError(DoBonusError):
    pass