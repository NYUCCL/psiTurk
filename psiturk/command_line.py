import argparse
import sys, os
from version import version_number 

def process():
	# figure out how we were invoked
	invoked_as = os.path.basename(sys.argv[0])

	if (invoked_as == "psiturk"):
		launch_dashboard()
	elif (invoked_as == "psiturk-server"):
		launch_server()
	elif (invoked_as == "psiturk-dashboard"):
		launch_dashboard()
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


def launch_dashboard():
	# add commands for testing, etc..
	parser = argparse.ArgumentParser(description='Launch psiTurk dashboard.')

	# optional flags
	parser.add_argument('-i', '--ip', default='localhost', 
						help='IP to run dashboard on. default is `localhost`.')
	parser.add_argument('-p', '--port', default=22361, 
    	help='Port to run dashboard on. default is 22361.')
	parser.add_argument('-v', '--version', help='Print version number.', action="store_true")
	args = parser.parse_args()

	# if requested version just print and quite
	if args.version:
		print version_number
	else:
		import dashboard_server as dbs
		dbs.launch(ip=args.ip, port=args.port)
