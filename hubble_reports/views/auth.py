from app import app, db
from ..models import User


@app.route("/auth")
def auth():
    user = db.get_or_404(User, 64)
    return str(user.email)
