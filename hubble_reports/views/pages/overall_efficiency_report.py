import dash
import logging
import numpy as np
import pandas as pd
import plotly.express as px

from dash import dash_table, callback, dcc, html
from sqlalchemy import create_engine
from dash.dash_table.Format import Format, Symbol, Scheme
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from config import BaseConfig
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import get_logger


logger = get_logger(__name__, level=logging.DEBUG)

dash.register_page(
    __name__,
    path="/report",
)

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

df.rename(
    columns={
        "authorized_hours": "actual_efficiency",
        "name": "team",
        "entry_date": "date",
    },
    inplace=True,
)
df_overall_eff = df.copy()
df_overall_eff.loc[:, "capacity"] = 100 * df_overall_eff["actual_efficiency"] / df_overall_eff["expected_efficiency"]
df_overall_eff["capacity"] = df_overall_eff["capacity"].fillna(0)
df_overall_eff.replace(np.inf, 100.0, inplace=True)
df_overall_eff["date"] = pd.to_datetime(df_overall_eff["date"], format=r"%Y-%m-%d")

logger.info(f"\n\n\n\n========Info=======\n{df}\n")

min_year = df_overall_eff["date"].min().year
max_year = df_overall_eff["date"].max().year
till_date = df_overall_eff["date"].max().strftime("%B %Y")

df_overall_eff = df_overall_eff.groupby("team").mean(numeric_only=True)["capacity"].reset_index()
df_overall_eff["ratings"] = df_overall_eff["capacity"].apply(
    lambda a: "Excellent" if a > 121 else "Good" if a > 120 else "Needs Improvement"
)
df_overall_eff["trends"] = df_overall_eff["capacity"].apply(
    lambda a: "↑" if a > 121 else "↔︎" if a > 120 else "↓"
)

fig_bar = (
    px.histogram(
        df_overall_eff,
        x="team",
        y="capacity",
        color="team",
        text_auto=True,
        # text="capacity",
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
                # animate=True,
            ),
            href="/dash/detail-report",
        ),
        dash_table.DataTable(
            data=df_overall_eff.to_dict("records"),
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


@callback(
    Output("session", "data"),
    Input("overall_efficiency", "clickData"),
)
def display_click_data(clickdata):
    logger.info(f"\n\n\n\n========ClickData=======\n{clickdata}\n")

    if not clickdata:
        raise PreventUpdate
    print("\n\n\nCallback_context:\n", clickdata["points"][0]["x"], "\n\n\n")

    column = clickdata["points"][0]["x"]

    return column