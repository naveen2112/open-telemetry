import dash
import pandas as pd
import plotly.express as px

from dash import dcc, html, callback
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
from sqlalchemy import case, null
from sqlalchemy.exc import PendingRollbackError

from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import ceiling


dash.register_page(__name__, path="/monetization")

layout = [
    html.Div(
        children=[
            html.H2("Description:"),
            html.Div(
                id="monetisation-description",
                children=[
                    html.Li(
                        children=r"Red region shows the monetisation gap % exceeding 10%, While the green region shows monetisation gap % within limit"
                    ),
                    html.Li(
                        children=r"Monetisation gap % having negative % are shown as 0% in the graph"
                    ),
                ],
                style={
                    "paddingLeft": "25px",
                },
            ),
        ]
    ),
    dcc.Loading(
        type="default",
        children=dcc.Graph(
            id="monetization-report",
            config={"displaylogo": False},
        ),
    ),
]


def create_line_chart(
    df: pd.DataFrame, no_of_columns: int, fig_subplots: make_subplots
) -> make_subplots:
    for i, team in enumerate(df["Teams"].unique()):
        df_team = df[df["Teams"] == team].copy()
        fig = px.line(
            df_team,
            x="Date",
            y="Gap",
            text="Gap",
            markers="circle",
            hover_data={
                "Teams": True,
            },
            title="Teams",
        )
        fig.update_traces(
            marker=dict(color=df_team["team_color"]),
            line=dict(color=df_team["team_color"].unique()[0]),
            texttemplate="%{y:0.01f}%",
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                + "Gap: %{y:0.01f}%<br>"
                + "Date: %{x}<br>"
            ),
        )
        fig_subplots.append_trace(
            fig["data"][0], row=i // no_of_columns + 1, col=int(i % no_of_columns) + 1
        )
    return fig_subplots


@callback(
    Output("monetization-report", "figure"),
    [
        Input("min-date-range", "data"),
        Input("max-date-range", "data"),
    ],
)
def monetization_report(min_date_sess, max_date_sess):
    try:
        df = pd.read_sql_query(
            db.session.query(
                db.func.date_trunc("month", TimesheetEntry.entry_date).label("Date"),
                Team.name.label("Teams"),
                case(
                    [(db.func.sum(TimesheetEntry.authorized_hours) == 0, null())],
                    else_=(
                        100
                        * (
                            db.func.sum(ExpectedUserEfficiency.expected_efficiency)
                            - db.func.sum(TimesheetEntry.authorized_hours)
                        )
                        / db.func.sum(TimesheetEntry.authorized_hours)
                    ),
                ).label("Gap"),
            )
            .join(
                TimesheetEntry,
                db.and_(
                    TimesheetEntry.team_id == Team.id,
                    db.and_(
                        TimesheetEntry.entry_date >= min_date_sess,
                        TimesheetEntry.entry_date <= max_date_sess,
                    ),
                ),
            )
            .join(
                ExpectedUserEfficiency,
                TimesheetEntry.user_id == ExpectedUserEfficiency.user_id,
            )
            .group_by(
                db.func.date_trunc("month", TimesheetEntry.entry_date),
                Team.name,
            )
            .statement,
            con=db.engine,
            parse_dates=["Date"],
        )
    except PendingRollbackError:
        db.session.rollback()
    # Pivoting is done to create a matrix of Teams(row) X Date (column) to find missing records
    df_pivot = df.pivot_table(index="Teams", columns="Date", values="Gap").reset_index()
    df_pivot = df_pivot.fillna(0)
    value_vars = df_pivot.columns[1:]
    # By using melt we can rearrange the dateframe to our required structure
    # Basically it is the opposite of pivot_table function of pandas
    df_melted = df_pivot.melt(
        id_vars="Teams", value_vars=value_vars, var_name="Date", value_name="Gap"
    )
    df = df_melted.sort_values(by=["Teams", "Date"])

    df["color"] = df["Gap"].apply(lambda x: "orange" if x > 10 else "blue")
    df["text"] = df["Gap"].apply(lambda x: str(x) if x > 10 else "")
    df.sort_values(["Date", "Teams"], ascending=[True, True], inplace=True)
    df["Date"] = df["Date"].dt.strftime(r"%b %y")
    df["team_color"] = "white"

    for i, team in enumerate(df.Teams.unique()):
        df["team_color"].loc[df["Teams"] == team] = px.colors.qualitative.Dark24[i]

    no_of_teams = len(df["Teams"].unique())
    no_of_rows = int(ceiling(no_of_teams / 2, 1))
    no_of_columns = 2
    fig_subplots = make_subplots(
        rows=no_of_rows,
        cols=no_of_columns,
        vertical_spacing=0.075,
        horizontal_spacing=0.03,
        subplot_titles=df["Teams"].unique(),
        start_cell="bottom-left",
        y_title="Gap, %",
        x_title="Date",
    )

    max_gap = ceiling(df["Gap"].max() * 1.75, 5)
    min_gap = min(-max_gap / 4, ceiling(df["Gap"].min() * 1.25, 5))

    fig_subplots = create_line_chart(df, no_of_columns, fig_subplots)

    fig_subplots.add_hrect(
        y0=10,
        y1=max_gap,
        annotation_text="<b>Good</b>",
        annotation_position="top right",
        fillcolor="green",
        opacity=0.075,
        line_width=0,
    )
    fig_subplots.add_hrect(
        y0=min_gap,
        y1=10,
        annotation_text="<b>Need Improvements</b>",
        annotation_position="bottom right",
        fillcolor="red",
        opacity=0.075,
        line_width=0,
    )

    fig_subplots.update_traces(
        textposition="top center",
    )
    fig_subplots.update_yaxes(
        showgrid=False, range=[min_gap, max_gap], automargin="left+top"
    )
    fig_subplots.update_layout(
        height=no_of_rows * 200,
        hovermode="x",
        template="plotly_white",
        margin=dict(t=50, r=0, l=0, b=0),
        hoverlabel=dict(
            font_color="white",
        ),
    )

    return fig_subplots
