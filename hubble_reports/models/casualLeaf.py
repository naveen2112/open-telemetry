from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from .core import db

class CasualLeaf(db.Model):
    __tablename__ = 'casual_leaves'

    id = db.Column(db.BigInteger, primary_key=True, server_default="nextval('casual_leaves_id_seq'::regclass)")
    days = db.Column(db.Numeric(8, 2), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    updated_by = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))

    user = relationship('User')