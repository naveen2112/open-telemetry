from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User

class ExpectedUserEfficiencies(db.Model):
    __tablename__ = 'expected_user_efficiencies'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    expected_efficiency = db.Column(db.Float(53), nullable=False)
    effective_from = db.Column(db.Date, nullable=False)
    effective_to = db.Column(db.Date)
    updated_by = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))

    user = db.relationship('User', primaryjoin='ExpectedUserEfficiencies.updated_by == User.id')
    user1 = db.relationship('User', primaryjoin='ExpectedUserEfficiencies.user_id == User.id')