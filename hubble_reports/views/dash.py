import pandas as pd
import plotly.express as px
import numpy as np

import pathlib
from hubble_reports.hubble_reports import reports
from flask import render_template_string, current_app, url_for, redirect, session, g
from flask_login import login_required, logout_user
from sqlalchemy import create_engine
from flask.helpers import get_root_path
from dash.dependencies import Input, Output

from dash import Dash, dash_table, callback, dcc
from dash.dash_table.Format import Format, Symbol, Scheme
from dash.exceptions import PreventUpdate
import dash

from dash import Dash, dcc, html
from config import BaseConfig
from app import app

from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import get_logger
import logging

logger = get_logger(__name__, level=logging.DEBUG)

dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname="/dash/",
    use_pages=True,
)


# FYI, you need both an app context and a request context to use url_for() in the Jinja2 templates
with app.app_context(), app.test_request_context():
    layout_dash = (
        pathlib.Path(get_root_path(__name__))
        .parent.joinpath("templates")
        .joinpath("dashboard.html")
    )
    logger.info(f"\n\n\n\n=========>>>layout_dash:\n{layout_dash}\n\n")
    
    with open(layout_dash, "r") as f:
        html_body = render_template_string(f.read())
        html_body = html_body.replace("HEADER", "Welcome User!!!")

dash_app.index_string = html_body

dash_app.layout = html.Div(
    [
    dcc.Location(id="url", refresh=False),
    html.H1('First'),
    html.Div(id="page-content"),
    dcc.Store(id="session", storage_type="session"),
    dash.page_container,
]
)

@reports.route("/dash")
# @login_required
def dash_entry():
    return dash_app.index()
