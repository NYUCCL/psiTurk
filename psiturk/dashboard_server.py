# Import flask
import os, sys
import argparse
from flask import Flask, render_template, request, Response, jsonify
import werkzeug.serving
import subprocess
import dashboard as Dashboard
import webbrowser
import socket
from PsiTurkConfig import PsiTurkConfig
import signal
import urllib2

config = PsiTurkConfig()


def launch_browser(port):
    launchurl = "http://{host}:{port}/dashboard".format(
        host=config.get("Server Parameters", "host"), 
        port=port)
    webbrowser.open(launchurl, new=1, autoraise=True)

def is_port_available(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', port))
        s.shutdown(1)
        return 0
    except:
        return 1

def find_open_port():
    open_port = next(port for port in range(5000, 10000) if is_port_available(port))
    return(open_port)


app = Flask("Psiturk_Dashboard",
            template_folder=os.path.join(os.path.dirname(__file__), "templates_dashboard"), 
            static_folder=os.path.join(os.path.dirname(__file__), "static_dashboard"))

# Routes for handling dashboard activity
@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Serves dashboard.
    """
    return render_template('dashboard.html')

@app.route('/dashboard_model', methods=['GET', 'POST'])
def dashbaord_model():
    """
    Sync for dashboard model.
    """
    if request.method == 'GET':
        return jsonify(config.get_serialized())

    if request.method == 'POST':
        config_model = request.json
        config.set_serialized(config_model)

    return render_template('dashboard.html')

@app.route('/at_a_glance_model', methods=['GET'])
def at_a_glance_model():
    """
    Sync for dashboard at-a-glance pane.
    """
    services = Dashboard.MTurkServices(config)

    if request.method == 'GET':
        summary = services.get_summary()
        if summary:
            return summary
        else:
            return jsonify(error="unable to access aws")

@app.route('/verify_aws_login', methods=['POST'])
def verify_aws():
    """
    """
    services = Dashboard.MTurkServices(config)
    key_id = request.json['aws_access_key_id']
    secret_key = request.json['aws_secret_access_key']
    is_valid = services.verify_aws_login(key_id, secret_key)
    return jsonify(aws_accnt=is_valid)


@app.route('/mturk_services', methods=['POST'])
def turk_services():
    """
    """
    services = Dashboard.MTurkServices(config)
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
    """
    services = Dashboard.MTurkServices(config)
    return jsonify(hits=services.get_active_hits())

@app.route('/monitor_server', methods=['GET'])
def monitor_server():
    server = Dashboard.Server(port=config.getint('Server Parameters', 'port'))
    server.start_monitoring()
    return "Monitoring..."

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
            server = Dashboard.Server(port=test_port)
            is_available = server.is_port_available(test_port)
        return jsonify(is_available=is_available)
    return "port check"

@app.route("/server_status", methods=["GET"])
def status():
    server = Dashboard.Server(port=config.getint('Server Parameters', 'port'))
    return(jsonify(state=server.check_port_state()))

@app.route("/participant_status", methods=["GET"])
def participant_status():
    database = Dashboard.Database()
    status = database.get_participant_status()
    return status

@app.route("/favicon.ico")
def favicon():
    """
    Serving a favicon
    """
    print "got favicon request"
    return app.send_static_file('favicon.ico')

#----------------------------------------------
# psiTurk server routes
#----------------------------------------------
@app.route("/launch", methods=["GET"])
def launch_psiturk():
    server_command = "{python_exec} '{server_script}'".format(
        python_exec = sys.executable,
        server_script = os.path.join(os.path.dirname(__file__), "psiturk_server.py")
    )
    print(server_command)
    subprocess.Popen(server_command, shell=True)
    return "psiTurk launching..."

@app.route("/shutdown_dashboard", methods=["GET"])
def shutdown():
    pid = os.getpid()
    print("shutting down dashboard at pid %s..." % pid)
    os.kill(pid, signal.SIGKILL)
    return "shutting down dashboard..."

@app.route("/shutdown_psiturk", methods=["GET"])
def shutdown_psiturk():
    psiturk_server_url = "http://{host}:{port}/ppid".format(
        host=config.get("Server Parameters", "host"),
        port=config.getint("Server Parameters", "port"))
    ppid_request = urllib2.Request(psiturk_server_url)
    ppid = urllib2.urlopen(ppid_request).read()
    print("shutting down PsiTurk server at pid %s..." % ppid)
    os.kill(int(ppid), signal.SIGKILL)
    return "shutting down dashboard..."

def run_dev_server():
    app.debug = True

def launch():
    parser = argparse.ArgumentParser(description='Launch psiTurk dashboard.')
    parser.add_argument('-p', '--port', default=22361,
                        help='optional port for dashboard. default is 22361.')
    args = parser.parse_args()
    dashboard_port = args.port

    already_running = False
    launch_browser(dashboard_port)
    try:
        app.run(debug=True, port=dashboard_port, host='0.0.0.0')
    except socket.error:
        print "Server is already running!"


if __name__ == "__main__":
    launch()
