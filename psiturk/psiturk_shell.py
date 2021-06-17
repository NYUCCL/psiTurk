# coding: utf-8
""" PsiturkShell is a commandline interface for psiTurk, which provides
functionality for maintaining the experiment server and interacting with
Mechanical Turk."""
from __future__ import generator_stop
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus
import urllib3.contrib.pyopenssl
from psiturk.utils import *
from psiturk.models import Participant
from psiturk.db import migrate_db
from psiturk import experiment_server_controller as control
from psiturk.psiturk_config import PsiturkConfig
from psiturk.version import version_number
from psiturk.amt_services_wrapper import MTurkServicesWrapper
from .psiturk_exceptions import *
import webbrowser
from docopt import docopt, DocoptExit
from cmd2 import Cmd
from fuzzywuzzy import process
import certifi
import random
import string
import os
import json
import time
import re
import subprocess
import sys
from functools import wraps
import shlex
urllib3.contrib.pyopenssl.inject_into_urllib3()
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where())


try:
    # prefer gnureadline if user has installed it
    import gnureadline as readline
except ImportError:
    try:
        # next pyreadline if user has installed it (windows)
        import pyreadline as readline
    except ImportError:
        import readline


def docopt_cmd(func):
    """
    This decorator is used to simplify the try/except block and pass the result
    of the docopt parsing to the called action.
    """
    @wraps(func)
    def helper_fn(self, arg):
        """helper function for docopt"""
        try:
            arg = shlex.split(arg)
            opt = docopt(helper_fn.__doc__, arg)
        except DocoptExit as exception:
            # The DocoptExit is thrown when the args do not match.
            # We print a message to the user and the usage block.
            self.poutput('Invalid Command!')
            self.poutput(exception)
            return
        except SystemExit:
            # The SystemExit exception prints the usage for --help
            # We do not need to do the print here.
            return
        return func(self, opt)

    return helper_fn


class PsiturkNetworkShell(Cmd, object):
    """ Creates the Psiturk Network Shell interfrace """

    _cached_amt_services_wrapper = None

    @property
    def amt_services_wrapper(self):
        if not self._cached_amt_services_wrapper:
            try:
                _wrapper = MTurkServicesWrapper(
                    config=self.config, mode=self.mode)
                self._cached_amt_services_wrapper = _wrapper
            except AmtServicesException as e:
                still_can_do = '\n'.join([
                    '',
                    'You can still use the psiturk server by running non-AWS commands such as:',
                    '- `psiturk server <subcommand>`',
                    '- `psiturk server on`',
                    '- `psiturk server off`',
                    '- `psiturk debug -p`'])
                message = e.message
                if not self.quiet:
                    message = '{}{}'.format(message, still_can_do)
                self.perror(message)
                sys.exit()
            except PsiturkException as e:
                self.poutput(e)

        return self._cached_amt_services_wrapper

    def postcmd(self, *args):
        if not self.quiet:
            self.prompt = self.color_prompt()
        return Cmd.postcmd(self, *args)

    def complete(self, text, state):
        """ Add space after a completion, makes tab completion with
        multi-word commands cleaner. """
        return Cmd.complete(self, text, state) + ' '

    def default(self, statement):
        cmd = statement.command

        ''' Collect incorrect and mistyped commands '''
        choices = ["help", "mode", "psiturk_status", "server", "shortcuts",
                   "worker", "db", "edit", "open", "config", "show",
                   "debug", "setup_example", "status", "amt_balance",
                   "download_datafiles", "exit", "hit", "load", "quit", "save",
                   "shell", "version"]
        self.poutput("{} is not a psiTurk command. See 'help'.".format(cmd))
        guess = process.extractOne(cmd, choices)
        if guess and guess[1] > 50:
            self.poutput("Did you mean this?\n\t{}".format(guess[0]))

    def __init__(self, config, server, mode='sandbox', quiet=False):
        persistent_history_file = config.get('Shell Parameters',
                                             'persistent_history_file')

        # Prevents running of commands by abbreviation
        self.abbrev = False
        self.debug = True
        self.help_path = os.path.join(os.path.dirname(__file__), "shell_help/")
        self.psiturk_header = 'psiTurk command help:'
        self.super_header = 'basic CMD command help:'

        self.config = config
        self.server = server

        self.mode = mode
        self.sandbox_hits = 0
        self.live_hits = 0

        Cmd.__init__(self, persistent_history_file=persistent_history_file)
        self.quiet = quiet
        self.feedback_to_output = True

        if not self.quiet and not self.amt_services_wrapper:
            sys.exit()

        if not self.quiet:
            self.maybe_update_hit_tally()
            self.prompt = self.color_prompt()
            self.intro = self.get_intro_prompt()
        else:
            self.intro = ''

    def server_off(self):
        if (self.server.is_server_running() == 'yes' or
                self.server.is_server_running() == 'maybe'):
            self.server.shutdown()
            self.poutput('Please wait. This could take a few seconds.')
            while self.server.is_server_running() != 'no':
                time.sleep(0.5)
        else:
            self.poutput('Your server is already off.')

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   basic command line functions
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.

    def get_intro_prompt(self):
        """ Overloads intro prompt with network-aware version if you can reach
        psiTurk.org, request system status message. """
        status_msg_url = 'https://raw.githubusercontent.com/NYUCCL/psiTurk/master/status_msg.txt'
        r = http.request('GET', status_msg_url)
        status_message = r.data.decode('utf-8')

        return status_message + colorize('psiTurk version ' + version_number +
                                         '\nType "help" for more information.',
                                         'green', False)

    def color_prompt(self):
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
        mode_str = 'sdbx' if self.mode == 'sandbox' else 'live'
        prompt += ' mode:' + colorize(mode_str, 'bold')
        hit_count = self.sandbox_hits if self.mode == 'sandbox' else self.live_hits
        prompt += ' #HITs:' + str(hit_count)
        prompt += ']$ '
        return prompt

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   basic command line functions
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.

    def do_version(self, _):
        """ Print version number """
        self.poutput('psiTurk version ' + version_number)

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
            self.help_config()

    def complete_config(self, text, line, begidx, endidx):
        """ Tab-complete config command """
        config_commands = ('print', 'reload', 'help')
        return [i for i in config_commands if i.startswith(text)]

    def help_config(self):
        """ Help for config """
        with open(self.help_path + 'config.txt', 'r') as help_text:
            self.poutput(help_text.read())

    def print_config(self, _):
        """ Print configuration. """
        for section in self.config.sections():
            self.poutput('[%s]' % section)
            items = dict(self.config.items(section))
            for k in items:
                self.poutput("%(a)s=%(b)s" % {'a': k, 'b': items[k]})
            print('')

    def reload_config(self, _):
        """ Reload config. """
        # TODO: I don't think that this follows all the way through!
        restart_server = False
        if (self.server.is_server_running() == 'yes' or
                self.server.is_server_running() == 'maybe'):
            user_input = input("Reloading configuration requires the server "
                               "to restart. Really reload? y or n: ")
            if user_input != 'y':
                return
            restart_server = True
        self.config.load_config()
        if restart_server:
            self.server_restart()

    def do_setup_example(self, _):
        """ Load psiTurk demo."""
        from . import setup_example as se
        se.setup_example()

    def help_debug(self):
        """ Help for debug """
        with open(self.help_path + 'debug.txt', 'r') as help_text:
            self.poutput(help_text.read())

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
        """ Execute on EOF """
        return self.do_quit(arg)

    def do_exit(self, arg):
        """ Execute on exit """
        return self.do_quit(arg)

    def do_quit(self, _):
        """ Execute on quit """
        if (self.server.is_server_running() == 'yes' or
                self.server.is_server_running() == 'maybe'):
            user_input = input("Quitting shell will shut down experiment "
                               "server.  Really quit? y or n: ")
            if user_input == 'y':
                self.server_off()
            else:
                return
        return True

    def do_psiturk_status(self, _):
        """ Print psiTurk news """
        self.poutput(self.get_intro_prompt())

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   Local SQL database commands
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.

    def do_download_datafiles(self, _):
        """ Download datafiles. """
        contents = {"trialdata": lambda p: p.get_trial_data(), "eventdata":
                    lambda p: p.get_event_data(), "questiondata": lambda p:
                    p.get_question_data()}
        query = Participant.query.all()
        for k in contents:
            ret = "".join([contents[k](p) for p in query])
            temp_file = open(k + '.csv', 'w')
            temp_file.write(ret)
            temp_file.close()

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   hit management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def hit_list(self, active_hits, reviewable_hits, all_studies):
        """ List hits. """
        if active_hits:
            hits_data = (self.amt_services_wrapper.get_active_hits(
                all_studies)).data
        elif reviewable_hits:
            hits_data = (self.amt_services_wrapper.get_reviewable_hits(
                all_studies)).data
        else:
            hits_data = (self.amt_services_wrapper.get_all_hits(
                all_studies)).data
        if not hits_data:
            self.poutput('*** no hits retrieved')
        else:
            for hit in hits_data:
                self.poutput(hit)

    def _estimate_expenses(self, num_workers, reward):
        """ Returns tuple describing expenses:
        amount paid to workers
        amount paid to amazon"""

        # fee structure changed 07.22.15:
        # 20% for HITS with < 10 assignments
        # 40% for HITS with >= 10 assignments
        commission = 0.2
        if float(num_workers) >= 10:
            commission = 0.4
        work = float(num_workers) * float(reward)
        fee = work * commission
        return work, fee, work + fee

    def _confirm_dialog(self, prompt):
        """ Prompts for a 'yes' or 'no' to given prompt. """
        response = input(prompt).strip().lower()
        valid = {'y': True, 'ye': True, 'yes': True, 'n': False, 'no': False}
        while True:
            try:
                return valid[response]
            except KeyError:
                response = input("Please respond 'y' or 'n': ").strip().lower()

    def hit_create(self, num_workers, reward, duration,
                   require_qualification_ids=None, block_qualification_ids=None, **kwargs):

        # backwards compatibility
        if 'whitelist_qualification_ids' in kwargs and not require_qualification_ids:
            require_qualification_ids = kwargs['whitelist_qualification_ids']
        if 'blacklist_qualification_ids' in kwargs and not block_qualification_ids:
            block_qualification_ids = kwargs['blacklist_qualification_ids']

        if require_qualification_ids is None:
            require_qualification_ids = []
        if block_qualification_ids is None:
            block_qualification_ids = []

        # Argument retrieval and validation
        if num_workers is None:
            num_workers = input('number of participants? ').strip()
        try:
            num_workers = int(num_workers)
        except ValueError:
            self.poutput('*** number of participants must be a whole number')
            return
        if num_workers <= 0:
            self.poutput('*** number of participants must be greater than 0')
            return

        if reward is None:
            reward = input('reward per HIT? ').strip()
        p = re.compile(r'^\d*\.\d\d$')
        m = p.match(reward)
        if m is None:
            self.poutput('*** reward must have format [dollars].[cents]')
            return
        try:
            reward = float(reward)
        except (ValueError, OverflowError):
            self.poutput('*** reward must be in format [dollars].[cents]')
            return

        if duration is None:
            duration = input(
                'duration of hit (in hours, it can be decimals)? ').strip()
        try:
            duration = float(duration)
        except ValueError:
            self.poutput('*** duration must a number')
            return
        if duration <= 0:
            self.poutput('*** duration must be greater than 0')
            return

        _, fee, total = self._estimate_expenses(num_workers, reward)

        if not self.quiet:
            dialog_query = '\n'.join(['*****************************',
                                      '    Max workers: %d' % num_workers,
                                      '    Reward: $%.2f' % reward,
                                      '    Duration: %s hours' % duration,
                                      '    Fee: $%.2f' % fee,
                                      '    ________________________',
                                      '    Total: $%.2f' % total,
                                      'Create %s HIT [y/n]? ' % colorize(self.mode, 'bold')])
            if not self._confirm_dialog(dialog_query):
                self.poutput('*** Cancelling HIT creation.')
                return

        try:
            create_hit_response = self.amt_services_wrapper.create_hit(num_workers=num_workers, reward=reward,
                                                                       duration=duration,
                                                                       require_qualification_ids=require_qualification_ids,
                                                                       block_qualification_ids=block_qualification_ids)

            if create_hit_response.status != 'success':
                self.poutput('Error during hit creation.')
                print(create_hit_response)
                return
            else:
                self.maybe_update_hit_tally()

            hit_id = create_hit_response.data['hit_id']

            # TODO: "with qualification type ids..."
            self.poutput('\n'.join(['*****************************',
                                    '  Created %s HIT' % colorize(
                                        self.mode, 'bold'),
                                    '    HITid: %s' % str(hit_id),
                                    '    Max workers: %d' % num_workers,
                                    '    Reward: $%.2f' % reward,
                                    '    Duration: %s hours' % duration,
                                    '    Fee: $%.2f' % fee,
                                    '    ________________________',
                                    '    Total: $%.2f' % total]))

            # Print the Ad Url
            base = self.config.get_ad_url()
            assignmentid = str(self.random_id_generator())
            hitid = str(self.random_id_generator())
            workerid = str(self.random_id_generator())

            ad_url = f'{base}?mode={self.mode}&assignmentId=debug{assignmentid}&hitId=debug{hitid}&workerId=debug{workerid}'
            self.poutput(f'  Ad URL: {ad_url}')
            self.poutput(
                "Note: This url cannot be used to run your full psiTurk experiment."
                "It is only for testing your ad."
            )

            # Print the Mturk Url
            mturk_url = ''
            if self.mode == 'sandbox':
                mturk_url_base = 'https://workersandbox.mturk.com'
            else:  # self.mode == 'live':
                mturk_url_base = 'https://worker.mturk.com'
            title = quote_plus(
                str(self.config.get('HIT Configuration', 'title', raw=True)))
            mturk_url = f'{mturk_url_base}/projects?filters%5Bsearch_term%5D={title}'

            self.poutput(f'  MTurk URL: {mturk_url}')
            self.poutput(
                "Hint: In OSX, you can open a terminal link using cmd + click")
        except Exception as e:
            self.poutput(e)

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   worker management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def worker_list(self, chosen_hits=None, status=None, all_studies=False):
        try:
            workers = (self.amt_services_wrapper.get_assignments(
                hit_ids=chosen_hits, assignment_status=status, all_studies=all_studies)).data['assignments']
            if not len(workers):
                self.poutput("*** no workers match your request")
            else:
                worker_json = json.dumps(workers, indent=4,
                                         separators=(',', ': '), default=str)
                if worker_json:
                    self.poutput(worker_json)

        except Exception as e:
            self.poutput(colorize(repr(e), 'red'))

    # TODO: consider renaming all to all_hits; shadows built-in
    def worker_approve(self, all=False, chosen_hits=None, assignment_ids=None, all_studies=False, force=False):

        if all_studies and not force:
            self.poutput(
                'option --all-studies must be used along with --force')
            return

        all_studies_msg = ' for the current study'
        if all_studies:
            all_studies_msg = ' from all studies'

        force_msg = ''
        if force:
            force_msg = " even if they're not found in the local psiturk db"

        if all:
            self.poutput("Approving all submissions{}{}...".format(
                all_studies_msg, force_msg))
            result = self.amt_services_wrapper.approve_all_assignments(
                all_studies=all_studies)
            if not result.success:
                return self.poutput(result)
            for _result in result.data['results']:
                self.poutput(_result)
        elif chosen_hits:
            self.poutput("Approving submissions for HITs {}{}{}".format(
                ' '.join(chosen_hits), all_studies_msg, force_msg))
            for hit_id in chosen_hits:
                result = self.amt_services_wrapper.approve_assignments_for_hit(
                    hit_id, all_studies=all_studies)
                if not result.success:
                    return self.poutput(result)
                for _result in result.data['results']:
                    self.poutput(_result)
        else:
            self.poutput("Approving specified submissions{}{}...".format(
                all_studies_msg, force_msg))
            for assignment_id in assignment_ids:
                result = self.amt_services_wrapper.approve_assignment_by_assignment_id(
                    assignment_id, all_studies=all_studies)
                self.poutput(result)

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   server management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.

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

    def complete_server(self, text, line, begidx, endidx):
        """ Tab-complete server command """
        server_commands = ('on', 'off', 'restart', 'log', 'help')
        return [i for i in server_commands if i.startswith(text)]

    def help_server(self):
        """ Help for server """
        with open(self.help_path + 'server.txt', 'r') as help_text:
            self.poutput(help_text.read())

    def server_on(self):
        """ Start experiment server """
        self.server.startup()
        time.sleep(0.5)

    def server_restart(self):
        """ Restart experiment server """
        self.server_off()
        self.server_on()

    def server_log(self):
        """ Launch log """
        logfilename = self.config.get('Server Parameters', 'logfile')
        if sys.platform == "darwin":
            args = ["open", "-a", "Console.app", logfilename]
        else:
            args = ["xterm", "-e", "'tail -f %s'" % logfilename]
        subprocess.Popen(args, close_fds=True)
        self.poutput("Log program launching...")

    def do_status(self, arg):  # overloads do_status with AMT info
        """ Notify user of server status. """
        server_status = self.server.is_server_running()
        if server_status == 'yes':
            self.poutput('Server: ' + colorize('currently online', 'green'))
        elif server_status == 'no':
            self.poutput('Server: ' + colorize('currently offline', 'red'))
        elif server_status == 'maybe':
            self.poutput('Server: ' + colorize('status unknown', 'yellow'))
        elif server_status == 'blocked':
            self.poutput('Server: ' + colorize('blocked', 'red'))

        # server_status = self.server.is_server_running()  # Not used
        self.update_hit_tally()
        hit_count = self.sandbox_hits if self.mode == 'sandbox' else self.live_hits
        self.poutput('AMT worker site - ' + colorize(self.mode, 'bold') + ': '
                     + str(hit_count) + ' HITs available')

    def maybe_update_hit_tally(self):
        if not self.quiet:
            self.update_hit_tally()

    def update_hit_tally(self):
        """ Tally hits """
        num_hits = (self.amt_services_wrapper.tally_hits()).data['hit_tally']
        if self.mode == 'sandbox':
            self.sandbox_hits = num_hits
        else:
            self.live_hits = num_hits

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   hit management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    def do_amt_balance(self, _):
        """ Get MTurk balance """
        balance = (self.amt_services_wrapper.amt_balance()).data
        self.poutput(balance)

    def help_amt_balance(self):
        """ Get help for amt_balance. """
        with open(self.help_path + 'amt.txt', 'r') as help_text:
            self.poutput(help_text.read())

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   qualification type management
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    @docopt_cmd
    def do_qualifications(self, arg):
        """
        Usage: qualifications list
        """
        if arg['list']:
            self.do_list_qualifications()

    def do_list_qualifications(self):
        result = (self.amt_services_wrapper.list_qualification_types(MustBeOwnedByCaller=True))
        if not result.success:
            return self.poutput(result)
        qualification_types = result.data['qualification_types']
        only_these_keys = ['Name', 'Description', 'QualificationTypeId']
        q_type_projection = [{key: q_type[key] for key in only_these_keys} for q_type in qualification_types if q_type['QualificationTypeStatus'] == 'Active']
        if not q_type_projection:
            self.poutput('No custom qualifications found.')
        for q_type in q_type_projection:
            self.poutput(q_type)

    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    #   Basic shell commands
    # +-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.+-+.
    @docopt_cmd
    def do_mode(self, arg):
        """
        Usage: mode
               mode <which>
        """
        if arg['<which>'] is None:
            # then toggle the `mode`
            mode = 'live' if self.mode == 'sandbox' else 'sandbox'
        else:
            # then accept what's given
            mode = arg['<which>']
        self.set_mode(mode)

    def help_mode(self):
        """ Help """
        with open(self.help_path + 'mode.txt', 'r') as help_text:
            self.poutput(help_text.read())

    def set_mode(self, mode):
        known_modes = ['sandbox', 'live']
        if mode not in known_modes:
            self.poutput('mode {} is not recognized.'.format(mode))
            return

        current_mode = self.mode
        if mode == current_mode:
            self.poutput('mode is already {}'.format(mode))
            return
        else:
            restart_server = False
            if self.server.is_server_running() == 'yes' or self.server.is_server_running() == 'maybe':
                if not self.quiet:
                    r = input("Switching modes requires the server to restart. Really "
                              "switch modes? y or n: ")
                    if r != 'y':
                        return
                    else:
                        restart_server = True

            self.mode = mode
            self.amt_services_wrapper.set_mode(mode)

            self.update_hit_tally()
            self.poutput('Entered %s mode' % colorize(mode, 'bold'))
            if restart_server:
                self.server_restart()

    @docopt_cmd
    def do_hit(self, arg):
        """
        Usage:
          hit create [<num_workers> <reward> <duration>] [--require-qualification-id <require_qualification_id>]... [--block-qualification-id <block_qualification_id>]...
          hit extend <HITid> [(--assignments <number>)] [(--expiration <minutes>)]
          hit expire (--all | <HITid> ...)
          hit delete (--all | <HITid> ...) [--all-studies]
          hit list [--active | --reviewable] [--all-studies]
          hit help
        """

        all_studies = arg['--all-studies']

        if arg['create']:
            self.hit_create(arg['<num_workers>'], arg['<reward>'], arg['<duration>'],
                            require_qualification_ids=arg['<require_qualification_id>'],
                            block_qualification_ids=arg['<block_qualification_id>'])
        elif arg['extend']:
            result = self.amt_services_wrapper.extend_hit(
                arg['<HITid>'][0], assignments=arg['<number>'], minutes=arg['<minutes>'])
            self.poutput(result)
        elif arg['expire']:
            did_something = False
            if arg['--all']:
                result = self.amt_services_wrapper.expire_all_hits()
                if not result.success:
                    return self.poutput(result)
                for _result in result.data['results']:
                    self.poutput(_result)
                did_something = True
            elif arg['<HITid>']:
                did_something = True
                for hit_id in arg['<HITid>']:
                    result = self.amt_services_wrapper.expire_hit(hit_id)
                    self.poutput(result)
            if did_something:
                self.update_hit_tally()
        elif arg['delete']:
            did_something = False
            if arg['--all']:
                result = self.amt_services_wrapper.delete_all_hits(all_studies=all_studies)
                if not result.success:
                    return self.poutput(result)
                results = result.data['results']
                for _result in results:
                    self.poutput(_result)
                did_something = True
            elif arg['<HITid>']:
                did_something = True
                for hit_id in arg['<HITid>']:
                    result = self.amt_services_wrapper.delete_hit(hit_id)
                    self.poutput(result)
            if did_something:
                self.update_hit_tally()
        elif arg['list']:
            self.hit_list(arg['--active'], arg['--reviewable'],
                          all_studies)
        else:
            self.help_hit()

    hit_commands = ('create', 'extend', 'expire', 'delete', 'list')

    def complete_hit(self, text, line, begidx, endidx):
        """ Tab-complete hit command. """
        return [i for i in PsiturkNetworkShell.hit_commands if
                i.startswith(text)]

    def help_hit(self):
        """ HIT help """
        with open(self.help_path + 'hit.txt', 'r') as help_text:
            self.poutput(help_text.read())

    @docopt_cmd
    def do_worker(self, arg):
        """
        Usage:
          worker approve (--all | --hit <hit_id> ... | <assignment_id> ...) [--all-studies] [--force]
          worker reject (--hit <hit_id> | <assignment_id> ...) [--all-studies]
          worker unreject (--hit <hit_id> | <assignment_id> ...) [--all-studies]
          worker bonus (--amount <amount> | --auto) [--reason=<reason>] (--all | --hit <hit_id> | <assignment_id> ...) [--override-bonused-status] [--all-studies]
          worker list [--submitted | --approved | --rejected] [(--hit <hit_id> ...)] [--all-studies]
          worker help

        Options:
          --reason REASON    the reason...
        """
        all_studies = arg['--all-studies']
        if arg['approve']:
            self.worker_approve(arg['--all'], arg['<hit_id>'],
                                arg['<assignment_id>'], all_studies, arg['--force'])
        elif arg['reject']:
            results = None
            if arg['<hit_id>']:
                result = self.amt_services_wrapper.reject_assignments_for_hit(
                    arg['<hit_id>'], all_studies=all_studies)
                if not result.success:
                    return self.poutput(result)
                results = result.data['results']
            elif arg['<assignment_id>']:
                result = self.amt_services_wrapper.reject_assignments(
                    arg['<assignment_id>'], all_studies=all_studies)
                if not result.success:
                    return self.poutput(result)
                results = result.data['results']
            if results:
                for _result in results:
                    self.poutput(_result)

        elif arg['unreject']:
            if arg['<hit_id>']:
                self.amt_services_wrapper.unreject_assignments_for_hit(
                    arg['<hit_id>'], all_studies=all_studies)
            elif arg['<assignment_id>']:
                for assignment_id in arg['<assignment_id>']:
                    result = self.amt_services_wrapper.unreject_assignment(
                        assignment_id, all_studies=all_studies)
                    self.poutput(result)

        elif arg['list']:
            status = None
            if arg['--submitted']:
                status = 'Submitted'

            elif arg['--approved']:
                status = 'Approved'

            elif arg['--rejected']:
                status = 'Rejected'

            self.worker_list(
                status=status, chosen_hits=arg['<hit_id>'], all_studies=all_studies)

        elif arg['bonus']:
            reason = arg['--reason']
            if isinstance(reason, list):
                reason = ' '.join(reason)
            if not reason:
                if self.config.get('Shell Parameters', 'bonus_message'):
                    reason = self.config.get(
                        'Shell Parameters', 'bonus_message')
                    self.poutput(
                        f'Using bonus `reason` from config file: "{reason}"')
                while not reason:
                    user_input = input("Type the reason for the bonus. Workers "
                                       "will see this message: ")
                    reason = user_input

            override_bonused_status = arg['--override-bonused-status']

            if arg['--auto']:
                amount = 'auto'
            else:
                amount = float(arg['<amount>'])

            results = None
            if arg['<hit_id>']:
                result = (self.amt_services_wrapper.bonus_assignments_for_hit(
                    arg['<hit_id>'][0], amount, reason, all_studies=all_studies, override_bonused_status=override_bonused_status))
                if not result.success:
                    return self.poutput(result)
                results = result.data['results']

            elif arg['--all']:
                result = self.amt_services_wrapper.bonus_all_local_assignments(
                    amount, reason, override_bonused_status)
                if not result.success:
                    return self.poutput(result)
                results = result.data['results']

            elif arg['<assignment_id>']:
                results = [
                    self.amt_services_wrapper.bonus_assignment_for_assignment_id(
                        assignment_id, amount, reason, override_bonused_status) for assignment_id in arg['<assignment_id>']]

            if results:
                [self.poutput(_result) for _result in results]
        else:
            self.help_worker()

    worker_commands = ('approve', 'reject', 'unreject',
                       'bonus', 'list', 'help')

    def complete_worker(self, text, line, begidx, endidx):
        """ Tab-complete worker command. """
        return [i for i in PsiturkNetworkShell.worker_commands if
                i.startswith(text)]

    def help_worker(self):
        """ Help for worker command. """
        with open(self.help_path + 'worker.txt', 'r') as help_text:
            self.poutput(help_text.read())

    @docopt_cmd
    def do_debug(self, arg):
        """
        Usage: debug [options]

        -p, --print-only        just provides the URL, doesn't attempt to
                                launch browser
        """
        try:
            base_url = self.config.get_ad_url()
            self.pfeedback('generating debug url using `ad_url` config var')
        except PsiturkException:
            self.pfeedback('`ad_url_*` config vars not set; using Server '
                           'Parameters host and port vars.')
            host = self.config.get('Server Parameters', 'host')
            port = self.config.get('Server Parameters', 'port')
            base_url = f"http://{host}:{port}/ad"

        launch_url = (f'{base_url}?'
                      f'assignmentId=debug{self.random_id_generator()}'
                      f'&hitId=debug{self.random_id_generator()}'
                      f'&workerId=debug{self.random_id_generator()}'
                      f'&mode=debug')

        if arg['--print-only']:
            self.poutput(launch_url)
        else:
            self.poutput("Launching browser pointed at your randomized debug link, "
                         "\n\t" + launch_url)
            webbrowser.open(launch_url, new=1, autoraise=True)

    def random_id_generator(self, size=6, chars=string.ascii_uppercase +
                            string.digits):
        """ Generate random id numbers """
        return ''.join(random.choice(chars) for x in range(size))

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
            self.print_topics(self.misc_header, list(
                help_struct.keys()), 15, 80)
            self.print_topics(self.super_header, cmds_super, 15, 80)

    @docopt_cmd
    def do_migrate(self, arg):
        """
        Usage:
          migrate db
        """

        # Right now, the only thing it does is copies all hitids from
        # the assignments table into the amt_hits table
        result = migrate_db()
        self.poutput(result['message'])

    migrate_commands = ('db')

    def complete_migrate(self, text, line, begidx, endidx):
        """ Tab-complete migrate command """
        return [i for i in migrate_commands if i.startswith(text)]

def run(script=None, execute=None, testfile=None, quiet=False):
    try:
        using_libedit = 'libedit' in readline.__doc__
        if using_libedit:
            print('\n'.join([
                'libedit version of readline detected.',
                'readline will not be well behaved, which may cause all sorts',
                'of problems for the psiTurk shell. We highly recommend installing',
                'the gnu version of readline by running "sudo pip install gnureadline".',
                'Note: "pip install readline" will NOT work because of how the OSX',
                'pythonpath is structured.']))
    except TypeError:
        pass  # pyreadline doesn't have anything for __doc__
    # Drop arguments which were already processed in command_line.py
    sys.argv = [sys.argv[0]]
    config = PsiturkConfig()
    config.load_config()
    server = control.ExperimentServerController(config)
    shell = PsiturkNetworkShell(
        config, server,
        mode=config.get('Shell Parameters', 'launch_in_mode'),
        quiet=quiet)

    if script:
        shell.runcmds_plus_hooks([f'load {script}'])
    elif execute:
        shell.runcmds_plus_hooks([execute])
    else:
        shell.cmdloop()
