import argparse
import sys, os
from version import version_number 


def process():
	# figure out how we were invoked
	invoked_as = os.path.basename(sys.argv[0])

	if (invoked_as == "psiturk"):
		launch_shell()
	elif (invoked_as == "psiturk-server"):
		launch_server()
	elif (invoked_as == "psiturk-shell"):
		launch_shell()
	elif (invoked_as == "psiturk-setup-example"):
		setup_example()

def setup_example():
	# add commands for testing, etc..
	parser = argparse.ArgumentParser(description='Creates a simple default project (stroop) in the current directory with the necessary psiTurk files.')

	# optional flags
	parser.add_argument('-v', '--version', help='Print version number.', action="store_true")
	args = parser.parse_args()

	# if requested version just print and quite
	if args.version:
		print version_number
	else:
		import setup_example as se
		se.setup_example()

def launch_server():
	# add commands for testing, etc..
	parser = argparse.ArgumentParser(description='Launch psiTurk experiment webserver process on the host/port defined in config.txt.')

	# optional flags
	parser.add_argument('-v', '--version', help='Print version number.', action="store_true")
	args = parser.parse_args()

	# if requested version just print and quite
	if args.version:
		print version_number
	else:
		import experiment_server as es
		es.launch()

def launch_shell():
	# add commands for testing, etc..
	parser = argparse.ArgumentParser(description='Launch the psiTurk interactive shell.')

	# optional flags
	parser.add_argument('-v', '--version', help='Print version number.', action="store_true")
	args = parser.parse_args()

	# if requested version just print and quite
	if args.version:
		print version_number
	else:
		import psiturk_shell as ps
		ps.run()
