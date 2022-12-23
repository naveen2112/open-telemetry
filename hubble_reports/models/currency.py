from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class Currency(db.Model):
    __tablename__ = 'currencies'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    symbol = db.Column(db.String(255), nullable=False)
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())