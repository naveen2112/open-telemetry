import msal

from flask_login import login_required, logout_user, login_user
from flask import session, url_for, render_template, redirect, request

from app import login_manager
from hubble_reports.hubble_reports import reports
from hubble_reports.models import User

from config import BaseConfig


@login_manager.user_loader
def user_loader(user_id):
    user_email = session["user"]["preferred_username"]
    return User.query.filter(
        User.email == user_email
    ).first()


@reports.route("/login")
def login() -> render_template:
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(
        authority=BaseConfig.AUTHORITY_SIGN_ON_SIGN_OUT
    )
    return render_template("login.html", auth_url=session["flow"]["auth_uri"])


@reports.route(BaseConfig.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized() -> render_template:
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args
        )
        if "error" in result:
            return render_template("auth/error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    mailid = session["user"]["preferred_username"]
    login_user(User.query.filter(User.email == mailid).first())
    return redirect(url_for("/dash"))


def _load_cache() -> object:
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache) -> None:
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

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
    session.clear()  # Wipe out user and its token cache from session
    logout_user()
    return redirect(  # Also logout from your tenant's web session
        BaseConfig.AUTHORITY_SIGN_ON_SIGN_OUT
        + "/oauth2/v2.0/logout"
        + "?post_logout_redirect_uri="
        + url_for("reports.index", _external=True, _scheme="https")
    )