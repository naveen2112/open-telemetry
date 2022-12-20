from flask import session, url_for, render_template, redirect
import msal
from hubble_reports.hubble_reports import reports


# @reports.route("/")
# def hello_world():
#     return "<p>Hello World, Welcome to Home Page!</p>"

@reports.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template('index.html', user=session["user"], version=msal.__version__)