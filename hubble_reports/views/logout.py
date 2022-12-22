from flask import session, url_for, render_template, redirect
import logging
from hubble_reports.hubble_reports import reports
from config import BaseConfig
from hubble_reports.utils import get_logger

logger = get_logger(__name__,level=logging.DEBUG)

@reports.route("/logout")
def logout():
    logger.info(f"\n\n\n\n========LogOut=======\n")
    session.clear()  # Wipe out user and its token cache from session
    if session:
        logger.error(f"\n\n\n=============>>>Session not cleared:{session}\n\n")
    else:
        logger.info(f"\n\n\n=============>>>Session Cleared\n\n")
    return redirect(  # Also logout from your tenant's web session
        BaseConfig.AUTHORITY_SIGN_ON_SIGN_OUT + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))