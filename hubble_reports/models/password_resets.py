from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class PasswordResets(db.Model):
    __tablename__ = 'password_resets'

    email = db.Column(db.String(255), nullable=False, index=True, primary_key=True)
    token = db.Column(db.String(255), nullable=False, primary_key=True)
    created_at = db.Column(TIMESTAMP(precision=0), primary_key=True)