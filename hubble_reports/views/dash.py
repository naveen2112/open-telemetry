import dash
import pathlib
import logging

from dash import Dash, dcc, html, callback, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate 
from datetime import date
from dateutil import relativedelta
from flask import render_template_string
from flask_login import login_required
from flask.helpers import get_root_path

from app import app
from hubble_reports.hubble_reports import reports
from hubble_reports.utils import for_str_date_to_new_str_date, get_logger

logger = get_logger(__name__, logging.DEBUG)


style_dash = (
    pathlib.Path(get_root_path(__name__)).parent.joinpath("static").joinpath("style")
)

dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname="/report/",
    use_pages=True,
    assets_folder=style_dash,  # For setting css style
)

# FYI, you need both an app context and a request context to use url_for() in the Jinja2 templates
with app.app_context(), app.test_request_context():
    layout_dash = (
        pathlib.Path(get_root_path(__name__))
        .parent.joinpath("templates")
        .joinpath("dashboard.html")
    )

    with open(layout_dash, "r") as f:
        html_body = render_template_string(f.read())
        html_body = html_body.replace("HEADER", "Welcome User!!!")
dash_app.index_string = html_body

dash_app.layout = html.Div(
    className="overflow-hidden max-h-screen flex main-screen grow flex-col",
    children=[
        html.Div(
            className="header bg-white",
            children=html.Div(
                className="px-10 pt-5",
                children=[
                    dcc.Link(
                        id="nav-ref",
                        href="",
                    ),
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
                                        style={"width": 300},
                                        children=[
                                            html.Tr(
                                                html.Td(
                                                    dcc.DatePickerRange(
                                                        id="date-range-picker",
                                                        max_date_allowed=date.today(),
                                                    ),
                                                    colSpan=3,
                                                ),
                                            ),
                                            html.Tr(
                                                [
                                                    html.Td(
                                                        html.Div(
                                                            [
                                                                html.Button(
                                                                    "1 month",
                                                                    id="one_month_button",
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
                                                                    id="six_month_button",
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
                                                                    "1 year",
                                                                    id="one_year_button",
                                                                    n_clicks=0,
                                                                    className="bg-dark-blue text-white text-sm flex items-center justify-center w-20 cursor-default grow filter-button",
                                                                ),
                                                            ]
                                                        ),
                                                    ),
                                                ]
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ),
        dcc.Location(id="url", refresh=False),
        html.Div(
            className="overflow-auto grow bg-light-violet content-page",
            children=html.Div(
                className="px-5 h-full",
                children=[
                    dash.page_container,
                ],
            ),
        ),
        dcc.Store(id="team_selected", storage_type="session"),
        dcc.Store(id="min_date_range", storage_type="session"),
        dcc.Store(id="max_date_range", storage_type="session"),
    ],
)


@callback(
    Output("min_date_range", "data"),
    Output("max_date_range", "data"),
    Output("date-range-picker", "start_date"),
    Output("date-range-picker", "end_date"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),
    Input("one_month_button", "n_clicks"),
    Input("six_month_button", "n_clicks"),
    Input("one_year_button", "n_clicks"),
)
def update_date_range(end_date, st_date, btn1, btn2, btn3):

    if (not st_date) and (not end_date):
        st_date = date.today()
        end_date = st_date - relativedelta.relativedelta(
            months=+6, days=+st_date.day - 1
        )
    if "one_month_button" == ctx.triggered_id:
        st_date = date.today()
        end_date = st_date - relativedelta.relativedelta(
            months=+1, days=+st_date.day - 1
        )
    elif "six_month_button" == ctx.triggered_id:
        st_date = date.today()
        end_date = st_date - relativedelta.relativedelta(
            months=+6, days=+st_date.day - 1
        )
    elif "one_year_button" == ctx.triggered_id:
        st_date = date.today()
        end_date = st_date - relativedelta.relativedelta(
            years=+1, days=+st_date.day - 1
        )
    return st_date, end_date, end_date, st_date

@callback(
    Output("report-main-header", "children"),
    Output("report-sub-header", "children"),
    Input("url","pathname"),
    Input("max_date_range", "data"),
    Input("min_date_range", "data"),
    State("team_selected", "data"),
    )
def header_update(pathname, st_date, end_date, team):
    title = dash.no_update
    sub_title = dash.no_update
    logger.debug(f"\n\n\n\n========>\nPath name:\n{pathname}")
    logger.debug(f"\n\n=====>\nStartDate:\n{st_date}\nEndDate:\n{end_date}\n\n")
    if pathname == '/report/overall-efficiency':
        title = f"Teams Efficiency bandwidth- Fiscal Year {for_str_date_to_new_str_date(st_date, r'%Y-%m-%d', r'%B-%Y')} - {for_str_date_to_new_str_date(end_date, r'%Y-%m-%d', r'%B-%Y')} (Till, {for_str_date_to_new_str_date(end_date, r'%Y-%m-%d', r'%B %d, %Y')})",
        sub_title = f"Overall Efficiency"
    elif pathname == '/report/detail-report':
        title = f"Detailed Report for {team} in total hours"
        sub_title = f"Team wise Efficiency"
    else:
        ...
    return title, sub_title

@reports.route("/report")
@login_required
def dash_entry():
    return dash_app.index()
