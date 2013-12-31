"""
Usage:
    psiturk_shell
"""
import sys
import subprocess
import re
import time
import json
import os
import string
import random
import datetime

from cmd2 import Cmd
from docopt import docopt, DocoptExit
import readline

import webbrowser

import MySQLdb

from amt_services import MTurkServices, RDSServices
from psiturk_org_services import PsiturkOrgServices
from version import version_number
from psiturk_config import PsiturkConfig
import experiment_server_controller as control
from models import Participant

# Escape sequences for display.
def colorize(target, color):
    colored = ''
    if color == 'purple':
        colored = '\001\033[95m\002' + target
    elif color == 'cyan':
        colored = '\001\033[96m\002' + target
    elif color == 'darkcyan':
        colored = '\001\033[36m\002' + target
    elif color == 'blue':
        colored = '\001\033[93m\002' + target
    elif color == 'green':
        colored = '\001\033[92m\002' + target
    elif color == 'yellow':
        colored = '\001\033[93m\002' + target
    elif color == 'red':
        colored = '\001\033[91m\002' + target
    elif color == 'white':
        colored = '\001\033[37m\002' + target
    elif color == 'bold':
        colored = '\001\033[1m\002' + target
    elif color == 'underline':
        colored = '\001\033[4m\002' + target
    return colored + '\001\033[0m\002'


# Decorator function borrowed from docopt.
def docopt_cmd(func):
    """
    This decorator is used to simplify the try/except block and pass the result
    of the docopt parsing to the called action.
    """
    def fn(self, arg):
        try:
            opt = docopt(fn.__doc__, arg)
        except DocoptExit as e:
            # The DocoptExit is thrown when the args do not match.
            # We print a message to the user and the usage block.
            print('Invalid Command!')
            print(e)
            return
        except SystemExit:
            # The SystemExit exception prints the usage for --help
            # We do not need to do the print here.
            return
        return func(self, opt)
    fn.__name__ = func.__name__
    fn.__doc__ = func.__doc__
    fn.__dict__.update(func.__dict__)
    return fn


#---------------------------------
# psiturk shell class
#  -  all commands contained in methods titled do_XXXXX(self, arg)
#  -  if a command takes any arguments, use @docopt_cmd decorator
#     and describe command usage in docstring
#---------------------------------
class PsiturkShell(Cmd):


    def __init__(self, config, amt_services, aws_rds_services, web_services, server):
        Cmd.__init__(self)
        self.config = config
        self.server = server
        self.amt_services = amt_services
        self.web_services = web_services
        self.db_services = aws_rds_services
        self.sandbox = self.config.getboolean('HIT Configuration', 
                                              'using_sandbox')
        self.sandboxHITs = 0
        self.liveHITs = 0
        self.tally_hits()
        self.color_prompt()
        self.intro = colorize('psiTurk version ' + version_number +
                              '\nType "help" for more information.', 'green')
        # Prevents running of commands by abbreviation
        self.abbrev = False
        self.debug = True
        self.helpPath = os.path.join(os.path.dirname(__file__), "shell_help/")


    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  basic command line functions
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.

    def color_prompt(self):
        prompt = '[' + colorize('psiTurk', 'bold')
        serverString = ''
        server_status = self.server.is_server_running()
        if server_status == 'yes':
            serverString = colorize('on', 'green')
        elif server_status == 'no':
            serverString = colorize('off', 'red')
        elif server_status == 'maybe':
            serverString = colorize('wait', 'yellow')
        prompt += ' server:' + serverString
        if self.sandbox:
            prompt += ' mode:' + colorize('sdbx', 'bold')
        else:
            prompt += ' mode:' + colorize('live', 'bold')
        if self.sandbox:
            prompt += ' #HITs:' + str(self.sandboxHITs)
        else:
            prompt += ' #HITs:' + str(self.liveHITs)
        prompt += ']$ '
        self.prompt = prompt

    # keep persistent command history
    def preloop(self):
        # create file if it doesn't exist
        open('.psiturk_history', 'a').close()
        readline.read_history_file('.psiturk_history')
        for i in range(readline.get_current_history_length()):
            if readline.get_history_item(i) != None:
                self.history.append(readline.get_history_item(i))
        Cmd.preloop(self)

    def postloop(self):
        readline.write_history_file('.psiturk_history')
        Cmd.postloop(self)

    def onecmd_plus_hooks(self, line):
        if not line:
            return self.emptyline()
        return Cmd.onecmd_plus_hooks(self, line)

    def postcmd(self, stop, line):
        self.color_prompt()
        return Cmd.postcmd(self, stop, line)

    def emptyline(self):
        self.color_prompt()
    
    # add space after a completion, makes tab completion with 
    # multi-word commands cleaner
    def complete(self, text, state):
        return Cmd.complete(self, text, state) + ' '


    def tally_hits(self):
        hits = self.amt_services.get_active_hits()
        if hits:
            if self.sandbox:
                self.sandboxHITs = len(hits)
            else:
                self.liveHITs = len(hits)


    def hit_create(self, numWorkers, reward, duration):
        interactive = False
        if numWorkers is None:
            interactive = True
            numWorkers = raw_input('number of participants? ')
        try:
            int(numWorkers)
        except ValueError:

            print '*** number of participants must be a whole number'
            return
        if int(numWorkers) <= 0:
            print '*** number of participants must be greater than 0'
            return
        if interactive:
            reward = raw_input('reward per HIT? ')
        p = re.compile('\d*.\d\d')
        m = p.match(reward)
        if m is None:
            print '*** reward must have format [dollars].[cents]'
            return
        if interactive:
            duration = raw_input('duration of hit (in hours)? ')
        try:
            int(duration)
        except ValueError:
            print '*** duration must be a whole number'
            return
        if int(duration) <= 0:
            print '*** duration must be greater than 0'
            return
        self.config.set('HIT Configuration', 'max_assignments',
                        numWorkers)
        self.config.set('HIT Configuration', 'reward', reward)
        self.config.set('HIT Configuration', 'duration', duration)

        # register with the ad server (psiturk.org/ad/register) using POST
        if os.path.exists('templates/ad.html'):
            ad_html = open('templates/ad.html').read()
        else:
            print '*****************************'
            print '  Sorry there was an error registering ad.'
            print "  Both ad.html is required to be in the templates/ folder of your project so that these Ad can be served!"
            return

        size_of_ad = sys.getsizeof(ad_html)
        if size_of_ad >= 1048576:
            print '*****************************'
            print '  Sorry there was an error registering ad.'
            print "  Your local ad.html is %s byes, but the maximum template size uploadable to the Ad server is 1048576 bytes!", size_of_ad
            return

        # what all do we need to send to server?
        # 1. server
        # 2. port 
        # 3. support_ie?
        # 4. ad.html template
        # 5. contact_email in case an error happens
        
        ad_content = {
            "server": str(self.web_services.get_my_ip()),
            "port": str(self.config.get('Server Parameters', 'port')),
            "support_ie": str(self.config.get('Task Parameters', 'support_ie')),
            "is_sandbox": str(self.sandbox),
            "ad.html": ad_html,
            "contact_email": str(self.config.get('Secure Ad Server', 'contact_email'))
        }

        create_failed = False
        ad_id = self.web_services.create_ad(ad_content)
        if ad_id != False:
            ad_url = self.web_services.get_ad_url(ad_id)
            hit_config = {
                "ad_location": ad_url,
                "approve_requirement": self.config.get('HIT Configuration', 'Approve_Requirement'),
                "us_only": self.config.getboolean('HIT Configuration', 'US_only'),
                "lifetime": datetime.timedelta(hours=self.config.getfloat('HIT Configuration', 'lifetime')),
                "max_assignments": self.config.getint('HIT Configuration', 'max_assignments'),
                "title": self.config.get('HIT Configuration', 'title'),
                "description": self.config.get('HIT Configuration', 'description'),
                "keywords": self.config.get('HIT Configuration', 'keywords'),
                "reward": self.config.getfloat('HIT Configuration', 'reward'),
                "duration": datetime.timedelta(hours=self.config.getfloat('HIT Configuration', 'duration'))
            }
            hit_id = self.amt_services.create_hit(hit_config)
            if hit_id != False:
                if not self.web_services.set_ad_hitid(ad_id, hit_id):
                    create_failed = True
            else:
                create_failed = True
        else:
            create_failed = True

        if create_failed:
            print '*****************************'
            print '  Sorry there was an error creating hit and registering ad.'

        else:
            if self.sandbox:
                self.sandboxHITs += 1
            else:
                self.liveHITs += 1
            #print results
            total = float(numWorkers) * float(reward)
            fee = total / 10
            total = total + fee
            location = ''
            if self.sandbox:
                location = 'sandbox'
            else:
                location = 'live'
            print '*****************************'
            print '  Creating %s HIT' % colorize(location, 'bold')
            print '    HITid: ', str(hit_id)
            print '    Max workers: ' + numWorkers
            print '    Reward: $' + reward
            print '    Duration: ' + duration + ' hours'
            print '    Fee: $%.2f' % fee
            print '    ________________________'
            print '    Total: $%.2f' % total
            print '  Ad for this HIT now hosted at: http://psiturk.org/ad/' + str(ad_id) + "?assignmentId=debug" + str(self.random_id_generator()) \
                        + "&hitId=debug" + str(self.random_id_generator())



    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  server management
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def server_launch(self):
        self.server.startup()
        while self.server.is_server_running() != 'yes':
            time.sleep(0.5)
                
    def server_shutdown(self):
        self.server.shutdown()
        print 'Please wait. This could take a few seconds.'
        while self.server.is_server_running() != 'no':
            time.sleep(0.5)

    def server_relaunch(self):
        self.server_shutdown()
        self.server_launch()

    def server_log(self):
        logfilename = self.config.get('Server Parameters', 'logfile')
        if sys.platform == "darwin":
            args = ["open", "-a", "Console.app", logfilename]
        else:
            args = ["xterm", "-e", "'tail -f %s'" % logfilename]
        subprocess.Popen(args, close_fds=True)
        print "Log program launching..."

    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  worker management
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def worker_list(self):
        workers = self.amt_services.get_workers()
        if not workers:
            print colorize('failed to get workers', 'red')
        else:
            print json.dumps(self.amt_services.get_workers(), indent=4,
                             separators=(',', ': '))
    
    def worker_approve(self, allWorkers, assignment_ids = []):
        if allWorkers:
            workers = self.amt_services.get_workers()
            assignment_ids = [worker['assignmentId'] for worker in workers]
        for assignmentID in assignment_ids:
            success = self.amt_services.approve_worker(assignmentID)
            if success:
                print 'approved', assignmentID
            else:
                print '*** failed to approve', assignmentID

    def worker_reject(self, allWorkers, assignment_ids = None):
        if allWorkers:
            workers = self.amt_services.get_workers()
            assignment_ids = [worker['assignmentId'] for worker in workers]
        for assignmentID in assignment_ids:
            success = self.amt_services.reject_worker(assignmentID)
            if success:
                print 'rejected', assignmentID
            else:
                print '*** failed to reject', assignmentID

    
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  hit management
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def aws_balance(self):
        print self.amt_services.check_balance()

    
    def hit_list(self, allHits, activeHits, reviewableHits):
        hits_data = []
        if allHits:
            hits_data = self.amt_services.get_all_hits()
        elif activeHits:
            hits_data = self.amt_services.get_active_hits()
        elif reviewableHits:
            hits_data = self.amt_services.get_reviewable_hits()
        if not hits_data:
            print '*** no hits retrieved'
        else:
            for hit in hits_data:
                print hit
        

        

    def hit_extend(self, hitID, assignments, time):
        self.amt_services.extend_hit(hitID, assignments, time)




    def hit_dispose(self, allHits, hitIDs=None):
        if allHits:
            hits_data = self.amt_services.get_all_hits()
            hitIDs = [hit.options['hitid'] for hit in hits_data if (hit.options['status']=="Reviewable")]
        for hit in hitIDs:
            # check that the his is reviewable
            status = self.amt_services.get_hit_status(hit)
            if not status:
                print "*** Error getting hit status"
                return                
            if self.amt_services.get_hit_status(hit)!="Reviewable":
                print "*** This hit is not 'Reviewable' and so can not be disposed of"
                return
            else:
                self.amt_services.dispose_hit(hit)
                self.web_services.delete_ad(hit)  # also delete the ad
                if self.sandbox:
                    print "deleting sandbox HIT", hit
                    self.sandboxHITs -= 1
                else:
                    print "deleting live HIT", hit
                    self.liveHITs -= 1


    def hit_expire(self, allHits, hitIDs=None):
        if allHits:
            hits_data = self.amt_services.get_active_hits()
            hitIDs = [hit.options['hitid'] for hit in hits_data]
        for hit in hitIDs:
            self.amt_services.expire_hit(hit)
            if self.sandbox:
                print "expiring sandbox HIT", hit
                self.sandboxHITs -= 1
            else:
                print "expiring live HIT", hit
                self.liveHITs -= 1

    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  Local SQL database commands
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def do_get_db_config(self, arg):
        """
        Usage: get_db_config
               
        Description:
            Gets the current setting of the database (database_url)
        """
        print "Current database setting: \n\t", self.config.get("Database Parameters", "database_url")
    
    @docopt_cmd
    def do_use_local_sqllite_db(self, arg):
        """
        Usage: use_local_sqllite_db
               use_local_sqllite_db <filename> <tablename>
        """
        interactive = False
        if arg['<filename>'] is None:
            interactive = True
            arg['<filename>'] = raw_input('enter the filename of the SQLLite database you would like to use [default=participants.db]: ')
            if arg['<filename>']=='':
                arg['<filename>']='participants.db'
        base_url = "sqlite:///" + arg['<filename>']
        self.config.set("Database Parameters", "database_url", base_url)
        # restart servername


    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  AWS RDS commands
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def do_list_aws_db_instances(self, arg):
        instances = self.db_services.get_db_instances()
        for dbinst in instances:
            print dbinst.id+":"+dbinst.status

    @docopt_cmd
    def do_delete_aws_db_instance(self, arg):
        """
        Usage: delete_db_instance
               delete_db_instance <id>
        """
        interactive = False
        if arg['<id>'] is None:
            interactive = True
            arg['<id>'] = raw_input('enter the instance identify you would like to delete: ')
        try:
            str(arg['<id>'])
        except ValueError:
            print '*** Ids are strings.  Run `list_db_instances` to get a list of valid options.'
            return
        r = raw_input("Deleting an instance will erase all your data associated with the database in that instance. Really quit? y or n: ")
        if r == 'y':
            res = self.db_services.delete_db_instance(arg['<id>'])
            if res:
                print "AWS RDS database instance %s deleted." % arg['<id>']
            else:
                print "*** Error deleting database instance ", arg['<id>'], ". It maybe because it is still being created or is being backed up.  Run `list_db_instances` for current status."
        else:
            return

    def do_list_aws_regions(self, arg):
        print self.db_services.get_regions()

    def do_set_aws_region(self, arg):
        """
        Usage: set_aws_regions
               set_aws_regions <region_name>
        """
        interactive = False
        if arg['<region_name>'] is None:
            interactive = True
            arg['<region_name>'] = raw_input('Enter the region you like to use (`list_aws_regions` to see options): ')
        try:
            str(arg['<region_name>'])
        except ValueError:
            print '*** Ids are strings.  Run `list_db_instances` to get a list of valid options (i.e., status is `available`).'
            return
        else:
            self.db_services.set_region(arg['<region_name>'])

    @docopt_cmd
    def do_use_aws_db_instance(self, arg):
        """
        Usage: use_aws_db_instance
               use_aws_db_instance <id>
        """
        # set your database info to use the current instance
        # configure a security zone for this based on your ip
        interactive = False
        if arg['<id>'] is None:
            interactive = True
            arg['<id>'] = raw_input('enter the instance identify you would like to use: ')
        try:
            str(arg['<id>'])
        except ValueError:
            print '*** Ids are strings.  Run `list_db_instances` to get a list of valid options (i.e., status is `available`).'
            return

        r = raw_input("Switching your DB settings to use this instance.  Are you sure you want to do this? ")
        if r == 'y':
            # ask for password
            arg['<password>'] = raw_input('enter the master password for this instance: ')
            try:
                str(arg['<password>'])
            except ValueError:
                print '*** must be 8–41 alphanumeric characters'
                return

            # get instance
            myinstance = self.db_services.get_db_instance_info(arg['<id>'])
            if myinstance:
                # add security zone to this node to allow connections
                my_ip = self.web_services.get_my_ip()
                if not self.db_services.allow_access_to_instance(myinstance, my_ip):
                    print "*** Error authorizing your ip address to connect to server (%s)." % my_ip
                    return
                print "AWS RDS database instance %s selected." % arg['<id>']

                # using regular sql commands list available database on this node
                connection = MySQLdb.connect(
                        host= myinstance.endpoint[0],
                        user = myinstance.master_username,
                        passwd = arg['<password>']
                    ).cursor()
                connection.execute("show databases")
                db_names = connection.fetchall() 
                
                existing_dbs = [db[0] for db in db_names if db not in [('information_schema',), ('innodb',), ('mysql',), ('performance_schema',)]]
                create_db=False
                if len(existing_dbs)==0:
                    db_name = raw_input("No existing DBs in this instance.  Enter a new name to create one: ")
                    create_db=True
                else:
                    print "Here are the available database tables"
                    for db in existing_dbs:
                        print "\t" + db
                    print "\n"
                    db_name = raw_input("Enter the name of the database you want to use or a new name to create a new one: ")
                    if db_name not in existing_dbs:
                        create_db=True
                if create_db:
                    connection.execute("CREATE DATABASE %s;" % db_name)
                base_url = 'mysql://' + myinstance.master_username + ":" + arg['<password>'] + "@" + myinstance.endpoint[0] + ":" + str(myinstance.endpoint[1]) + "/" + db_name
                self.config.set("Database Parameters", "database_url", base_url)
                if self.server.is_server_running()=='maybe' or self.server.is_server_running()=='yes':
                    self.do_restart_server('')
            else:
                print "*** Error selecting database instance " + arg['<id>'] + ". Run `list_db_instances` for current status of instances."
        else:
            return


    @docopt_cmd
    def do_create_aws_db_instance(self, arg):
        """
        Usage: create_aws_db_instance
               create_aws_db_instance <id> <size> <username> <password> <dbname>
        """
        interactive = False
        if arg['<id>'] is None:
            interactive = True
            arg['<id>'] = raw_input('enter an identifier for the instance (1-63 alpha, first a letter): ')
        try:
            str(arg['<id>'])  # TODO: this should check the AWS rules instead of this string test
        except ValueError:
            print '*** Must contain 1-63 alphanumeric characters. First character must be a letter. May not end with a hyphen or contain two consecutive hyphens'
            return

        if interactive:
            arg['<size>'] = raw_input('size of db in GB (5-1024): ')
        try:
            int(arg['<size>'])
        except ValueError:
            print '*** size must be a whole number'
            return
        if int(arg['<size>']) < 5 or int(arg['<size>']) > 1024:
            print '*** size must be between 5-1024 GB'
            return

        if interactive:
            arg['<username>'] = raw_input('master username: ')
        try:
            str(arg['<username>']) # TODO: this should check the AWS rules instead of this string test
        except ValueError:
            print '*** 1–16 alphanumeric characters - first character must be a letter - cannot be a reserved MySQL word'
            return

        if interactive:
            arg['<password>'] = raw_input('master password: ')
        try:
            str(arg['<password>']) # TODO: this should check the AWS rules instead of this string test
        except ValueError:
            print '*** must be 8–41 alphanumeric characters'
            return

        if interactive:
            arg['<dbname>'] = raw_input('name for first database on this instance: ')
        try:
            str(arg['<dbname>']) # TODO: this should check the AWS rules instead of this string test
        except ValueError:
            print '*** Must contain 1–64 alphanumeric characters and cannot be a reserved MySQL word'
            return

        options = {
            'id': arg['<id>'],
            'size': arg['<size>'],
            'username': arg['<username>'],
            'password': arg['<password>'],
            'dbname': arg['<dbname>']
        }
        instance = self.db_services.create_db_instance(options)
        if not instance:
            print '*****************************'
            print '  Sorry there was an error creating db instance.'
        else:
            print '*****************************'
            print '  Creating AWS RDS MySQL Instance'
            print '    id: ', str(options['id'])
            print '    size: ', str(options['size']), " GB"
            print '    username: ', str(options['username'])
            print '    password: ', str(options['password'])
            print '    dbname: ',  str(options['dbname'])
            print '    type: MySQL/db.t1.micro'
            print '    ________________________'
            print ' Please wait a few moments while your database is created in the cloud.  You can run `list_db_instances` to verify it was created.'

    @docopt_cmd
    def do_mode(self, arg):
        """
        Usage: mode
               mode <which>
        """
        if arg['<which>'] is None:
            if self.sandbox:
                arg['<which>'] = 'live'
            else:
                arg['<which>'] = 'sandbox'
        if arg['<which>'] == 'live':
            self.sandbox = False
            self.config.set('HIT Configuration', 'using_sandbox', False)
            self.amt_services.set_sandbox(False)
            self.tally_hits()
            print 'Entered ' + colorize('live', 'bold') + ' mode'
        else:
            self.sandbox = True
            self.config.set('HIT Configuration', 'using_sandbox', True)
            self.amt_services.set_sandbox(True)
            self.tally_hits()
            print 'Entered ' + colorize('sandbox', 'bold') + ' mode'

    def help_mode(self):
        with open(self.helpPath + 'mode.txt', 'r') as helpText:
            print helpText.read()


    def random_id_generator(self, size = 6, chars = string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))

    @docopt_cmd
    def do_debug(self, arg):
        """
        Usage: debug [options]

        -p, --print-only         just provides the URL, doesn't attempt to launch browser
        """
        if self.server.is_server_running() == 'no' or self.server.is_server_running()=='maybe':
            print "Error: Sorry, you need to have the server running to debug your experiment.  Try 'server launch' first."
            return

        base_url = "http://" + self.config.get('Server Parameters', 'host') + ":" + self.config.get('Server Parameters', 'port') + "/ad"
        launchurl = base_url + "?assignmentId=debug" + str(self.random_id_generator()) \
                    + "&hitId=debug" + str(self.random_id_generator()) \
                    + "&workerId=debug" + str(self.random_id_generator())

        if arg['--print-only']:
            print "Here's your randomized debug link, feel free to request another:\n\t", launchurl
        else:
            print "Launching browser pointed at your randomized debug link, feel free to request another.\n\t", launchurl
            webbrowser.open(launchurl, new=1, autoraise=True)

    def help_debug(self):
        with open(self.helpPath + 'debug.txt', 'r') as helpText:
            print helpText.read()

    def do_version(self, arg):
        print 'psiTurk version ' + version_number

    def do_print_config(self, arg):
        for section in self.config.sections():
            print '[%s]' % section
            items = dict(self.config.items(section))
            for k in items:
                print "%(a)s=%(b)s" % {'a': k, 'b': items[k]}
            print ''
            
    def do_reload_config(self, arg):
        self.config.load_config()

    def do_status(self, arg):
        server_status = self.server.is_server_running()
        if server_status == 'yes':
            print 'Server: ' + colorize('currently online', 'green')
        elif server_status == 'no':
            print 'Server: ' + colorize('currently offline', 'red')
        elif server_status == 'maybe':
            print 'Server: ' + colorize('please wait', 'yellow')
        self.tally_hits()
        if self.sandbox:
            print 'AMT worker site - ' + colorize('sandbox', 'bold') + ': ' + str(self.sandboxHITs) + ' HITs available'
        else:
            print 'AMT worker site - ' + colorize('live', 'bold') + ': ' + str(self.liveHITs) + ' HITs available'

    def do_setup_example(self, arg):
        import setup_example as se
        se.setup_example()
        
    def do_download_datafiles(self, arg):
        contents = {"trialdata": lambda p: p.get_trial_data(), "eventdata": lambda p: p.get_event_data(), "questiondata": lambda p: p.get_question_data()}
        query = Participant.query.all()
        for k in contents:
            ret = "".join([contents[k](p) for p in query])
            f = open(k + '.csv', 'w')
            f.write(ret)
            f.close()

    def do_eof(self, arg):
        self.do_quit(arg)
        return True

    def do_quit(self, arg):
        if self.server.is_server_running() == 'yes' or self.server.is_server_running() == 'maybe':
            r = raw_input("Quitting shell will shut down experiment server. Really quit? y or n: ")
            if r == 'y':
                self.server_shutdown()
            else:
                return
        return True

    @docopt_cmd
    def do_server(self, arg):
        """
        Usage: 
          server launch
          server shutdown
          server relaunch
          server log
          server help
        """
        if arg['launch']:
            self.server_launch()
        elif arg['shutdown']:
            self.server_shutdown()
        elif arg['relaunch']:
            self.server_relaunch()
        elif arg['log']:
            self.server_log()
        else:
            self.help_server()

    server_commands = ('launch', 'shutdown', 'relaunch', 'log', 'help')

    def complete_server(self, text, line, begidx, endidx):
        return  [i for i in PsiturkShell.server_commands if i.startswith(text)]

    def help_server(self):
        with open(self.helpPath + 'server.txt', 'r') as helpText:
            print helpText.read()

    @docopt_cmd
    def do_hit(self, arg):
        """
        Usage:
          hit create [<numWorkers> <reward> <duration>]
          hit extend <HITid> [--assignments <number>] [--expiration <time>]
          hit expire (--all | <HITid> ...)
          hit dispose (--all | <HITid> ...)
          hit list (all | active | reviewable)
          hit help
        """
        if arg['create']:
            self.hit_create(arg['<numWorkers>'], arg['<reward>'], arg['<duration>'])
        elif arg['extend']:
            self.hit_extend(arg['<HITid>'], arg['--assignments'], arg['--expiration'])
        elif arg['expire']:
            self.hit_expire(arg['--all'], arg['<HITid>'])
        elif arg['dispose']:
            self.hit_dispose(arg['--all'], arg['<HITid>'])
        elif arg['list']:
            self.hit_list(arg['all'], arg['active'], arg['reviewable'])
        else:
            self.help_hit()

    hit_commands = ('create', 'extend', 'expire', 'dispose', 'list')

    def complete_hit(self, text, line, begidx, endidx):
        return  [i for i in PsiturkShell.hit_commands if i.startswith(text)]

    def help_hit(self):
        with open(self.helpPath + 'hit.txt', 'r') as helpText:
            print helpText.read()
        

    @docopt_cmd
    def do_worker(self, arg):
        """
        Usage:
          worker approve (--all | <assignment_id> ...)
          worker reject (--all | <assignment_id> ...)
          worker list
          worker help
        """
        if arg['approve']:
            self.worker_approve(arg['--all'], arg['<assignment_id>'])
        elif arg['reject']:
            self.worker_reject(arg['--all'], arg['<assignment_id>'])
        elif arg['list']:
            self.worker_list()
        else:
            self.help_worker()

    worker_commands = ('approve', 'reject', 'list', 'help')

    def complete_worker(self, text, line, begidx, endidx):
        return  [i for i in PsiturkShell.worker_commands if i.startswith(text)]

    def help_worker(self):
        with open(self.helpPath + 'worker.txt', 'r') as helpText:
            print helpText.read()

    @docopt_cmd
    def do_aws(self, arg):
        """
        Usage: 
          aws balance
          aws help
        """
        if arg['balance']:
            self.aws_balance()
    
    aws_commands = ('balance', 'help')

    def complete_aws(self, text, line, begidx, endidx):
        return [i for i in PsiturkShell.aws_commands if i.startswith(text)]

    def help_aws(self):
        with open(self.helpPath + 'aws.txt', 'r') as helpText:
            print helpText.read()

#### DEPRECATED COMMANDS
    def do_start_server(self, arg):
        print 'start_server deprecated, try \'server launch\''
        self.server_launch()

    def do_stop_server(self, arg):
        print 'stop_server deprecated, try \'server shutdown\''
        self.server_shutdown()

    def do_restart_server(self, arg):
        print 'restart_server deprecated, try \'server relaunch\''
        self.server_relaunch()

    def do_open_server_log(self, arg):
        print 'open_server_log deprecated, try \'server log\''
        self.server_log()

    def do_list_workers(self, arg):
        print 'list_workers deprecated, try \'worker list\''
        self.worker_list()

    @docopt_cmd
    def do_approve_worker(self, arg):
        """
        Usage: approve_worker (--all | <assignment_id> ...)

        -a, --all        approve all completed workers
        """
        print 'approve_worker deprecated, try \'worker approve\''
        self.worker_approve(arg['--all'], arg['<assignment_id>)'])

    @docopt_cmd
    def do_reject_worker(self, arg):
        """
        Usage: reject_worker (--all | <assignment_id> ...)

        -a, --all           reject all completed workers
        """
        print 'reject_worker deprecated, try \'worker reject\''
        self.worker_reject(arg['--all'], arg['<assignment_id>'])

    def do_check_balance(self, arg):
        print 'check_balance is deprecated, try \'aws balance\''
        self.aws_balance()

    @docopt_cmd
    def do_create_hit(self, arg):
        """
        Usage: create_hit (<numWorkers> <reward> <duration>)
        """
        print 'create_hit deprecated, try \'hit create\''
        self.hit_create(arg['<numWorkers>'], arg['<reward>'], arg['<duration>'])

    def do_list_all_hits(self, arg):
        print 'list_all_hits deprecated, try \'hit list all\''
        self.hit_list(True, False, False)        

    def do_list_active_hits(self, arg):
        print 'list_active_hits deprecated, try \'hit list active\''
        self.hit_list(False, True, False)


    def do_list_reviewable_hits(self, arg):
        print 'list_reviewable_hits deprecated, try \'hit list reviewable\''
        self.hit_list(False, False, True)

    @docopt_cmd
    def do_expire_hit(self, arg):
        """
        Usage: expire_hit (--all | <HITid> ...)

        -a, --all              expire all HITs
        """
        print 'expire_hit deprecated, try \'hit expire\''
        self.hit_expire(arg['--all'], arg['<HITid>'])

    @docopt_cmd
    def do_dispose_hit(self, arg):
        """
        Usage: dispose_hit (--all | <HITid> ...)

        -a, --all              delete all "Reviewable"/"Expired" HITs
        """
        print 'dispose_hit deprecated, try \'hit dispose\''
        self.hit_dispose(arg['--all'], arg['<HITid>'])

    @docopt_cmd
    def do_extend_hit(self, arg):
        """
        Usage: extend_hit <HITid> [options]

        -a <number>, --assignments <number>    Increase number of assignments on HIT
        -e <time>, --expiration <time>         Increase expiration time on HIT (hours)
        """
        print 'extend_hit deprecated, try \'hit extend\''
        self.hit_extend(arg['<HITid>'], arg['--assignments'], arg['--expiration'])


def run():
    opt = docopt(__doc__, sys.argv[1:])
    config = PsiturkConfig()
    config.load_config()
    amt_services = MTurkServices(config.get('AWS Access', 'aws_access_key_id'), \
                             config.get('AWS Access', 'aws_secret_access_key'), \
                             config.getboolean('HIT Configuration','using_sandbox'))
    aws_rds_services = RDSServices(config.get('AWS Access', 'aws_access_key_id'), \
                             config.get('AWS Access', 'aws_secret_access_key'))
    web_services = PsiturkOrgServices(config.get('Secure Ad Server','location'), config.get('Secure Ad Server', 'contact_email'))
    server = control.ExperimentServerController(config)
    shell = PsiturkShell(config, amt_services, aws_rds_services, web_services, server)
    shell.cmdloop()
