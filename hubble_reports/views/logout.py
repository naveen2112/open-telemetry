from flask import session, url_for, render_template, redirect
import msal
from hubble_reports.hubble_reports import reports
from config import BaseConfig


@reports.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        BaseConfig.AUTHORITY_SIGN_ON_SIGN_OUT + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))