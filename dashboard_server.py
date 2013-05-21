# Import flask
from flask import Flask, render_template, request,\
                  Response, make_response, jsonify
import werkzeug.serving
import subprocess
from gevent import monkey
from socketio import socketio_manage
from socketio.server import SocketIOServer
import dashboard as Dashboard


monkey.patch_all()

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
def create_hit():
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

@app.route("/launch", methods=["GET"])
def launch():
    subprocess.Popen("python psiturk_server.py", shell=True)
    return "psiTurk launching..."

@werkzeug.serving.run_with_reloader
def run_dev_server():
    app.debug = True
    port = 5000
    SocketIOServer(('', port), app, resource="socket.io").serve_forever()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    run_dev_server()
