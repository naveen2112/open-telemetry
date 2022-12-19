from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class FailedJob(db.Model):
    __tablename__ = 'failed_jobs'

    id = db.Column(db.BigInteger, primary_key=True)
    uuid = db.Column(db.String(255), nullable=False, unique=True)
    connection = db.Column(db.Text, nullable=False)
    queue = db.Column(db.Text, nullable=False)
    payload = db.Column(db.Text, nullable=False)
    exception = db.Column(db.Text, nullable=False)
    failed_at = db.Column(TIMESTAMP(precision=0), nullable=False, server_default="CURRENT_TIMESTAMP")