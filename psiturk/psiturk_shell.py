# coding: utf-8
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

import sqlalchemy as sa

from amt_services import MTurkServices, RDSServices
from psiturk_org_services import PsiturkOrgServices
from version import version_number
from psiturk_config import PsiturkConfig
import experiment_server_controller as control
from db import db_session, init_db
from models import Participant

#  colorize target string. Set use_escape to false when text will not be
# interpreted by readline, such as in intro message.
def colorize(target, color, use_escape=True):
    def escape(code):
        return '\001%s\002' % code
    if color == 'purple':
        color_code = '\033[95m'
    elif color == 'cyan':
        color_code = '\033[96m'
    elif color == 'darkcyan':
        color_code = '\033[36m'
    elif color == 'blue':
        color_code = '\033[93m'
    elif color == 'green':
        color_code = '\033[92m'
    elif color == 'yellow':
        color_code = '\033[93m'
    elif color == 'red':
        color_code = '\033[91m'
    elif color == 'white':
        color_code = '\033[37m'
    elif color == 'bold':
        color_code = '\033[1m'
    elif color == 'underline':
        color_code = '\033[4m'
    else:
        color_code = ''
    if use_escape:
        return escape(color_code) + target + escape('\033[0m')
    else:
        return color_code + target + '\033[m'

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
class PsiturkShell(Cmd, object):
    """
    Usage:
        psiturk -c
        psiturk_shell -c
    """

    def __init__(self, config, server):
        Cmd.__init__(self)
        self.config = config
        self.server = server

        # Prevents running of commands by abbreviation
        self.abbrev = False
        self.debug = True
        self.helpPath = os.path.join(os.path.dirname(__file__), "shell_help/")
        self.psiTurk_header = 'psiTurk command help:'
        self.super_header = 'basic CMD command help:'

        self.color_prompt()
        self.intro = self.get_intro_prompt()


    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  basic command line functions
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def check_offline_configuration(self):
        quit_on_start = False
        database_url = self.config.get('Database Parameters', 'database_url')
        host = self.config.get('Server Parameters', 'host', 'localhost')
        if database_url[:6] != 'sqlite':
            print "*** Error: config.txt option 'database_url' set to use mysql://.  Please change this sqllite:// while in cabin mode."
            quit_on_start = True
        if host != 'localhost':
            print "*** Error: config option 'host' is not set to localhost.  Please change this to localhost while in cabin mode."
            quit_on_start = True
        if quit_on_start:
            exit()

    def get_intro_prompt(self):
        # offline message
        sysStatus = open(self.helpPath + 'cabin.txt', 'r')
        server_msg = sysStatus.read()
        return server_msg + colorize('psiTurk version ' + version_number +
                                     '\nType "help" for more information.', 'green', False)

    def do_psiturk_status(self, args):
        print self.get_intro_prompt()

    def color_prompt(self):
        prompt = '[' + colorize('psiTurk', 'bold')
        serverString = ''
        server_status = self.server.is_server_running()
        if server_status == 'yes':
            serverString = colorize('on', 'green')
        elif server_status == 'no':
            serverString = colorize('off', 'red')
        elif server_status == 'maybe':
            serverString = colorize('unknown', 'yellow')
        prompt += ' server:' + serverString
        prompt += ' mode:' + colorize('cabin', 'bold')
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


    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  server management
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def server_on(self):
        self.server.startup('True')
        while self.server.is_server_running() != 'yes':
            time.sleep(0.5)

    def server_off(self):
        self.server.shutdown()
        print 'Please wait. This could take a few seconds.'
        while self.server.is_server_running() != 'no':
            time.sleep(0.5)

    def server_restart(self):
        self.server_off()
        self.server_on()

    def server_log(self):
        logfilename = self.config.get('Server Parameters', 'logfile')
        if sys.platform == "darwin":
            args = ["open", "-a", "Console.app", logfilename]
        else:
            args = ["xterm", "-e", "'tail -f %s'" % logfilename]
        subprocess.Popen(args, close_fds=True)
        print "Log program launching..."

    @docopt_cmd
    def do_debug(self, arg):
        """
        Usage: debug [options]

        -p, --print-only         just provides the URL, doesn't attempt to launch browser
        """
        if self.server.is_server_running() == 'no' or self.server.is_server_running()=='maybe':
            print "Error: Sorry, you need to have the server running to debug your experiment.  Try 'server on' first."
            return

        if 'OPENSHIFT_SECRET_TOKEN' in os.environ:
            base_url = "http://" + self.config.get('Server Parameters', 'host') + "/ad"
        else:
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
        restartServer = False
        if self.server.is_server_running() == 'yes' or self.server.is_server_running() == 'maybe':
            r = raw_input("Reloading configuration requires the server to restart. Really reload? y or n: ")
            if r != 'y':
                return
            restartServer = True
        self.config.load_config()
        if restartServer:
            self.server_restart()



    def do_status(self, arg):
        server_status = self.server.is_server_running()
        if server_status == 'yes':
            print 'Server: ' + colorize('currently online', 'green')
        elif server_status == 'no':
            print 'Server: ' + colorize('currently offline', 'red')
        elif server_status == 'maybe':
            print 'Server: ' + colorize('status unknown', 'yellow')

    def do_setup_example(self, arg):
        import setup_example as se
        se.setup_example()


    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  Local SQL database commands
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def db_get_config(self):
        print "Current database setting (database_url): \n\t", self.config.get("Database Parameters", "database_url")

    def db_use_local_file(self, filename=None):
        interactive = False
        if filename is None:
            interactive = True
            filename = raw_input('Enter the filename of the local SQLLite database you would like to use [default=participants.db]: ')
            if filename=='':
                filename='participants.db'
        base_url = "sqlite:///" + filename
        self.config.set("Database Parameters", "database_url", base_url)
        print "Updated database setting (database_url): \n\t", self.config.get("Database Parameters", "database_url")
        if self.server.is_server_running() == 'yes':
            self.server_restart()

    def do_download_datafiles(self, arg):
        contents = {"trialdata": lambda p: p.get_trial_data(), "eventdata": lambda p: p.get_event_data(), "questiondata": lambda p: p.get_question_data()}
        query = Participant.query.all()
        for k in contents:
            ret = "".join([contents[k](p) for p in query])
            f = open(k + '.csv', 'w')
            f.write(ret)
            f.close()

    @docopt_cmd
    def do_open(self, arg):
        """
        Usage: open
               open <folder>

        Opens folder or current directory using the local system's shell command 'open'.
        """
        if arg['<folder>'] is None:
            subprocess.call(["open"])
        else:
            subprocess.call(["open",arg['<folder>']])

    def do_eof(self, arg):
        self.do_quit(arg)
        return True

    def do_exit(self, arg):
        self.do_quit(arg)
        return True

    def do_quit(self, arg):
        if self.server.is_server_running() == 'yes' or self.server.is_server_running() == 'maybe':
            r = raw_input("Quitting shell will shut down experiment server. Really quit? y or n: ")
            if r == 'y':
                self.server_off()
            else:
                return
        return True

    @docopt_cmd
    def do_server(self, arg):
        """
        Usage:
          server on
          server off
          server restart
          server log
          server help
        """
        if arg['on']:
            self.server_on()
        elif arg['off']:
            self.server_off()
        elif arg['restart']:
            self.server_restart()
        elif arg['log']:
            self.server_log()
        else:
            self.help_server()

    server_commands = ('on', 'off', 'restart', 'log', 'help')

    def complete_server(self, text, line, begidx, endidx):
        return  [i for i in PsiturkShell.server_commands if i.startswith(text)]

    def help_server(self):
        with open(self.helpPath + 'server.txt', 'r') as helpText:
            print helpText.read()

    def random_id_generator(self, size = 6, chars = string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))

    # modified version of standard cmd help which lists psiturk commands first
    def do_help(self, arg):
        if arg:
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc = getattr(self, 'do_' + arg).__doc__
                    if doc:
                        self.stdout.write("%s\n" % str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n" % str(self.nohelp % (arg,)))
                return
            func()
        else:
            # Modifications start here
            names = dir(PsiturkShell)
            superNames = dir(Cmd)
            newNames = [m for m in names if m not in superNames]
            help = {}
            cmds_psiTurk = []
            cmds_super = []
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd = name[3:]
                    if cmd in help:
                        del help[cmd]
                    if name in newNames:
                        cmds_psiTurk.append(cmd)
                    else:
                        cmds_super.append(cmd)
            self.stdout.write("%s\n" % str(self.doc_leader))
            self.print_topics(self.psiTurk_header, cmds_psiTurk, 15, 80)
            self.print_topics(self.misc_header, help.keys(), 15, 80)
            self.print_topics(self.super_header, cmds_super, 15, 80)


class PsiturkNetworkShell(PsiturkShell):

    def __init__(self, config, amt_services, aws_rds_services, web_services, server, sandbox):
        self.config = config
        self.amt_services = amt_services
        self.web_services = web_services
        self.db_services = aws_rds_services
        self.sandbox = sandbox

        self.sandboxHITs = 0
        self.liveHITs = 0
        self.tally_hits()
        PsiturkShell.__init__(self, config, server)

        # Prevents running of commands by abbreviation
        self.abbrev = False
        self.debug = True
        self.helpPath = os.path.join(os.path.dirname(__file__), "shell_help/")
        self.psiTurk_header = 'psiTurk command help:'
        self.super_header = 'basic CMD command help:'



    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  basic command line functions
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def get_intro_prompt(self):  # overloads intro prompt with network-aware version
        # if you can reach psiTurk.org, request system status
        # message
        server_msg = self.web_services.get_system_status()
        return server_msg + colorize('psiTurk version ' + version_number +
                                     '\nType "help" for more information.', 'green', False)

    def color_prompt(self):  # overloads prompt with network info
        prompt = '[' + colorize('psiTurk', 'bold')
        serverString = ''
        server_status = self.server.is_server_running()
        if server_status == 'yes':
            serverString = colorize('on', 'green')
        elif server_status == 'no':
            serverString = colorize('off', 'red')
        elif server_status == 'maybe':
            serverString = colorize('unknown', 'yellow')
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

    def server_on(self):
        self.server.startup(str(self.sandbox))
        while self.server.is_server_running() != 'yes':
            time.sleep(0.5)


    def do_status(self, arg): # overloads do_status with AMT info
        super(PsiturkNetworkShell, self).do_status(arg)
        server_status = self.server.is_server_running()
        self.tally_hits()
        if self.sandbox:
            print 'AMT worker site - ' + colorize('sandbox', 'bold') + ': ' + str(self.sandboxHITs) + ' HITs available'
        else:
            print 'AMT worker site - ' + colorize('live', 'bold') + ': ' + str(self.liveHITs) + ' HITs available'


    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  worker management
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def worker_list(self, submitted, approved, rejected, chosenHit):
        workers = None
        if submitted:
            workers = self.amt_services.get_workers("Submitted")
        elif approved:
            workers = self.amt_services.get_workers("Approved")
        elif rejected:
            workers = self.amt_services.get_workers("Rejected")
        else:
            workers = self.amt_services.get_workers()
        if workers==False:
            print colorize('*** failed to get workers', 'red')
        if chosenHit:
            workers = [worker for worker in workers if worker['hitId']==chosenHit]
            print 'listing workers for HIT', chosenHit
        if not len(workers):
            print "*** no workers match your request"
        else:
            print json.dumps(workers, indent=4,
                             separators=(',', ': '))

    def worker_approve(self, chosenHit, assignment_ids = None):
        if chosenHit:
            workers = self.amt_services.get_workers("Submitted")
            assignment_ids = [worker['assignmentId'] for worker in workers if worker['hitId']==chosenHit]
            print 'approving workers for HIT', chosenHit
        for assignmentID in assignment_ids:
            success = self.amt_services.approve_worker(assignmentID)
            if success:
                print 'approved', assignmentID
            else:
                print '*** failed to approve', assignmentID

    def worker_reject(self, chosenHit, assignment_ids = None):
        if chosenHit:
            workers = self.amt_services.get_workers("Submitted")
            assignment_ids = [worker['assignmentId'] for worker in workers if worker['hitId']==chosenHit]
            print 'rejecting workers for HIT',chosenHit
        for assignmentID in assignment_ids:
            success = self.amt_services.reject_worker(assignmentID)
            if success:
                print 'rejected', assignmentID
            else:
                print '*** failed to reject', assignmentID

    def worker_unreject(self, chosenHit, assignment_ids = None):
        if chosenHit:
            workers = self.amt_services.get_workers("Rejected")
            assignment_ids = [worker['assignmentId'] for worker in workers if worker['hitId']==chosenHit]
        for assignmentID in assignment_ids:
            success = self.amt_services.unreject_worker(assignmentID)
            if success:
                print 'unrejected %s' % (assignmentID)
            else:
                print '*** failed to unreject', assignmentID

    def worker_bonus(self, chosenHit, auto, amount, reason, assignment_ids = None):
        while not reason:
            r = raw_input("Type the reason for the bonus. Workers will see this message: ")
            reason = r
        #bonus already-bonused workers if the user explicitly lists their worker IDs
        overrideStatus = True
        if chosenHit:
            overrideStatus = False
            workers = self.amt_services.get_workers("Approved")
            if workers==False:
                print "No approved workers for HIT", chosenHit
                return
            assignment_ids = [worker['assignmentId'] for worker in workers if worker['hitId']==chosenHit]
            print 'bonusing workers for HIT', chosenHit
        for assignmentID in assignment_ids:
            try:
                init_db()
                part = Participant.query.\
                       filter(Participant.assignmentid == assignmentID).\
                       filter(Participant.endhit != None).\
                       one()
                if auto:
                    amount = part.bonus
                status = part.status
                if amount<=0:
                    print "bonus amount <=$0, no bonus given to", assignmentID
                elif status==7 and not overrideStatus:
                    print "bonus already awarded to ", assignmentID
                else:
                    success = self.amt_services.bonus_worker(assignmentID, amount, reason)
                    if success:
                        print "gave bonus of $" + str(amount) + " to " + assignmentID
                        part.status = 7
                        db_session.add(part)
                        db_session.commit()
                        db_session.remove()
                    else:
                        print "*** failed to bonus", assignmentID
            except:
                print "*** failed to bonus", assignmentID

    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  hit management
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def do_amt_balance(self, arg):
        print self.amt_services.check_balance()
    def help_amt_balance(self):
        with open(self.helpPath + 'amt.txt', 'r') as helpText:
            print helpText.read()

    def hit_list(self, activeHits, reviewableHits):
        hits_data = []
        if activeHits:
            hits_data = self.amt_services.get_active_hits()
        elif reviewableHits:
            hits_data = self.amt_services.get_reviewable_hits()
        else:
            hits_data = self.amt_services.get_all_hits()
        if not hits_data:
            print '*** no hits retrieved'
        else:
            for hit in hits_data:
                print hit

    def hit_extend(self, hitID, assignments, minutes):
        """ Add additional worker assignments or minutes to a HIT.

        Args:
            hitID: A list conaining one hitID string.
            assignments: Variable <int> for number of assignments to add.
            minutes: Variable <int> for number of minutes to add.

        Returns:
            A side effect of this function is that the state of a HIT changes on AMT servers.

        Raises:

        """

        assert type(hitID) is list
        assert type(hitID[0]) is str

        if self.amt_services.extend_hit(hitID[0], assignments, minutes):
            print "HIT extended."

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
                success = self.amt_services.dispose_hit(hit)
                #self.web_services.delete_ad(hit)  # also delete the ad
                if success:
                    if self.sandbox:
                        print "deleting sandbox HIT", hit
                    else:
                        print "deleting live HIT", hit
        self.tally_hits()

    def hit_expire(self, allHits, hitIDs=None):
        if allHits:
            hits_data = self.amt_services.get_active_hits()
            hitIDs = [hit.options['hitid'] for hit in hits_data]
        for hit in hitIDs:
            success = self.amt_services.expire_hit(hit)
            if success:
                if self.sandbox:
                    print "expiring sandbox HIT", hit
                else:
                    print "expiring live HIT", hit
        self.tally_hits()

    def tally_hits(self):
        hits = self.amt_services.get_active_hits()
        numHits = 0
        if hits:
            numHits = len(hits)
        if self.sandbox:
            self.sandboxHITs = numHits
        else:
            self.liveHITs = numHits


    def hit_create(self, numWorkers, reward, duration):

        server_loc = str(self.config.get('Server Parameters', 'host'))
        if server_loc in ['localhost', '127.0.0.1']:
            print '\n'.join(['*****************************',
                             '  Sorry, your server is set for local debugging only.  You cannot make public',
                             '  HITs or Ads. Please edit the config.txt file inside your project folder and',
                             '  set the \'host\' variable in the \'Server Parameters\' section to something',
                             '  other than \'localhost\' or \'127.0.0.1\'. This will make your psiturk server',
                             '  process reachable by the external world.  The most useful option is \'0.0.0.0\'',
                             '  Note: You will need to restart the server for your changes to take effect.',
                             ''])

            r = raw_input('\n'.join(['  If you are using an external server process, press `y` to continue.',
                                     '  Otherwise, press `n` to cancel:']))
            if r!='y':
                return

        if not self.web_services.check_credentials():
            print '\n'.join(['*****************************',
                            '  Sorry, your psiTurk Credentials are invalid.\n ',
                            '  You cannot create ads and hits until you enter valid credentials in ',
                            '  the \'psiTurk Access\' section of ~/.psiturkconfig.  You can obtain your',
                            '  credentials or sign up at https://www.psiturk.org/login.\n'])
            return


        if not self.amt_services.verify_aws_login():
            print '\n'.join(['*****************************',
                             '  Sorry, your AWS Credentials are invalid.\n ',
                             '  You cannot create ads and hits until you enter valid credentials in ',
                             '  the \'AWS Access\' section of ~/.psiturkconfig.  You can obtain your ',
                             '  credentials via the Amazon AMT requester website.\n'])
            return

        if self.server.is_server_running() != 'yes':
            print '\n'.join(['*****************************',
                             '  Your psiTurk server is currently not running but you are trying to create ',
                             '  an Ad/HIT.  This can cause problems for worker trying to access your ',
                             '  hit.  Please start the server by first typing \'server on\' then try this ',
                             '  command again.',
                             ''])
            r = raw_input('\n'.join(['  If you are using an external server process, press `y` to continue.',
                                      '  Otherwise, press `n` to cancel:']))
            if r!='y':
                return

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

        # register with the ad server (psiturk.org/ad/register) using POST
        if os.path.exists('templates/ad.html'):
            ad_html = open('templates/ad.html').read()
        else:
            print '\n'.join(['*****************************',
                             '  Sorry, there was an error registering ad.',
                             '  Both ad.html is required to be in the templates/ folder of your project so that these Ad can be served!'])
            return

        size_of_ad = sys.getsizeof(ad_html)
        if size_of_ad >= 1048576:
            print '\n'.join(['*****************************',
                             '  Sorry, there was an error registering ad.',
                             '  Your local ad.html is %s byes, but the maximum template size uploadable to the Ad server is 1048576 bytes!' % size_of_ad])
            return

        # what all do we need to send to server?
        # 1. server
        # 2. port
        # 3. support_ie?
        # 4. ad.html template
        # 5. contact_email in case an error happens
        ad_content = {'psiturk_external': True,
              'server': str(self.web_services.get_my_ip()),
              'port': str(self.config.get('Server Parameters', 'port')),
              'browser_exclude_rule': str(self.config.get('HIT Configuration', 'browser_exclude_rule')),
              'is_sandbox': int(self.sandbox),
              'ad_html': ad_html,
              # 'amt_hit_id': hitid, Don't know this yet
              'organization_name': str(self.config.get('HIT Configuration', 'organization_name')),
              'experiment_name': str(self.config.get('HIT Configuration', 'title')),
              'contact_email_on_error': str(self.config.get('HIT Configuration', 'contact_email_on_error')),
              'ad_group': str(self.config.get('HIT Configuration', 'ad_group')),
              'keywords': str(self.config.get('HIT Configuration', 'psiturk_keywords'))
        }

        create_failed = False
        fail_msg = None
        ad_id = self.web_services.create_ad(ad_content)
        if ad_id != False:
            ad_url = self.web_services.get_ad_url(ad_id, int(self.sandbox))
            hit_config = {
                "ad_location": ad_url,
                "approve_requirement": self.config.get('HIT Configuration', 'Approve_Requirement'),
                "us_only": self.config.getboolean('HIT Configuration', 'US_only'),
                "lifetime": datetime.timedelta(hours=self.config.getfloat('HIT Configuration', 'lifetime')),
                "max_assignments": numWorkers,
                "title": self.config.get('HIT Configuration', 'title'),
                "description": self.config.get('HIT Configuration', 'description'),
                "keywords": self.config.get('HIT Configuration', 'amt_keywords'),
                "reward": reward,
                "duration": datetime.timedelta(hours=int(duration))
            }
            hit_id = self.amt_services.create_hit(hit_config)
            if hit_id != False:
                if not self.web_services.set_ad_hitid(ad_id, hit_id, int(self.sandbox)):
                    create_failed = True
                    fail_msg = "  Unable to update Ad on http://ad.psiturk.org to point at HIT."
            else:
                create_failed = True
                fail_msg = "  Unable to create HIT on Amazon Mechanical Turk."
        else:
            create_failed = True
            fail_msg = "  Unable to create Ad on http://ad.psiturk.org."

        if create_failed:
            print '\n'.join(['*****************************',
                             '  Sorry, there was an error creating hit and registering ad.'])
            if fail_msg:
                print fail_msg

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
            print '\n'.join(['*****************************',
                             '  Creating %s HIT' % colorize(location, 'bold'),
                             '    HITid: %s' % str(hit_id),
                             '    Max workers: %s' % numWorkers,
                             '    Reward: $%s' %reward,
                             '    Duration: %s hours' % duration,
                             '    Fee: $%.2f' % fee,
                             '    ________________________',
                             '    Total: $%.2f' % total])
            if self.sandbox:
                print('  Ad for this HIT now hosted at: https://sandbox.ad.psiturk.org/view/%s?assignmentId=debug%s&hitId=debug%s'
                      % (str(ad_id), str(self.random_id_generator()), str(self.random_id_generator())))
                print "Note: This sandboxed ad will expire from the server in 15 days."
            else:
                print('  Ad for this HIT now hosted at: https://ad.psiturk.org/view/%s?assignmentId=debug%s&hitId=debug%s'
                      % (str(ad_id), str(self.random_id_generator()), str(self.random_id_generator())))


    @docopt_cmd
    def do_db(self, arg):
        """
        Usage:
          db get_config
          db use_local_file [<filename>]
          db use_aws_instance [<instance_id>]
          db aws_list_regions
          db aws_get_region
          db aws_set_region [<region_name>]
          db aws_list_instances
          db aws_create_instance [<instance_id> <size> <username> <password> <dbname>]
          db aws_delete_instance [<instance_id>]
          db help
        """
        if arg['get_config']:
            self.db_get_config()
        elif arg['use_local_file']:
            self.db_use_local_file(arg['<filename>'])
        elif arg['use_aws_instance']:
            self.db_use_aws_instance(arg['<instance_id>'])
            pass
        elif arg['aws_list_regions']:
            self.db_aws_list_regions()
        elif arg['aws_get_region']:
            self.db_aws_get_region()
        elif arg['aws_set_region']:
            self.db_aws_set_region(arg['<region_name>'])
        elif arg['aws_list_instances']:
            self.db_aws_list_instances()
        elif arg['aws_create_instance']:
            self.db_create_aws_db_instance(arg['<instance_id>'], arg['<size>'], arg['<username>'], arg['<password>'], arg['<dbname>'])
        elif arg['aws_delete_instance']:
            self.db_aws_delete_instance(arg['<instance_id>'])
        else:
            self.help_db()

    db_commands = ('get_config', 'use_local_file', 'use_aws_instance', 'aws_list_regions', 'aws_get_region', 'aws_set_region', 'aws_list_instances', 'aws_create_instance', 'aws_delete_instance', 'help')

    def complete_db(self, text, line, begidx, endidx):
        return  [i for i in PsiturkNetworkShell.db_commands if i.startswith(text)]

    def help_db(self):
        with open(self.helpPath + 'db.txt', 'r') as helpText:
            print helpText.read()


    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  AWS RDS commands
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def db_aws_list_regions(self):
        regions = self.db_services.list_regions()
        if regions != []:
            print "Avaliable AWS regions:"
        for reg in regions:
            print '\t' + reg,
            if reg == self.db_services.get_region():
                print "(currently selected)"
            else:
                print ''

    def db_aws_get_region(self):
        print self.db_services.get_region()

    def db_aws_set_region(self, region_name):
        interactive = False
        if region_name is None:
            interactive = True
            self.db_aws_list_regions()
            allowed_regions = self.db_services.list_regions()
            region_name = "NONSENSE WORD1234"
            tries = 0
            while region_name not in allowed_regions:
                if tries == 0:
                    region_name = raw_input('Enter the name of the region you would like to use: ')
                else:
                    print "*** The region name (%s) you entered is not allowed, please choose from the list printed above (use type 'db aws_list_regions'." % region_name
                    region_name = raw_input('Enter the name of the region you would like to use: ')
                tries+=1
                if tries > 5:
                    print "*** Error, region you are requesting not available.  No changes made to regions."
                    return
        self.db_services.set_region(region_name)
        print "Region updated to ", region_name
        self.config.set('AWS Access', 'aws_region', region_name, True)
        if self.server.is_server_running() == 'yes':
            self.server_restart()

    def db_aws_list_instances(self):
        instances = self.db_services.get_db_instances()
        if not instances:
            print "There are no DB instances associated with your AWS account in region ", self.db_services.get_region()
        else:
            print "Here are the current DB instances associated with your AWS account in region ", self.db_services.get_region()
            for dbinst in instances:
                print '\t'+'-'*20
                print "\tInstance ID: " + dbinst.id
                print "\tStatus: " + dbinst.status

    def db_aws_delete_instance(self, instance_id):
        interactive = False
        if instance_id is None:
            interactive = True

        instances = self.db_services.get_db_instances()
        instance_list = [dbinst.id for dbinst in instances]

        if interactive:
            valid = False
            if len(instances)==0:
                print "There are no instances you can delete currently.  Use `db aws_create_instance` to make one."
                return
            print "Here are the available instances you can delete:"
            for inst in instances:
                print "\t ", inst.id, "(", inst.status, ")"
            while not valid:
                instance_id = raw_input('Enter the instance identity you would like to delete: ')
                res = self.db_services.validate_instance_id(instance_id)
                if (res == True):
                    valid = True
                else:
                    print res + " Try again, instance name not valid.  Check for typos."
                if instance_id in instance_list:
                    valid = True
                else:
                    valid = False
                    print "Try again, instance not present in this account.  Try again checking for typos."
        else:
            res = self.db_services.validate_instance_id(instance_id)
            if (res != True):
                print "*** Error, instance name either not valid.  Try again checking for typos."
                return
            if instance_id not in instance_list:
                print "*** Error, This instance not present in this account.  Try again checking for typos.  Run `db aws_list_instances` to see valid list."
                return

        r = raw_input("Deleting an instance will erase all your data associated with the database in that instance. Really quit? y or n: ")
        if r == 'y':
            res = self.db_services.delete_db_instance(instance_id)
            if res:
                print "AWS RDS database instance %s deleted.  Run `db aws_list_instances` for current status." % instance_id
            else:
                print "*** Error deleting database instance ", instance_id, ". It maybe because it is still being created, deleted, or is being backed up.  Run `db aws_list_instances` for current status."
        else:
            return

    def db_use_aws_instance(self, instance_id):
        # set your database info to use the current instance
        # configure a security zone for this based on your ip
        interactive = False
        if instance_id is None:
            interactive = True

        instances = self.db_services.get_db_instances()
        instance_list = [dbinst.id for dbinst in instances]

        if len(instances)==0:
            print "There are no instances in this region/account.  Use `db aws_create_instance` to make one first."
            return

        # show list of available instances, if there are none cancel immediately
        if interactive:
            valid = False
            print "Here are the available instances you have.  You can only use those listed as 'available':"
            for inst in instances:
                print "\t ", inst.id, "(", inst.status, ")"
            while not valid:
                instance_id = raw_input('Enter the instance identity you would like to use: ')
                res = self.db_services.validate_instance_id(instance_id)
                if (res == True):
                    valid = True
                else:
                    print res + " Try again, instance name not valid.  Check for typos."
                if instance_id in instance_list:
                    valid = True
                else:
                    valid = False
                    print "Try again, instance not present in this account.  Try again checking for typos."
        else:
            res = self.db_services.validate_instance_id(instance_id)
            if (res != True):
                print "*** Error, instance name either not valid.  Try again checking for typos."
                return
            if instance_id not in instance_list:
                print "*** Error, This instance not present in this account.  Try again checking for typos.  Run `db aws_list_instances` to see valid list."
                return

        r = raw_input("Switching your DB settings to use this instance.  Are you sure you want to do this? ")
        if r == 'y':
            # ask for password
            valid = False
            while not valid:
                password = raw_input('enter the master password for this instance: ')
                res = self.db_services.validate_instance_password(password)
                if res != True:
                    print "*** Error: password seems incorrect, doesn't conform to AWS rules.  Try again"
                else:
                    valid = True

            # get instance
            myinstance = self.db_services.get_db_instance_info(instance_id)
            if myinstance:
                # add security zone to this node to allow connections
                my_ip = self.web_services.get_my_ip()
                if not self.db_services.allow_access_to_instance(myinstance, my_ip):
                    print "*** Error authorizing your ip address to connect to server (%s)." % my_ip
                    return
                print "AWS RDS database instance %s selected." % instance_id

                # using regular sql commands list available database on this node
                try:
                    db_url = 'mysql://' + myinstance.master_username + ":" + password + "@" + myinstance.endpoint[0] + ":" + str(myinstance.endpoint[1])
                    engine = sa.create_engine(db_url, echo=False)
                    e = engine.connect().execute
                    db_names = e("show databases").fetchall()
                except:
                    print "***  Error connecting to instance.  Your password my be incorrect."
                    return
                existing_dbs = [db[0] for db in db_names if db not in [('information_schema',), ('innodb',), ('mysql',), ('performance_schema',)]]
                create_db=False
                if len(existing_dbs)==0:
                    valid = False
                    while not valid:
                        db_name = raw_input("No existing DBs in this instance.  Enter a new name to create one: ")
                        res = self.db_services.validate_instance_dbname(db_name)
                        if res == True:
                            valid = True
                        else:
                            print res + " Try again."
                    create_db=True
                else:
                    print "Here are the available database tables"
                    for db in existing_dbs:
                        print "\t" + db
                    valid = False
                    while not valid:
                        db_name = raw_input("Enter the name of the database you want to use or a new name to create a new one: ")
                        res = self.db_services.validate_instance_dbname(db_name)
                        if res == True:
                            valid = True
                        else:
                            print res + " Try again."
                    if db_name not in existing_dbs:
                        create_db=True
                if create_db:
                    try:
                        connection.execute("CREATE DATABASE %s;" % db_name)
                    except:
                        print "*** Error creating database %s on instance %s" % (db_name,instance_id)
                        return
                base_url = 'mysql://' + myinstance.master_username + ":" + password + "@" + myinstance.endpoint[0] + ":" + str(myinstance.endpoint[1]) + "/" + db_name
                self.config.set("Database Parameters", "database_url", base_url)
                print "Successfully set your current database (database_url) to \n\t%s" % base_url
                if self.server.is_server_running()=='maybe' or self.server.is_server_running()=='yes':
                    self.do_restart_server('')
            else:
                print '\n'.join(["*** Error selecting database instance %s." % arg['<id>'],
                                 "Run `db list_db_instances` for current status of instances, only `available`",
                                 "instances can be used.  Also, your password may be incorrect."])
        else:
            return


    def db_create_aws_db_instance(self, instid=None, size=None, username=None, password=None, dbname=None):
        interactive = False
        if instid is None:
            interactive = True

        if interactive:
            print '\n'.join(['*************************************************',
                             'Ok, here are the rules on creating instances:',
                             '',
                             'instance id:',
                             '  Each instance needs an identifier.  This is the name',
                             '  of the virtual machine created for you on AWS.',
                             '  Rules are 1-63 alphanumeric characters, first must',
                             '  be a letter, must be unique to this AWS account.',
                             '',
                             'size:',
                             '  The maximum size of you database in GB.  Enter an',
                             '  integer between 5-1024',
                             '',
                             'master username:',
                             '  The username you will use to connect.  Rules are',
                             '  1-16 alphanumeric characters, first must be a letter,',
                             '  cannot be a reserved MySQL word/phrase',
                             '',
                             'master password:',
                             '  Rules are 8-41 alphanumeric characters',
                             '',
                             'database name:',
                             '  The name for the first database on this instance.  Rules are',
                             '  1-64 alphanumeric characters, cannot be a reserved MySQL word',
                             '*************************************************',
                             ''])

        if interactive:
            valid = False
            while not valid:
                instid = raw_input('enter an identifier for the instance (see rules above): ')
                res = self.db_services.validate_instance_id(instid)
                if res == True:
                    valid = True
                else:
                    print res + " Try again."
        else:
            res = self.db_services.validate_instance_id(instid)
            if res is not True:
                print res
                return

        if interactive:
            valid = False
            while not valid:
                size = raw_input('size of db in GB (5-1024): ')
                res = self.db_services.validate_instance_size(size)
                if res == True:
                    valid = True
                else:
                    print res + " Try again."
        else:
            res = self.db_services.validate_instance_size(size)
            if res is not True:
                print res
                return

        if interactive:
            valid = False
            while not valid:
                username = raw_input('master username (see rules above): ')
                res = self.db_services.validate_instance_username(username)
                if res == True:
                    valid = True
                else:
                    print res + " Try again."
        else:
            res = self.db_services.validate_instance_username(username)
            if res is not True:
                print res
                return

        if interactive:
            valid = False
            while not valid:
                password = raw_input('master password (see rules above): ')
                res = self.db_services.validate_instance_password(password)
                if res == True:
                    valid = True
                else:
                    print res + " Try again."
        else:
            res = self.db_services.validate_instance_password(password)
            if res is not True:
                print res
                return

        if interactive:
            valid = False
            while not valid:
                dbname = raw_input('name for first database on this instance (see rules): ')
                res = self.db_services.validate_instance_dbname(dbname)
                if res == True:
                    valid = True
                else:
                    print res + " Try again."
        else:
            res = self.db_services.validate_instance_dbname(dbname)
            if res is not True:
                print res
                return

        options = {
            'id': instid,
            'size': size,
            'username': username,
            'password': password,
            'dbname': dbname
        }
        instance = self.db_services.create_db_instance(options)
        if not instance:
            print '\n'.join(['*****************************',
                             '  Sorry, there was an error creating db instance.'])
        else:
            print '\n'.join(['*****************************',
                             '  Creating AWS RDS MySQL Instance',
                             '    id: ' + str(options['id']),
                             '    size: ' + str(options['size']) + " GB",
                             '    username: ' + str(options['username']),
                             '    password: ' + str(options['password']),
                             '    dbname: ' +  str(options['dbname']),
                             '    type: MySQL/db.t1.micro',
                             '    ________________________',
                             ' Be sure to store this information in a safe place.',
                             ' Please wait 5-10 minutes while your database is created in the cloud.',
                             ' You can run \'db aws_list_instances\' to verify it was created (status',
                             ' will say \'available\' when it is ready'])


    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #  Basic shell commands
    #+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    @docopt_cmd
    def do_mode(self, arg):
        """
        Usage: mode
               mode <which>
        """
        restartServer = False
        if self.server.is_server_running() == 'yes' or self.server.is_server_running() == 'maybe':
            r = raw_input("Switching modes requires the server to restart. Really switch modes? y or n: ")
            if r != 'y':
                return
            restartServer = True
        if arg['<which>'] is None:
            if self.sandbox:
                arg['<which>'] = 'live'
            else:
                arg['<which>'] = 'sandbox'
        if arg['<which>'] == 'live':
            self.sandbox = False
            self.amt_services.set_sandbox(False)
            self.tally_hits()
            print 'Entered %s mode' % colorize('live', 'bold')
        else:
            self.sandbox = True
            self.amt_services.set_sandbox(True)
            self.tally_hits()
            print 'Entered %s mode' % colorize('sandbox', 'bold')
        if restartServer:
            self.server_restart()
    def help_mode(self):
        with open(self.helpPath + 'mode.txt', 'r') as helpText:
            print helpText.read()

    @docopt_cmd
    def do_hit(self, arg):
        """
        Usage:
          hit create [<numWorkers> <reward> <duration>]
          hit extend <HITid> [(--assignments <number>)] [(--expiration <minutes>)]
          hit expire (--all | <HITid> ...)
          hit dispose (--all | <HITid> ...)
          hit list [--active | --reviewable]
          hit help
        """

        if arg['create']:
            self.hit_create(arg['<numWorkers>'], arg['<reward>'], arg['<duration>'])
        elif arg['extend']:
            self.hit_extend(arg['<HITid>'], arg['<number>'], arg['<minutes>'])
        elif arg['expire']:
            self.hit_expire(arg['--all'], arg['<HITid>'])
        elif arg['dispose']:
            self.hit_dispose(arg['--all'], arg['<HITid>'])
        elif arg['list']:
            self.hit_list(arg['--active'], arg['--reviewable'])
        else:
            self.help_hit()

    hit_commands = ('create', 'extend', 'expire', 'dispose', 'list')

    def complete_hit(self, text, line, begidx, endidx):
        return  [i for i in PsiturkNetworkShell.hit_commands if i.startswith(text)]

    def help_hit(self):
        with open(self.helpPath + 'hit.txt', 'r') as helpText:
            print helpText.read()


    @docopt_cmd
    def do_worker(self, arg):
        """
        Usage:
          worker approve (--hit <hit_id> | <assignment_id> ...)
          worker reject (--hit <hit_id> | <assignment_id> ...)
          worker unreject (--hit <hit_id> | <assignment_id> ...)
          worker bonus  (--amount <amount> | --auto) (--hit <hit_id> | <assignment_id> ...)
          worker list [--submitted | --approved | --rejected] [(--hit <hit_id>)]
          worker help
        """
        if arg['approve']:
            self.worker_approve(arg['<hit_id>'], arg['<assignment_id>'])
        elif arg['reject']:
            self.worker_reject(arg['<hit_id>'], arg['<assignment_id>'])
        elif arg['unreject']:
            self.worker_unreject(arg['<hit_id>'], arg['<assignment_id>'])
        elif arg['list']:
            self.worker_list(arg['--submitted'], arg['--approved'], arg['--rejected'], arg['<hit_id>'])
        elif arg['bonus']:
            self.worker_bonus(arg['<hit_id>'], arg['--auto'], arg['<amount>'], "", arg['<assignment_id>'])
        else:
            self.help_worker()

    worker_commands = ('approve', 'reject', 'unreject', 'bonus', 'list', 'help')

    def complete_worker(self, text, line, begidx, endidx):
        return  [i for i in PsiturkNetworkShell.worker_commands if i.startswith(text)]

    def help_worker(self):
        with open(self.helpPath + 'worker.txt', 'r') as helpText:
            print helpText.read()

    # modified version of standard cmd help which lists psiturk commands first
    def do_help(self, arg):
        if arg:
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc = getattr(self, 'do_' + arg).__doc__
                    if doc:
                        self.stdout.write("%s\n" % str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n" % str(self.nohelp % (arg,)))
                return
            func()
        else:
            # Modifications start here
            names = dir(PsiturkNetworkShell)
            superNames = dir(Cmd)
            newNames = [m for m in names if m not in superNames]
            help = {}
            cmds_psiTurk = []
            cmds_super = []
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]]=1
            names.sort()
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd = name[3:]
                    if cmd in help:
                        del help[cmd]
                    if name in newNames:
                        cmds_psiTurk.append(cmd)
                    else:
                        cmds_super.append(cmd)
            self.stdout.write("%s\n" % str(self.doc_leader))
            self.print_topics(self.psiTurk_header, cmds_psiTurk, 15, 80)
            self.print_topics(self.misc_header, help.keys(), 15, 80)
            self.print_topics(self.super_header, cmds_super, 15, 80)

def run(cabinmode=False, script=None):
    usingLibedit = 'libedit' in readline.__doc__
    if usingLibedit:
        print colorize('\n'.join(['libedit version of readline detected.',
                                   'readline will not be well behaved, which may cause all sorts',
                                   'of problems for the psiTurk shell. We highly recommend installing',
                                   'the gnu version of readline by running "sudo pip install gnureadline".',
                                   'Note: "pip install readline" will NOT work because of how the OSX',
                                   'pythonpath is structured.']), 'red', False)
    sys.argv = [sys.argv[0]] # drop arguments which were already processed in command_line.py
    #opt = docopt(__doc__, sys.argv[1:])
    config = PsiturkConfig()
    config.load_config()
    server = control.ExperimentServerController(config)
    if cabinmode:
        shell = PsiturkShell(config, server)
        shell.check_offline_configuration()
    else:
        amt_services = MTurkServices(config.get('AWS Access', 'aws_access_key_id'), \
                                     config.get('AWS Access', 'aws_secret_access_key'),
                                     config.getboolean('Shell Parameters', 'launch_in_sandbox_mode'))
        aws_rds_services = RDSServices(config.get('AWS Access', 'aws_access_key_id'), \
                                 config.get('AWS Access', 'aws_secret_access_key'),
                                 config.get('AWS Access', 'aws_region'))
        web_services = PsiturkOrgServices(config.get('psiTurk Access', 'psiturk_access_key_id'),
                                 config.get('psiTurk Access', 'psiturk_secret_access_id'))
        shell = PsiturkNetworkShell(config, amt_services, aws_rds_services, web_services, server, \
                                    config.getboolean('Shell Parameters', 'launch_in_sandbox_mode'))
    if script:
        with open(script, 'r') as f:
            for line in f:
                shell.onecmd_plus_hooks(line)
    else:
        shell.cmdloop()
