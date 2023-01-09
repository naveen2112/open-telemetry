import dash
import pandas as pd
import plotly.express as px

from dash import dash_table, callback, dcc, html
from sqlalchemy import create_engine
from dash.dash_table.Format import Format, Symbol, Scheme
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from datetime import datetime

from config import BaseConfig
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import for_str_date_to_new_str_date


dash.register_page(
    __name__,
    path="/overall-efficiency",
)

db_conn = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
layout = html.Div(
    id="overall_eff",
    children=[
        dcc.Link(
            dcc.Graph(
                id="overall_efficiency",
                animate=True,
            ),
            href="/report/detail-report",
        ),
        dash_table.DataTable(
            id="overall_efficiency_table",
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
            style_table={
                "margin-left": "auto",
                "margin-right": "auto",
                "padding-bottom": "1.25rem",
            },
        ),
    ],
)


@callback(
    Output("nav-ref", "children"),
    Output("report-main-header", "children"),
    Output("report-sub-header", "children"),
    Output("overall_efficiency", "figure"),
    Output("overall_efficiency_table", "data"),
    Input("min_date_range", "data"),
    Input("max_date_range", "data"),
)
def update_figure(st_date, end_date):
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
                    TimesheetEntry.authorized_hours
                    / ExpectedUserEfficiency.expected_efficiency
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
        lambda a: "Excellent" if a > 121 else "Good" if a > 120 else "Needs Improvement"
    )
    df["trends"] = df["capacity"].apply(
        lambda a: "↑" if a > 121 else "↔︎" if a > 120 else "↓"
    )

    fig_bar = (
        px.bar(
            df,
            x="team",
            y="capacity",
            color="team",
            text_auto=True,
            text="capacity",
            height=360,
            labels={"team": "Teams", "capacity": "Capacity"},
        )
        .update_traces(texttemplate="%{y:0.0f}%")
        .update_layout(title_x=0.5)
    )
    fig_bar.update_layout(transition={"duration": 1000}, plot_bgcolor="white")
    fig_bar.add_hline(y=100, line_dash="dash", line_color="magenta")
    title = (
        f"Teams Efficiency bandwidth- Fiscal Year {for_str_date_to_new_str_date(st_date, r'%Y-%m-%d', r'%B-%Y')} - {for_str_date_to_new_str_date(end_date, r'%Y-%m-%d', r'%B-%Y')} (Till, {for_str_date_to_new_str_date(end_date, r'%Y-%m-%d', r'%B %d, %Y')})",
    )
    sub_title = "Overall team efficiency"
    nav_item = (
        dcc.Link(
            "< Back to Index page",
            href="/report",
            className="flex items-center text-sm text-dark-blue",
        ),
    )
    return nav_item, title, sub_title, fig_bar, df.to_dict("records")


@callback(
    Output("team_selected", "data"),
    Input("overall_efficiency", "clickData"),
)
def store_data(clickdata):
    if not clickdata:
        raise PreventUpdate
    column = clickdata["points"][0]["x"]
    return column
