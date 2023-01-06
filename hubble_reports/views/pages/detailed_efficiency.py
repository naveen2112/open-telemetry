import dash
import logging
import pandas as pd
import plotly.express as px

from dash import callback, dcc, html
from sqlalchemy import create_engine
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import date, datetime

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
        html.H1(id="detail-title", children=["Detail-report"]),
        # html.H4("<h1>Good</h1>"),
        dcc.Graph(
            id="detailed_efficiency",
        ),
        html.H2("Slider"),
        html.Br(),
        html.Div(id="date_range_picked"),
    ],
)

# @callback(
#     Output()
# )

@callback(
    Output("detailed_efficiency", "figure"),
    Input("team_selected", "data"),
    Input("min_date_range", "data"),
    Input("max_date_range", "data"),
    prevent_initial_callbacks=False,
)
def detailed_eff(column, min_date_sess, max_date_sess):

    val1 = datetime.strptime(min_date_sess, r'%Y-%m-%d')
    val2 = datetime.strptime(max_date_sess, r'%Y-%m-%d')
    min_date_sess = min(val1, val2).strftime(r'%Y-%m-%d')
    max_date_sess = max(val1, val2).strftime(r'%Y-%m-%d')
    
    logger.info(f"\n\n\nTeam Data clicked=====\n{column}\n\n")
    logger.debug(f"\n\nDetailed:\n\n\n{column = }\n\n{min_date_sess = }\n\n{max_date_sess = }")
    df = pd.read_sql_query(
        db.session.query(
            db.func.date_trunc("month", TimesheetEntry.entry_date).label(
                "display_date"
            ),
            db.func.sum(TimesheetEntry.authorized_hours).label('actual_hours'),
            db.func.sum(
                ExpectedUserEfficiency.expected_efficiency
            ).label("expected_hours"),
        )
        .join(TimesheetEntry, TimesheetEntry.user_id == ExpectedUserEfficiency.user_id)
        .join(Team, Team.id == TimesheetEntry.team_id)
        .filter(
            db.and_(
                Team.name == column,
                db.and_(
                (min_date_sess <= TimesheetEntry.entry_date),
                (TimesheetEntry.entry_date <= max_date_sess)),
            )
        )
        .group_by(db.func.date_trunc("month", TimesheetEntry.entry_date))
        .order_by(db.func.date_trunc("month", TimesheetEntry.entry_date))
        .statement,
        con=db_conn,
        parse_dates=['display_date']
    )
    logger.debug(f'\n\n\nBefore Melted dataframe:\n{df}')
    df = pd.DataFrame(
    pd.melt(
            df,
            id_vars=["display_date"],
            value_vars=["actual_hours", "expected_hours"],
            var_name="efficiency",
            value_name="efficiency_value",
        )
    )
    df['formated_date'] = df.display_date.dt.strftime('%B %Y')
    logger.debug(f'\n\n\nMelted dataframe:\n{df}')

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
    fig_bar_detail.update_xaxes(tickmode = 'array')
    return fig_bar_detail

# @callback(
#     Output("min_date_range", "data"),
#     Output("max_date_range", "data"),
#     Input("date-range-picker", "start_date"),
#     Input("date-range-picker", "end_date"),
#     )
# def update_date_range(st_date, end_date):
#     if (not st_date) and (not end_date):
#         raise PreventUpdate

#     logger.info(f"\n\n\n\n\nUPdate Date range\nStart Date:\n{st_date}\t{type(st_date)}\n\nEnd Date:\n{end_date}\t{type(end_date)}\n\n")
    
#     return st_date, end_date

@callback(
    Output("date_range_picked", "children"),
    Input("min_date_range", "data"),
    Input("max_date_range", "data"),
    Input("team_selected", "data"),
)
def date_range_slider(min_date, max_date, team):
    logger.debug(f"\n\nDate rage value in {__name__}:\n{min_date}\t{max_date}\n\n")
    # logger.info(f"\n\nDate rage value in {__name__}:\n{type(val[0])}\n{team}\n")
    logger.info(f"\n\n\nInside range:\n\n")
    if not min_date and not max_date:
        return PreventUpdate
    column = team
    # val1 = [
    #     df_detail_report_slide.min().iloc[val[0], 0].strftime(r"%Y %b"),
    #     df_detail_report_slide.max().iloc[val[1] - 1, 0].strftime(r"%Y %b"),
    # ]

    return f"You have selected between {max_date}, {min_date}"
