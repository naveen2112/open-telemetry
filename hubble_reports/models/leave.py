from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User

class Leave(db.Model):
    __tablename__ = 'leaves'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    date_of_leave = db.Column(db.Date, nullable=False)
    session = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    days = db.Column(db.Numeric(8, 2), nullable=False)
    month_year = db.Column(db.String(255), nullable=False)
    updated_by = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())

    user = db.relationship('User', primaryjoin='Leave.updated_by == User.id')
    user1 = db.relationship('User', primaryjoin='Leave.user_id == User.id')