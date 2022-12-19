from sqlalchemy import BigInteger, Column, ForeignKey, String, Table, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

from .core import db


class Client(Base):
    __tablename__ = 'clients'

    id = db.Column(BigInteger, primary_key=True, server_default=text("nextval('clients_id_seq'::regclass)"))
    name = db.Column(String(255), nullable=False)
    state = db.Column(String(255))
    country = db.Column(String(255))
    zip = db.Column(String(255))
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))
    street = db.Column(String(255))
    city = db.Column(String(255))
    currency_id = db.Column(ForeignKey('currencies.id', ondelete='CASCADE', onupdate='CASCADE'))

    currency = relationship('Currency')


t_permission_role = Table(
    'permission_role', metadata,
    db.Column('permission_id', ForeignKey('permissions.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False),
    db.Column('role_id', ForeignKey('roles.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
)