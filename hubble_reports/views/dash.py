import dash
import pandas as pd
import pathlib
import plotly.express as px
import logging

from dash import Dash, dcc, html, callback, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import date, datetime, timedelta
from dateutil import relativedelta
from flask import render_template_string
from flask_login import login_required
from flask.helpers import get_root_path
from sqlalchemy import create_engine

from app import app
from config import BaseConfig
from hubble_reports.hubble_reports import reports
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import str_dat_to_nstr_date, get_logger

logger = get_logger(__name__, logging.DEBUG)


style_dash = (
    pathlib.Path(get_root_path(__name__)).parent.joinpath("static").joinpath("style")
)

dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname="/report/",
    assets_folder=style_dash,  # For setting css style
)

db_conn = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)

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
                                                                    "Fiscal year",
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
            className="overflow-auto grow content-page bg-white",
            children=html.Div(
                className="px-5 h-full bg-white",
                children=[
                    html.Div(
                        id="page-content",
                        children=[
                            html.Div(
                                id="overall_eff",
                                children=[
                                    dcc.Loading(
                                        type="default",
                                        children=[
                                            dcc.Graph(
                                                id="overall_efficiency",
                                                config={"displaylogo": False},
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dcc.Loading(
                                type="default",
                                children=html.Div(
                                    id="detail_efficiency",
                                    children=html.H3(
                                        "Note: Click on the graph to display corresponding teams detail report"
                                    ),
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ),
        dcc.Store(id="team_selected", storage_type="session"),
        dcc.Store(id="min_date_range", storage_type="session"),
        dcc.Store(id="max_date_range", storage_type="session"),
    ],
)

# For storing in session and updating the date range picker
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
        # Default date range on login is fiscal year April till last working friday
        st_date = date.today()
        st_date = st_date - timedelta(days=st_date.weekday() + 3)
        end_date = date(
            year=st_date.year - (1 if st_date.month < 4 else 0), month=4, day=1
        )

    if "one_month_button" == ctx.triggered_id:
        st_date = date.today()
        end_date = st_date - relativedelta.relativedelta(
            months=+1, days=+st_date.day - 1
        )
        st_date = st_date - timedelta(days=st_date.day)

    elif "six_month_button" == ctx.triggered_id:
        st_date = date.today()
        end_date = st_date - relativedelta.relativedelta(
            months=+6, days=+st_date.day - 1
        )
        st_date = st_date - timedelta(days=st_date.day)
        logger.info(
            f"\n\n=====>\nMonth{st_date}\n\t{st_date - timedelta(days=st_date.day)}"
        )

    elif "one_year_button" == ctx.triggered_id:
        st_date = date.today()
        st_date = st_date - timedelta(days=st_date.weekday() + 3)
        end_date = date(
            year=st_date.year - (1 if st_date.month < 4 else 0), month=4, day=1
        )
        logger.info(f"\n\nMonth:\t{end_date}\n")
    return st_date, end_date, end_date, st_date


# For modifying headers
@callback(
    Output("report-main-header", "children"),
    Output("report-sub-header", "children"),
    Input("url", "pathname"),
    Input("max_date_range", "data"),
    Input("min_date_range", "data"),
    State("team_selected", "data"),
)
def header_update(pathname, st_date, end_date, team):
    title = dash.no_update
    sub_title = dash.no_update
    logger.debug(f"\n\n\n\n========>\nPath name:\n{pathname}")
    logger.debug(f"\n\n=====>\nStartDate:\n{st_date}\nEndDate:\n{end_date}\n\n")
    if pathname == "/report":
        title = (
            f"Efficiency bandwidth- Fiscal Year "
            + f"{str_dat_to_nstr_date(st_date, r'%Y-%m-%d', r'%B-%Y')}"
            + f" - {str_dat_to_nstr_date(end_date, r'%Y-%m-%d', r'%B-%Y')} "
            + f"(Till, {str_dat_to_nstr_date(end_date, r'%Y-%m-%d', r'%B %d, %Y')})",
        )
        sub_title = f"Overall Efficiency & Detailed Report"
    elif pathname == "/report/detail-report":
        title = f"Detailed Report for {team} in total hours"
        sub_title = f"Team wise Efficiency"
    else:
        ...
    return title, sub_title


# For Overall efficiency report
@callback(
    Output("overall_efficiency", "figure"),
    Input("min_date_range", "data"),
    Input("max_date_range", "data"),
)
def update_figure_1(st_date, end_date):
    # Below st_date and end_date received are not exactly min date & max date, so it is corrected
    val1 = datetime.strptime(st_date, r"%Y-%m-%d")
    val2 = datetime.strptime(end_date, r"%Y-%m-%d")
    st_date = min(val1, val2).strftime(r"%Y-%m-%d")
    end_date = max(val1, val2).strftime(r"%Y-%m-%d")

    df = pd.read_sql_query(
        db.session.query(
            db.func.avg(
                100
                * (
                    (
                        TimesheetEntry.authorized_hours
                        / ExpectedUserEfficiency.expected_efficiency
                    )
                )
            ).label("capacity"),
            Team.name.label("team"),
        )
        .join(
            ExpectedUserEfficiency,
            TimesheetEntry.user_id == ExpectedUserEfficiency.user_id,
        )
        .join(Team, TimesheetEntry.team_id == Team.id)
        .filter(
            db.and_(
                (st_date <= TimesheetEntry.entry_date),
                (TimesheetEntry.entry_date <= end_date),
            ),
        )
        .group_by(Team.name)
        .statement,
        db_conn,
    )
    df["ratings"] = df["capacity"].apply(
        lambda a: "Excellent" if a > 100 else "Good" if a >= 90 else "Needs Improvement"
    )
    df["trends"] = df["capacity"].apply(
        lambda a: "↑" if a > 100 else "↔︎" if a > 90 else "↓"
    )
    df["customdata"] = "/report/detail-report"

    fig_bar = px.line(
        df,
        x="team",
        y="capacity",
        text="capacity",
        height=450,
        labels={"team": "Teams", "capacity": "Capacity"},
        hover_data={
            "capacity": ":.1f",
            "ratings": True,
        },
        title="Overall Efficiency",
    ).update_traces(
        texttemplate="<b>%{y:0.01f}%</b>",
        textposition="top left",
        marker=dict(size=15, color="rgb(34,72,195)"),
        line_color="rgb(34,72,195)",
    )
    fig_bar.update_layout(
        xaxis_title=None,
        plot_bgcolor="white",
        hovermode="x",
        height=350,
        margin={
            "l": 0,
            "r": 30,
            "t": 25,
            "b": 30,
        },
        title_x=0.5,
        title_y=0.98,
    )

    low_y = df["capacity"].min() - 10
    high_y = df["capacity"].max() + 20
    fig_bar.update_yaxes(title="Capacity, (%)", range=[low_y, high_y])
    fig_bar.add_hrect(
        y0=high_y,
        y1=100,
        annotation_text="<b>Excellent</b>",
        annotation_position="top right",
        fillcolor="green",
        opacity=0.2,
        line_width=0,
    )
    fig_bar.add_hrect(
        y0=100,
        y1=90,
        annotation_text="<b>Good</b>",
        annotation_position="right",
        fillcolor="blue",
        opacity=0.1,
        line_width=0,
    )
    fig_bar.add_hrect(
        y0=90,
        y1=low_y,
        annotation_text="<b>Need Improvement</b>",
        annotation_position="bottom right",
        fillcolor="red",
        opacity=0.2,
        line_width=0,
    )
    return fig_bar


# For Detailed Efficiency report
@callback(
    Output("detail_efficiency", "children"),
    Input("team_selected", "data"),
    Input("min_date_range", "data"),
    Input("max_date_range", "data"),
    prevent_initial_callbacks=False,
)
def detailed_eff(team, min_date_sess, max_date_sess):
    # Below st_date and end_date received are not exactly min date & max date, so it is corrected
    if not team:
        return PreventUpdate
    val1 = datetime.strptime(min_date_sess, r"%Y-%m-%d")
    val2 = datetime.strptime(max_date_sess, r"%Y-%m-%d")
    min_date_sess = min(val1, val2).strftime(r"%Y-%m-%d")
    max_date_sess = max(val1, val2).strftime(r"%Y-%m-%d")

    df = pd.read_sql_query(
        db.session.query(
            db.func.date_trunc("month", TimesheetEntry.entry_date).label(
                "display_date"
            ),
            db.func.sum(TimesheetEntry.authorized_hours).label("actual_hours"),
            db.func.sum(ExpectedUserEfficiency.expected_efficiency).label(
                "expected_hours"
            ),
        )
        .join(TimesheetEntry, TimesheetEntry.user_id == ExpectedUserEfficiency.user_id)
        .join(Team, Team.id == TimesheetEntry.team_id)
        .filter(
            db.and_(
                Team.name == team,
                db.and_(
                    (min_date_sess <= TimesheetEntry.entry_date),
                    (TimesheetEntry.entry_date <= max_date_sess),
                ),
            )
        )
        .group_by(db.func.date_trunc("month", TimesheetEntry.entry_date))
        .order_by(db.func.date_trunc("month", TimesheetEntry.entry_date))
        .statement,
        con=db_conn,
        parse_dates=["display_date"],
    )

    df = pd.DataFrame(
        pd.melt(
            df,
            id_vars=["display_date"],
            value_vars=["actual_hours", "expected_hours"],
            var_name="efficiency",
            value_name="efficiency_value",
        )
    )
    df["formated_date"] = df.display_date.dt.strftime(r"%b %Y")

    fig_bar_detail = px.bar(
        data_frame=df,
        x="formated_date",
        y="efficiency_value",
        color="efficiency",
        text="efficiency_value",
        title=f"{team} Team Efficiency",
        labels={"formated_date": "Time", "efficiency_value": "Efficiency"},
        barmode="group",
    ).update_traces(texttemplate="%{text:0}")
    fig_bar_detail.update_xaxes(tickmode="array", title=None)
    fig_bar_detail.update_layout(
        plot_bgcolor="white",
        height=325,
        margin={
            "l": 0,
            "r": 30,
            "t": 15,
            "b": 25,
        },
        title_x=0.5,
        title_y=0.97,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.97,
            xanchor="right",
            x=1,
            title="Approved Hours:",
        ),
        yaxis_title="Efficiency, (hrs)",
    )
    labels = {"actual_hours": "Actual Hours", "expected_hours": "Expected Hours"}
    fig_bar_detail.for_each_trace(lambda t: t.update(name=labels[t.name]))
    detail_layout = (
        dcc.Graph(
            id="detailed_efficiency_chart",
            figure=fig_bar_detail,
            config={"displaylogo": False},
        ),
    )
    return detail_layout


@callback(
    Output("team_selected", "data"),
    Input("overall_efficiency", "clickData"),
)
def store_data(clickdata):
    if not clickdata:
        raise PreventUpdate
    team = clickdata["points"][0]["x"]
    return team


@reports.route("/report")
@login_required
def dash_entry():
    return dash_app.index()
