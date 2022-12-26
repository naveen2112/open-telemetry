from hubble_reports.models.core import db
from hubble_reports.hubble_reports import reports
from hubble_reports.models import User
import logging
from hubble_reports.utils import get_logger, login_required
from flask import abort

logger = get_logger(__name__,level=logging.DEBUG)

@reports.route("/auth")
@login_required
def auth() -> str:
    logger.info(f"\n\n\n\n========Auth=======\n")
    user = db.get_or_404(User, 64)
    return str(user.email)

@reports.route("/error")
def server_error() -> str:
    abort(405)