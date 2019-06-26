from __future__ import print_function
import psiturk.experiment_server_controller as control
from psiturk.psiturk_config import PsiturkConfig
from psiturk.psiturk_shell import PsiturkNetworkShell
import os
import shutil
import glob
import sys

from cmd2 import History


def do_setup():
    shutil.rmtree('psiturk-example', ignore_errors=True)
    import psiturk.setup_example as se
    se.setup_example()

    # change config file...
    with open('config.txt', 'r') as file:
        config_file = file.read()

    config_file = config_file.replace(
        'use_psiturk_ad_server = true', 'use_psiturk_ad_server = false')
    config_file = config_file.replace(
        'ad_location = false', 'ad_location = https://example.test/pub')

    with open('config.txt', 'w') as file:
        file.write(config_file)

    # os.chdir('psiturk-example') # the setup script already chdirs into here, although I don't like that it does that
    os.environ['AWS_ACCESS_KEY_ID'] = 'foo'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'bar'
    os.environ.pop('AWS_PROFILE', None)


def do_commands(shell, cmds, name='yee'):
    shell.history = History()
    cmds = ['mode sandbox'] + cmds
    for cmd in cmds:
        shell.history.append(cmd)
        print('Running: {}'.format(cmd))
    transcript_name = '{}.transcript'.format(name)
    shell.runcmds_plus_hooks(['history -t {}'.format(transcript_name)])
    with open(transcript_name, 'r') as infile:
        print(infile.read())


def do_cleanup():
    transcripts_folder = os.path.join('..', 'shell_transcripts')
    for transcript in glob.glob('*.transcript'):
        print('Moving {}'.format(transcript))
        try:
            os.remove(os.path.join(transcripts_folder, transcript))
        except OSError:
            pass
        shutil.move(transcript, os.path.join(transcripts_folder))
    os.chdir('..')
    shutil.rmtree('psiturk-example', ignore_errors=True)


do_setup()


try:

    config = PsiturkConfig()
    config.load_config()
    server = control.ExperimentServerController(config)

    launch_in_sandbox_mode = True
    quiet = False

    shell = PsiturkNetworkShell(
        config, server,
        launch_in_sandbox_mode,
        quiet=quiet)

    # #########################
    # all `do_` commands:
    # #################
    # [] def do_psiturk_status
    # [] def do_debug
    # [] def do_version
    # [] def do_dev

    # def do_config(self, arg):
    #    """
    #    Usage:
    # []      config print
    # []      config reload
    # []      config help
    #    """

    # []     def do_status(self, _):
    # []     def do_setup_example(self, _):
    # []     def db_get_config(self):
    # []     def db_use_local_file(
    # []     def do_download_datafiles(self, _):
    # []     def do_open(self, arg):
    # []     def do_eof(self, arg):
    # []     def do_exit(self, arg):
    # []     def do_quit(self, _):
    # []     def do_server(self, arg):
    # []     def do_help(self, arg):
    # []     def do_quit(self, _):
    # []     def do_status(self, arg): # overloads do_status with AMT info
    # [x]    def do_amt_balance(self, _):
    do_commands(shell, cmds=['amt_balance'], name='amt_balance')

    # def do_db(self, arg):
    #    """
    #    Usage:
    # []     db get_config
    # []     db use_local_file [<filename>]
    # []     db use_aws_instance [<instance_id>]
    # []     db aws_list_regions
    # []     db aws_get_region
    # []     db aws_set_region [<region_name>]
    # []     db aws_list_instances
    # []     db aws_create_instance [<instance_id> <size> <username> <password>
    # []                             <dbname>]
    # []     db aws_delete_instance [<instance_id>]
    # []     db help
    #    """

    # def do_mode(self, arg):
    #    """
    #    Usage: mode
    # []           mode <which>
    do_commands(shell, cmds=['mode'], name='mode_switch_unspecified')
    do_commands(shell, cmds=['mode sandbox'],
                name='mode_sandbox_alreadyonmode')
    do_commands(shell, cmds=['mode live'], name='mode_live')
    # switch to live and then back to sandbox
    do_commands(shell, cmds=['mode live', 'mode sandbox'],
                name='mode_live_then_sandbox')

    #    """

    # def do_hit(self, arg):
    #    """
    #    Usage:
    # []      hit create [<numWorkers> <reward> <duration>]
    do_commands(shell, cmds=['hit create 1 0.01 1'], name='hit_create')

    # []      hit extend <HITid> [(--assignments <number>)] [(--expiration <minutes>)]
    do_commands(shell, cmds=[
                'hit extend ABC --assignments 1 --expiration 1'], name='hit_extend')

    # []      hit expire (--all | <HITid> ...)
    do_commands(shell, cmds=['hit expire ABC'], name='hit_expire_hitid')
    do_commands(shell, cmds=['hit expire --all'], name='hit_expire_all')

    # []      hit delete (--all | <HITid> ...)
    do_commands(shell, cmds=['hit delete --all'], name='hit_delete_all')
    do_commands(shell, cmds=['hit delete ABC'], name='hit_delete_hitid')

    # []      hit list [--active | --reviewable] [--all-studies]
    do_commands(shell, cmds=['hit list'], name='hit_list')
    do_commands(shell, cmds=['hit list --active'], name='hit_list_active')
    do_commands(shell, cmds=['hit list --active --all-studies'],
                name='hit_list_active_allstudies')
    do_commands(shell, cmds=['hit list --reviewable'],
                name='hit_list_reviewable')

    # []      hit help
    do_commands(shell, cmds=['hit help'], name='hit_help')
    #    """

    # def do_worker(self, arg):
    #    """
    #    Usage:
    # []      worker approve (--all | --hit <hit_id> ... | <assignment_id> ...) [--all-studies] [--force]
    do_commands(shell, cmds=['worker approve --all'],
                name='worker_approve_all')
    do_commands(shell, cmds=['worker approve --hit ABC'],
                name='worker_approve_hitid')
    do_commands(shell, cmds=['worker approve 123'],
                name='worker_approve_assignmentid')
    do_commands(shell, cmds=[
                'worker approve --all --all-studies'], name='worker_approve_all_allstudies')

    # []      worker reject (--hit <hit_id> | <assignment_id> ...) [--all-studies]
    do_commands(shell, cmds=['worker reject --hit ABC'],
                name='worker_reject_hitid')
    do_commands(shell, cmds=['worker reject 123 456'],
                name='worker_reject_assignmentids')
    do_commands(shell, cmds=[
                'worker reject --hit ABC --all-studies'], name='worker_reject_hitid_allstudies')

    # []      worker unreject (--hit <hit_id> | <assignment_id> ...) [--all-studies]
    do_commands(shell, cmds=['worker unreject --hit ABC'],
                name='worker_unreject_hitid')
    do_commands(shell, cmds=['worker unreject 123 456'],
                name='worker_unreject_assignmentids')
    do_commands(shell, cmds=['worker unreject --hit ABC --all-studies'],
                name='worker_unreject_hitid_allstudies')

    # []      worker bonus  (--amount <amount> | --auto) (--reason) (--all | --hit <hit_id> | <assignment_id> ...) [--override-bonused-status] [--all-studies]
    do_commands(shell, cmds=[
                'worker bonus --amount 1.00 --reason "Yee!" --all'], name='worker_bonus_amount_reason_all')
    do_commands(shell, cmds=['worker bonus --amount 1.00 --reason "Yee!" --hit ABC --override-bonused-status'],
                name='worker_bonus_amount_reason_hitid_override')
    do_commands(shell, cmds=[
                'worker bonus --auto --reason "Yee!" --all'], name='worker_bonus_auto_reason_all')
    do_commands(shell, cmds=['worker bonus --amount 1.00 --reason "Yee!" --hit ABC'],
                name='worker_bonus_amount_reason_hitid')
    do_commands(shell, cmds=['worker bonus --amount 1.00 --reason "Yee!" 123 456'],
                name='worker_bonus_amount_reason_assignmentids')
    do_commands(shell, cmds=['worker bonus --amount 1.00 --reason "Yee!" --all --all-studies'],
                name='worker_bonus_amount_reason_all_allstudies')

    # []      worker list [--submitted | --approved | --rejected] [(--hit <hit_id>)] [--all-studies]
    do_commands(shell, cmds=['worker list'], name='worker_list')
    do_commands(shell, cmds=['worker list --submitted'],
                name='worker_list_submitted')
    do_commands(shell, cmds=['worker list --approved'],
                name='worker_list_approved')
    do_commands(shell, cmds=['worker list --rejected'],
                name='worker_list_rejected')

    do_commands(shell, cmds=['worker list --hit ABC'],
                name='worker_list_hitid')
    do_commands(shell, cmds=[
                'worker list --approved --hit ABC'], name='worker_list_approved_hitid')

    do_commands(shell, cmds=['worker list --submitted --all-studies'],
                name='worker_list_submitted_allstudies')

    # []      worker help
    do_commands(shell, cmds=['worker help'], name='worker_help')

    # def do_debug(self, arg):
    #    """
    #    Usage: debug [options]
    #
    #    -p, --print-only        just provides the URL, doesn't attempt to
    #                            launch browser
    #    """
    do_commands(shell, cmds=['debug -p'], name='debug_p')


except:
    raise
finally:
    do_cleanup()
