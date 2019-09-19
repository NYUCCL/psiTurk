from __future__ import print_function

import os
import shutil
import glob
import sys
import pytest
from unittest import mock

from cmd2.history import History

from distutils import file_util

@pytest.fixture(scope='function')
def get_shell(patch_aws_services, stubber, mocker):
    
    def do_it():
        from psiturk.psiturk_shell import PsiturkNetworkShell
        import psiturk.experiment_server_controller as control
        from psiturk.psiturk_config import PsiturkConfig
        
        import psiturk.experiment_server_controller
        mocker.patch.object(psiturk.experiment_server_controller.ExperimentServerController, 'is_port_available', lambda *args, **kwargs: True)
        
        mocker.patch.object(PsiturkNetworkShell,'get_intro_prompt', lambda *args, **kwargs: '')
        mocker.patch.object(PsiturkNetworkShell,'update_hit_tally', lambda *args, **kwargs: None)
        mocker.patch.object(PsiturkNetworkShell,'_confirm_dialog', lambda *args, **kwargs: True)

        config = PsiturkConfig()
        config.load_config()
        server = control.ExperimentServerController(config)

        launch_in_sandbox_mode = True
        quiet = False
        shell = PsiturkNetworkShell(
            config, server,
            launch_in_sandbox_mode,
            quiet=quiet)
        shell.persistent_history_file = None
        shell.echo = True
        stubber.assert_no_pending_responses()
        return shell
            
    return do_it

def test_do_worker_bonus_reason(get_shell, mocker):
    from psiturk.psiturk_shell import MTurkServicesWrapper
    patched = mocker.patch.object(MTurkServicesWrapper, 'bonus_all_local_assignments')
    shell = get_shell()
    
    shell.runcmds_plus_hooks(['worker bonus --amount 1.00 --all --reason "thanks for everything"'])
    
    patched.assert_called_with(float('1.00'), "thanks for everything", False)

@pytest.fixture()
def populate_db_for_shell_cmds(create_dummy_hit, create_dummy_assignment):
    assignmentids = ['123','456']
    create_dummy_hit(with_hit_id='ABC')
    for assignmentid in assignmentids:
        create_dummy_assignment({'assignmentid': assignmentid, 'hitid':'ABC'})

commands=[
    (['amt_balance'],'amt_balance'),
    (['mode'],'mode_switch_unspecified'),
    (['mode sandbox'],'mode_sandbox_alreadyonmode'),
    (['mode live'], 'mode_live'),
    (['mode live', 'mode sandbox'],'mode_live_then_sandbox'),
    (['hit create 1 0.01 1'], 'hit_create'),
    (['hit extend ABC --assignments 1 --expiration 1'], 'hit_extend'),
    (['hit expire ABC'], 'hit_expire_hitid'),
    (['hit expire --all'], 'hit_expire_all'),
    (['hit delete --all'], 'hit_delete_all'),
    (['hit delete ABC'], 'hit_delete_hitid'),
    (['hit list'], 'hit_list'),
    (['hit list --active'], 'hit_list_active'),
    (['hit list --active --all-studies'],'hit_list_active_allstudies'),
    (['hit list --reviewable'],'hit_list_reviewable'),
    (['hit help'], 'hit_help'),
    (['worker approve --all'],'worker_approve_all'),
    (['worker approve --hit ABC'],'worker_approve_hitid'),
    (['worker approve 123'],'worker_approve_assignmentid'),
    (['worker approve --all --all-studies'], 'worker_approve_all_allstudies'),
    (['worker reject --hit ABC'],'worker_reject_hitid'),
    (['worker reject 123 456'],'worker_reject_assignmentids'),
    (['worker reject --hit ABC --all-studies'], 'worker_reject_hitid_allstudies'),
    (['worker unreject --hit ABC'],'worker_unreject_hitid'),
    (['worker unreject 123 456'],'worker_unreject_assignmentids'),
    (['worker unreject --hit ABC --all-studies'],'worker_unreject_hitid_allstudies'),
    (['worker bonus --amount 1.00 --reason "Yee!" --all'], 'worker_bonus_amount_reason_all'),
    (['worker bonus --amount 1.00 --reason "Yee!" --hit ABC --override-bonused-status'],'worker_bonus_amount_reason_hitid_override'),
    (['worker bonus --auto --reason "Yee!" --all'], 'worker_bonus_auto_reason_all'),
    (['worker bonus --amount 1.00 --reason "Yee!" --hit ABC'],'worker_bonus_amount_reason_hitid'),
    (['worker bonus --amount 1.00 --reason "Yee!" 123 456'],'worker_bonus_amount_reason_assignmentids'),
    (['worker bonus --amount 1.00 --reason "Yee!" --all --all-studies'],'worker_bonus_amount_reason_all_allstudies'),
    (['worker list'], 'worker_list'),
    (['worker list --submitted'],'worker_list_submitted'),
    (['worker list --approved'],'worker_list_approved'),
    (['worker list --rejected'],'worker_list_rejected'),
    (['worker list --hit ABC'],'worker_list_hitid'),
    (['worker list --approved --hit ABC'], 'worker_list_approved_hitid'),
    (['worker list --submitted --all-studies'],'worker_list_submitted_allstudies'),
]

generate_transcripts = False

@pytest.mark.parametrize('cmds,name', commands)
def test_do_commands(get_shell, pytestconfig, cmds, name, stubber, capsys):
# def test_do_commands(get_shell, pytestconfig, cmds, name, stubber):
    
    transcript_name = '{}.transcript'.format(name)
    cmds = ['mode sandbox'] + cmds
    
    # (out, err) = capfd.readouterr()

    shell = get_shell()
    if generate_transcripts:
        shell.history = History()
        for cmd in cmds:
            stmt = shell.statement_parser.parse(cmd)
            shell.history.append(stmt)
            print('Running: {}'.format(cmd))
        shell.runcmds_plus_hooks(['history -t {}'.format(transcript_name)])
        with open(transcript_name, 'r') as infile:
            print(infile.read())
        file_util.copy_file(transcript_name, os.path.join(pytestconfig.rootdir, 'tests','shell_transcripts', transcript_name))
    else:
        # if name == 'worker_approve_all':
            # pytest.set_trace()
        response = shell.runcmds_plus_hooks(cmds)
        captured = capsys.readouterr()
        # with capsys.disabled():
            # print(captured.out)
            # print(captured.err)
        assert not captured.err

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
#    """

# def do_hit(self, arg):
#    """
#    Usage:
# []      hit create [<numWorkers> <reward> <duration>]
# []      hit extend <HITid> [(--assignments <number>)] [(--expiration <minutes>)]
# []      hit expire (--all | <HITid> ...)
# []      hit delete (--all | <HITid> ...)
# []      hit list [--active | --reviewable] [--all-studies]
# []      hit help
#    """

# def do_worker(self, arg):
#    """
#    Usage:
# []      worker approve (--all | --hit <hit_id> ... | <assignment_id> ...) [--all-studies] [--force]
# []      worker reject (--hit <hit_id> | <assignment_id> ...) [--all-studies]
# []      worker unreject (--hit <hit_id> | <assignment_id> ...) [--all-studies]
# []      worker bonus  (--amount <amount> | --auto) (--reason) (--all | --hit <hit_id> | <assignment_id> ...) [--override-bonused-status] [--all-studies]
# []      worker list [--submitted | --approved | --rejected] [(--hit <hit_id>)] [--all-studies]
# []      worker help

# def do_debug(self, arg):
#    """
#    Usage: debug [options]
#
#    -p, --print-only        just provides the URL, doesn't attempt to
#                            launch browser
#    """