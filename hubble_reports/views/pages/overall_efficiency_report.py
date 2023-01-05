import dash
import logging
import pandas as pd
import plotly.express as px

from dash import dash_table, callback, dcc, html
from sqlalchemy import create_engine
from dash.dash_table.Format import Format, Symbol, Scheme
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from datetime import date
from dateutil import relativedelta

from config import BaseConfig
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import get_logger


logger = get_logger(__name__, level=logging.DEBUG)

dash.register_page(
    __name__,
    path="/overall-efficiency",
)

db_conn = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
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
        ExpectedUserEfficiency, TimesheetEntry.user_id == ExpectedUserEfficiency.user_id
    )
    .join(Team, TimesheetEntry.team_id == Team.id)
    .group_by(Team.name)
    .statement,
    db_conn,
)




pd.read_sql_query(db.session.query(db.func.avg(100 * (TimesheetEntry.authorized_hours/ExpectedUserEfficiency.expected_efficiency)).label("capacity"), Team.name.label("team")).join(ExpectedUserEfficiency, TimesheetEntry.user_id == ExpectedUserEfficiency.user_id).join(Team, TimesheetEntry.team_id == Team.id).group_by(Team.name).statement, db_conn,)




df_date = pd.read_sql_query(
    db.session.query(
        db.func.min(TimesheetEntry.entry_date).label("min_date"),
        db.func.max(TimesheetEntry.entry_date).label("max_date"),
    )
    .join(
        ExpectedUserEfficiency, TimesheetEntry.user_id == ExpectedUserEfficiency.user_id
    )
    .statement,
    parse_dates=["min_date", "max_date"],
    con=db_conn,
)

min_year = df_date["min_date"].dt.year[0]
max_year = df_date["max_date"].dt.year[0]
till_date = df_date["max_date"].dt.strftime("%B %Y")[0]

df["ratings"] = df["capacity"].apply(
    lambda a: "Excellent" if a > 121 else "<h1>Good</h1>" if a > 120 else "Needs Improvement"
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
        title="Teams Capacity - Efficiency %",
        labels={"team": "Teams", "capacity": "Capacity"},
    )
    .update_traces(texttemplate="%{y:0.0f}%")
    .update_layout(title_x=0.5)
)

layout = html.Div(
    id="overall_eff",
    children=[
        html.Div(
            children=[
                html.H1(
                    id="dash_header",
                    children=f"Overall Team wise Efficiency Percentage",
                    style={"font-size": "25px", "font-align": "center"},
                )
            ],
        ),
        html.Br(),
        dcc.Link("Back", href="/report"),
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
            ),
            href="/report/detail-report",
        ),
        dash_table.DataTable(
            data=df.to_dict("records"),
            # columns=[{"name": i, "id": i} for i in df.columns],   #To give overall columns in a single statement
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


@callback(
    Output("team_selected", "data"),
    Output("min_date_range", "data"),
    Output("max_date_range", "data"),
    Input("overall_efficiency", "clickData"),
)
def display_click_data(clickdata):
    if not clickdata:
        raise PreventUpdate
    column = clickdata["points"][0]["x"]
    max_date = date.today()
    min_date = max_date - relativedelta.relativedelta(months=+6)
    logger.debug(f'\n\n\nDefault dates:\nCurrent date:\n{str(max_date.strftime(r"%Y-%m-%d"))}\nLast 6 months:\n{str(min_date.strftime(r"%Y-%m-%d"))}')
    return column, str(min_date.strftime(r"%Y-%m-%d")), str(max_date.strftime(r"%Y-%m-%d"))
