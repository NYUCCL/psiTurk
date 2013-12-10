
# this file imports custom routes into the experiment server

from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound


custom_code = Blueprint('custom_code', __name__, template_folder='templates')

@custom_code.route('/my_custom_view')
def my_custom_view():
	try:
		return render_template('custom.html')
	except TemplateNotFound:
		abort(404)