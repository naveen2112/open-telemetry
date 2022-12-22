from flask import session, url_for, render_template, redirect, request
import msal
from hubble_reports.hubble_reports import reports
from config import BaseConfig
import logging
from hubble_reports.utils import get_logger

logger = get_logger(__name__,level=logging.DEBUG)


@reports.route("/login")
def login():
    logger.info(f"\n\n\n\n========Login=======\n")
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(authority=BaseConfig.AUTHORITY_SIGN_ON_SIGN_OUT)   
    logger.debug(f"\n\n\n=============>>>Session\n{session['flow']}\n")
    return render_template("login.html", auth_url=session["flow"]["auth_uri"])

@reports.route(BaseConfig.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        logger.debug(f"\n\n\n=============>>>Result\n{result}\n")
        if "error" in result:
            return render_template("auth_error.html", result=result)

        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("reports.index"))


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    logger.debug(f"\n\n\n=============>>>Cache Deserialized\n{cache}\n")
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()
        logger.debug(f"\n\n\n=============>>>Token_cache\n{session}\n")
             

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("reports.authorized", _external=True,  _scheme='https'))

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        BaseConfig.CLIENT_ID, authority=authority or BaseConfig.AUTHORITY_SIGN_ON_SIGN_OUT,
        client_credential=BaseConfig.CLIENT_SECRET, token_cache=cache)


# reports.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template