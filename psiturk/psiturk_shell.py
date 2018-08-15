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

from cmd2 import Cmd
from docopt import docopt, DocoptExit

try:
    import gnureadline as readline
except ImportError:
    import readline

import webbrowser
import sqlalchemy as sa

from amt_services_wrapper import MTurkServicesWrapper
from psiturk_org_services import PsiturkOrgServices, TunnelServices
from version import version_number
from psiturk_config import PsiturkConfig
import experiment_server_controller as control
from models import Participant
from utils import *

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

    def __init__(self, config, server, quiet=False):
        Cmd.__init__(self)
        self.config = config
        self.server = server

        # Prevents running of commands by abbreviation
        self.abbrev = False
        self.debug = True
        self.help_path = os.path.join(os.path.dirname(__file__), "shell_help/")
        self.psiturk_header = 'psiTurk command help:'
        self.super_header = 'basic CMD command help:'
        
        if not self.quiet:
            self.color_prompt()
            self.intro = self.get_intro_prompt()
        else:
            self.intro = ''

        self.already_prelooped = False

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
        if not self.already_prelooped:
            self.already_prelooped = True
            open('.psiturk_history', 'a').close()  # create file if it doesn't exist
            readline.read_history_file('.psiturk_history')
            for i in range(readline.get_current_history_length()):
                if readline.get_history_item(i) is not None:
                    self.history.append(readline.get_history_item(i))

    def postloop(self):
        ''' Save history on exit. '''
        readline.write_history_file('.psiturk_history')

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
        ''' Refresh the prompt after an empty line is entered. '''
        self.color_prompt()

    def complete(self, text, state):
        ''' Add space after a completion, makes tab completion with
        multi-word commands cleaner. '''
        return Cmd.complete(self, text, state) + ' '
    
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   hit management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def hit_list(self, active_hits, reviewable_hits, all_studies):
        ''' List hits. '''
        if active_hits:
            hits_data = self.amt_services_wrapper.get_active_hits(all_studies)
        elif reviewable_hits:
            hits_data = self.amt_services_wrapper.get_reviewable_hits(all_studies)
        else:
            hits_data = self.amt_services_wrapper.get_all_hits(all_studies)
        if not hits_data:
            print '*** no hits retrieved'
        else:
            for hit in hits_data:
                print hit
    
    def _estimate_expenses(self, num_workers, reward):
        ''' Returns tuple describing expenses:
        amount paid to workers
        amount paid to amazon'''
        
        # fee structure changed 07.22.15:
        # 20% for HITS with < 10 assignments
        # 40% for HITS with >= 10 assignments
        commission = 0.2
        if float(num_workers) >= 10:
            commission = 0.4 
        work = float(num_workers) * float(reward)
        fee = work * commission
        return (work, fee, work+fee)
        
    def _confirm_dialog(self, prompt):
        ''' Prompts for a 'yes' or 'no' to given prompt. '''
        response = raw_input(prompt).strip().lower()
        valid = {'y': True, 'ye': True, 'yes': True, 'n': False, 'no': False}
        while True:
            try:
                return valid[response]
            except:
                response = raw_input("Please respond 'y' or 'n': ").strip().lower()
    
    def hit_create(self, numWorkers, reward, duration):
        
        if self.sandbox:
            mode = 'sandbox'
        else:
            mode = 'live'
        
        # Argument retrieval and validation
        if numWorkers is None:
            numWorkers = raw_input('number of participants? ').strip()
        try:
            numWorkers = int(numWorkers)
        except ValueError:
            print '*** number of participants must be a whole number'
            return
        if numWorkers <= 0:
            print '*** number of participants must be greater than 0'
            return

        if reward is None:
            reward = raw_input('reward per HIT? ').strip()
        p = re.compile('^\d*\.\d\d$')
        m = p.match(reward)
        if m is None:
            print '*** reward must have format [dollars].[cents]'
            return
        try:
            reward = float(reward)
        except:
            print '*** reward must be in format [dollars].[cents]'
            return
            
        if duration is None:
            duration = raw_input(
                'duration of hit (in hours, it can be decimals)? ').strip()
        try:
            duration = float(duration)
        except ValueError:
            print '*** duration must a number'
            return
        if duration <= 0:
            print '*** duration must be greater than 0'
            return

        _, fee, total = self._estimate_expenses(numWorkers, reward)
        
        if not self.quiet:
            dialog_query = '\n'.join(['*****************************',
                                      '    Max workers: %d' % numWorkers,
                                      '    Reward: $%.2f' % reward,
                                      '    Duration: %s hours' % duration,
                                      '    Fee: $%.2f' % fee,
                                      '    ________________________',
                                      '    Total: $%.2f' % total,
                                      'Create %s HIT [y/n]? ' % colorize(mode, 'bold')])
            if not self._confirm_dialog(dialog_query):
                print '*** Cancelling HIT creation.'
                return
        
        try:
            (hit_id, ad_id) = self.amt_services_wrapper.hit_create(numWorkers, reward,
                            duration)
                            
            print '\n'.join(['*****************************',
                             '  Created %s HIT' % colorize(mode, 'bold'),
                             '    HITid: %s' % str(hit_id),
                             '    Max workers: %d' % numWorkers,
                             '    Reward: $%.2f' % reward,
                             '    Duration: %s hours' % duration,
                             '    Fee: $%.2f' % fee,
                             '    ________________________',
                             '    Total: $%.2f' % total])
                             
            # Print the Ad Url
            use_psiturk_ad_server = self.config.getboolean('Shell Parameters', 'use_psiturk_ad_server')
            if use_psiturk_ad_server:
                ad_url = ''
                if use_psiturk_ad_server:
                    if self.sandbox:
                        ad_url_base = 'https://sandbox.ad.psiturk.org/view'
                    else:
                        ad_url_base = 'https://ad.psiturk.org/view'
                    ad_url = '{}/{}?assignmentId=debug{}&hitId=debug{}&workerId=debug{}'.format( 
                        ad_url_base, str(ad_id), str(self.random_id_generator()), str(self.random_id_generator()), str(self.random_id_generator()))

            else:
                options = { 
                    'base': self.config.get('Shell Parameters', 'ad_location'), 
                    'mode': mode,
                    'assignmentid': str(self.random_id_generator()),
                    'hitid': str(self.random_id_generator()),
                    'workerid': str(self.random_id_generator())
                  }
                ad_url = '{base}?mode={mode}&assignmentId=debug{assignmentid}&hitId=debug{hitid}&workerId=debug{workerid}'.format(**options)
            print('  Ad URL: {}'.format(ad_url) )
            print "Note: This url cannot be used to run your full psiTurk experiment.  It is only for testing your ad."

            # Print the Mturk Url
            mturk_url = ''
            if self.sandbox:
                mturk_url_base = 'https://workersandbox.mturk.com'
            else:
                mturk_url_base = 'https://worker.mturk.com'
            mturk_url = '{}/projects?filters%5Bsearch_term%5D={}'.format(
                mturk_url_base,
                urllib.quote_plus(
                    str(self.config.get('HIT Configuration', 'title'))))

            print('  MTurk URL: {}'.format(mturk_url) )
            print "Hint: In OSX, you can open a terminal link using cmd + click"
            if self.sandbox and use_psiturk_ad_server:
                print "Note: This sandboxed ad will expire from the server in 16 days."
        except Exception as e:
            print e
    
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   worker management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def worker_list(self, submitted, approved, rejected, chosen_hits, all_studies=False):
        try:
            status = None
            if submitted:
                status='Submitted'
            elif approved:
                status='Approved'
            elif rejected:
                status='Rejected'
                
            workers = self.amt_services_wrapper.get_workers(status, chosen_hits, all_studies=all_studies)
            if not len(workers):
                print "*** no workers match your request"
            else:
                worker_json = json.dumps(workers, indent=4,
                                 separators=(',', ': '))        
                if worker_json:
                    print worker_json
        
        except Exception as e:
            print colorize(repr(e), 'red')
    
    def worker_approve(self, all=False, chosen_hits=None, assignment_ids=None, all_studies=False, force=False):        
        
        if all_studies and not force:
            print 'option --all-studies must be used along with --force'
            return
        
        all_studies_msg = ' for the current study'
        if all_studies:
            all_studies_msg = ' from all studies'
        
        force_msg = ''
        if force:
            force_msg = " even if they're not found in the local psiturk db"
        
        if all:
            print "Approving all submissions{}{}...".format(all_studies_msg, force_msg)
        elif chosen_hits:
            print "Approving submissions for HITs {}{}{}".format(' '.join(chosen_hits), all_studies_msg, force_msg)
        else:
            print "Approving specified submissions{}{}...".format(all_studies_msg, force_msg)
            
        workers = self.amt_services_wrapper.get_workers("Submitted", chosen_hits, assignment_ids, all_studies=all_studies)
        if not workers:
            if chosen_hits:
                print "No submissions found for requested HIT ID(s). Are you in the right `mode`? Do you need to pass `--all-studies --force`?"
            elif assignment_ids:
                print "No submissions found for requested assignment ID(s). Are you in the right `mode`? Do you need to pass `--all-studies --force`?"
            else:
                print "No submissions found. Are you in the right `mode`? Do you need to pass `--all-studies`?"
            return        
        
        for worker in workers:
            try:
                result = self.amt_services_wrapper.approve_worker(worker, force=force)
                print result
            except Exception as e:
                print colorize(str(e), 'red')
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

        revproxy_url = False
        if self.config.has_option('Server Parameters','adserver_revproxy_host'):
            if self.config.has_option( 'Server Parameters', 'adserver_revproxy_port'):
                port = self.config.get( 'Server Parameters', 'adserver_revproxy_port')
            else:
                port = 80
            revproxy_url = "http://{}:{}/ad".format(self.config.get('Server Parameters', 
                                                                    'adserver_revproxy_host'),
                                                    port)

        if revproxy_url:
            base_url = revproxy_url
        elif 'OPENSHIFT_SECRET_TOKEN' in os.environ:
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
        ''' Tab-complete config command '''
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
        ''' Tab-complete server command '''
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

    _cached_web_services = None
    
    @property
    def web_services(self):
        if not self._cached_web_services:
            self._cached_web_services = PsiturkOrgServices(
                self.config.get('psiTurk Access', 'psiturk_access_key_id'),
                self.config.get('psiTurk Access', 'psiturk_secret_access_id')) 
            self.amt_services_wrapper.set_web_services(self._cached_web_services)
        return self._cached_web_services
    
    def __init__(self, config, server, sandbox, quiet=False):
        self.config = config
        self.quiet = quiet
        self.amt_services_wrapper = MTurkServicesWrapper(config=config, sandbox=sandbox)        
        
        self.sandbox = sandbox
        self.tunnel = TunnelServices()
        
        self.sandbox_hits = 0
        self.live_hits = 0
        
        if not quiet:
            self.update_hit_tally()
        PsiturkShell.__init__(self, config, server, quiet)

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
        self.update_hit_tally()
        if self.sandbox:
            print 'AMT worker site - ' + colorize('sandbox', 'bold') + ': ' \
            + str(self.sandbox_hits) + ' HITs available'
        else:
            print 'AMT worker site - ' + colorize('live', 'bold') + ': ' \
            + str(self.live_hits) + ' HITs available'

    def update_hit_tally(self):
        ''' Tally hits '''
        if not self.quiet:            
            num_hits = self.amt_services_wrapper.tally_hits()
            if self.sandbox:
                self.sandbox_hits = num_hits
            else:
                self.live_hits = num_hits

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   hit management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def do_amt_balance(self, _):
        ''' Get MTurk balance '''
        print self.amt_services_wrapper.amt_balance()

    def help_amt_balance(self):
        ''' Get help for amt_balance. '''
        with open(self.help_path + 'amt.txt', 'r') as help_text:
            print help_text.read()

    

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
        ''' Tab-complete db command '''
        return  [i for i in PsiturkNetworkShell.db_commands if \
                 i.startswith(text)]

    def help_db(self):
        ''' DB help '''
        with open(self.help_path + 'db.txt', 'r') as help_text:
            print help_text.read()

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
            self.set_sandbox(False)
            self.update_hit_tally()
            print 'Entered %s mode' % colorize('live', 'bold')
        else:
            self.set_sandbox(True)
            self.update_hit_tally()
            print 'Entered %s mode' % colorize('sandbox', 'bold')
        if restart_server:
            self.server_restart()
    def help_mode(self):
        ''' Help '''
        with open(self.help_path + 'mode.txt', 'r') as help_text:
            print help_text.read()
    
    def set_sandbox(self, is_sandbox):
        self.sandbox = is_sandbox
        self.amt_services_wrapper.set_sandbox(is_sandbox)
            
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
          hit list [--active | --reviewable] [--all-studies]
          hit help
        """

        if arg['create']:
            self.hit_create(arg['<numWorkers>'], arg['<reward>'],
                            arg['<duration>'])
            self.update_hit_tally()
        elif arg['extend']:
            self.amt_services_wrapper.hit_extend(arg['<HITid>'], arg['<number>'], arg['<minutes>'])
        elif arg['expire']:
            self.amt_services_wrapper.hit_expire(arg['--all'], arg['<HITid>'])
            self.update_hit_tally()
        elif arg['dispose']:
            self.amt_services_wrapper.hit_dispose(arg['--all'], arg['<HITid>'])
            self.update_hit_tally()
        elif arg['list']:
            self.hit_list(arg['--active'], arg['--reviewable'], arg['--all-studies'])
        else:
            self.help_hit()

    hit_commands = ('create', 'extend', 'expire', 'dispose', 'list')

    def complete_hit(self, text, line, begidx, endidx):
        ''' Tab-complete hit command. '''
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
          worker approve (--all | --hit <hit_id> ... | <assignment_id> ...) [--all-studies] [--force]
          worker reject (--hit <hit_id> | <assignment_id> ...)
          worker unreject (--hit <hit_id> | <assignment_id> ...)
          worker bonus  (--amount <amount> | --auto) (--hit <hit_id> | <assignment_id> ...)
          worker list [--submitted | --approved | --rejected] [(--hit <hit_id>)] [--all-studies]
          worker help
        """
        if arg['approve']:
            self.worker_approve(arg['--all'], arg['<hit_id>'], arg['<assignment_id>'], arg['--all-studies'], arg['--force'])
        elif arg['reject']:
            self.amt_services_wrapper.worker_reject(arg['<hit_id>'], arg['<assignment_id>'])
        elif arg['unreject']:
            self.amt_services_wrapper.worker_unreject(arg['<hit_id>'], arg['<assignment_id>'])
        elif arg['list']:
            self.worker_list(arg['--submitted'], arg['--approved'], arg['--rejected'], arg['<hit_id>'], arg['--all-studies'])
        elif arg['bonus']:
            self.amt_services_wrapper.worker_bonus(arg['<hit_id>'], arg['--auto'], arg['<amount>'], '',
                              arg['<assignment_id>'])
        else:
            self.help_worker()

    worker_commands = ('approve', 'reject', 'unreject', 'bonus', 'list', 'help')

    def complete_worker(self, text, line, begidx, endidx):
        ''' Tab-complete worker command. '''
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
        revproxy_url = False
        if self.config.has_option('Server Parameters','adserver_revproxy_host'):
            if self.config.has_option( 'Server Parameters', 'adserver_revproxy_port'):
                port = self.config.get( 'Server Parameters', 'adserver_revproxy_port')
            else:
                port = 80
            revproxy_url = "http://{}:{}/ad".format(self.config.get('Server Parameters', 
                                                                    'adserver_revproxy_host'),
                                                    port)

        if revproxy_url:
            base_url = revproxy_url
        elif 'OPENSHIFT_SECRET_TOKEN' in os.environ:
            base_url = "http://" + self.config.get('Server Parameters', 'host') + "/ad"
        else:
            if arg['--print-only']:
                my_ip = get_my_ip()
                base_url = "http://" + my_ip + ":" + \
                    self.config.get('Server Parameters', 'port') + "/ad"
            else:
                base_url = "http://" + self.config.get('Server Parameters',
                                                   'host') + \
                ":" + self.config.get('Server Parameters', 'port') + "/ad"


        launch_url = base_url + "?assignmentId=debug" + \
            str(self.random_id_generator()) \
            + "&hitId=debug" + str(self.random_id_generator()) \
            + "&workerId=debug" + str(self.random_id_generator() \
            + "&mode=debug")

        if arg['--print-only']:
            print("Here's your randomized debug link, feel free to request " \
                  "another:\n\t" + launch_url)

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

    def cmdloop(self):
        while True:
            stop = Cmd._cmdloop(self) 
            if not stop:
                self.intro = ''
                self.color_prompt()
                print "^C"
            else:
                break

def run(cabinmode=False, script=None, execute=None, quiet=False):
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
        shell = PsiturkNetworkShell(
            config, server, \
            config.getboolean('Shell Parameters', 'launch_in_sandbox_mode'), 
            quiet=quiet)

    if script:
        with open(script, 'r') as temp_file:
            for line in temp_file:
                shell.onecmd_plus_hooks(line)
    elif execute:
        shell.onecmd_plus_hooks(execute)
    else:
        shell.cmdloop()

