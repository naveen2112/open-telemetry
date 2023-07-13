"""
Module provides functions for managing token caching and authentication using 
the MSAL library in Python
"""
import msal

from hubble_report.settings import env


def load_cache(request):
    """
    Load the token cache from the session or create a new cache
    """
    cache = msal.SerializableTokenCache()
    if request.session.get("token_cache"):
        cache.deserialize(request.session["token_cache"])
    return cache


def save_cache(request, cache):
    """
    Save the token cache to the session if it has changed
    """
    if cache.has_state_changed:
        request.session["token_cache"] = cache.serialize()


def get_msal_app(cache=None):
    """
    Get the MSAL (Microsoft Authentication Library)
    ConfidentialClientApplication
    """
    return msal.ConfidentialClientApplication(
        env("CLIENT_ID"),
        authority=env("AUTHORITY_SIGN_ON_SIGN_OUT"),
        client_credential=env("CLIENT_SECRET"),
        token_cache=cache,
    )


def get_sign_in_flow(callback_module):
    """
    Get the MSAL authentication code flow for signing in
    """
    return get_msal_app().initiate_auth_code_flow(
        scopes=["user.read"],
        redirect_uri="https://"
        + callback_module
        + env("REDIRECT_PATH"),
    )


def get_token_from_code(request):
    """
    Get the access token from the authentication code
    """
    cache = load_cache(request)
    auth_app = get_msal_app(cache)
    flow = request.session.pop("auth_flow", {})
    result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)
    save_cache(request, cache)
    return result


def get_token(request):
    """
    Get the access token from the token cache
    """
    value_access_token = None
    cache = load_cache(request)
    auth_app = get_msal_app(cache)
    accounts = auth_app.get_accounts()
    if accounts:
        result = auth_app.acquire_token_silent(
            scopes=["user.read"], account=accounts[0]
        )
        save_cache(request, cache)
        value_access_token = result["access_token"]
    return value_access_token


def remove_user_and_token(request):
    """
    Remove the user and token information from the session
    """
    if "token_cache" in request.session:
        del request.session["token_cache"]

    if "user" in request.session:
        del request.session["user"]
