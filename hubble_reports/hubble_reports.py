from itertools import chain
from flask import Blueprint, session, g
from hubble_reports.models import db, User, RoleUser, PermissionRole, Permission
import logging
from hubble_reports.utils import get_logger

reports = Blueprint('reports', __name__, template_folder='templates')

from hubble_reports import views

global user_perm 
logger = get_logger(__name__,level=logging.DEBUG)
@reports.before_request
def user_permission():
    if 'user' in session.keys():
        mailid = session['user']['preferred_username']
        user_perm = db.session.query(Permission.name)\
                        .join(PermissionRole, PermissionRole.permission_id == Permission.id)\
                            .join(RoleUser, RoleUser.role_id == PermissionRole.role_id)\
                                .join(User, User.id == RoleUser.user_id)\
                                    .filter(User.email==mailid)
        g.user_perm = set(chain.from_iterable(user_perm))

    else:
        ...


@reports.after_request
def user_permission(response):
    g.user_perm = None
    return response
