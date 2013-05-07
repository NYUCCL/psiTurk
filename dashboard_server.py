# Import flask
from flask import Flask, render_template, request, Response, make_response, jsonify

# Import dashboard
import dashboard as Dashboard

# Can dashboard be accessed externally?
IS_SECURE = True

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
    my_dashboard = Dashboard.PsiTurkConfig()

    if request.method == 'GET':
        return jsonify(my_dashboard.get_serialized())

    if request.method == 'POST':
        config_model = request.json
        my_dashboard.set_serialized(config_model)

    return render_template('dashboard.html')

if __name__ == '__main__':
    print "Starting psiTurk dashboard..."
    if IS_SECURE:
        app.run(debug=False, port=5000)
    else:
        print "WARNING! Your server is exposed to the public."
        app.run(debug=False, host='0.0.0.0',  port=5000)
