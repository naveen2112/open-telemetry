# coding: utf-8
from sqlalchemy import BigInteger, Column, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Designation(Base):
    __tablename__ = 'designations'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('designations_id_seq'::regclass)"))
    name = Column(String(255), nullable=False)
    type = Column(String(255))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))