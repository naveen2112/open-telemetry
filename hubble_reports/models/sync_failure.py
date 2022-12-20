from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class SyncFailure(db.Model):
    __tablename__ = 'sync_failures'

    id = db.Column(db.BigInteger, primary_key=True)
    table_name = db.Column(db.String(255))
    type = db.Column(db.String(255))
    sync_start_time = db.Column(TIMESTAMP())
    sync_end_time = db.Column(TIMESTAMP())
    old_data = db.Column(db.JSON)
    new_data = db.Column(db.JSON)
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())