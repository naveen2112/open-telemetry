import dash
import pandas as pd
import pathlib
import plotly.express as px

from dash import Dash, dcc, html, callback, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import date, timedelta, datetime
from dateutil import relativedelta
from flask import render_template_string, current_app
from flask_login import login_required
from flask.helpers import get_root_path
from sqlalchemy import create_engine

from app import app
from config import BaseConfig
from hubble_reports.hubble_reports import reports
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import str_dat_to_nstr_date

from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry

dash.register_page(__name__, path='/monetization')

db_connection = create_engine(current_app.config.get("SQLALCHEMY_DATABASE_URI"))


ra = 60
dict_val = {
    "x": [datetime(year=2023 + (3 +(x//5))//12, month=(3 +(x//5))%12 +1, day=1) for x in range(ra)],
    "y":[9, 7, 13, 8, 11, 11, 8, 12, 0, 13, 9, 11, 8, 11, 9, 0, 3, 9, 13, 5, 11, 8, 0, 15, 0, 4, 1, 5, 6, 3, 1, 5, 14, 3, 12, 13, 4, 11, 6, 8, 10, 7, 8, 0, 6, 0, 10, 2, 13, 12, 7, 7, 2, 8, 14, 10, 7, 10, 13, 11],
    # "y": [randrange(0,15) for _ in range(ra)],
    "Teams":[
        "Android", "Ruby", "Python", "Swift","PHP",
        "Android", "Ruby", "Python", "Swift","PHP",
        "Android", "Ruby", "Python", "Swift","PHP",
        "Android", "Ruby", "Python", "Swift","PHP",
        "Android", "Ruby", "Python", "Swift","PHP",
        "Android", "Ruby", "Python", "Swift","PHP",
        "Android", "Ruby", "Python", "Swift","PHP",
        "Android", "Ruby", "Python", "Swift","PHP",
        "Android", "Ruby", "Python", "Swift","PHP",
        "Android", "Ruby", "Python", "Swift","PHP",
        "Android", "Ruby", "Python", "Swift","PHP",
        "Android", "Ruby", "Python", "Swift","PHP",
    ]
}
df = pd.DataFrame(dict_val, columns=dict_val.keys())
df['color'] = df['y'].apply(lambda x: 'orange' if x > 10 else 'blue')
df['text'] = df['y'].apply(lambda x: str(x) if x > 10 else '')
df.sort_values(['x', 'Teams'],ascending=[True, True] , inplace=True)
df['team_color']='white'

i=0
for team in df.Teams.unique():
    df['team_color'].loc[df['Teams']==team] = px.colors.qualitative.Dark24[i]
    i += 1

df['Date'] = df['x'].dt.strftime(r'%b %y')

figure = px.line(
    df, 
    x='Date', 
    y='y',
    color='Teams',
    text='y',
    hover_data={
            "y": ":.2f",
            # "Teams": False,
            "Date":False,
            "text":False,
            "color":False,
        },
    markers='circle',
    
    # hover_name='Teams',
    facet_row='Teams',
    facet_row_spacing=0.05,
    labels={
        'Teams':'Teams',
    },
    )
figure.update_yaxes(
    range=[0,df['y'].max()+7],
)
figure.update_layout(
    template="plotly_white",
    hovermode='x unified',
    height=800,
)
figure.update_traces(
    textposition="top center",
)
figure.update_annotations(
    textangle=0,
    xanchor='left',
    xref='paper',
    yanchor='top',

    y=df['y'].max()+7,
    yref='y domain',
    # y='relative',
    x=0.5,
    # y=17,
    # y=1,
    )
for da in figure['data']:
    if da['type'] in ['scatter', 'line']:
        da['line']['color'] = df[df['Teams']==da['name']]['team_color'].unique()[0]
    elif da['type'] == 'bar':
        da['marker']['color'] = df[df['Teams']==da['name']]['team_color'].unique()[0]
for i, da in enumerate(figure['layout']['annotations']):
    da['text'] = da['text'].replace('Teams=','')
    # print(df)
    da['yref'] = 'y'+str(i+1 if i > 0 else '')


# figure = px.line()
layout = [
    dcc.Graph(
        id="monetization-report",
        config={"displaylogo": False},
        figure=figure,
    ),
]
