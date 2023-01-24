import logging
from functools import wraps
from flask import abort, g
from hubble_reports.models import db, PermissionRole, Permission
from datetime import datetime


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    console = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s %(name)s] %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger


def verify_permission(*permissions_allowed: tuple[str]):
    def outer(f):
        @wraps(f)
        def inner(*args, **kwargs):
            permissions_set = set(permissions_allowed)

            user_perm = (
                db.session.query(Permission.name)
                .join(PermissionRole, PermissionRole.permission_id == Permission.id)
                .filter(
                    PermissionRole.role_id == g.user_role_id,
                    Permission.name.in_(permissions_set),
                )
                .all()
            )

            if user_perm != []:
                return f(*args, **kwargs)
            else:
                abort(403)

        return inner

    return outer

def str_dat_to_nstr_date(date:str, existing_format:str, new_format:str) -> str:
    """
    Updating date string to new specified date string format
    Eg:
    '2023-01-01' to 'Jan 01, 2023'
    """
    return datetime.strptime(date, existing_format).strftime(new_format)