from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class Permissions(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    group = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))

    roles = db.relationship('Role', secondary='permission_role')