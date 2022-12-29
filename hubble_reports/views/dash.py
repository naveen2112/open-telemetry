import pandas as pd
import plotly.express as px
import numpy as np

import pathlib
from hubble_reports.hubble_reports import reports
from flask import render_template_string, current_app, url_for
from sqlalchemy import create_engine
from flask.helpers import get_root_path
from dash import Dash
from dash import Dash, dcc, html
from config import BaseConfig
from app import app

from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import get_logger
import logging

logger = get_logger(__name__,level=logging.DEBUG)

app_dash = Dash(
    __name__,
    server=app,
    url_base_pathname='/dash/',
)


# FYI, you need both an app context and a request context to use url_for() in the Jinja2 templates
with app.app_context(), app.test_request_context():
    layout_dash = pathlib.Path(get_root_path(__name__)).parent.joinpath("templates").joinpath("dashboard.html")
    logger.info(f"\n\n\n\n=========>>>layout_dash:\n{layout_dash}\n\n")
    # logger.info(f"\n\n\n\n=========>>>template url_for:\n{url_for('templates', filename='layouts/base.html')}\n\n")
    with open(layout_dash, "r") as f:
        html_body = render_template_string(f.read())
        print('\n\n\n', html_body, '\n\n\n')
        
        app_dash.index_string = (html_body)

    db_conn = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)

    df_or = pd.read_sql_query(db.session.query(
        TimesheetEntry.authorized_hours, 
        Team.name, 
        ExpectedUserEfficiency.expected_efficiency)
        .join(TimesheetEntry, 
            TimesheetEntry.user_id == ExpectedUserEfficiency.user_id)
            .join(Team, Team.id == TimesheetEntry.team_id).statement, 
            db_conn)

    df = df_or.copy()


    df.loc[:, ('percentage')] = 0
    df.loc[:, 'percentage'] = 100 * df['authorized_hours']/df['expected_efficiency']
    df['percent_processed'] = 0
    df['percent_processed'] = df['percentage'].fillna(0)
    df.replace(np.inf, 100.0, inplace=True)
    logger.info(f"\n\n\n\n========Info=======\n{df}\n")
    df = df.groupby('name').mean(numeric_only=True)['percent_processed'].reset_index()
    fig_q1 = px.bar(df, x='name', y='percent_processed', color='name', text='percent_processed').update_traces(texttemplate='%{text:.2f}')
    app_dash.layout = html.Div(children=[
        html.H2(children='Productivity vs Efficiency for Team'),
        dcc.Graph(
            figure=fig_q1
        ),
    ])


# @reports.route("/dash")
# def dash_app():
#     return app_dash.index()