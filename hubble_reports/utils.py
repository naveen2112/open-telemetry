import logging
from functools import wraps
from flask import abort, session, g

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(level)
    console = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s %(name)s] %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger

loggered = get_logger(__name__,level=logging.DEBUG)

def verify_permission(*permissions_allowed: tuple[str]):
    def outer(f):
        @wraps(f)
        def inner(*args, **kwargs):
            permissions_set = set(permissions_allowed)
            loggered.info(f"\n\n\n==========>>>Verify Permission:\n\n")
            loggered.info(f"\n\n\n==========>>>Permission allowed:\n{permissions_set}\n\n")
            loggered.info(f"\n\n\n==========>>>User Permissions:\n{g.user_perm}\n\n")
            if g.user_perm is not None and not permissions_set.isdisjoint(g.user_perm):
                return f(*args, **kwargs)
            else:
                abort(403)
        return inner
    return outer