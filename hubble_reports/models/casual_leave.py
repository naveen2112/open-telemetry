from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User

class CasualLeave(db.Model):
    __tablename__ = 'casual_leaves'

    id = db.Column(db.BigInteger, primary_key=True)
    days = db.Column(db.Numeric(8, 2), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    updated_by = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())

    user = db.relationship('User')