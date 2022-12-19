from sqlalchemy import BigInteger, Column, Float, String, text
from sqlalchemy import Index, JSON
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from .core import db


class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    __table_args__ = (
        Index('subject', 'subject_type', 'subject_id'),
        Index('causer', 'causer_type', 'causer_id')
    )

    id = db.Column(db.BigInteger, primary_key=True, server_default="nextval('activity_log_id_seq'::regclass)")
    log_name = db.Column(db.String(255), index=True)
    description = db.Column(db.Text, nullable=False)
    subject_type = db.Column(db.String(255))
    subject_id = db.Column(db.BigInteger)
    causer_type = db.Column(db.String(255))
    causer_id = db.Column(db.BigInteger)
    properties = db.Column(JSON)
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    event = db.Column(db.String(255))
    batch_uuid = db.Column(UUID)