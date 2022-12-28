import logging
import msal

from flask_login import login_required, logout_user, login_user
from flask import session, url_for, render_template, redirect, request, abort

from app import login_manager
from hubble_reports.hubble_reports import reports
from hubble_reports.models import db, User
from hubble_reports.utils import get_logger

from config import BaseConfig


logger = get_logger(__name__, level=logging.DEBUG)
from hubble_reports.utils import verify_permission


@reports.route("/auth")
@login_required
def auth() -> str:
    logger.info(f"\n\n\n\n========Auth=======\n")
    user = db.get_or_404(User, 64)
    return str(user.email)


@login_manager.user_loader
def user_loader(user_id):
    logger.info(f"\n\n\n\n========Login manager: UserLoader========\n")
    user_email = session["user"]["preferred_username"]
    logger.debug(f"\n\n\n=============>>>User id\n{user_email}\n")
    return User.query.filter(
        User.email == session["user"]["preferred_username"]
    ).first()


@reports.route("/login")
def login() -> render_template:
    logger.info(f"\n\n\n\n========Login=======\n")
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(
        authority=BaseConfig.AUTHORITY_SIGN_ON_SIGN_OUT
    )
    logger.debug(f"\n\n\n=============>>>Session\n{session['flow']}\n")
    return render_template("login.html", auth_url=session["flow"]["auth_uri"])


@reports.route(
    BaseConfig.REDIRECT_PATH
)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized() -> render_template:
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args
        )
        logger.debug(f"\n\n\n=============>>>Result\n{result}\n")
        if "error" in result:
            return render_template("auth/error.html", result=result)

        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    mailid = session["user"]["preferred_username"]
    login_user(User.query.filter(User.email == mailid).first())
    return redirect(url_for("reports.index"))


def _load_cache() -> object:
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    logger.debug(f"\n\n\n=============>>>Cache Deserialized\n{type(cache)}\n")
    return cache


def _save_cache(cache) -> None:
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()
        logger.debug(f"\n\n\n=============>>>Token_cache\n{session}\n")


def _build_auth_code_flow(authority=None, scopes=None) -> dict:
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("reports.authorized", _external=True, _scheme="https"),
    )


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        BaseConfig.CLIENT_ID,
        authority=authority or BaseConfig.AUTHORITY_SIGN_ON_SIGN_OUT,
        client_credential=BaseConfig.CLIENT_SECRET,
        token_cache=cache,
    )


@reports.route("/logout")
@login_required
def logout() -> redirect:
    logger.info(f"\n\n\n\n========LogOut=======\n")
    session.clear()  # Wipe out user and its token cache from session
    logout_user()
    return redirect(  # Also logout from your tenant's web session
        BaseConfig.AUTHORITY_SIGN_ON_SIGN_OUT
        + "/oauth2/v2.0/logout"
        + "?post_logout_redirect_uri="
        + url_for("reports.index", _external=True, _scheme="https")
    )


@reports.route("/error")
@verify_permission('timesheet.view_user', 'timesheet.up')
def server_error() -> str:
    abort(500)
