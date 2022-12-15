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
