from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class SyncHistory(db.Model):
    __tablename__ = 'sync_histories'

    id = db.Column(db.BigInteger, primary_key=True)
    table = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255))
    count = db.Column(db.BigInteger)
    start_time = db.Column(TIMESTAMP())
    end_time = db.Column(TIMESTAMP())
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())