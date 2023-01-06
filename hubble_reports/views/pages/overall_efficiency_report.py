import dash
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import dash_table, callback, dcc, html
from sqlalchemy import create_engine
from dash.dash_table.Format import Format, Symbol, Scheme
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from datetime import date, datetime
from dateutil import relativedelta

from config import BaseConfig
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import get_logger
from hubble_reports.utils import for_str_date_to_new_str_date


logger = get_logger(__name__, level=logging.DEBUG)

dash.register_page(
    __name__,
    path="/overall-efficiency",
)

db_conn = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
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
        html.H2(
            id="overall_efficiency_title",
        ),
        dcc.Link(
            dcc.Graph(
                id="overall_efficiency",
                # figure=fig_bar,
            ),
            href="/report/detail-report",
        ),
        # dcc.Graph(id='trail_table'),
        dash_table.DataTable(
            id="overall_efficiency_table",
            # data=df.to_dict("records"),
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
    Output("overall_efficiency_title", "children"),
    Output("overall_efficiency", "figure"),
    Output("overall_efficiency_table", "data"),
    # Output("trail_table", "figure"),
    Input("min_date_range", "data"),
    Input("max_date_range", "data"),
)
def update_figure(st_date, end_date):
    logger.debug(f"\n\n\nUPADATING THE FIGURE:\n\n")
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

    # pd.read_sql_query(db.session.query(db.func.avg(100 * (TimesheetEntry.authorized_hours/ExpectedUserEfficiency.expected_efficiency)).label("capacity"), Team.name.label("team")).join(ExpectedUserEfficiency, TimesheetEntry.user_id == ExpectedUserEfficiency.user_id).join(Team, TimesheetEntry.team_id == Team.id).group_by(Team.name).statement, db_conn,)

    df_date = pd.read_sql_query(
        db.session.query(
            db.func.min(TimesheetEntry.entry_date).label("min_date"),
            db.func.max(TimesheetEntry.entry_date).label("max_date"),
        )
        .join(
            ExpectedUserEfficiency,
            TimesheetEntry.user_id == ExpectedUserEfficiency.user_id,
        )
        .statement,
        parse_dates=["min_date", "max_date"],
        con=db_conn,
    )

    df["ratings"] = df["capacity"].apply(
        lambda a: "<h1>Excellent<\h1>"
        if a > 121
        else "<h1>Good</h1>"
        if a > 120
        else "Needs Improvement"
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
    title = (
        f"Teams Efficiency bandwidth- Fiscal Year {for_str_date_to_new_str_date(st_date, r'%Y-%m-%d', r'%B-%Y')} - {for_str_date_to_new_str_date(end_date, r'%Y-%m-%d', r'%B-%Y')} (Till, {for_str_date_to_new_str_date(end_date, r'%Y-%m-%d', r'%B %d, %Y')})",
    )
    logger.debug(f"\n\n\nUpdated Title:\t{title = }\n\n\n")

    """
    # Need to check

    
    # fig = go.Figure(data=[go.Table(
    #     header=dict(values=list(df.columns),
    #                 # fill_color='paleturquoise',
    #                 align='left'),
    #     cells=dict(values=[df.capacity, df.team, df.ratings, df.trends],
    #             # fill_color='lavender',
    #             align='left'))
    # ])"""
    return title, fig_bar, df.to_dict("records")  # , fig


@callback(
    Output("team_selected", "data"),
    Input("overall_efficiency", "clickData"),
)
def store_data(clickdata):
    if not clickdata:
        raise PreventUpdate
    column = clickdata["points"][0]["x"]
    return column
