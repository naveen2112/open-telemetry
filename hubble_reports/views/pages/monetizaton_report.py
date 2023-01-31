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
from plotly.subplots import make_subplots
from sqlalchemy import create_engine

from hubble_reports.hubble_reports import reports
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import str_dat_to_nstr_date, ceiling

from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry

dash.register_page(__name__, path="/monetization")

db_connection = create_engine(current_app.config.get("SQLALCHEMY_DATABASE_URI"))


layout = [
    html.Div(
        children=[
        html.H2('Description:'),
        html.Div(
            id='description',
            children=[
                html.Li(
            children=r'Red region shows the monetisation gap % exceeding 10%, While the green region shows monetisation gap % within limit'
        ),
        html.Li(
            children=r'Monetisation gap % having negative % are shown as 0% in the graph'
        ),
        ],
        style={
            'paddingLeft':'25px',
        }
        )
        ]
    ),
    dcc.Loading(
        type="default",
        children=dcc.Graph(
        id="monetization-report",
        config={"displaylogo": False},
    ),)
]

def create_line_chart(df, row, column, fig_subplots):
    figure_traces = []
    for i, team in enumerate(df['Teams'].unique()):
        df_team = df[df['Teams']==team].copy()
        fig = px.line(
            df_team, 
            x='Date', 
            y='Gap',
            text='Gap',
            markers='circle', 
            hover_data={
                'Teams':True,
                },
            title='Teams',
        )
        fig.update_traces(
            marker=dict(color=df_team['team_color']),
            line=dict(color=df_team['team_color'].unique()[0]),
            texttemplate="%{y:0.01f}%",
            hovertemplate=("<b>%{team}</b><br>" +
                        "Gap: %{y:0.01f}%<br>" +
                        "Date: %{x}<br>"),
        )
        fig_subplots.append_trace(fig['data'][0], row= i//column +1, col=int(i%column)+1)
    return fig_subplots

@callback(
    Output('monetization-report', 'figure'),
    [
        Input("url", "pathname"),
        Input("min-date-range", "data"),
        Input("max-date-range", "data"),
    ],
)
def monetization_report(urlname, min_date_sess, max_date_sess):
    df = pd.read_sql_query(
    db.session.query(
        db.func.date_trunc("month", TimesheetEntry.entry_date).label("Date"),
        db.func.greatest(
            100
            * (
                db.func.sum(TimesheetEntry.authorized_hours)
                - db.func.sum(ExpectedUserEfficiency.expected_efficiency)
            )
            / db.func.sum(TimesheetEntry.authorized_hours), 0
        ).label("Gap"),
        Team.name.label("Teams"),
    )
    .join(
        ExpectedUserEfficiency, TimesheetEntry.user_id == ExpectedUserEfficiency.user_id
    )
    .join(Team, Team.id == TimesheetEntry.team_id)
    .filter(
        db.and_(
            min_date_sess <= TimesheetEntry.entry_date,
            max_date_sess >= TimesheetEntry.entry_date,
        )
    )
    .group_by(db.func.date_trunc("month", TimesheetEntry.entry_date), Team.name)
    .order_by(db.func.date_trunc("month", TimesheetEntry.entry_date))
    .statement,
    con=db_connection,
    parse_dates=["Date"],
    )

    df["color"] = df["Gap"].apply(lambda x: "orange" if x > 10 else "blue")
    df["text"] = df["Gap"].apply(lambda x: str(x) if x > 10 else "")
    df.sort_values(["Date", "Teams"], ascending=[True, True], inplace=True)
    df["team_color"] = "white"
    df['Date'] = df["Date"].dt.strftime(r'%b %y')
    
    
    for i, team in enumerate(df.Teams.unique()):
        df["team_color"].loc[df["Teams"] == team] = px.colors.qualitative.Dark24[i]

    no_of_teams = len(df['Teams'].unique())
    row = int(ceiling(no_of_teams/2,1))
    column = 2
    fig_subplots = make_subplots(
    rows=row,
    cols=column,
    vertical_spacing=0.1,
    horizontal_spacing=0.03,
    subplot_titles=df['Teams'].unique(),
    start_cell='bottom-left',
    y_title='Gap, %',
    x_title='Date',
    )

    max_gap = ceiling(df['Gap'].max()*1.25, 5)
    
    fig_subplots = create_line_chart(df, row, column, fig_subplots)

    fig_subplots.add_hrect(
        y0=-10,
        y1=10,
        annotation_text="<b>Good</b>",
        annotation_position="bottom right",
        fillcolor="green",
        opacity=0.075,
        line_width=0,
    )
    fig_subplots.add_hrect(
        y0=max_gap,
        y1=10,
        annotation_text="<b>Need Improvements</b>",
        annotation_position="top right",
        fillcolor="red",
        opacity=0.075,
        line_width=0,
    )

    fig_subplots.update_yaxes(
        showgrid=False,
        range=[-10, max_gap],
    )

    fig_subplots.update_traces(
        textposition="top center",
                        )

    fig_subplots.update_layout(
        height=700,
        hovermode='x',
        template="plotly_white",
        margin=dict(t=50, r=12, l=65),
        )

    return fig_subplots
