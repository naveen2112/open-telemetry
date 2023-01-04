import dash
import logging
import pandas as pd
import plotly.express as px

from dash import callback, dcc, html
from sqlalchemy import create_engine
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from config import BaseConfig
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import get_logger


logger = get_logger(__name__, level=logging.DEBUG)

dash.register_page(
    __name__,
    path="/detail-report",
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

df["date"] = pd.to_datetime(df["date"], format=r"%Y-%m-%d")

df_detail_report = (
    df.groupby([df["date"], "team"],)
    .sum(numeric_only=True)[["actual_efficiency", "expected_efficiency"]]
    .reset_index()
)

df_detail_report = pd.DataFrame(
    pd.melt(
        df_detail_report,
        id_vars=["date", "team"],
        value_vars=["actual_efficiency", "expected_efficiency"],
        var_name="efficiency",
        value_name="efficiency_value",
    )
)
df_detail_report = df_detail_report.sort_values('date')


df_detail_report_slide = df_detail_report.groupby(df_detail_report['date'].dt.strftime(r"%Y %b"), sort=False) 
range_df_detail_report = df_detail_report_slide.sum(numeric_only=True).reset_index()

layout = html.Div(
    id="detailed_eff",
    children=[
        html.H1(id="detail-title", children=["Detail-report"]),


        html.Div(
            [
                dcc.DatePickerRange(
                    id="date-range-picker",
                    style={"width": 330},
                ),
            ]
        ),


        dcc.Graph(
            id="detailed_efficiency",
         
            ),
        html.H2('Slider'),
        html.Br(),
        dcc.RangeSlider(0, len(df_detail_report.groupby(df_detail_report['date'].dt.strftime(r"%Y %b"), sort=False)),
            marks={d: f"{range_df_detail_report.loc[d,'date']}" for d in range(len(df_detail_report_slide))},
            value=[0, len(df_detail_report_slide)],
            id='date_range'
        ),
        html.Div(id='date_range_picked')
    ],
)

@callback(
    Output("detailed_efficiency", "figure"),
    Input("team_selected", "data"),
    Input('date_range', 'value'),
    prevent_initial_callbacks=False,
)
def detailed_eff(data, val):
    
    # if not data:
    #     raise PreventUpdate
    logger.info(f"\n\n\nTeam Data clicked=====\n{data}\n\n")
    print(f"\n\nDetailed:\n{val}\n\n{data}\n\n")
    column = data
    df_range =  df_detail_report.groupby(df_detail_report['date'].dt.strftime(r"%Y %b"), sort=False).sum(numeric_only=True).iloc[val[0]:val[-1]].reset_index()
    print(f"\n\nMin range:\n{df_range['date'].min()}\n\nMax range:\n{df_range['date'].max()}\n\n")
    fig_bar_detail = (
        px.bar(
            data_frame=df_detail_report[(df_detail_report['team']==column) & ((df_detail_report['date'].dt.strftime(r"%Y %b")>=df_range['date'].min()) & (df_detail_report['date'].dt.strftime(r"%Y %b")<=df_range['date'].max()))].groupby([df_detail_report['date'].dt.strftime("%Y %b"), 'efficiency'], sort=False).sum(numeric_only=True).reset_index(),
            x="date",
            y="efficiency_value",
            color="efficiency",
            text="efficiency_value",
            title=f"{column.capitalize()} Detailed Capacity - Efficiency",
            labels={"date": "Time", "efficiency_value": "Efficiency"},
            barmode="group",
        )
        .update_traces(texttemplate="%{text:0}")
        .update_layout(
            title_x=0.5,
            xaxis_range=[df_range['date'].min(), df_range['date'].max()],
            xaxis=dict(
                range=[df_range['date'].min(), df_range['date'].max()],
                ),
    ))
    return fig_bar_detail



@callback(
    Output('date_range_picked', 'children'),
    Input('date_range', 'value'),
    Input("session", "data"),
)
def date_range_slider(val, data):
    logger.debug(f"\n\nDate rage value in {__name__}:\n{val}\n\n")
    print(f"\n\nDate rage value in {__name__}:\n{type(val[0])}\n{data}\n")
    print(f"\n\n\nInside range:\n\n")
    if not val:
        return PreventUpdate
    column = data
    val1 = [
        df_detail_report_slide.min().iloc[val[0], 0].strftime(r"%Y %b"), 
        df_detail_report_slide.max().iloc[val[1]-1, 0].strftime(r"%Y %b")
        ]

    return f"You have selected {val1}" 