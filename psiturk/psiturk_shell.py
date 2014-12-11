# coding: utf-8
""" PsiturkShell is a commandline interface for psiTurk, which provides
functionality for maintaining the experiment server and interacting with
Mechanical Turk."""

import sys
import subprocess
import re
import time
import json
import os
import string
import random
import datetime
import urllib
import signal
from fuzzywuzzy import process
import atexit

from cmd2 import Cmd
from docopt import docopt, DocoptExit
import readline

import webbrowser
import sqlalchemy as sa

from amt_services import MTurkServices, RDSServices
from psiturk_org_services import PsiturkOrgServices, TunnelServices
from version import version_number
from psiturk_config import PsiturkConfig
import experiment_server_controller as control
from db import db_session, init_db
from models import Participant


def colorize(target, color, use_escape=True):
    ''' Colorize target string. Set use_escape to false when text will not be
    interpreted by readline, such as in intro message.'''
    def escape(code):
        ''' Escape character '''
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

def docopt_cmd(func):
    """
    This decorator is used to simplify the try/except block and pass the result
    of the docopt parsing to the called action.
    """
    def helper_fn(self, arg):
        '''helper function for docopt'''
        try:
            opt = docopt(helper_fn.__doc__, arg)
        except DocoptExit as exception:
            # The DocoptExit is thrown when the args do not match.
            # We print a message to the user and the usage block.
            print 'Invalid Command!'
            print exception
            return
        except SystemExit:
            # The SystemExit exception prints the usage for --help
            # We do not need to do the print here.
            return
        return func(self, opt)
    helper_fn.__name__ = func.__name__
    helper_fn.__doc__ = func.__doc__
    helper_fn.__dict__.update(func.__dict__)
    return helper_fn


# ---------------------------------
#  psiturk shell class
#   -  all commands contained in methods titled do_something(self, arg)
#   -  if a command takes any arguments, use @docopt_cmd decorator
#      and describe command usage in docstring
# ---------------------------------
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
        self.help_path = os.path.join(os.path.dirname(__file__), "shell_help/")
        self.psiturk_header = 'psiTurk command help:'
        self.super_header = 'basic CMD command help:'

        self.color_prompt()
        self.intro = self.get_intro_prompt()

    def default(self, cmd):
        ''' Collect incorrect and mistyped commands '''
        choices = ["help", "mode", "psiturk_status", "server", "shortcuts",
                   "worker", "db", "edit", "open", "config", "show",
                   "debug", "setup_example", "status", "tunnel", "amt_balance",
                   "download_datafiles", "exit", "hit", "load", "quit", "save",
                   "shell", "version"]
        print "%s is not a psiTurk command. See 'help'." %(cmd)
        print "Did you mean this?\n      %s" %(process.extractOne(cmd,
                                                                  choices)[0])


    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   basic command line functions
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def check_offline_configuration(self):
        ''' Check offline configuration file'''
        quit_on_start = False
        database_url = self.config.get('Database Parameters', 'database_url')
        host = self.config.get('Server Parameters', 'host', 'localhost')
        if database_url[:6] != 'sqlite':
            print("*** Error: config.txt option 'database_url' set to use " 
                "mysql://.  Please change this sqllite:// while in cabin mode.")
            quit_on_start = True
        if host != 'localhost':
            print("*** Error: config option 'host' is not set to localhost. " 
                "Please change this to localhost while in cabin mode.")
            quit_on_start = True
        if quit_on_start:
            exit()

    def get_intro_prompt(self):
        ''' Print cabin mode message '''
        sys_status = open(self.help_path + 'cabin.txt', 'r')
        server_msg = sys_status.read()
        return server_msg + colorize('psiTurk version ' + version_number +
                                     '\nType "help" for more information.',
                                     'green', False)

    def do_psiturk_status(self, _):
        ''' Print psiTurk news '''
        print self.get_intro_prompt()

    def color_prompt(self):
        ''' Construct psiTurk shell prompt '''
        prompt = '[' + colorize('psiTurk', 'bold')
        server_string = ''
        server_status = self.server.is_server_running()
        if server_status == 'yes':
            server_string = colorize('on', 'green')
        elif server_status == 'no':
            server_string = colorize('off', 'red')
        elif server_status == 'maybe':
            server_string = colorize('unknown', 'yellow')
        elif server_status == 'blocked':
            server_string = colorize('blocked', 'red')
        prompt += ' server:' + server_string
        prompt += ' mode:' + colorize('cabin', 'bold')
        prompt += ']$ '
        self.prompt = prompt

    def preloop(self):
        ''' Keep persistent command history. '''
        open('.psiturk_history', 'a').close()  # create file if it doesn't exist
        readline.read_history_file('.psiturk_history')
        for i in range(readline.get_current_history_length()):
            if readline.get_history_item(i) is not None:
                self.history.append(readline.get_history_item(i))
        Cmd.preloop(self)

    def postloop(self):
        ''' Save history on exit. '''
        readline.write_history_file('.psiturk_history')
        Cmd.postloop(self)

    def onecmd_plus_hooks(self, line):
        ''' Trigger hooks after command. '''
        if not line:
            return self.emptyline()
        return Cmd.onecmd_plus_hooks(self, line)

    def postcmd(self, stop, line):
        ''' Exit cmd cleanly. '''
        self.color_prompt()
        return Cmd.postcmd(self, stop, line)

    def emptyline(self):
        ''' Create blank line. '''
        self.color_prompt()


    def complete(self, text, state):
        ''' Add space after a completion, makes tab completion with
        multi-word commands cleaner. '''
        return Cmd.complete(self, text, state) + ' '


    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   server management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def server_on(self):
        ''' Start experiment server '''
        self.server.startup()
        time.sleep(0.5)

    def server_off(self):
        ''' Stop experiment server '''
        if (self.server.is_server_running() == 'yes' or
                self.server.is_server_running() == 'maybe'):
            self.server.shutdown()
            print 'Please wait. This could take a few seconds.'
            time.sleep(0.5)

    def server_restart(self):
        ''' Restart experiment server '''
        self.server_off()
        self.server_on()

    def server_log(self):
        ''' Launch log '''
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

        -p, --print-only        just provides the URL, doesn't attempt to
                                launch browser
        """
        if (self.server.is_server_running() == 'no' or
                self.server.is_server_running() == 'maybe'):
            print("Error: Sorry, you need to have the server running to debug "
                   "your experiment.  Try 'server on' first.")
            return

        if 'OPENSHIFT_SECRET_TOKEN' in os.environ:
            base_url = "http://" + self.config.get('Server Parameters', 'host')\
            + "/ad"
        else:
            base_url = "http://" + self.config.get('Server Parameters', 'host')\
            + ":" + self.config.get('Server Parameters', 'port') + "/ad"

        launch_url = base_url + "?assignmentId=debug" \
            + str(self.random_id_generator()) + "&hitId=debug" \
            + str(self.random_id_generator()) + "&workerId=debug" \
            + str(self.random_id_generator() + "&mode=debug")

        if arg['--print-only']:
            print("Here's your randomized debug link, feel free to request " \
                  "another:\n\t" + launch_url)
        else:
            print("Launching browser pointed at your randomized debug link, " \
                  "feel free to request another.\n\t" + launch_url)
            webbrowser.open(launch_url, new=1, autoraise=True)

    def help_debug(self):
        ''' Help for debug '''
        with open(self.help_path + 'debug.txt', 'r') as help_text:
            print help_text.read()

    def do_version(self, _):
        ''' Print version number '''
        print 'psiTurk version ' + version_number


    @docopt_cmd
    def do_config(self, arg):
        """
        Usage:
          config print
          config reload
          config help
        """
        if arg['print']:
            self.print_config(arg)
        elif arg['reload']:
            self.reload_config(arg)
        else:
            self.help_server()

    config_commands = ('print', 'reload', 'help')

    def complete_config(self, text, line, begidx, endidx):
        ''' Not sure what this does... '''
        return  [i for i in PsiturkShell.config_commands if i.startswith(text)]

    def help_config(self):
        ''' Help for config '''
        with open(self.help_path + 'config.txt', 'r') as help_text:
            print help_text.read()

    def print_config(self, _):
        ''' Print configuration. '''
        for section in self.config.sections():
            print '[%s]' % section
            items = dict(self.config.items(section))
            for k in items:
                print "%(a)s=%(b)s" % {'a': k, 'b': items[k]}
            print ''

    def reload_config(self, _):
        ''' Reload config. '''
        restart_server = False
        if (self.server.is_server_running() == 'yes' or
                self.server.is_server_running() == 'maybe'):
            user_input = raw_input("Reloading configuration requires the server "
                                   "to restart. Really reload? y or n: ")
            if user_input != 'y':
                return
            restart_server = True
        self.config.load_config()
        if restart_server:
            self.server_restart()

    def do_status(self, _):
        ''' Notify user of server status. '''
        server_status = self.server.is_server_running()
        if server_status == 'yes':
            print 'Server: ' + colorize('currently online', 'green')
        elif server_status == 'no':
            print 'Server: ' + colorize('currently offline', 'red')
        elif server_status == 'maybe':
            print 'Server: ' + colorize('status unknown', 'yellow')
        elif server_status == 'blocked':
            print 'Server: ' + colorize('blocked', 'red')

    def do_setup_example(self, _):
        ''' Load psiTurk demo.'''
        import setup_example as se
        se.setup_example()


    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   Local SQL database commands
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def db_get_config(self):
        ''' Get database config. '''
        print "Current database setting (database_url): \n\t", \
        self.config.get("Database Parameters", "database_url")

    def db_use_local_file(self, arg, filename=None):
        ''' Use local file for DB. '''
        # interactive = False  # Never used
        if filename is None:
            # interactive = True  # Never used
            filename = raw_input('Enter the filename of the local SQLLite '
                                 'database you would like to use '
                                 '[default=participants.db]: ')
            if filename == '':
                filename = 'participants.db'
        base_url = "sqlite:///" + filename
        self.config.set("Database Parameters", "database_url", base_url)
        print "Updated database setting (database_url): \n\t", \
        self.config.get("Database Parameters", "database_url")
        if self.server.is_server_running() == 'yes':
            self.server_restart()

    def do_download_datafiles(self, _):
        ''' Download datafiles. '''
        contents = {"trialdata": lambda p: p.get_trial_data(), "eventdata": \
                    lambda p: p.get_event_data(), "questiondata": lambda p: \
                    p.get_question_data()}
        query = Participant.query.all()
        for k in contents:
            ret = "".join([contents[k](p) for p in query])
            temp_file = open(k + '.csv', 'w')
            temp_file.write(ret)
            temp_file.close()

    @docopt_cmd
    def do_open(self, arg):
        """
        Usage: open
               open <folder>

        Opens folder or current directory using the local system's shell
        command 'open'.
        """
        if arg['<folder>'] is None:
            subprocess.call(["open"])
        else:
            subprocess.call(["open", arg['<folder>']])

    def do_eof(self, arg):
        ''' Execute on EOF '''
        return self.do_quit(arg)

    def do_exit(self, arg):
        ''' Execute on exit '''
        return self.do_quit(arg)

    def do_quit(self, _):
        ''' Execute on quit '''
        if (self.server.is_server_running() == 'yes' or
                self.server.is_server_running() == 'maybe'):
            user_input = raw_input("Quitting shell will shut down experiment " 
                                    "server.  Really quit? y or n: ")
            if user_input == 'y':
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
        ''' Not sure what this does... '''
        return  [i for i in PsiturkShell.server_commands if i.startswith(text)]

    def help_server(self):
        ''' Help for server '''
        with open(self.help_path + 'server.txt', 'r') as help_text:
            print help_text.read()

    def random_id_generator(self, size=6, chars=string.ascii_uppercase +
                            string.digits):
        ''' Generate random id numbers '''
        return ''.join(random.choice(chars) for x in range(size))

    def do_help(self, arg):
        ''' Modified version of standard cmd help which lists psiturk commands
            first'''
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
            super_names = dir(Cmd)
            new_names = [m for m in names if m not in super_names]
            help_struct = {}
            cmds_psiturk = []
            cmds_super = []
            for name in names:
                if name[:5] == 'help_':
                    help_struct[name[5:]] = 1
            names.sort()
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd = name[3:]
                    if cmd in help_struct:
                        del help_struct[cmd]
                    if name in new_names:
                        cmds_psiturk.append(cmd)
                    else:
                        cmds_super.append(cmd)
            self.stdout.write("%s\n" % str(self.doc_leader))
            self.print_topics(self.psiturk_header, cmds_psiturk, 15, 80)
            self.print_topics(self.misc_header, help_struct.keys(), 15, 80)
            self.print_topics(self.super_header, cmds_super, 15, 80)


class PsiturkNetworkShell(PsiturkShell):
    ''' Extends PsiturkShell class to include online psiTurk.org features '''

    def __init__(self, config, amt_services, aws_rds_services, web_services,
                 server, sandbox):
        self.config = config
        self.amt_services = amt_services
        self.web_services = web_services
        self.db_services = aws_rds_services
        self.sandbox = sandbox
        self.tunnel = TunnelServices()

        self.sandbox_hits = 0
        self.live_hits = 0
        self.tally_hits()
        PsiturkShell.__init__(self, config, server)

        # Prevents running of commands by abbreviation
        self.abbrev = False
        self.debug = True
        self.help_path = os.path.join(os.path.dirname(__file__), "shell_help/")
        self.psiturk_header = 'psiTurk command help:'
        self.super_header = 'basic CMD command help:'

    def do_quit(self, _):
        '''Override do_quit for network clean up.'''
        if (self.server.is_server_running() == 'yes' or
                self.server.is_server_running() == 'maybe'):
            user_input = raw_input("Quitting shell will shut down experiment " 
                                    "server. Really quit? y or n: ")
            if user_input == 'y':
                self.server_off()
            else:
                return False
        return True

    def server_off(self):
        if (self.server.is_server_running() == 'yes' or
                self.server.is_server_running() == 'maybe'):
            self.server.shutdown()
            print 'Please wait. This could take a few seconds.'
            self.clean_up()
            while self.server.is_server_running() != 'no':
                time.sleep(0.5)
        else:
            print 'Your server is already off.'

    def server_restart(self):
        ''' Restart server '''
        self.server_off()
        self.clean_up()
        self.server_on()

    def clean_up(self):
        ''' Clean up child and orphaned processes. '''
        if self.tunnel.is_open:
            print 'Closing tunnel...'
            self.tunnel.close()
            print 'Done.'
        else:
            pass


    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   basic command line functions
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.

    def get_intro_prompt(self):
        ''' Overloads intro prompt with network-aware version if you can reach
        psiTurk.org, request system status message'''
        server_msg = self.web_services.get_system_status()
        return server_msg + colorize('psiTurk version ' + version_number +
                                     '\nType "help" for more information.',
                                     'green', False)

    def color_prompt(self):  # overloads prompt with network info
        prompt = '[' + colorize('psiTurk', 'bold')
        server_string = ''
        server_status = self.server.is_server_running()
        if server_status == 'yes':
            server_string = colorize('on', 'green')
        elif server_status == 'no':
            server_string = colorize('off', 'red')
        elif server_status == 'maybe':
            server_string = colorize('status unknown', 'yellow')
        elif server_status == 'blocked':
            server_string = colorize('blocked', 'red')
        prompt += ' server:' + server_string
        if self.sandbox:
            prompt += ' mode:' + colorize('sdbx', 'bold')
        else:
            prompt += ' mode:' + colorize('live', 'bold')
        if self.tunnel.is_open:
            prompt += ' tunnel:' + colorize('✓', 'green')
        if self.sandbox:
            prompt += ' #HITs:' + str(self.sandbox_hits)
        else:
            prompt += ' #HITs:' + str(self.live_hits)
        prompt += ']$ '
        self.prompt = prompt

    def server_on(self):
        self.server.startup()
        time.sleep(0.5)

    def do_status(self, arg): # overloads do_status with AMT info
        super(PsiturkNetworkShell, self).do_status(arg)
        # server_status = self.server.is_server_running()  # Not used
        self.tally_hits()
        if self.sandbox:
            print 'AMT worker site - ' + colorize('sandbox', 'bold') + ': ' \
            + str(self.sandbox_hits) + ' HITs available'
        else:
            print 'AMT worker site - ' + colorize('live', 'bold') + ': ' \
            + str(self.live_hits) + ' HITs available'


    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   worker management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    @staticmethod
    def add_bonus(worker_dict):
        " Adds DB-logged worker bonus to worker list data "
        try:
            worker = Participant.query.filter(
                Participant.assignmentid == worker_dict['assignmentId']).one()
            worker_dict['bonus'] = worker.bonus
        except sa.exc.InvalidRequestError:
            # assignment is found on mturk but not in local database.
            worker_dict['bonus'] = 'N/A'
        return worker_dict

    def worker_list(self, submitted, approved, rejected, chosen_hit):
        ''' List worker stats '''
        workers = None
        if submitted:
            workers = self.amt_services.get_workers("Submitted")
        elif approved:
            workers = self.amt_services.get_workers("Approved")
        elif rejected:
            workers = self.amt_services.get_workers("Rejected")
        else:
            workers = self.amt_services.get_workers()
        if workers is False:
            print colorize('*** failed to get workers', 'red')
        if chosen_hit:
            workers = [worker for worker in workers if \
                       worker['hitId'] == chosen_hit]
            print 'listing workers for HIT', chosen_hit
        if not len(workers):
            print "*** no workers match your request"
        else:
            workers = [self.add_bonus(worker)
                       for worker in workers]
            print json.dumps(workers, indent=4,
                             separators=(',', ': '))

    def worker_approve(self, chosen_hit, assignment_ids=None):
        ''' Approve worker '''
        if chosen_hit:
            workers = self.amt_services.get_workers("Submitted")
            assignment_ids = [worker['assignmentId'] for worker in workers if \
                              worker['hitId'] == chosen_hit]
            print 'approving workers for HIT', chosen_hit
        for assignment_id in assignment_ids:
            success = self.amt_services.approve_worker(assignment_id)
            if success:
                print 'approved', assignment_id
            else:
                print '*** failed to approve', assignment_id

    def worker_reject(self, chosen_hit, assignment_ids = None):
        ''' Reject worker '''
        if chosen_hit:
            workers = self.amt_services.get_workers("Submitted")
            assignment_ids = [worker['assignmentId'] for worker in workers if \
                              worker['hitId'] == chosen_hit]
            print 'rejecting workers for HIT', chosen_hit
        for assignment_id in assignment_ids:
            success = self.amt_services.reject_worker(assignment_id)
            if success:
                print 'rejected', assignment_id
            else:
                print '*** failed to reject', assignment_id

    def worker_unreject(self, chosen_hit, assignment_ids = None):
        ''' Unreject worker '''
        if chosen_hit:
            workers = self.amt_services.get_workers("Rejected")
            assignment_ids = [worker['assignmentId'] for worker in workers if \
                              worker['hitId'] == chosen_hit]
        for assignment_id in assignment_ids:
            success = self.amt_services.unreject_worker(assignment_id)
            if success:
                print 'unrejected %s' % (assignment_id)
            else:
                print '*** failed to unreject', assignment_id

    def worker_bonus(self, chosen_hit, auto, amount, reason,
                     assignment_ids=None):
        ''' Bonus worker '''
        while not reason:
            user_input = raw_input("Type the reason for the bonus. Workers "
                                   "will see this message: ")
            reason = user_input
        # Bonus already-bonused workers if the user explicitly lists their
        # worker IDs
        override_status = True
        if chosen_hit:
            override_status = False
            workers = self.amt_services.get_workers("Approved")
            if workers is False:
                print "No approved workers for HIT", chosen_hit
                return
            assignment_ids = [worker['assignmentId'] for worker in workers if \
                              worker['hitId'] == chosen_hit]
            print 'bonusing workers for HIT', chosen_hit
        for assignment_id in assignment_ids:
            try:
                init_db()
                part = Participant.query.\
                       filter(Participant.assignmentid == assignment_id).\
                       filter(Participant.endhit != None).\
                       one()
                if auto:
                    amount = part.bonus
                status = part.status
                if amount <= 0:
                    print "bonus amount <=$0, no bonus given to", assignment_id
                elif status == 7 and not override_status:
                    print "bonus already awarded to ", assignment_id
                else:
                    success = self.amt_services.bonus_worker(assignment_id,
                                                             amount, reason)
                    if success:
                        print "gave bonus of $" + str(amount) + " to " + \
                        assignment_id
                        part.status = 7
                        db_session.add(part)
                        db_session.commit()
                        db_session.remove()
                    else:
                        print "*** failed to bonus", assignment_id
            except:
                print "*** failed to bonus", assignment_id

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   hit management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def do_amt_balance(self, _):
        ''' Get MTurk balance '''
        print self.amt_services.check_balance()

    def help_amt_balance(self):
        ''' Get help for amt_balance. '''
        with open(self.help_path + 'amt.txt', 'r') as help_text:
            print help_text.read()

    def hit_list(self, active_hits, reviewable_hits):
        ''' List hits. '''
        hits_data = []
        if active_hits:
            hits_data = self.amt_services.get_active_hits()
        elif reviewable_hits:
            hits_data = self.amt_services.get_reviewable_hits()
        else:
            hits_data = self.amt_services.get_all_hits()
        if not hits_data:
            print '*** no hits retrieved'
        else:
            for hit in hits_data:
                print hit

    def hit_extend(self, hit_id, assignments, minutes):
        """ Add additional worker assignments or minutes to a HIT.

        Args:
            hit_id: A list conaining one hit_id string.
            assignments: Variable <int> for number of assignments to add.
            minutes: Variable <int> for number of minutes to add.

        Returns:
            A side effect of this function is that the state of a HIT changes
            on AMT servers.

        Raises:

        """

        assert type(hit_id) is list
        assert type(hit_id[0]) is str

        if self.amt_services.extend_hit(hit_id[0], assignments, minutes):
            print "HIT extended."

    def hit_dispose(self, all_hits, hit_ids=None):
        ''' Dispose HIT. '''
        if all_hits:
            hits_data = self.amt_services.get_all_hits()
            hit_ids = [hit.options['hitid'] for hit in hits_data if \
                       hit.options['status'] == "Reviewable"]
        for hit in hit_ids:
            # Check that the HIT is reviewable
            status = self.amt_services.get_hit_status(hit)
            if not status:
                print "*** Error getting hit status"
                return
            if self.amt_services.get_hit_status(hit) != "Reviewable":
                print("*** This hit is not 'Reviewable' and so can not be "
                      "disposed of")
                return
            else:
                success = self.amt_services.dispose_hit(hit)
                # self.web_services.delete_ad(hit)  # also delete the ad
                if success:
                    if self.sandbox:
                        print "deleting sandbox HIT", hit
                    else:
                        print "deleting live HIT", hit
        self.tally_hits()

    def hit_expire(self, all_hits, hit_ids=None):
        ''' Expire all HITs. '''
        if all_hits:
            hits_data = self.amt_services.get_active_hits()
            hit_ids = [hit.options['hitid'] for hit in hits_data]
        for hit in hit_ids:
            success = self.amt_services.expire_hit(hit)
            if success:
                if self.sandbox:
                    print "expiring sandbox HIT", hit
                else:
                    print "expiring live HIT", hit
        self.tally_hits()

    def tally_hits(self):
        ''' Tally hits '''
        hits = self.amt_services.get_active_hits()
        num_hits = 0
        if hits:
            num_hits = len(hits)
        if self.sandbox:
            self.sandbox_hits = num_hits
        else:
            self.live_hits = num_hits

    def hit_create(self, numWorkers, reward, duration):

        server_loc = str(self.config.get('Server Parameters', 'host'))
        if server_loc in ['localhost', '127.0.0.1']:
            print '\n'.join(['*****************************',
            "  Sorry, your server is set for local debugging only.  You cannot",\
            "  make public HITs or Ads.  Please edit the config.txt file inside",\
            "  your project folder and set the 'host' variable in the 'Server",\
            "  Parameters' section to something other than 'localhost' or",\
            "  '127.0.0.1'.  This will make your psiturk server process",\
            "  reachable by the external world.  The most useful option is",\
            "  '0.0.0.0'", ""])

            user_input = raw_input(
                '\n'.join(['  If you are using an external server process press'\
                           ' `y` to continue.', '  Otherwise press `n` to'\
                           ' cancel:  ']
                          ))
            if user_input != 'y':
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
            user_input = raw_input('\n'.join([
                '  If you are using an external server process, press `y` to continue.',
                '  Otherwise, press `n` to cancel:'
            ]))
            if user_input != 'y':
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
            duration = raw_input('duration of hit (in hours or h:mm)? ')

        try:
            durParts = duration.split(":")
            if len(durParts) == 1:
                hrs = int(durParts[0])
                mns = 0
            elif len(durParts) == 2:
                hrs = int(durParts[0])
                mns = int(durParts[1])
            else:
                raise ValueError
        except ValueError:
            print '*** duration must be a number of hours or in the form [hours]:[minutes]'
            return
        if (hrs < 0 or mns < 0 or (hrs == 0 and mns == 0)):
            print '*** duration must be greater than 0'
            return

        # register with the ad server (psiturk.org/ad/register) using POST
        if os.path.exists('templates/ad.html'):
            ad_html = open('templates/ad.html').read()
        else:
            print '\n'.join(['*****************************',
                             '  Sorry, there was an error registering ad.',
                             '  Both ad.html is required to be in the templates folder',
                             '  of your project so that these Ad can be served!'])
            return

        size_of_ad = sys.getsizeof(ad_html)
        if size_of_ad >= 1048576:
            print '\n'.join(['*****************************',
                             '  Sorry, there was an error registering ad.',
                             '  Your local ad.html is %s byes, but the maximum',
                             '  template size uploadable to the Ad server is',
                             '  1048576 bytes!' % size_of_ad])
            return

        # what all do we need to send to server?
        # 1. server
        # 2. port
        # 3. support_ie?
        # 4. ad.html template
        # 5. contact_email in case an error happens

        if self.tunnel.is_open:
            ip_address = self.tunnel.url
            port = str(self.tunnel.tunnel_port)  # Set by tunnel server.
        else:
            ip_address = str(self.web_services.get_my_ip())
            port = str(self.config.get('Server Parameters', 'port'))
        ad_content = {
            'psiturk_external': True,
            'server': ip_address,
            'port': port,
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
        if ad_id is not False:

            hit_config = {
                "ad_location": self.web_services.get_ad_url(ad_id, int(self.sandbox)),
                "approve_requirement": self.config.get('HIT Configuration', 'Approve_Requirement'),
                "us_only": self.config.getboolean('HIT Configuration', 'US_only'),
                "lifetime": datetime.timedelta(hours=self.config.getfloat('HIT Configuration', 'lifetime')),
                "max_assignments": numWorkers,
                "title": self.config.get('HIT Configuration', 'title'),
                "description": self.config.get('HIT Configuration', 'description'),
                "keywords": self.config.get('HIT Configuration', 'amt_keywords'),
                "reward": reward,
                "duration": datetime.timedelta(hours = hrs, minutes = mns)
            }
            hit_id = self.amt_services.create_hit(hit_config)
            if hit_id is not False:
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
                self.sandbox_hits += 1
            else:
                self.live_hits += 1
            # print results
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
                print('  Ad URL: https://sandbox.ad.psiturk.org/view/%s?assignmentId=debug%s&hitId=debug%s&workerId=debug%s'
                      % (str(ad_id), str(self.random_id_generator()), str(self.random_id_generator()), str(self.random_id_generator())))
                print "Note: This url cannot be used to run your full psiTurk experiment.  It is only for testing your ad."
                print('  Sandbox URL: https://workersandbox.mturk.com/mturk/searchbar?selectedSearchType=hitgroups&searchWords=%s'
                      % (urllib.quote_plus(str(self.config.get('HIT Configuration', 'title')))))
                print "Hint: In OSX, you can open a terminal link using cmd + click"
                print "Note: This sandboxed ad will expire from the server in 16 days."
            else:
                print('  Ad URL: https://ad.psiturk.org/view/%s?assignmentId=debug%s&hitId=debug%s&workerId=debug%s'
                      % (str(ad_id), str(self.random_id_generator()), str(self.random_id_generator()), str(self.random_id_generator())))
                print "Note: This url cannot be used to run your full psiTurk experiment.  It is only for testing your ad."
                print('  MTurk URL: https://www.mturk.com/mturk/searchbar?selectedSearchType=hitgroups&searchWords=%s'
                        % (urllib.quote_plus(str(self.config.get('HIT Configuration', 'title')))))
                print "Hint: In OSX, you can open a terminal link using cmd + click"


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
          db aws_create_instance [<instance_id> <size> <username> <password>
                                  <dbname>]
          db aws_delete_instance [<instance_id>]
          db help
        """
        if arg['get_config']:
            self.db_get_config()
        elif arg['use_local_file']:
            self.db_use_local_file(arg, filename=arg['<filename>'])
        elif arg['use_aws_instance']:
            self.db_use_aws_instance(arg['<instance_id>'], arg)
        elif arg['aws_list_regions']:
            self.db_aws_list_regions()
        elif arg['aws_get_region']:
            self.db_aws_get_region()
        elif arg['aws_set_region']:
            self.db_aws_set_region(arg['<region_name>'])
        elif arg['aws_list_instances']:
            self.db_aws_list_instances()
        elif arg['aws_create_instance']:
            self.db_create_aws_db_instance(arg['<instance_id>'], arg['<size>'],
                                           arg['<username>'],
                                           arg['<password>'], arg['<dbname>'])
        elif arg['aws_delete_instance']:
            self.db_aws_delete_instance(arg['<instance_id>'])
        else:
            self.help_db()

    db_commands = ('get_config', 'use_local_file', 'use_aws_instance',
                   'aws_list_regions', 'aws_get_region', 'aws_set_region',
                   'aws_list_instances', 'aws_create_instance',
                   'aws_delete_instance', 'help')

    def complete_db(self, text, line, begidx, endidx):
        return  [i for i in PsiturkNetworkShell.db_commands if \
                 i.startswith(text)]

    def help_db(self):
        ''' DB help '''
        with open(self.help_path + 'db.txt', 'r') as help_text:
            print help_text.read()


    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   AWS RDS commands
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def db_aws_list_regions(self):
        ''' List AWS DB regions '''
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
        ''' Get AWS region '''
        print self.db_services.get_region()

    def db_aws_set_region(self, region_name):
        ''' Set AWS region '''
        # interactive = False # Not used
        if region_name is None:
            # interactive = True  # Not used
            self.db_aws_list_regions()
            allowed_regions = self.db_services.list_regions()
            region_name = "NONSENSE WORD1234"
            tries = 0
            while region_name not in allowed_regions:
                if tries == 0:
                    region_name = raw_input('Enter the name of the region you '
                                            'would like to use: ')
                else:
                    print("*** The region name (%s) you entered is not allowed, " \
                          "please choose from the list printed above (use type 'db " \
                          "aws_list_regions'." % region_name)
                    region_name = raw_input('Enter the name of the region you '
                                            'would like to use: ')
                tries += 1
                if tries > 5:
                    print("*** Error, region you are requesting not available.  "
                          "No changes made to regions.")
                    return
        self.db_services.set_region(region_name)
        print "Region updated to ", region_name
        self.config.set('AWS Access', 'aws_region', region_name, True)
        if self.server.is_server_running() == 'yes':
            self.server_restart()

    def db_aws_list_instances(self):
        ''' List AWS DB instances '''
        instances = self.db_services.get_db_instances()
        if not instances:
            print("There are no DB instances associated with your AWS account " \
                "in region " + self.db_services.get_region())
        else:
            print("Here are the current DB instances associated with your AWS " \
                "account in region " + self.db_services.get_region())
            for dbinst in instances:
                print '\t'+'-'*20
                print "\tInstance ID: " + dbinst.id
                print "\tStatus: " + dbinst.status

    def db_aws_delete_instance(self, instance_id):
        ''' Delete AWS DB instance '''
        interactive = False
        if instance_id is None:
            interactive = True

        instances = self.db_services.get_db_instances()
        instance_list = [dbinst.id for dbinst in instances]

        if interactive:
            valid = False
            if len(instances) == 0:
                print("There are no instances you can delete currently.  Use "
                      "`db aws_create_instance` to make one.")
                return
            print "Here are the available instances you can delete:"
            for inst in instances:
                print "\t ", inst.id, "(", inst.status, ")"
            while not valid:
                instance_id = raw_input('Enter the instance identity you would '
                                        'like to delete: ')
                res = self.db_services.validate_instance_id(instance_id)
                if res is True:
                    valid = True
                else:
                    print(res + " Try again, instance name not valid.  Check " \
                        "for typos.")
                if instance_id in instance_list:
                    valid = True
                else:
                    valid = False
                    print("Try again, instance not present in this account.  "
                          "Try again checking for typos.")
        else:
            res = self.db_services.validate_instance_id(instance_id)
            if res is not True:
                print("*** Error, instance name either not valid.  Try again " 
                     "checking for typos.")
                return
            if instance_id not in instance_list:
                print("*** Error, This instance not present in this account.  "
                     "Try again checking for typos.  Run `db aws_list_instances` to "
                     "see valid list.")
                return

        user_input = raw_input(
            "Deleting an instance will erase all your data associated with the "
            "database in that instance.  Really quit? y or n:"
        )
        if user_input == 'y':
            res = self.db_services.delete_db_instance(instance_id)
            if res:
                print("AWS RDS database instance %s deleted.  Run `db " \
                    "aws_list_instances` for current status." % instance_id)
            else:
                print("*** Error deleting database instance %s.  " \
                    "It maybe because it is still being created, deleted, or is " \
                    "being backed up.  Run `db aws_list_instances` for current " \
                    "status." % instance_id)
        else:
            return

    def db_use_aws_instance(self, instance_id, arg):
        ''' set your database info to use the current instance configure a
        security zone for this based on your ip '''
        interactive = False
        if instance_id is None:
            interactive = True

        instances = self.db_services.get_db_instances()
        instance_list = [dbinst.id for dbinst in instances]

        if len(instances) == 0:
            print("There are no instances in this region/account.  Use `db "
                "aws_create_instance` to make one first.")
            return

        # show list of available instances, if there are none cancel immediately
        if interactive:
            valid = False
            print("Here are the available instances you have.  You can only "
                "use those listed as 'available':")
            for inst in instances:
                print "\t ", inst.id, "(", inst.status, ")"
            while not valid:
                instance_id = raw_input('Enter the instance identity you would '
                                        'like to use: ')
                res = self.db_services.validate_instance_id(instance_id)
                if res is True:
                    valid = True
                else:
                    print(res + " Try again, instance name not valid.  Check "
                          "for typos.")
                if instance_id in instance_list:
                    valid = True
                else:
                    valid = False
                    print("Try again, instance not present in this account. "
                          "Try again checking for typos.")
        else:
            res = self.db_services.validate_instance_id(instance_id)
            if res != True:
                print("*** Error, instance name either not valid.  Try again "
                      "checking for typos.")
                return
            if instance_id not in instance_list:
                print("*** Error, This instance not present in this account. "
                      "Try again checking for typos.  Run `db aws_list_instances` to "
                      "see valid list.")
                return

        user_input = raw_input(
            "Switching your DB settings to use this instance. Are you sure you "
            "want to do this? "
        )
        if user_input == 'y':
            # ask for password
            valid = False
            while not valid:
                password = raw_input('enter the master password for this '
                                     'instance: ')
                res = self.db_services.validate_instance_password(password)
                if res != True:
                    print("*** Error: password seems incorrect, doesn't "
                          "conform to AWS rules.  Try again")
                else:
                    valid = True

            # Get instance
            myinstance = self.db_services.get_db_instance_info(instance_id)
            if myinstance:
                # Add security zone to this node to allow connections
                my_ip = self.web_services.get_my_ip()
                if (not self.db_services.allow_access_to_instance(myinstance,
                                                                  my_ip)):
                    print("*** Error authorizing your ip address to connect to " \
                          "server (%s)." % my_ip)
                    return
                print "AWS RDS database instance %s selected." % instance_id

                # Using regular SQL commands list available database on this
                # node
                try:
                    db_url = 'mysql://' + myinstance.master_username + ":" \
                        + password + "@" + myinstance.endpoint[0] + ":" + \
                        str(myinstance.endpoint[1])
                    engine = sa.create_engine(db_url, echo=False)
                    eng = engine.connect().execute
                    db_names = eng("show databases").fetchall()
                except:
                    print("***  Error connecting to instance.  Your password "
                          "might be incorrect.")
                    return
                existing_dbs = [db[0] for db in db_names if db not in \
                                [('information_schema',), ('innodb',), \
                                 ('mysql',), ('performance_schema',)]]
                create_db = False
                if len(existing_dbs) == 0:
                    valid = False
                    while not valid:
                        db_name = raw_input("No existing DBs in this instance. "
                                            "Enter a new name to create one: ")
                        res = self.db_services.validate_instance_dbname(db_name)
                        if res is True:
                            valid = True
                        else:
                            print res + " Try again."
                    create_db = True
                else:
                    print "Here are the available database tables"
                    for database in existing_dbs:
                        print "\t" + database
                    valid = False
                    while not valid:
                        db_name = raw_input(
                            "Enter the name of the database you want to use or "
                            "a new name to create  a new one: "
                        )
                        res = self.db_services.validate_instance_dbname(db_name)
                        if res is True:
                            valid = True
                        else:
                            print res + " Try again."
                    if db_name not in existing_dbs:
                        create_db = True
                if create_db:
                    try:
                        connection.execute("CREATE DATABASE %s;" % db_name)
                    except:
                        print("*** Error creating database %s on instance " \
                              "%s" % (db_name, instance_id))
                        return
                base_url = 'mysql://' + myinstance.master_username + ":" + \
                    password + "@" + myinstance.endpoint[0] + ":" + \
                    str(myinstance.endpoint[1]) + "/" + db_name
                self.config.set("Database Parameters", "database_url", base_url)
                print("Successfully set your current database (database_url) " \
                      "to \n\t%s" % base_url)
                if (self.server.is_server_running() == 'maybe' or
                        self.server.is_server_running() == 'yes'):
                    self.do_restart_server('')
            else:
                print '\n'.join([
                    "*** Error selecting database instance %s." % arg['<id>'],
                    "Run `db list_db_instances` for current status of instances, only `available`",
                    "instances can be used.  Also, your password may be incorrect."
                ])
        else:
            return


    def db_create_aws_db_instance(self, instid=None, size=None, username=None,
                                  password=None, dbname=None):
        ''' Create db instance on AWS '''
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
                instid = raw_input('enter an identifier for the instance (see '
                                   'rules above): ')
                res = self.db_services.validate_instance_id(instid)
                if res is True:
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
                if res is True:
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
                if res is True:
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
                if res is True:
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
                dbname = raw_input('name for first database on this instance \
                                   (see rules): ')
                res = self.db_services.validate_instance_dbname(dbname)
                if res is True:
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


    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   Basic shell commands
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    @docopt_cmd
    def do_mode(self, arg):
        """
        Usage: mode
               mode <which>
        """
        restart_server = False
        if self.server.is_server_running() == 'yes' or self.server.is_server_running() == 'maybe':
            r = raw_input("Switching modes requires the server to restart. Really "
                          "switch modes? y or n: ")
            if r != 'y':
                return
            restart_server = True
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
        if restart_server:
            self.server_restart()
    def help_mode(self):
        ''' Help '''
        with open(self.help_path + 'mode.txt', 'r') as help_text:
            print help_text.read()

    @docopt_cmd
    def do_tunnel(self, arg):
        """
        Usage: tunnel open
               tunnel change
               tunnel status
        """
        if arg['open']:
            self.tunnel_open()
        elif arg['change']:
            self.tunnel_change()
        elif arg['status']:
            self.tunnel_status()

    # def help_tunnel(self):
    #     with open(self.help_path + 'tunnel.txt', 'r') as helpText:
    #         print helpText.read()

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
            self.hit_create(arg['<numWorkers>'], arg['<reward>'],
                            arg['<duration>'])
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
        ''' Complete HIT. '''
        return  [i for i in PsiturkNetworkShell.hit_commands if \
                 i.startswith(text)]

    def help_hit(self):
        ''' HIT help '''
        with open(self.help_path + 'hit.txt', 'r') as help_text:
            print help_text.read()


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
            self.worker_list(arg['--submitted'], arg['--approved'],
                             arg['--rejected'], arg['<hit_id>'])
        elif arg['bonus']:
            self.worker_bonus(arg['<hit_id>'], arg['--auto'], arg['<amount>'],
                              "", arg['<assignment_id>'])
        else:
            self.help_worker()

    worker_commands = ('approve', 'reject', 'unreject', 'bonus', 'list', 'help')

    def complete_worker(self, text, line, begidx, endidx):
        ''' Complete worker. '''
        return  [i for i in PsiturkNetworkShell.worker_commands if \
                 i.startswith(text)]

    def help_worker(self):
        ''' Help for worker command. '''
        with open(self.help_path + 'worker.txt', 'r') as help_text:
            print help_text.read()

    @docopt_cmd
    def do_debug(self, arg):
        """
        Usage: debug [options]

        -p, --print-only        just provides the URL, doesn't attempt to
                                launch browser
        """
        if (self.server.is_server_running() == 'no' or
                self.server.is_server_running() == 'maybe'):
            print("Error: Sorry, you need to have the server running to debug "
                  "your experiment.  Try 'server on' first.")
            return

        if 'OPENSHIFT_SECRET_TOKEN' in os.environ:
            base_url = "http://" + self.config.get('Server Parameters',
                                                   'host') + "/ad"
        else:
            base_url = "http://" + self.config.get('Server Parameters',
                                                   'host') + \
                ":" + self.config.get('Server Parameters', 'port') + "/ad"

        my_ip = self.web_services.get_my_ip()
        remote_url = "http://" + my_ip + ":" + \
            self.config.get('Server Parameters', 'port') + "/ad"

        launch_url = base_url + "?assignmentId=debug" + \
            str(self.random_id_generator()) \
            + "&hitId=debug" + str(self.random_id_generator()) \
            + "&workerId=debug" + str(self.random_id_generator() \
            + "&mode=debug")

        remote_launch_url = remote_url + "?assignmentId=debug" + \
            str(self.random_id_generator()) \
            + "&hitId=debug" + str(self.random_id_generator()) \
            + "&workerId=debug" + str(self.random_id_generator() \
            + "&mode=debug")

        if arg['--print-only']:
            print("Here's your randomized debug link, feel free to request " \
                  "another:\n\t" + remote_launch_url)

        else:
            print("Launching browser pointed at your randomized debug link, " \
                  "feel free to request another.\n\t" + launch_url)
            webbrowser.open(launch_url, new=1, autoraise=True)

    # Modified version of standard cmd help which lists psiturk commands first.
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
            super_names = dir(Cmd)
            new_names = [m for m in names if m not in super_names]
            help_struct = {}
            cmds_psiTurk = []
            cmds_super = []
            for name in names:
                if name[:5] == 'help_':
                    help_struct[name[5:]]=1
            names.sort()
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    cmd = name[3:]
                    if cmd in help_struct:
                        del help_struct[cmd]
                    if name in new_names:
                        cmds_psiTurk.append(cmd)
                    else:
                        cmds_super.append(cmd)
            self.stdout.write("%s\n" % str(self.doc_leader))
            self.print_topics(self.psiturk_header, cmds_psiTurk, 15, 80)
            self.print_topics(self.misc_header, help_struct.keys(), 15, 80)
            self.print_topics(self.super_header, cmds_super, 15, 80)

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   tunnel
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.

    def tunnel_open(self):
        ''' Open tunnel '''
        if (self.server.is_server_running() == 'no' or
                self.server.is_server_running() == 'maybe'):
            print("Error: Sorry, you need to have the server running to open a "
                  "tunnel.  Try 'server on' first.")
        else:
            self.tunnel.open()

    def tunnel_status(self):
        ''' Get tunnel status '''
        if self.tunnel.is_open:
            print "For tunnel status, navigate to http://127.0.0.1:4040"
            print "Hint: In OSX, you can open a terminal link using cmd + click"
        else:
            print("Sorry, you need to open a tunnel to check the status. Try" 
                  "'tunnel open' first.")

    def tunnel_change(self):
        ''' Change tunnel url '''
        print('Tearing down old tunnel if present...')
        self.tunnel.change_tunnel_ad_url()
        print("New tunnel ready. Run 'tunnel open' to start.")

def run(cabinmode=False, script=None):
    using_libedit = 'libedit' in readline.__doc__
    if using_libedit:
        print colorize('\n'.join([
            'libedit version of readline detected.',
            'readline will not be well behaved, which may cause all sorts',
            'of problems for the psiTurk shell. We highly recommend installing',
            'the gnu version of readline by running "sudo pip install gnureadline".',
            'Note: "pip install readline" will NOT work because of how the OSX',
            'pythonpath is structured.'
        ]), 'red', False)
    sys.argv = [sys.argv[0]] # Drop arguments which were already processed in command_line.py
    #opt = docopt(__doc__, sys.argv[1:])
    config = PsiturkConfig()
    config.load_config()
    server = control.ExperimentServerController(config)
    if cabinmode:
        shell = PsiturkShell(config, server)
        shell.check_offline_configuration()
    else:
        amt_services = MTurkServices(
            config.get('AWS Access', 'aws_access_key_id'), \
            config.get('AWS Access', 'aws_secret_access_key'),
            config.getboolean('Shell Parameters', 'launch_in_sandbox_mode'))
        aws_rds_services = RDSServices(
            config.get('AWS Access', 'aws_access_key_id'), \
            config.get('AWS Access', 'aws_secret_access_key'),
            config.get('AWS Access', 'aws_region'))
        web_services = PsiturkOrgServices(
            config.get('psiTurk Access', 'psiturk_access_key_id'),
            config.get('psiTurk Access', 'psiturk_secret_access_id'))
        shell = PsiturkNetworkShell(
            config, amt_services, aws_rds_services, web_services, server, \
            config.getboolean('Shell Parameters', 'launch_in_sandbox_mode'))

    if script:
        with open(script, 'r') as temp_file:
            for line in temp_file:
                shell.onecmd_plus_hooks(line)
    else:
        def handler(signum, frame):
            """ just do nothing """

        signal.signal(signal.SIGINT, handler)
        shell.cmdloop()

    @atexit.register
    def clean_up():
        ''' Catch abrupt keyboard interrupts '''
        try:
            if (shell.server.is_server_running() == 'yes' or
                    shell.server.is_server_running() == 'maybe'):
                shell.server_off()
            if not cabinmode:
                shell.tunnel.close()
        except:
            pass
