# Import flask
import os
from flask import Flask, render_template, request,\
                  Response, make_response, jsonify
import werkzeug.serving
import subprocess
from gevent import monkey
from socketio import socketio_manage
from socketio.server import SocketIOServer
import dashboard as Dashboard
import sys


monkey.patch_all()

dashboard_port = int(sys.argv[1])


app = Flask(__name__)

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
    config = Dashboard.PsiTurkConfig()

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
    config = Dashboard.PsiTurkConfig()
    services = Dashboard.MTurkServices(config)

    if request.method == 'GET':
        return services.get_summary()

@app.route('/create_hit', methods=['GET'])
def create_hit_route():
    """
    Create HIT on AMT
    """
    return "HIT created"

@app.route('/monitor_server', methods=['GET'])
def monitor_server():
    config = Dashboard.PsiTurkConfig()
    server = Dashboard.Server(port=config.port)
    server.start_monitoring()
    return "Monitoring"

@app.route('/is_port_available', methods=['POST'])
def create_hit():
    """
    Check if port is available on localhost
    """
    if request.method == 'POST':
        test_port = request.json['port']
        config = Dashboard.PsiTurkConfig()
        if test_port == config.port:
            is_available = 1
        else:
            server = Dashboard.Server(port=test_port)
            is_available = server.is_port_available(test_port)
        return jsonify(is_available=is_available)
    return "port check"

@app.route('/socket.io/<path:rest>')
def push_stream(rest):
    try:
        socketio_manage(request.environ, {'/server_status': Dashboard.ServerNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection",
                     exc_info=True)
    return "socket attempt"

@app.route("/server_status", methods=["GET"])
def status():
    status = request.args.get('status', None)
    if status:
        Dashboard.ServerNamespace.broadcast('status', status)
        return Response("Status change")
    else:
        return Response("Missing status")

@app.route("/participant_status", methods=["GET"])
def participant_status():
    database = Dashboard.Database()
    status = database.get_participant_status()
    print status
    return status


#----------------------------------------------
# psiTurk server routes
#----------------------------------------------
@app.route("/launch", methods=["GET"])
def launch():
    subprocess.Popen("python psiturk_server.py", shell=True)
    return "psiTurk launching..."

@app.route('/shutdown', methods=["GET"])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


#----------------------------------------------
# Server routines
#----------------------------------------------
def shutdown_server():
    # This assumes that psiTurk is the only gunicorn process. Otherwise, problems...
    # gunicorn_pid = int(find_process("gunicorn: master"))
    # print gunicorn_pid
    # os.kill(gunicorn_pid, 15)  # Sig 15 allows for processes to exit "gently"
    psiturk_pids = map(lambda pid: int(pid), find_process('psiturk_server').split())
    map(lambda pid: os.kill(pid, 15), psiturk_pids)  # Kill processes
    # map(lambda pid: os.killpg(pid, 15), psiturk_pids)  # Kill parents (gunicorn)
    return("Threads terminated")

def find_process(name):
    ps = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE, close_fds=True)
    grep = subprocess.Popen(['grep', str(name)], stdin=ps.stdout, stdout=subprocess.PIPE, close_fds=True)
    remove_grep = subprocess.Popen(['grep', '-v','grep'], stdin=grep.stdout, stdout=subprocess.PIPE, close_fds=True)
    awk = subprocess.Popen(['awk', '{print $2}'], stdin=remove_grep.stdout,\
                           stdout=subprocess.PIPE, close_fds=True).communicate()[0]
    return awk


@werkzeug.serving.run_with_reloader
def run_dev_server():
    app.debug = True
    port = dashboard_port
    SocketIOServer(('', port), app, resource="socket.io").serve_forever()

if __name__ == "__main__":
    app.run(debug=True, port=dashboard_port)
    run_dev_server()
