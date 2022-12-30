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
import dash

from dash import Dash, dcc, html
from config import BaseConfig
from app import app

from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import get_logger
import logging

logger = get_logger(__name__,level=logging.DEBUG)

dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/dash/',
    suppress_callback_exceptions=True,
)

# dash.register_page("overall_eff", layout=html.Div('overall_eff'), path='/capacity')
# dash.register_page("home", layout=html.Div('home'), path='/')
# session['dash'].header = f"Welcome, {session['user'].name}!!!"
# FYI, you need both an app context and a request context to use url_for() in the Jinja2 templates
# def dash_call():
with app.app_context(), app.test_request_context():
    layout_dash = pathlib.Path(get_root_path(__name__)).parent.joinpath("templates").joinpath("dashboard.html")
    logger.info(f"\n\n\n\n=========>>>layout_dash:\n{layout_dash}\n\n")
    # logger.info(f"\n\n\n\n=========>>>template url_for:\n{url_for('templates', filename='layouts/base.html')}\n\n")
    with open(layout_dash, "r") as f:
        html_body = render_template_string(f.read())
        html_body = html_body.replace('HEADER', 'Welcome User!!!')
        print('\n\n\n', html_body, '\n\n\n')
        
dash_app.index_string = (html_body)

db_conn = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)

df_or = pd.read_sql_query(db.session.query(
    TimesheetEntry.authorized_hours, 
    TimesheetEntry.entry_date,
    Team.name, 
    ExpectedUserEfficiency.expected_efficiency,
    )
    .join(TimesheetEntry, 
        TimesheetEntry.user_id == ExpectedUserEfficiency.user_id)
        .join(Team, Team.id == TimesheetEntry.team_id).statement, 
        db_conn)

df = df_or.copy()

df.rename(columns={
    'authorized_hours':'actual_efficiency', 
    'name':'team',
    'entry_date':'date',
    }, 
    inplace=True
)

df.loc[:, 'capacity'] = 100 * df['actual_efficiency']/df['expected_efficiency']
df['capacity'] = df['capacity'].fillna(0)
df.replace(np.inf, 100.0, inplace=True)
# data['date']=pd.to_datetime(data['date'],format='%Y-%m-%d')
df['date'] = pd.to_datetime(df['date'], format=r"%Y-%m-%d")
logger.info(f"\n\n\n\n========Info=======\n{df}\n")
min_year= df['date'].min().year
max_year= df['date'].max().year

till_date= df['date'].max().strftime("%B %Y")
df = df.groupby('team').mean(numeric_only=True)['capacity'].reset_index()
fig_q1 = (px.bar(df, x='team', y='capacity', 
color='team', text='capacity', 
title="Teams Capacity - Efficiency %",
labels={'team':'Teams', 'capacity': 'Capacity'}
)
.update_traces(texttemplate='%{text:0.0f}%').update_layout(title_x=0.5))
df['ratings'] = ['Excellent' if val>121 else 'Good' if val>120 else 'Needs Improvement' for val in df['capacity']]
df['trends'] = df['capacity'].apply(lambda a: "↑" if a>121 else "↔︎" if a>120 else "↓")
# min_year, max_year, till_date = (df['date'].min().year, df['date'].max().year, df['date'].format("%B %Y"))
df['capacity'] = df['capacity']/100

dash_app.layout = html.Div([
dcc.Location(id='url', refresh=False),
html.Div(id='page-content')
])


index_page = html.Div([
    html.H1(children=f"g.user")
    # html.Br(),
    # dcc.Link('Go to Page 2', href='/page-2'),
])

layout = html.Div(id='overall_eff',children=[
    html.Div(
        id='hello',
        title='Hover to see me',
        children=[
        html.H1(
            id="dash_header",
            children=f'Overall Team wise Efficiency Percentage', 
            style={"font-size":"25px", "font-align":"center"},
        )], 
            
            ),
    html.Br(),
    dcc.Link('Back', href='/dash'),
    html.Br(),
    html.H2(children=f'Teams Efficiency bandwidth- Fiscal Year {min_year} - {max_year} (Till, {till_date})'),
    dcc.Graph(
        figure=fig_q1,
        id="overall_efficiency"
    ),
    dash_table.DataTable(
        data=df.to_dict('records'), 
        # columns=[{"name": i, "id": i} for i in df.columns],
        columns=[
            {'name': ['Teams Ratings & Trend','Team'], 'id': 'team', 'type': 'text'},
            {'name': ['Teams Ratings & Trend','Capacity'], 'id': 'capacity', 'type': 'numeric', 'format':dash_table.FormatTemplate.percentage(0)},
            {'name': ['Teams Ratings & Trend','Ratings'], 'id': 'ratings', 'type': 'text'},
            {'name': ['Teams Ratings & Trend','Trends'], 'id': 'trends', 'type': 'text'},
        ],
        merge_duplicate_headers=True,
        style_cell={'textAlign': 'left', 'fontSize':'20px'},
        style_header={
            'backgroundColor': 'orange',
            'fontWeight': 'bold',
            'textAlign':'center',
        },
        )

])

@dash_app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dash/capacity':
        return layout
    else:
        return index_page

# @dash_app.callback(
#     Input('overall_eff_graph', 'clickData')
# )
@dash_app.callback(
    Output("dash_header", 'children'),
    Input("overall_efficiency", 'clickData'),
    )
def dash_into():
    # session['dash'].header = f"Welcome, {session['user'].name}!!!"
    return f"Welcome, {g.user}!!!"


@reports.route("/dash")
# @login_required
def dash_entry():
    return dash_app.index()
