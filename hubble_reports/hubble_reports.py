from flask import Blueprint

reports = Blueprint('reports', __name__)

from hubble_reports import views
