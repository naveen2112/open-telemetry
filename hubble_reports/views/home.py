from flask import session, url_for, render_template, redirect

from hubble_reports.hubble_reports import reports


@reports.route("/")
def index() -> render_template:
    if not session.get("user"):
        return redirect(url_for("reports.login"))
    return render_template('index.html', user=session["user"])