from itertools import chain
from flask import Blueprint, session, g, abort
from hubble_reports.models import db, User, RoleUser
import logging
from hubble_reports.utils import get_logger

reports = Blueprint("reports", __name__, template_folder="templates", static_folder="static")

from hubble_reports import views

global user_role_id


@reports.before_request
def user_permission():
    if "user" in session.keys():
        mailid = session["user"]["preferred_username"]
        g.user_role_id = (
            db.session.query(RoleUser.role_id)
            .join(User, User.id == RoleUser.user_id)
            .filter(User.email == mailid).first()
        )
        g.user_role_id = g.user_role_id[0]
        if g.user_role_id is None:
            abort(403)
    
    else:
        ...


@reports.after_request
def user_permission(response):
    g.user_perm = None
    return response
