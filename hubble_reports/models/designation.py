from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class Designation(db.Model):
    __tablename__ = 'designations'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255))
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))