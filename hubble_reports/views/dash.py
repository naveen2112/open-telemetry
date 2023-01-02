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
    suppress_callback_exceptions=True,
    # use_pages=True,
    # pages_folder='hubble_reports.views',
)

dash.register_page(
    "dash_logout",
    layout=html.Div(children=redirect("reports.logout")),
    path="/dash/logout",
)
# dash.register_page("home", layout=html.Div('home'), path='/')
# session['dash'].header = f"Welcome, {session['user'].name}!!!"
# FYI, you need both an app context and a request context to use url_for() in the Jinja2 templates
# def dash_call():
with app.app_context(), app.test_request_context():
    layout_dash = (
        pathlib.Path(get_root_path(__name__))
        .parent.joinpath("templates")
        .joinpath("dashboard.html")
    )
    logger.info(f"\n\n\n\n=========>>>layout_dash:\n{layout_dash}\n\n")
    # logger.info(f"\n\n\n\n=========>>>template url_for:\n{url_for('templates', filename='layouts/base.html')}\n\n")
    with open(layout_dash, "r") as f:
        html_body = render_template_string(f.read())
        html_body = html_body.replace("HEADER", "Welcome User!!!")
        # print("\n\n\n", html_body, "\n\n\n")

dash_app.index_string = html_body

db_conn = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)

df_or = pd.read_sql_query(
    db.session.query(
        TimesheetEntry.authorized_hours,
        TimesheetEntry.entry_date,
        Team.name,
        ExpectedUserEfficiency.expected_efficiency,
    )
    .join(TimesheetEntry, TimesheetEntry.user_id == ExpectedUserEfficiency.user_id)
    .join(Team, Team.id == TimesheetEntry.team_id)
    .statement,
    db_conn,
)

df = df_or.copy()


def team_efficiency_dataframe(df_t: pd.DataFrame, range_slide=None):
    df_t.sort_values(
        "date",
    )
    logger.info(f"\n\n\n\n\nSorting DataFrame:\n{df_t}\n\n")


df.rename(
    columns={
        "authorized_hours": "actual_efficiency",
        "name": "team",
        "entry_date": "date",
    },
    inplace=True,
)


df.loc[:, "capacity"] = 100 * df["actual_efficiency"] / df["expected_efficiency"]
df["capacity"] = df["capacity"].fillna(0)
df.replace(np.inf, 100.0, inplace=True)
# data['date']=pd.to_datetime(data['date'],format='%Y-%m-%d')
df["date"] = pd.to_datetime(df["date"], format=r"%Y-%m-%d")
# team_efficiency_dataframe(df)
logger.info(f"\n\n\n\n========Info=======\n{df}\n")
min_year = df["date"].min().year
max_year = df["date"].max().year
df1 = (
    df.groupby([df["date"], "team"],)
    .sum(numeric_only=True)[["actual_efficiency", "expected_efficiency"]]
    .reset_index()
)
till_date = df["date"].max().strftime("%B %Y")
df = df.groupby("team").mean(numeric_only=True)["capacity"].reset_index()
# df1 = (df1.reset_index(level='team')
#     .reset_index(level='date'))
df1 = pd.DataFrame(
    pd.melt(
        df1,
        id_vars=["date", "team"],
        value_vars=["actual_efficiency", "expected_efficiency"],
        var_name="efficiency",
        value_name="efficiency_value",
    )
)
df1 = df1.sort_values('date')

# def teams_overall_efficiency(df: pd.DataFrame) -> html:
#     fig_bar = (
#         px.bar(
#             df,
#             x="team",
#             y="capacity",
#             color="team",
#             text="capacity",
#             title="Teams Capacity - Efficiency %",
#             labels={"team": "Teams", "capacity": "Capacity"},
#         )
#         .update_traces(texttemplate="%{text:0.0f}%")
#         .update_layout(title_x=0.5)
#     )
#     return fig_bar


df["ratings"] = [
    "Excellent" if val > 121 else "Good" if val > 120 else "Needs Improvement"
    for val in df["capacity"]
]
df["trends"] = df["capacity"].apply(
    lambda a: "↑" if a > 121 else "↔︎" if a > 120 else "↓"
)
# min_year, max_year, till_date = (df['date'].min().year, df['date'].max().year, df['date'].format("%B %Y"))
# df["capacity"] = df["capacity"] / 100

dash_app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
        dcc.Store(id="session", storage_type="session"),
        dash.page_container,
    ]
)

fig_bar = (
    px.bar(
        df,
        x="team",
        y="capacity",
        color="team",
        text="capacity",
        title="Teams Capacity - Efficiency %",
        labels={"team": "Teams", "capacity": "Capacity"},
    )
    .update_traces(texttemplate="%{text:0.0f}%")
    .update_layout(title_x=0.5)
)


index_page = html.Div(
    [
        html.H1(children=f"g.user")
        # html.Br(),
        # dcc.Link('Go to Page 2', href='/page-2'),
    ]
)

layout = html.Div(
    id="overall_eff",
    children=[
        html.Div(
            id="hello",
            title="Hover to see me",
            children=[
                html.H1(
                    id="dash_header",
                    children=f"Overall Team wise Efficiency Percentage",
                    style={"font-size": "25px", "font-align": "center"},
                )
            ],
        ),
        html.Br(),
        dcc.Link("Back", href="/dash"),
        html.Br(),
        dcc.Link("logout", href="/logout", refresh=True),
        html.Br(),
        html.H2(
            id="overall_efficiency_title",
            children=f"Teams Efficiency bandwidth- Fiscal Year {min_year} - {max_year} (Till, {till_date})",
        ),
        dcc.Link(
            dcc.Graph(
                id="overall_efficiency",
                figure=fig_bar,
                animate=True,
            ),
            href="/dash/detail-report",
        ),
        dash_table.DataTable(
            data=df.to_dict("records"),
            # columns=[{"name": i, "id": i} for i in df.columns],
            columns=[
                {
                    "name": ["Teams Ratings & Trend", "Team"],
                    "id": "team",
                    "type": "text",
                },
                {
                    "name": ["Teams Ratings & Trend", "Capacity"],
                    "id": "capacity",
                    "type": "numeric",
                    "format": Format(precision=2, scheme=Scheme.fixed)
                    .symbol(Symbol.yes)
                    .symbol_suffix("%"),
                },
                {
                    "name": ["Teams Ratings & Trend", "Ratings"],
                    "id": "ratings",
                    "type": "text",
                },
                {
                    "name": ["Teams Ratings & Trend", "Trends"],
                    "id": "trends",
                    "type": "text",
                },
            ],
            merge_duplicate_headers=True,
            style_cell={
                "textAlign": "left",
                "fontSize": "20px",
                "if": "",
            },
            style_header={
                "backgroundColor": "orange",
                "fontWeight": "bold",
                "textAlign": "center",
            },
            style_data_conditional=[
                {
                    "if": {
                        "column_id": ["trends", "ratings"],
                    },
                    "color": "green",
                },
                {
                    "if": {
                        "column_id": ["trends", "ratings"],
                        "filter_query": "{capacity} <= 121 && {capacity} > 120",
                    },
                    "color": "orange",
                },
                {
                    "if": {
                        "column_id": ["trends", "ratings"],
                        "filter_query": "{capacity} <= 120",
                    },
                    "color": "red",
                },
            ],
        ),
    ],
)
layout_logout = html.Div(
    id="dash_logout",
    children=[
        dcc.Location(id="url_out"),
        html.H2(children="Are you sure to logout?"),
        html.Br(),
        html.Button("Yes", id="dash-logout", n_clicks=0),
    ],
)


# @dash_app.callback(Output("url_out", "pathname"), Input("dash-logout", "clickData"))
# def dash_loggingout(click):
#     return redirect("reports.logout")


@dash_app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/dash/report":
        return layout
    elif pathname == "/dash/detail-report":
        logger.info(f"layout_expected")
        return layout_expected
    elif pathname == "/dash/logout":
        return layout_logout
    else:
        return index_page


@dash.callback(
    # Output('click-data', 'children'),
    Output("session", "data"),
    Input("overall_efficiency", "clickData"),
)
def display_click_data(clickdata):

    if not clickdata:
        raise PreventUpdate
    print("\n\n\nCallback_context:\n", clickdata["points"][0]["x"], "\n\n\n")

    column = clickdata["points"][0]["x"]

    return column
# df1.loc[]
_config = {'autosizable': True}
layout_expected = html.Div(
    id="detailed_eff",
    children=[
        html.H1(id="detail-title", children=["Detail-report"]),
        dcc.Graph(id="detailed_efficiency", animate=True, config=_config),
        html.H2('Slider'),
        html.Br(),
        dcc.RangeSlider(0, len(df1.groupby(df1['date'].dt.strftime(r"%Y %b"), sort=False)),
            marks={d: f'{d}' for d in range(len(df1.groupby(df1['date'].dt.strftime(r"%Y %b"), sort=False)))},
            value=[0, len(df1.groupby(df1['date'].dt.strftime(r"%Y %b"), sort=False))],
            id='date_range'
        ),
        html.Div(id='date_range_picked')
    ],
)


@dash_app.callback(
    Output("detailed_efficiency", "figure"),
    Input("session", "data"),
    Input('date_range', 'value'),
    prevent_initial_callbacks=True,
)
def detailed_eff(data, val):
    
    if not data:
        raise PreventUpdate
    logger.info(f"\n\n\nTeam Data clicked=====\n{data}\n\n")
    print(f"\n\nDetailed:\n{val}\n\n{data}\n\n")
    column = data
    df_range =  df1.groupby(df1['date'].dt.strftime(r"%Y %b"), sort=False).sum(numeric_only=True).iloc[val[0]:val[-1]].reset_index()
    # df_range = df1.groupby(['date','efficiency','team']).loc[val[0]:val[-1]].sum(numeric_only=True).reset_index()
    print(f"\n\nMin range:\n{df_range['date'].min()}\n\nMax range:\n{df_range['date'].max()}\n\n")
    fig_bar_detail = (
        px.bar(
            data_frame=df1[(df1['team']==column) & ((df1['date'].dt.strftime(r"%Y %b")>=df_range['date'].min()) & (df1['date'].dt.strftime(r"%Y %b")<=df_range['date'].max()))].groupby([df1['date'].dt.strftime("%Y %b"), 'efficiency'], sort=False).sum(numeric_only=True).reset_index(),
            # data_frame=df1[(df1['team']==column)],
            x="date",
            y="efficiency_value",
            color="efficiency",
            text="efficiency_value",
            title=f"{column.capitalize()} Detailed Capacity - Efficiency",
            labels={"date": "Time", "efficiency_value": "Efficiency"},
            barmode="group",
            
            # layout_xaxis_range=[df_range['date'].min(), df_range['date'].max()]
        )
        .update_traces(texttemplate="%{text:0}")
        .update_layout(
            title_x=0.5,
            # uirevision='range',
            # bargap=0.1,
            # bargroupgap=0.05, 
            xaxis_range=[df_range['date'].min(), df_range['date'].max()],
            # autorange=True,
            # xaxis=dict(
            #     range=[df_range['date'].min(), df_range['date'].max()],
            #     # rangeslider_visible=True,
            #     # side='top',
            # #   tickmode='array',
            # #   tickformat='Q%q %Y \n',
            # #   ticklabelmode='period',
            # #   ticks='outside'
            #     ),
    ))
    fig_bar_detail.update_layout(
    xaxis=dict(
        # autorange=True,
        fixedrange=False,
        
        # boundmode='soft',
        # bounds=[df_range['date'].min(), df_range['date'].max()],
        # constrain='range',
#         rangeselector=dict(
#             buttons=list([
#                 dict(count=6,
#                      label="6m",
#                      step="month",
#                      stepmode="backward"),
#                 dict(count=1,
#                      label="YTD",
#                      step="year",
#                      stepmode="todate"),
#                 dict(count=1,
#                      label="1y",
#                      step="year",
#                      stepmode="backward"),
#                 dict(step="all")
            # ])
        # ),
#         rangeslider=dict(
#             visible=True
        ),
        yaxis=dict(
        autorange=True,
        fixedrange=False,
        ),
#         type="date"
    )
# )
    # fig_bar_detail['layout']['xaxis'].update(autorange=True, rangemode = 'normal')
    # fig_bar_detail.update_layout(transition_duration=500)
    # fig_bar_detail.update_xaxes(autorange=True)
    # fig_bar_detail.update_yaxes(autorange=True)
    return fig_bar_detail



@dash_app.callback(
    # [
        Output('date_range_picked', 'children'),
        # Output("detailed_efficiency", "figure"),
    # ],
    Input('date_range', 'value'),
    Input("session", "data"),
)
def date_range_slider(val, data):
    logger.debug(f"\n\nDate rage value in {__name__}:\n{val}\n\n")
    print(f"\n\nDate rage value in {__name__}:\n{type(val[0])}\n{data}\n")
    # print(f"\n\nDate range value=\n{val}\n\nClicked Data:\n{data}\n\n")
    # if val[0]==0:
    #     return PreventUpdate
    print(f"\n\n\nInside range:\n\n")
    column = data

    return f"You have selected {val}"

# @dash_app.callback(
#     # [
#         # Output('date_range_picked', 'children'),
#     Output("detailed_efficiency", "figure"),
#     # ],
#     Input('date_range', 'value'),
#     Input("session", "data"),
# )
# def date_range_slider_graph(val, data):
#     # logger.debug(f"\n\nDate rage in graph value in {__name__}:\n{val}\n\n")
#     print(f"\n\nDate rage in graph value in {__name__}:\n{type(val[0])}\n{data}\n")
#     # print(f"\n\nDate range value=\n{val}\n\nClicked Data:\n{data}\n\n")
#     if val[0]==0:
#         return PreventUpdate
#     print(f"\n\n\nInside range:\n\n")
#     column = data
#     fig_bar_detail = (
#         px.bar(
#             df1[df1["team"] == column].loc[val[0]:val[1]],
#             x="date",
#             y="efficiency_value",
#             color="efficiency",
#             text="efficiency_value",
#             title=f"{column.capitalize()} Detailed Capacity - Efficiency",
#             labels={"date": "Time", "efficiency_value": "Efficiency"},
#             barmode="group",
#         )
#         .update_traces(texttemplate="%{text:0.0f}%")
#         .update_layout(title_x=0.5)
#     )

#     return fig_bar_detail

@reports.route("/dash")
# @login_required
def dash_entry():
    return dash_app.index()
