from flask import session, url_for, render_template, redirect
from flask_login import login_user
from hubble_reports.hubble_reports import reports
from hubble_reports.models import User


@reports.route("/")
def index() -> render_template:
    if not session.get("user"):
        return redirect(url_for("reports.login"))
    condition = session['user']['preferred_username']
    login_user(User.query.filter(User.email=='sharan@mallow-tech.com').first())
    return render_template('index_login.html', user=session["user"])