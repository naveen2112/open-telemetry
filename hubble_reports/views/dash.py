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

db_connection = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)

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
                        id="page-content",
                        children=[
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
                        ],
                    ),
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


# For modifying headers
@callback(
    Output("report-main-header", "children"),
    Output("report-sub-header", "children"),
    Input("url", "pathname"),
    Input("min-date-range", "data"),
    Input("max-date-range", "data"),
    State("team-selected", "data"),
)
def header_update(pathname, st_date, end_date, team):
    title = dash.no_update
    sub_title = dash.no_update
    if pathname == "/":
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
    Output("overall-efficiency", "figure"),
    Input("min-date-range", "data"),
    Input("max-date-range", "data"),
)
def overall_efficiency_report(st_date, end_date):

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
            Team.id.label("team_id"),
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
        .group_by(
            Team.name,
            Team.id,
        )
        .statement,
        db_connection,
    )
    df["ratings"] = df["capacity"].apply(
        lambda a: "Excellent" if a > 100 else "Good" if a >= 90 else "Needs Improvement"
    )
    df["trends"] = df["capacity"].apply(
        lambda a: "↑" if a > 100 else "↔︎" if a > 90 else "↓"
    )

    overall_line_chart = px.line(
        df,
        x="team",
        y="capacity",
        text="capacity",
        height=450,
        labels={"team": "Teams", "capacity": "Capacity"},
        hover_data={
            "capacity": ":.1f",
            "ratings": True,
            "team_id": False,
        },
        title="Overall Efficiency",
    ).update_traces(
        texttemplate="<b>%{y:0.01f}%</b>",
        textposition="top left",
        marker=dict(size=15, color="rgb(34,72,195)"),
        line_color="rgb(34,72,195)",
    )
    overall_line_chart.update_layout(
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
        transition={
            "duration": 500,
        },
    )

    y_range_min = df["capacity"].min() - 10
    y_range_max = df["capacity"].max() + 20
    overall_line_chart.update_yaxes(
        title="Capacity, (%)", range=[y_range_min, y_range_max]
    )
    overall_line_chart.add_hrect(
        y0=y_range_max,
        y1=100,
        annotation_text="<b>Excellent</b>",
        annotation_position="top right",
        fillcolor="green",
        opacity=0.2,
        line_width=0,
    )
    overall_line_chart.add_hrect(
        y0=100,
        y1=90,
        annotation_text="<b>Good</b>",
        annotation_position="right",
        fillcolor="blue",
        opacity=0.1,
        line_width=0,
    )
    overall_line_chart.add_hrect(
        y0=90,
        y1=y_range_min,
        annotation_text="<b>Need Improvement</b>",
        annotation_position="bottom right",
        fillcolor="red",
        opacity=0.2,
        line_width=0,
    )
    return overall_line_chart


# For Detailed Efficiency report
@callback(
    Output("detail-efficiency", "children"),
    Input("team-selected", "data"),
    Input("min-date-range", "data"),
    Input("max-date-range", "data"),
    prevent_initial_callbacks=False,
)
def detailed_efficiency_report(team, min_date_sess, max_date_sess):

    if not team:
        return PreventUpdate

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
                Team.id == team["id"],
                db.and_(
                    (min_date_sess <= TimesheetEntry.entry_date),
                    (TimesheetEntry.entry_date <= max_date_sess),
                ),
            )
        )
        .group_by(db.func.date_trunc("month", TimesheetEntry.entry_date))
        .order_by(db.func.date_trunc("month", TimesheetEntry.entry_date))
        .statement,
        con=db_connection,
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

    detail_bar_chart = px.bar(
        data_frame=df,
        x="formated_date",
        y="efficiency_value",
        color="efficiency",
        text="efficiency_value",
        title=f"{team['name']} Team Efficiency",
        labels={"formated_date": "Time", "efficiency_value": "Efficiency"},
        barmode="group",
    ).update_traces(texttemplate="%{text:0}")
    detail_bar_chart.update_xaxes(tickmode="array", title=None)
    detail_bar_chart.update_layout(
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
        transition={
            "duration": 500,
        },
    )
    labels = {"actual_hours": "Actual Hours", "expected_hours": "Expected Hours"}
    detail_bar_chart.for_each_trace(lambda t: t.update(name=labels[t.name]))
    detail_layout = (
        dcc.Graph(
            id="detailed_efficiency_chart",
            figure=detail_bar_chart,
            config={"displaylogo": False},
        ),
    )
    return detail_layout


@callback(
    Output("team-selected", "data"),
    Input("overall-efficiency", "clickData"),
)
def store_data(clickdata):
    if not clickdata:
        raise PreventUpdate
    team = {
        "id": clickdata["points"][0]["customdata"][1],
        "name": clickdata["points"][0]["x"],
    }
    return team


@reports.route("/")
@login_required
def dash_index():
    return dash_app.index()
