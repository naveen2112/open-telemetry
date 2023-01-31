from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User

class Holiday(db.Model):
    __tablename__ = 'holidays'

    id = db.Column(db.BigInteger, primary_key=True)
    date_of_holiday = db.Column(db.Date, nullable=False)
    month_year = db.Column(db.String(255), nullable=False)
    updated_by = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())

    user = db.relationship('User')