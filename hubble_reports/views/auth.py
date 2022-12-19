from app import db
from hubble_reports.hubble_reports import reports
from ..models import User


@reports.route("/auth")
def auth():
    user = db.get_or_404(User, 64)
    return str(user.email)
