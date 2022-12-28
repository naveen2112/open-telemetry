from itertools import chain
from flask import Blueprint, session, g, abort
from hubble_reports.models import db, User, RoleUser, PermissionRole, Permission
import logging
from hubble_reports.utils import get_logger

reports = Blueprint("reports", __name__, template_folder="templates")

from hubble_reports import views

global user_perm
logger = get_logger(__name__, level=logging.DEBUG)


@reports.before_request
def user_permission():
    if "user" in session.keys():
        mailid = session["user"]["preferred_username"]
        user_role_ids = (
            db.session.query(RoleUser.role_id)
            .join(User, User.id == RoleUser.user_id)
            .filter(User.email == mailid)
        )
        if user_role_ids is not None:
            user_perm = (
                db.session.query(Permission.name)
                .join(PermissionRole, PermissionRole.permission_id == Permission.id)
                .filter(PermissionRole.role_id.in_(*user_role_ids))
                .all()
            )
            logger.info(f"\n\n\n\n\n============>User permission in before request:\n\n{user_perm}\n\n")
            g.user_perm = set(chain.from_iterable(user_perm))
        else:
            abort(403)
    else:
        ...


@reports.after_request
def user_permission(response):
    g.user_perm = None
    return response
