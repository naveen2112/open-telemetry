from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class ExpectedUserEfficiency(db.Model):
    __tablename__ = 'expected_user_efficiency'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    team_id = db.Column(db.ForeignKey('teams.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    efficiency = db.Column(db.Float(53), nullable=False)
    effective_from = db.Column(db.Date, nullable=False)
    effective_to = db.Column(db.Date)
    updated_by = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))

    team = db.relationship('Team')
    user = db.relationship('User', primaryjoin='ExpectedUserEfficiency.updated_by == User.id')
    user1 = db.relationship('User', primaryjoin='ExpectedUserEfficiency.user_id == User.id')