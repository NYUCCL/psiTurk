import os
from ConfigParser import ConfigParser
from boto.mturk.connection import MTurkConnection

framework_root = os.path.abspath( 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                 os.path.pardir))
configfilename = os.path.join(framework_root, 'config.txt')

config = ConfigParser()
config.read( configfilename )

host = 'mechanicalturk.amazonaws.com'
mturkparams = dict(
    aws_access_key_id = config.get( 'AWS Access', 'aws_access_key_id' ),
    aws_secret_access_key = config.get( 'AWS Access', 'aws_secret_access_key' ),
    host=host)
mtc = MTurkConnection( **mturkparams )

###########################################################
# let's start
###########################################################
if __name__ == '__main__':
    print mtc.get_account_balance()
