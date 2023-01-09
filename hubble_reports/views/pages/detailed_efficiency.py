import dash
import logging
import pandas as pd
import plotly.express as px

from dash import callback, dcc, html
from sqlalchemy import create_engine
from dash.dependencies import Input, Output
from datetime import datetime

from config import BaseConfig
from hubble_reports.models import db, Team, ExpectedUserEfficiency, TimesheetEntry
from hubble_reports.utils import get_logger

logger = get_logger(__name__, level=logging.DEBUG)


dash.register_page(
    __name__,
    path="/detail-report",
)

db_conn = create_engine(BaseConfig.SQLALCHEMY_DATABASE_URI)


layout = html.Div(
    id="detailed_eff",
    children=[
        dcc.Loading(
            type='default',
            children=dcc.Graph(
            id="detailed_efficiency",
        ),
        ),
    ],
)


@callback(
    Output("detailed_efficiency", "figure"),
    Input("team_selected", "data"),
    Input("min_date_range", "data"),
    Input("max_date_range", "data"),
    prevent_initial_callbacks=False,
)
def detailed_eff(column, min_date_sess, max_date_sess):
    # Below st_date and end_date received are not exactly min date & max date, so it is corrected
    val1 = datetime.strptime(min_date_sess, r"%Y-%m-%d")
    val2 = datetime.strptime(max_date_sess, r"%Y-%m-%d")
    min_date_sess = min(val1, val2).strftime(r"%Y-%m-%d")
    max_date_sess = max(val1, val2).strftime(r"%Y-%m-%d")

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
                Team.name == column,
                db.and_(
                    (min_date_sess <= TimesheetEntry.entry_date),
                    (TimesheetEntry.entry_date <= max_date_sess),
                ),
            )
        )
        .group_by(db.func.date_trunc("month", TimesheetEntry.entry_date))
        .order_by(db.func.date_trunc("month", TimesheetEntry.entry_date))
        .statement,
        con=db_conn,
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

    fig_bar_detail = (
        px.bar(
            data_frame=df,
            x="formated_date",
            y="efficiency_value",
            color="efficiency",
            text="efficiency_value",
            title=f"{column.capitalize()} Detailed Capacity - Efficiency",
            labels={"formated_date": "Time", "efficiency_value": "Efficiency"},
            barmode="group",
        )
        .update_traces(texttemplate="%{text:0}")
        .update_layout(
            title_x=0.5,
        )
    )
    fig_bar_detail.update_xaxes(tickmode="array")
    fig_bar_detail.update_layout(transition={"duration": 1000})
    return fig_bar_detail
