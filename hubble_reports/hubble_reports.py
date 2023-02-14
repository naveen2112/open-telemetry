from flask import Blueprint, session, g, abort
from sqlalchemy.exc import PendingRollbackError

from hubble_reports.models import db, User, RoleUser

reports = Blueprint("reports", __name__, template_folder="templates")


global user_role_id


@reports.before_request
def user_permission():
    if "user" in session.keys():
        mail_id = session["user"]["preferred_username"]
        try:
            g.user_role_id = (
                db.session.query(RoleUser.role_id)
                .join(User, User.id == RoleUser.user_id)
                .filter(User.email == mail_id).first()
            )
        except PendingRollbackError:
            db.session.rollback()
        g.user_role_id = g.user_role_id[0]
        if g.user_role_id is None:
            abort(403)
    
    else:
        ...


@reports.after_request
def user_permission(response):
    g.user_perm = None
    return response
