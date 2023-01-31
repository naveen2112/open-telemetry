from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .currency import Currency

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(255))
    country = db.Column(db.String(255))
    zip = db.Column(db.String(255))
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())
    street = db.Column(db.String(255))
    city = db.Column(db.String(255))
    currency_id = db.Column(db.ForeignKey('currencies.id', ondelete='CASCADE', onupdate='CASCADE'))

    currency = db.relationship('Currency')

