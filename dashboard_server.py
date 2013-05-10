# Import flask
from flask import Flask, render_template, request, Response, make_response, jsonify

# Import dashboard
import dashboard as Dashboard

# Can dashboard be accessed externally?
IS_SECURE = False

app = Flask(__name__)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Serves dashboard.
    """
    return render_template('dashboard.html')

# @app.route('/dashboard', methods=['GET'])
# def dashbaord():
#     """
#     Serves dashboard.
#     """
#     return render_template('dashboard.html')

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
    config = Dashboard.PsiTurkConfig()
    services = Dashboard.MTurkServices(config)

    services.create_hit()

    return "HIT created"


if __name__ == '__main__':
    print "Starting psiTurk dashboard..."
    if IS_SECURE:
        app.run(debug=False, port=5000)
    else:
        print "WARNING! Your server is exposed to the public."
        app.run(debug=True, host='0.0.0.0',  port=5000)
