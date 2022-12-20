from sqlalchemy.dialects.postgresql import TIMESTAMP
from .core import db

class Branch(db.Model):
    __tablename__ = 'branches'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    street = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    country = db.Column(db.String(255))
    pincode = db.Column(db.Float(53))
    latitude = db.Column(db.Float(53))
    longitude = db.Column(db.Float(53))
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())