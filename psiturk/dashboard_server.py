# Import flask
import os, sys, subprocess
import argparse
from flask import Flask, Response, render_template, request, jsonify
import urllib2
import webbrowser
from psiturk_config import PsiturkConfig
from models import Participant
import experiment_server_controller as control
from amt_services import MTurkServices
from db import db_session

config = PsiturkConfig()

server_controller = control.ExperimentServerController(config.getint("Server Parameters", "port"), hostname=config.get("Server Parameters", "host"))

app = Flask("Psiturk_Dashboard",
            template_folder=os.path.join(os.path.dirname(__file__), "templates_dashboard"), 
            static_folder=os.path.join(os.path.dirname(__file__), "static_dashboard"))

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Some supporting classes needed by the dashboard_server
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#----------------------------------------------
# vanilla exception handler
#----------------------------------------------
class DashboardServerException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Dashboard Server Routes
#    two subsections
#       - routes for handling dashboard interactivity
#       - routes for interacting with experiment server
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#----------------------------------------------
# Routes for handling dashboard interactivity
#----------------------------------------------
@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Serves dashboard.
    """
    return render_template('dashboard.html')

@app.route('/dashboard_model', methods=['GET', 'POST'])
def dashboard_model():
    """
    Sync for dashboard model.
    """
    if request.method == 'GET':
        return jsonify(config.get_serialized())

    if request.method == 'POST':
        config_model = request.json
        reset_server = config.set_serialized(config_model)
    
    if reset_server:
        if server_controller.is_port_available() == 0:
            server_controller.shutdown()
            server_controller.startup()
    
    return render_template('dashboard.html')

@app.route('/at_a_glance_model', methods=['GET'])
def at_a_glance_model():
    """
    Sync for dashboard at-a-glance pane.
    """
    services = MTurkServices(config)

    if request.method == 'GET':
        summary = services.get_summary()
        if summary:
            return summary
        else:
            return jsonify(error="unable to access aws")

@app.route('/verify_aws_login', methods=['POST'])
def verify_aws():
    """
    Verifies current aws login keys are valid
    """
    services = MTurkServices(config)
    key_id = request.json['aws_access_key_id']
    secret_key = request.json['aws_secret_access_key']
    is_valid = services.verify_aws_login(key_id, secret_key)
    return jsonify(aws_accnt=is_valid)

@app.route('/mturk_services', methods=['POST'])
def turk_services():
    """
    """
    services = MTurkServices(config)
    mturk_request = request.json
    if "mturk_request" in request.json:
        if request.json["mturk_request"] == "create_hit":
            services.create_hit()
            return jsonify(msg="hit created")
        elif request.json["mturk_request"] == "expire_hit":
            hitid = request.json["hitid"]
            services.expire_hit(hitid)
            return jsonify(msg="hit expired")
        elif request.json["mturk_request"] == "extend_hit":
           hitid = request.json["hitid"]
           assignments_increment = request.json["assignments_increment"]
           expiration_increment = request.json["expiration_increment"]
           services.extend_hit(hitid, assignments_increment, expiration_increment)
           return jsonify(msg="hit expired")
    return jsonify(error="psiTurk failed to recognize your request.")

@app.route('/get_log', methods=['POST'])
def get_log():
    """
    provides an jsonified interface to the log file in the dashbaord
    """
    if "log_level" in request.json:
        return jsonify(log="hello")
    return jsonify(error="did not specify the log level correctly")

@app.route('/get_hits', methods=['GET'])
def get_hits():
    """
    provides an jsonified collection of active hits
    """
    services = MTurkServices(config)
    return jsonify(hits=services.get_active_hits())

@app.route('/get_workers', methods=['GET'])
def get_workers():
    """
    provides an jsonified collection of workers pending review
    """
    services = MTurkServices(config)
    return jsonify(workers=services.get_workers())

@app.route('/reject_worker', methods=['POST'])
def reject_worker():
      if "assignmentId" in request.json:
          services = MTurkServices(config)
          services.reject_worker(request.json["assignmentId"])
          return("Worker rejected")
      return("Error: Missing assignment id")

@app.route('/approve_worker', methods=['POST'])
def approve_worker():
      CREDITED = 5
      if "assignmentId" in request.json:
          assignment_id = request.json["assignmentId"]
          services = MTurkServices(config)
          services.reject_worker(assignment_id)
          try:
              part = Participant.query.\
                        filter(Participant.assignmentid == assignment_id).one()
              part.status = CREDITED
              db_session.add(part)
              db_session.commit()
          except:
              print "Error: Database failed to credit participant"
          return("Worker approved")
      return("Error: Missing assignment id")

@app.route('/is_port_available', methods=['POST'])
def is_port_available_route():
    """
    Check if port is available on localhost
    """
    if request.method == 'POST':
        test_port = request.json['port']
        if test_port == config.getint('Server Parameters', 'port'):
            is_available = 1
        else:
            is_available = control.is_port_available(ip='127.0.0.1', port=test_port)
        return jsonify(is_available=is_available)
    return "port check"

@app.route('/is_internet_available', methods=['GET'])
def is_internet_on():
    try:
        response=urllib2.urlopen('http://www.google.com', timeout=1)
        return "true"
    except urllib2.URLError as err: pass
    return "false"

@app.route("/server_status", methods=["GET"])
def status():
    return(jsonify(state=server_controller.is_port_available()))

# this function appears unimplemented in the dashboard currently
# @app.route("/participant_status", methods=["GET"])
# def participant_status():
#     database = Dashboard.Database()
#     status = database.get_participant_status()
#     return status

@app.route("/favicon.ico")
def favicon():
    """
    Serving a favicon
    """
    print "got favicon request"
    return app.send_static_file('favicon.ico')

@app.route("/data/<filename>", methods=["GET"])
def download_datafile(filename):
    if filename[-4:] != ".csv":
        raise Exception("/data received Invalid filename: %s" % filename)
    content, scope = filename[:-4].split("_")
    if scope == "all":
        query = Participant.query.all()
    else:
        raise Exception("Not implemented: data file scope %s" % scope)
    subjresults = []
    header = "" # By default, no header.
    if content == "trialdata":
        datafun = lambda p: p.get_trial_data()
    elif content == "eventdata":
        header = "uniqueid,event_type,interval,value,timestamp\n"
        datafun = lambda p: p.get_event_data()
    elif content == "questiondata":
        datafun = lambda p: p.get_question_data()
    else:
        raise Exception("Not implemented: data type %s" % content)
    ret = header + "".join([datafun(participant) for participant in query])
    response = Response(ret, content_type="text/csv", headers={'Content-Disposition': 'attachment;filename=%s' % filename})
    return response

@app.route("/launch_log", methods=["GET"])
def launch_log():
    logfilename = config.get('Server Parameters', 'logfile')
    if sys.platform == "darwin":
        args = ["open", "-a", "Console.app", logfilename]
    else:
        # assume linux
        args = ["xterm", "-e", "'tail -f %s'" % logfilename]
    subprocess.Popen(args, close_fds=True)
    return("Log program launching...")

#----------------------------------------------
# routes for interfacing with ExperimentServerController
#----------------------------------------------
@app.route("/launch", methods=["GET"])
def launch_experiment_server():
    server_controller.startup()
    return "Experiment Server launching..."

@app.route("/shutdown_dashboard", methods=["GET"])
def shutdown_dashboard():
    print("Attempting to shut down.")
    #server_controller.shutdown()  # Must do this; otherwise zombie server remains on dashboard port; not sure why
    request.environ.get('werkzeug.server.shutdown')()
    return("shutting down dashboard server...")

@app.route("/shutdown_psiturk", methods=["GET"])  ## TODO: Kill psiturk reference
def shutdown_experiment_server():
    server_controller.shutdown()
    return("shutting down Experiment Server...")


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Supporting functions
#   general purpose helper functions used by the dashboard server
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def launch_browser(hostname, port):
    launchurl = "http://{host}:{port}/dashboard".format(host=hostname, port=port)
    webbrowser.open(launchurl, new=1, autoraise=True)

def launch_browser_when_online(ip, port):
    return control.wait_until_online(lambda: launch_browser(ip, port), ip, port)
    
def run_dev_server():
    app.debug = True

#  this is the entry point to the script when running 'psiturk' from the command line
def launch():
    parser = argparse.ArgumentParser(description='Launch psiTurk dashboard.')
    parser.add_argument('-p', '--port', default=22361,
                        help='optional port for dashboard. default is 22361.')
    args = parser.parse_args()
    dashboard_ip = "0.0.0.0"
    dashboard_port = args.port
    
    browser_launch_thread = launch_browser_when_online(dashboard_ip, dashboard_port)
    if not control.is_port_available(ip=dashboard_ip, port=dashboard_port):
        print "Server is already running on http://localhost:%s/dashboard!" % dashboard_port
    else:
        port = config.getint('Server Parameters', 'port')
        print "Serving on ", "http://" +  dashboard_ip + ":" + str(dashboard_port)
        app.run(debug=True, use_reloader=False, port=dashboard_port, host=dashboard_ip)
 
if __name__ == "__main__":
    launch()
