# coding: utf-8
from sqlalchemy import BigInteger, Column, Date, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Team(Base):
    __tablename__ = 'teams'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('teams_id_seq'::regclass)"))
    name = Column(String(255), nullable=False)
    type = Column(String(255))
    started_at = Column(Date)
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))