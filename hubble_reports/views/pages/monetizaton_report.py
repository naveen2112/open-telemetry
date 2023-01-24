import dash
import pandas as pd
import pathlib
import plotly.express as px

from dash import Dash, dcc, html, callback, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import date, timedelta, datetime
from dateutil import relativedelta
from flask import render_template_string, current_app
from flask_login import login_required
from flask.helpers import get_root_path
from plotly.subplots import make_subplots
from sqlalchemy import create_engine

from app import app
from config import BaseConfig
from hubble_reports.hubble_reports import reports
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import str_dat_to_nstr_date, ceiling

from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry

dash.register_page(__name__, path="/monetization")

db_connection = create_engine(current_app.config.get("SQLALCHEMY_DATABASE_URI"))


layout = [
    dcc.Loading(
        type="default",
        children=dcc.Graph(
        id="monetization-report",
        config={"displaylogo": False},
    ),)
]

def create_line_chart(df):
        fig = px.line(
            df, 
            x='Date', 
            y='Gap',
            text='Gap',
            markers='circle', 
            hover_data={
                'Teams':True,
                },
            title='Teams',
        )
        fig.update_traces(
            marker=dict(color=df['team_color']),
            line=dict(color=df['team_color'].unique()[0]),
            texttemplate="%{y:0.01f}%",
        )
        
        
        figure_traces = []
        print(fig)
        for trace in range(len(fig["data"])):
            figure_traces.append(fig["data"][trace])
        return figure_traces

@callback(
    Output('monetization-report', 'figure'),
    [
        Input("url", "pathname"),
        Input("min-date-range", "data"),
        Input("max-date-range", "data"),
    ],
)
def monetization_report(urlname, min_date_sess, max_date_sess):
    df = pd.read_sql_query(
    db.session.query(
        db.func.date_trunc("month", TimesheetEntry.entry_date).label("Date"),
        db.func.greatest(
            100
            * (
                db.func.sum(TimesheetEntry.authorized_hours)
                - db.func.sum(ExpectedUserEfficiency.expected_efficiency)
            )
            / db.func.sum(TimesheetEntry.authorized_hours), 0
        ).label("Gap"),
        Team.name.label("Teams"),
    )
    .join(
        ExpectedUserEfficiency, TimesheetEntry.user_id == ExpectedUserEfficiency.user_id
    )
    .join(Team, Team.id == TimesheetEntry.team_id)
    .filter(
        db.and_(
            min_date_sess <= TimesheetEntry.entry_date,
            max_date_sess >= TimesheetEntry.entry_date,
        )
    )
    .group_by(db.func.date_trunc("month", TimesheetEntry.entry_date), Team.name)
    .order_by(db.func.date_trunc("month", TimesheetEntry.entry_date))
    .statement,
    con=db_connection,
    parse_dates=["Date"],
    )

    # df = pd.DataFrame(dict_val, columns=dict_val.keys())
    df["color"] = df["Gap"].apply(lambda x: "orange" if x > 10 else "blue")
    df["text"] = df["Gap"].apply(lambda x: str(x) if x > 10 else "")
    df.sort_values(["Date", "Teams"], ascending=[True, True], inplace=True)
    df["team_color"] = "white"
    df['Date'] = df["Date"].dt.strftime(r'%b %y')
    
    for i, team in enumerate(df.Teams.unique()):
        df["team_color"].loc[df["Teams"] == team] = px.colors.qualitative.Dark24[i]
    figure = px.line(
        df,
        x="Date",
        y="Gap",
        color="Teams",
        text="Gap",
        hover_data={
            "Gap": ":.2f",
            # "Teams": False,
            "Date": False,
            "text": False,
            "color": False,
        },
        markers="circle",
        # hover_name='Teams',
        facet_col="Teams",
        facet_row_spacing=0.025,
        facet_col_wrap=2,
        # facet_col_spacing=0.01,
        labels={
            "Teams": "Teams",
        },
    )
    figure.update_traces(
        texttemplate="<b>%{y:0.01f}%</b>",)
    figure.update_yaxes(
        # range=[0, df["Gap"].max() + 7],
    )
    figure.update_layout(
        template="plotly_white",
        hovermode="x unified",
        height=700,
    )
    figure.update_traces(
        textposition="top center",
    )
    figure.update_annotations(
        textangle=0,
        xanchor="left",
        xref="paper",
        yanchor="top",
        y=df["Gap"].max() + 7,
        yref="y domain",
        # y='relative',
        x=0.5,
        # y=17,
        # y=1,
    )
    for da in figure["data"]:
        if da["type"] in ["scatter", "line"]:
            da["line"]["color"] = df[df["Teams"] == da["name"]]["team_color"].unique()[0]
        elif da["type"] == "bar":
            da["marker"]["color"] = df[df["Teams"] == da["name"]]["team_color"].unique()[0]
    for i, da in enumerate(figure["layout"]["annotations"]):
        da["text"] = da["text"].replace("Teams=", "")
        da["yref"] = "y" + str(i + 1 if i > 0 else "")
        da["x"] = 0.25 if i%2 == 0 else 0.75
    
    # return figure

    no_of_teams = len(df['Teams'].unique())
    fig_subplots = make_subplots(
    rows=int(ceiling(no_of_teams/2,1)),#len(df['Teams'].unique()), 
    cols=2, 
    # shared_xaxes='columns',
    # shared_yaxes=True,
    vertical_spacing=0.15,
    horizontal_spacing=0.05,
    subplot_titles=df['Teams'].unique(),
    start_cell='bottom-left',
    y_title='Gap, %',
    x_title='Date',
    )
    fig_subplots.update_layout(
        height=700,
        # title='Subplots for different teams in different charts'
        # title_text="Stacked Subplots with Shared X-Axes",
        )


    max_gap = ceiling(df['Gap'].max()*1.25, 5)
    no_of_dates = len(df['Date'].unique())
    

    for i, team in enumerate(df.Teams.unique()):
        unique_team_df = df[df['Teams']==team].copy()
        figure_traces = create_line_chart(unique_team_df)
        for traces in figure_traces:
            fig_subplots.append_trace(traces, row= i//2 +1, col=int(i%2)+1)

        data=fig_subplots['data'][i]
        x_axis = data['xaxis']
        y_axis = data['yaxis']
        # fig_subplots.add_layout_image(
        #     dict(
        #         source=f"static/images/png/{team.lower()}.png",
        #         xref=x_axis,
        #         yref=y_axis,
        #         xanchor='center',
        #         yanchor='middle',
        #         # x=len(df[df["Teams"] == team]['Date'].unique())/2-0.5,
        #         x=no_of_dates/2-0.5,
        #         y=max_gap/2,
        #         sizex=1 if no_of_dates >1 else 0.5,
        #         sizey=max_gap/2,
        #         sizing="stretch",
        #         opacity=0.5,
        #         layer="below",
        #     ),
        # )

    fig_subplots.add_hrect(
        y0=-10,
        y1=10,
        annotation_text="<b>Good</b>",
        annotation_position="bottom right",
        fillcolor="green",
        opacity=0.075,
        line_width=0,
    )
    fig_subplots.add_hrect(
        y0=max_gap,
        y1=10,
        annotation_text="<b>Need Improvements</b>",
        annotation_position="top right",
        fillcolor="red",
        opacity=0.075,
        line_width=0,
    )

    fig_subplots.update_yaxes(
        range=[-10, max_gap],
        # title='Gap, %',
    )

    fig_subplots.update_traces(textposition="top center")

    fig_subplots.update_layout(
        hovermode='x',
        template="plotly_white",
        )
    print(fig_subplots)

    return fig_subplots
