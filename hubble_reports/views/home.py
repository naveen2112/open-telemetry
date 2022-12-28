from flask import session, render_template
from flask_login import login_required
from hubble_reports.hubble_reports import reports


@reports.route("/")
@login_required
def index() -> render_template:
    return render_template('index_login.html', user=session["user"])