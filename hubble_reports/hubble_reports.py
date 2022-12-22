from flask import Blueprint

reports = Blueprint('reports', __name__, template_folder='templates')

from hubble_reports import views
