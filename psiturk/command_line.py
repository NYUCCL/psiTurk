''' This module supports commandline functionality '''

import argparse
import sys, os
from psiturk.version import version_number
from psiturk.psiturk_org_services import ExperimentExchangeServices


def process():
    ''' Figure out how we were invoked '''
    invoked_as = os.path.basename(sys.argv[0])

    if invoked_as == "psiturk":
        launch_shell()
    elif invoked_as == "psiturk-server":
        launch_server()
    elif invoked_as == "psiturk-shell":
        launch_shell()
    elif invoked_as == "psiturk-setup-example":
        setup_example()
    elif invoked_as == "psiturk-install":
        install_from_exchange()

def install_from_exchange():
    ''' Install from experiment exchange. '''
    parser = argparse.ArgumentParser(
        description='Download experiment from the psiturk.org experiment\
        exchange (http://psiturk.org/ee).'
    )
    parser.add_argument(
        'exp_id', metavar='exp_id', type=str, help='the id number of the\
        experiment in the exchange'
    )
    args = parser.parse_args()
    exp_exch = ExperimentExchangeServices()
    exp_exch.download_experiment(args.exp_id)

def setup_example():
    ''' Add commands for testing, etc. '''
    parser = argparse.ArgumentParser(
        description='Creates a simple default project (stroop) in the current\
        directory with the necessary psiTurk files.'
    )

    # Optional flags
    parser.add_argument(
        '-v', '--version', help='Print version number.', action="store_true"
    )
    args = parser.parse_args()

    # If requested version just print and quite
    if args.version:
        print version_number
    else:
        import psiturk.setup_example as se
        se.setup_example()

def launch_server():
    ''' Add commands for testing, etc.. '''
    parser = argparse.ArgumentParser(
        description='Launch psiTurk experiment webserver process on the\
        host/port defined in config.txt.'
    )

    # Optional flags
    parser.add_argument(
        '-v', '--version', help='Print version number.', action="store_true"
    )
    args = parser.parse_args()

    # If requested version just print and quite
    if args.version:
        print version_number
    else:
        import psiturk.experiment_server as es
        es.launch()

def launch_shell():
    ''' Add commands for testing, etc.. '''
    parser = argparse.ArgumentParser(
        description='Launch the psiTurk interactive shell.'
    )

    # Optional flags
    parser.add_argument(
        '-v', '--version', help='Print version number.', action="store_true"
    )
    parser.add_argument(
        '-c', '--cabinmode', help='Launch psiturk in cabin (offline) mode',
        action="store_true"
    )
    parser.add_argument(
        '-s', '--script', help='Run commands from a script file'
    )
    args = parser.parse_args()
    # If requested version just print and quite
    if args.version:
        print version_number
    else:
        import psiturk.psiturk_shell as ps
        if args.script:
            ps.run(cabinmode=args.cabinmode, script=args.script)
        else:
            ps.run(cabinmode=args.cabinmode)
