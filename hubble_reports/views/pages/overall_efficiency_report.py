import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    path="/overall-report",
)

db_conn = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)
layout = html.Div(
    id="overall_eff_1",
    children=[
        
            dcc.Loading(
                 type='default',
                children=dcc.Link(
                children=[
                    dcc.Graph(
                    id="overall_efficiency_1",
                animate=True,
            ),],
            href="/report/detail-report",
            ),
            
        ),
    ],
)


@callback(
    Output("overall_efficiency_1", "figure"),
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
                    (TimesheetEntry.authorized_hours
                    / ExpectedUserEfficiency.expected_efficiency)
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
    df['customdata']='/report/detail-report'

    fig_bar = (
        px.line(
            df,
            x="team",
            y="capacity",
            text="capacity",
            height=450,
            labels={"team": "Teams", "capacity": "Capacity"},
            hover_data={
                'capacity':':.1f',
                'ratings':True,
                },
        )
        .update_traces(
            texttemplate="<b>%{y:0.01f}%</b>", 
            textposition="top left", 
            marker=dict(size=15, color='rgb(34,72,195)'),
            line_color="rgb(34,72,195)",
            )
    )
    fig_bar.update_layout(
        plot_bgcolor="white", 
        hovermode='x', 
        modebar_activecolor='orange',
        modebar={
                "bgcolor": "rgba(0,0,0,0)",
                "color":"rgba(0,0,0,0.1)",
                },
                )
    
    low_y = df["capacity"].min() - 10
    high_y = df["capacity"].max() + 20
    fig_bar.update_yaxes(range=[low_y, high_y])
    fig_bar.add_hrect(y0=high_y, y1=100, 
              annotation_text="<b>Excellent</b>", annotation_position="top right",
              fillcolor="green", opacity=0.2, line_width=0)
    fig_bar.add_hrect(y0=90, y1=100, 
              annotation_text="<b>Good</b>", annotation_position="right",
              fillcolor="blue", opacity=0.1, line_width=0)
    fig_bar.add_hrect(y0=low_y, y1=90, 
              annotation_text="<b>Need Improvement</b>", annotation_position="bottom right",
              fillcolor="red", opacity=0.2, line_width=0)
    return fig_bar

    
@callback(
    Output("team_selected", "data"),
    Input("overall_efficiency_1", "clickData"),
)
def store_data(clickdata):
    if not clickdata:
        raise PreventUpdate
    column = clickdata["points"][0]["x"]
    return column
