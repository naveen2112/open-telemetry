import os


def get_env(key: str, default: str = None, error: bool = False) -> str:
    """
    Gets an environment variable from the system while substituting a default value in if set

    If error is also set and default is not, it will return a Value error expeting a value
    """
    value = os.environ.get(key.upper(), default)

    if error and default is None and value is None:
        raise ValueError(
            f"dotenv error: Expecting a value for '{key}' in the environment variables"
        )

    return value


def get_env_int(key: str, default: int = None, error: bool = False) -> int:
    """
    Returns an integer value of a environment variable
    """
    str_default = str(default)
    value = get_env(key, default=str_default, error=error)

    try:
        return int(value)
    except ValueError:
        if error and default is None:
            raise ValueError("dotenv error: '{key}' is not a valid integer")
        return default


def get_env_bool(key: str, default: bool = None, error: bool = False) -> bool:
    """
    Returns an boolean value of a environment variable
    """
    str_default = str(default).lower()
    value = get_env(key, default=str_default, error=error)

    try:
        return value.lower() == "true"
    except ValueError:
        if error and default is None:
            raise ValueError("dotenv error: '{key}' is not a valid boolean")
        return default


class BaseConfig(object):
    SQLALCHEMY_DATABASE_URI = get_env("SQLALCHEMY_DATABASE_URI", error=True)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = get_env("SECRET_KEY")

    #Azure Credentials
    # CLIENT_ID = "Enter_the_Application_Id_here"
    # CLIENT_SECRET = "Enter_the_Client_Secret_Here"
    REDIRECT_PATH = "/getAToken"
    MICROSOFT_AUTHORIZE_URL="https://login.microsoftonline.com/0bb778d4-8a1e-4eb6-a165-f8029c8a5e13/oauth2/v2.0/authorize?"
    MICROSOFT_AUTH_TENANT=""
    MICROSOFT_CALLBACK_URL="https://hubble.mallow-tech.com/callback"
    MICROSOFT_CLIENT_ID="6f7d8df3-b3e3-40c5-9f85-eecc23e457c7"
    MICROSOFT_CLIENT_SECRET="2Ts8Q~HCRV1gYghvcgbLB1Yapl-Riu0keOSyedA7"
    MICROSOFT_GRAPH_USER_SCOPES="User.Read"
    MICROSOFT_HOST_URL="https://login.microsoftonline.com"
    MICROSOFT_TENANT_ID="0bb778d4-8a1e-4eb6-a165-f8029c8a5e13"
    MICROSOFT_TOKEN_URL="https://login.microsoftonline.com/0bb778d4-8a1e-4eb6-a165-f8029c8a5e13/oauth2/v2.0/token"
