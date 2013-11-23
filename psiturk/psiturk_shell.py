"""
Usage:
    psiturk_shell
    psiturk_shell setup_example
"""
import sys
import re
import time
import json

from cmd2 import Cmd
from docopt import docopt, DocoptExit
import readline

from amt_services import MTurkServices
from version import version_number
from psiturk_config import PsiturkConfig
import experiment_server_controller as control
# import dashboard_server as dbs


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
class Psiturk_Shell(Cmd):
    def __init__(self, config, services, server):
        Cmd.__init__(self)
        self.config = config
        self.server = server
        self.services = services
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

    def onecmd_plus_hooks(self, line):
        if not line:
            return self.emptyline()
        return Cmd.onecmd_plus_hooks(self, line)

    def postcmd(self, stop, line):
        self.color_prompt()
        return Cmd.postcmd(self, stop, line)

    def emptyline(self):
        self.color_prompt()

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
            self.tally_hits()
            print 'Entered ' + colorize('live', 'bold') + ' mode'
        else:
            self.sandbox = True
            self.config.set('HIT Configuration', 'using_sandbox', True)
            self.tally_hits()
            print 'Entered ' + colorize('sandbox', 'bold') + ' mode'


    #@docopt_cmd
    # def do_dashboard(self, arg):
    #     """
    #     Usage: dashboard [options]
    #
    #     -i <address>, --ip <address>    IP to run dashboard on. [default: localhost].
    #     -p <num>, --port <num>          Port to run dashboard on. [default: 22361].
    #     """
    #     arg['--port'] = int(arg['--port'])
    #     dbs.launch(ip=arg['--ip'], port=arg['--port'])
    def do_version(self, arg):
        print 'psiTurk version ' + version_number

    def do_print_config(self, arg):
        f = open('config.txt', 'r')
        for line in f:
            sys.stdout.write(line)

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

    def tally_hits(self):
        hits = self.services.get_active_hits()
        if hits:
            if self.sandbox:
                self.sandboxHITs = len(hits)
            else:
                self.liveHITs = len(hits)

    @docopt_cmd
    def do_create_hit(self, arg):
        """
        Usage: create_hit
               create_hit <numWorkers> <reward> <duration>
        """
        interactive = False
        if arg['<numWorkers>'] is None:
            interactive = True
            arg['<numWorkers>'] = raw_input('number of participants? ')
        try:
            int(arg['<numWorkers>'])
        except ValueError:

            print '*** number of participants must be a whole number'
            return
        if int(arg['<numWorkers>']) <= 0:
            print '*** number of participants must be greater than 0'
            return
        if interactive:
            arg['<reward>'] = raw_input('reward per HIT? ')
        p = re.compile('\d*.\d\d')
        m = p.match(arg['<reward>'])
        if m is None:
            print '*** reward must have format [dollars].[cents]'
            return
        if interactive:
            arg['<duration>'] = raw_input('duration of hit (in hours)? ')
        try:
            int(arg['<duration>'])
        except ValueError:
            print '*** duration must be a whole number'
            return
        if int(arg['<duration>']) <= 0:
            print '*** duration must be greater than 0'
            return
        self.config.set('HIT Configuration', 'max_assignments',
                        arg['<numWorkers>'])
        self.config.set('HIT Configuration', 'reward', arg['<reward>'])
        self.config.set('HIT Configuration', 'duration', arg['<duration>'])
        self.services.create_hit()
        if self.sandbox:
            self.sandboxHITs += 1
        else:
            self.liveHITs += 1
        # print results
        total = float(arg['<numWorkers>']) * float(arg['<reward>'])
        fee = total / 10
        total = total + fee
        location = ''
        if self.sandbox:
            location = 'sandbox'
        else:
            location = 'live'
        print '*****************************'
        print '  Creating %s HIT' % colorize(location, 'bold')
        print '    Max workers: ' + arg['<numWorkers>']
        print '    Reward: $' + arg['<reward>']
        print '    Duration: ' + arg['<duration>'] + ' hours'
        print '    Fee: $%.2f' % fee
        print '    ________________________'
        print '    Total: $%.2f' % total

    def do_setup_example(self, arg):
        import setup_example as se
        se.setup_example()

    def do_start_server(self, arg):
        self.server.startup()
        while self.server.is_server_running() != 'yes':
            time.sleep(0.5)

    def do_stop_server(self, arg):
        self.server.shutdown()
        print 'Please wait. This could take a few seconds.'
        while self.server.is_server_running() != 'no':
            time.sleep(0.5)

    # This doesn't work with the server's slow shutdown right now.
    def do_restart_server(self, arg):
        self.do_stop_server('')
        self.do_start_server('')

    def do_list_workers(self, arg):
        workers = self.services.get_workers()
        if not workers:
            print colorize('failed to get workers', 'red')
        else:
            print json.dumps(self.services.get_workers(), indent=4,
                             separators=(',', ': '))

    @docopt_cmd
    def do_approve_worker(self, arg):
        """
        Usage: approve_worker (--all | <assignment_id> ...)

        -a, --all        approve all completed workers

        """
        if arg['--all']:
            workers = self.services.get_workers()
            arg['<assignment_id>'] = [worker['assignmentId'] for worker in workers]
        for assignmentID in arg['<assignment_id>']:
            success = self.services.approve_worker(assignmentID)
            if success:
                print 'approved', assignmentID
            else:
                print '*** failed to approve', assignmentID

    @docopt_cmd
    def do_reject_worker(self, arg):
        """
        Usage: reject_worker (--all | <assignment_id> ...)

        -a, --all           reject all completed workers
        """
        if arg['--all']:
            workers = self.services.get_workers()
            arg['<assignment_it>'] = [worker['assignmentId'] for worker in workers]
        for assignmentID in arg['<assignment_id>']:
            success = self.services.reject_worker(assignmentID)
            if success:
                print 'rejected', assignmentID
            else:
                print '*** failed to reject', assignmentID

    def do_check_balance(self, arg):
        print self.services.check_balance()

    def do_list_active_hits(self, arg):
        hits_data = self.services.get_active_hits()
        if not hits_data:
            print '*** no active hits retrieved'
        else:
            print json.dumps(hits_data, indent=4, separators=(',', ': '))

    @docopt_cmd
    def do_extend_hit(self, arg):
        """
        Usage: extend_hit <HITid> [options]

        -a <number>, --assignments <number>    Increase number of assignments on HIT
        -e <time>, --expiration <time>         Increase expiration time on HIT (hours)
        """
        self.services.extend_hit(self, arg['<HITid>'], arg['--assignments'],
                                 arg['--expiration'])

    @docopt_cmd
    def do_expire_hit(self, arg):
        """
        Usage: expire_hit (--all | <HITid> ...)

        -a, --all              expire all HITs
        """
        if arg['--all']:
            hits_data = self.services.get_active_hits()
            arg['<HITid>'] = [hit['hitid'] for hit in hits_data]
        for hit in arg['<HITid>']:
            self.services.expire_hit(hit)
            if self.sandbox:
                print "expiring sandbox HIT", hit
                self.sandboxHITs -= 1
            else:
                print "expiring live HIT", hit
                self.liveHITs -= 1

    def do_eof(self, arg):
        self.do_quit(arg)
        return True

    def do_quit(self, arg):
        if self.server.is_server_running() == 'yes' or self.server.is_server_running() == 'maybe':
            r = raw_input("Quitting shell will shut down experiment server. Really quit? y or n: ")
            if r == 'y':
                self.do_stop_server('')
            else:
                return
        return True


def run():
    opt = docopt(__doc__, sys.argv[1:])
    config = PsiturkConfig()
    config.load_config()
    services = MTurkServices(config)
    server = control.ExperimentServerController(config)
    shell = Psiturk_Shell(config, services, server)
    shell.cmdloop()
