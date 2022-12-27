from flask import session, url_for, render_template, redirect
from flask_login import login_user
from hubble_reports.hubble_reports import reports
from hubble_reports.models import User
import logging
from hubble_reports.utils import get_logger

logger = get_logger(__name__,level=logging.DEBUG)
@reports.route("/")
def index() -> render_template:
    if not session.get("user"):
        return redirect(url_for("reports.login"))
    
    mailId = session['user']['preferred_username']
    logger.info(f"\n\n\n\n\n============>MailId:\n\n{mailId}\n\n")
    login_user(User.query.filter(User.email==mailId).first())
    return render_template('index_login.html', user=session["user"])