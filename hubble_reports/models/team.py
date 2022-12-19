from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255))
    started_at = db.Column(db.Date)
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))