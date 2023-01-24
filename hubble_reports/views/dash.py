import dash
import pandas as pd
import pathlib
import plotly.express as px

from dash import Dash, dcc, html, callback, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import date, timedelta
from dateutil import relativedelta
from flask import render_template_string, current_app
from flask_login import login_required
from flask.helpers import get_root_path
from sqlalchemy import create_engine

from app import app
from hubble_reports.hubble_reports import reports
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import str_dat_to_nstr_date


style_dash = pathlib.Path(get_root_path(__name__)).parent.joinpath("static")

dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname="/",
    assets_folder=style_dash,  # For setting css style
    assets_url_path="static",
    use_pages=True,
)

for view_func in app.view_functions:
    if view_func.startswith(dash_app.config["routes_pathname_prefix"]):
        app.view_functions[view_func] = login_required(app.view_functions[view_func])

# db_connection = create_engine(current_app.config.get("SQLALCHEMY_DATABASE_URI"))

# FYI, you need both an app context and a request context to use url_for() in the Jinja2 templates
with app.app_context(), app.test_request_context():
    layout_dash = (
        pathlib.Path(get_root_path(__name__))
        .parent.joinpath("templates")
        .joinpath("dashboard.html")
    )

    with open(layout_dash, "r") as f:
        html_body = render_template_string(f.read())
dash_app.index_string = html_body

dash_app.layout = html.Div(
    className="overflow-hidden max-h-screen flex main-screen grow flex-col",
    children=[
        html.Div(
            className="header bg-white",
            children=html.Div(
                className="px-10 pt-5",
                children=[
                    html.Div(
                        className="flex justify-between mb-7 items-center",
                        children=[
                            html.Div(
                                className="text-dark-black text-lg mb-1 leading-none",
                                children=[
                                    html.H1(
                                        id="report-main-header",
                                        children=["HEADER FOR THE FILE"],
                                    ),
                                    html.Div(
                                        id="report-sub-header",
                                        className="text-dark-black-50 text-sm",
                                        children=[
                                            html.H2("SUBHEADER FOR THE FILE"),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                title='Enter in "MM/DD/YYYY" format',
                                children=[
                                    html.Table(
                                        style={"width": 288},
                                        children=[
                                            html.Tr(
                                                html.Td(
                                                    dcc.DatePickerRange(
                                                        id="date-range-picker",
                                                        max_date_allowed=date.today(),
                                                        display_format="DD-MM-YYYY",
                                                        stay_open_on_select=True,
                                                        updatemode="bothdates",
                                                    ),
                                                    colSpan=3,
                                                ),
                                                style={
                                                    "textAlign": "center",
                                                },
                                            ),
                                            html.Tr(
                                                [
                                                    html.Td(
                                                        html.Div(
                                                            [
                                                                html.Button(
                                                                    "1 month",
                                                                    id="one-month-button",
                                                                    n_clicks=0,
                                                                    className="bg-dark-blue text-white text-sm flex items-center justify-center w-20 cursor-default grow filter-button",
                                                                ),
                                                            ]
                                                        )
                                                    ),
                                                    html.Td(
                                                        html.Div(
                                                            [
                                                                html.Button(
                                                                    "6 months",
                                                                    id="six-month-button",
                                                                    n_clicks=0,
                                                                    className="bg-dark-blue text-white text-sm flex items-center justify-center w-20 cursor-default grow filter-button",
                                                                ),
                                                            ],
                                                        ),
                                                        style={
                                                            "textAlign": "center",
                                                        },
                                                    ),
                                                    html.Td(
                                                        html.Div(
                                                            [
                                                                html.Button(
                                                                    "Fiscal year",
                                                                    id="one-year-button",
                                                                    n_clicks=0,
                                                                    className="bg-dark-blue text-white text-sm flex items-center justify-center w-20 cursor-default grow filter-button",
                                                                ),
                                                            ]
                                                        ),
                                                        style={
                                                            "textAlign": "right",
                                                        },
                                                    ),
                                                ]
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Link(rel="stylesheet", href="/static/style/style.css"),
                ],
            ),
        ),
        dcc.Location(id="url", refresh=False),
        html.Div(
            className="overflow-auto grow content-page bg-white",
            children=html.Div(
                className="px-5 h-full bg-white",
                children=[
                    html.Div(
                        id = 'home-page',
                    ),
                    dash.page_container,
                ],
            ),
        ),
        dcc.Store(id="team-selected", storage_type="session"),
        dcc.Store(id="min-date-range", storage_type="session"),
        dcc.Store(id="max-date-range", storage_type="session"),
    ],
)


# For storing in session and updating the date range picker
@callback(
    Output("min-date-range", "data"),
    Output("max-date-range", "data"),
    Output("date-range-picker", "start_date"),
    Output("date-range-picker", "end_date"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("one-month-button", "n_clicks"),
    Input("six-month-button", "n_clicks"),
    Input("one-year-button", "n_clicks"),
)
def update_date_range(st_date, end_date, btn1, btn2, btn3):

    if (not st_date) and (not end_date):
        # Default date range on login is fiscal year April till last working friday
        end_date = date.today()
        end_date = end_date - timedelta(days=end_date.weekday() + 3)
        st_date = date(
            year=end_date.year - (1 if end_date.month < 4 else 0), month=4, day=1
        )

    if "one-month-button" == ctx.triggered_id:
        end_date = date.today()
        st_date = end_date - relativedelta.relativedelta(
            months=+1, days=+end_date.day - 1
        )
        end_date = end_date - timedelta(days=end_date.day)

    elif "six-month-button" == ctx.triggered_id:
        end_date = date.today()
        st_date = end_date - relativedelta.relativedelta(
            months=+6, days=+end_date.day - 1
        )
        end_date = end_date - timedelta(days=end_date.day)

    elif "one-year-button" == ctx.triggered_id:
        end_date = date.today()
        end_date = end_date - timedelta(days=end_date.weekday() + 3)
        st_date = date(
            year=end_date.year - (1 if end_date.month < 4 else 0), month=4, day=1
        )
    return st_date, end_date, st_date, end_date


# For modifying headers & home page content
@callback(
    Output("report-main-header", "children"),
    Output("report-sub-header", "children"),
    Output("home-page","children"),
    Input("url", "pathname"),
    Input("min-date-range", "data"),
    Input("max-date-range", "data"),
    State("team-selected", "data"),
)
def header_update(pathname, st_date, end_date, team):
    title = dash.no_update
    sub_title = dash.no_update
    home_page = ''
    if pathname == "/efficiency":
        title = (
            f"Efficiency bandwidth- Fiscal Year "
            + f"{str_dat_to_nstr_date(st_date, r'%Y-%m-%d', r'%B-%Y')}"
            + f" - {str_dat_to_nstr_date(end_date, r'%Y-%m-%d', r'%B-%Y')} "
            + f"(Till, {str_dat_to_nstr_date(end_date, r'%Y-%m-%d', r'%B %d, %Y')})",
        )
        sub_title = f"Overall Efficiency & Detailed Report"
    elif pathname == "/monetization":
        title = (
            f"Monetization Gap report for teams"
            # + f"{str_dat_to_nstr_date(st_date, r'%Y-%m-%d', r'%B-%Y')}"
            # + f" - {str_dat_to_nstr_date(end_date, r'%Y-%m-%d', r'%B-%Y')} "
            # + f"(Till, {str_dat_to_nstr_date(end_date, r'%Y-%m-%d', r'%B %d, %Y')})",
        )
        sub_title = (f"{str_dat_to_nstr_date(st_date, r'%Y-%m-%d', r'%B-%Y')}"
            + f" - {str_dat_to_nstr_date(end_date, r'%Y-%m-%d', r'%B-%Y')} "
            + f"(Till, {str_dat_to_nstr_date(end_date, r'%Y-%m-%d', r'%B %d, %Y')})",)
    elif pathname == "/":
       title = 'Dash Board for Reports'
       sub_title = ''
       home_page =     html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
                if page['name'] != 'Not found 404'
        ]
    ),
    else:
        ...
    return title, sub_title, home_page


@reports.route("/")
@login_required
def dash_index():
    return dash_app.index()
