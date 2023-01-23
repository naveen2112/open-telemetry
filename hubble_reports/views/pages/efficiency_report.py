import dash
import pandas as pd
import pathlib
import plotly.express as px

from dash import Dash, dcc, html, callback, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import date, timedelta
from dateutil import relativedelta
from flask import render_template_string
from flask_login import login_required
from flask.helpers import get_root_path
from sqlalchemy import create_engine

from app import app
from config import BaseConfig
from hubble_reports.hubble_reports import reports
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import str_dat_to_nstr_date


layout = [
    dcc.Graph(
        id="overall-efficiency",
        config={"displaylogo": False},
    ),
    dcc.Loading(
        type="default",
        children=html.Div(
            id="detail-efficiency",
            children=html.H3(
                "Note: Click on the graph to display corresponding teams detail report"
            ),
        ),
    ),
]
