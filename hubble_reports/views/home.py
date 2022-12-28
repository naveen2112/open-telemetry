from flask import session, render_template
from flask_login import login_required
from hubble_reports.hubble_reports import reports
import logging
from hubble_reports.utils import get_logger

logger = get_logger(__name__,level=logging.DEBUG)
@reports.route("/")
@login_required
def index() -> render_template:
    logger.info(f"\n\n\n\n\n============>Home:\n\n\n\n")
    return render_template('index_login.html', user=session["user"])