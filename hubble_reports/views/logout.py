from flask import session, url_for, redirect
import logging
from hubble_reports.hubble_reports import reports
from config import BaseConfig
from hubble_reports.utils import get_logger, login_required

logger = get_logger(__name__,level=logging.DEBUG)

@reports.route("/logout")
@login_required
def logout() -> redirect:
    logger.info(f"\n\n\n\n========LogOut=======\n")
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        BaseConfig.AUTHORITY_SIGN_ON_SIGN_OUT + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("reports.index", _external=True, _scheme='https'))