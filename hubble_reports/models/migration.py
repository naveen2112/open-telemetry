# coding: utf-8
from sqlalchemy import Column, Integer, String, Table, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Migration(Base):
    __tablename__ = 'migrations'

    id = Column(Integer, primary_key=True, server_default=text("nextval('migrations_id_seq'::regclass)"))
    migration = Column(String(255), nullable=False)
    batch = Column(Integer, nullable=False)


t_password_resets = Table(
    'password_resets', metadata,
    Column('email', String(255), nullable=False, index=True),
    Column('token', String(255), nullable=False),
    Column('created_at', TIMESTAMP(precision=0))
)