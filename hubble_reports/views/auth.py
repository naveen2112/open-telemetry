import msal

from flask_login import login_required, logout_user, login_user
from flask import (
    session,
    url_for,
    render_template,
    redirect,
    request,
    current_app,
    abort,
)

from app import login_manager
from hubble_reports.hubble_reports import reports
from hubble_reports.models import User, db
from sqlalchemy.exc import PendingRollbackError


@login_manager.user_loader
def user_loader(user_id):
    user_email = session["user"]["preferred_username"]
    return db.session.query(User).filter(User.email == mail_id).first()


@reports.route("/login")
def login() -> render_template:
    return render_template("login.html", auth_url=url_for("reports.get_token"))


@reports.route("/get-token")
def get_token():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(
        authority=current_app.config.get("AUTHORITY_SIGN_ON_SIGN_OUT")
    )
    return redirect(session["flow"]["auth_uri"])


@reports.route(
    current_app.config.get("REDIRECT_PATH")
)  # Its absolute URL must match your app's redirect_uri set in AAD
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
    mail_id = session["user"]["preferred_username"]
    try:
        login_user(db.session.query(User).filter(User.email == mail_id).first())
    except AttributeError:
        abort(401)
    except PendingRollbackError:
        db.session.rollback()
    return redirect(url_for("reports.dash_index"))


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
        current_app.config.get("CLIENT_ID"),
        authority=authority or current_app.config.get("AUTHORITY_SIGN_ON_SIGN_OUT"),
        client_credential=current_app.config.get("CLIENT_SECRET"),
        token_cache=cache,
    )


@reports.route("/logout")
@login_required
def logout() -> redirect:
    session.clear()  # Wipe out user and its token cache from session
    logout_user()
    return redirect(  # Also logout from your tenant's web session
        current_app.config.get("AUTHORITY_SIGN_ON_SIGN_OUT")
        + "/oauth2/v2.0/logout"
        + "?post_logout_redirect_uri="
        + url_for("reports.login", _external=True, _scheme="https")
    )
