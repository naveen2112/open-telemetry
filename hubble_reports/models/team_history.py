from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class TeamHistory(db.Model):
    __tablename__ = 'team_histories'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    team_id = db.Column(db.ForeignKey('teams.id', ondelete='CASCADE', onupdate='CASCADE'))
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)
    status = db.Column(db.String(255))
    deleted_at = db.Column(TIMESTAMP(precision=0))
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))

    team = db.relationship('Team')
    user = db.relationship('User')