""" This module supports commandline functionality """
from __future__ import generator_stop
import argparse
import sys
import os
from psiturk.version import version_number


def process():
    """Figure out how we were invoked."""
    invoked_as = os.path.basename(sys.argv[0])

    if invoked_as == "psiturk":
        launch_shell()
    elif invoked_as == "psiturk-server":
        launch_server()
    elif invoked_as == "psiturk-shell":
        launch_shell()
    elif invoked_as == "psiturk-setup-example":
        setup_example()
    elif invoked_as == "psiturk-heroku-config":
        from psiturk.do_heroku_setup import do_heroku_setup
        do_heroku_setup()


def setup_example():
    """Add commands for testing, etc."""
    parser = argparse.ArgumentParser(
        description='Creates a simple default project (stroop) in the current\
        directory with the necessary psiTurk files.'
    )

    # Optional flags
    parser.add_argument(
        '-v', '--version', help='Print version number.', action="store_true"
    )
    args = parser.parse_args()

    # If requested version just print and quit
    if args.version:
        print(version_number)
    else:
        import psiturk.setup_example as se
        se.setup_example()


def launch_server():
    """Add commands for testing, etc."""
    parser = argparse.ArgumentParser(
        description='Launch psiTurk experiment webserver process on the\
        host/port defined in config.txt.'
    )

    # Optional flags
    parser.add_argument(
        '-v', '--version', help='Print version number.', action="store_true"
    )
    args = parser.parse_args()

    # If requested version just print and quit
    if args.version:
        print(version_number)
    else:
        import psiturk.experiment_server as es
        es.launch()


def launch_shell():
    """Add commands for testing, etc."""
    parser = argparse.ArgumentParser(
        description='Launch the psiTurk interactive shell.'
    )

    # Optional flags
    parser.add_argument(
        '-v', '--version', help='Print version number.', action="store_true"
    )

    script_group = parser.add_mutually_exclusive_group()
    script_group.add_argument(
        '-s', '--script', help='Run commands from a script file'
    )
    script_group.add_argument(
        '-e', '--execute', help='Execute one command specified on the command line'
    )
    script_group.add_argument(
        '-t', '--test', help='Run cmd2 unittest using provided file'
    )
    args, unknownargs = parser.parse_known_args()
    # If requested version just print and quit
    if args.version:
        print(version_number)
    else:
        import psiturk.psiturk_shell as ps
        if args.script:
            ps.run(script=args.script, quiet=True)
        elif args.test:
            ps.run(testfile=args.test, quiet=True)
        elif args.execute or unknownargs:
            if unknownargs:
                import shlex
                execute = ' '.join([shlex.quote(e) for e in unknownargs])
            else:
                execute = args.execute
            ps.run(execute=execute, quiet=True)
        else:
            ps.run()
