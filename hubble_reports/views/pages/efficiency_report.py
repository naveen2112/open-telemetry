import dash
import pandas as pd
import plotly.express as px

from dash import dcc, html, callback
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from flask import current_app
from sqlalchemy import create_engine

from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry


db_connection = create_engine(current_app.config.get("SQLALCHEMY_DATABASE_URI"))

dash.register_page(__name__, path='/efficiency')

layout = [
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
]


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
        raise PreventUpdate

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