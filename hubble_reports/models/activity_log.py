from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from .core import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    __table_args__ = (
        db.Index('subject', 'subject_type', 'subject_id'),
        db.Index('causer', 'causer_type', 'causer_id')
    )

    id = db.Column(db.BigInteger, primary_key=True)
    log_name = db.Column(db.String(255), index=True)
    description = db.Column(db.Text, nullable=False)
    subject_type = db.Column(db.String(255))
    subject_id = db.Column(db.BigInteger)
    causer_type = db.Column(db.String(255))
    causer_id = db.Column(db.BigInteger)
    properties = db.Column(db.JSON)
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    event = db.Column(db.String(255))
    batch_uuid = db.Column(UUID)