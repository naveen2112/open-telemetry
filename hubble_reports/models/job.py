# coding: utf-8
from sqlalchemy import BigInteger, Column, Integer, SmallInteger, String, Text, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('jobs_id_seq'::regclass)"))
    queue = Column(String(255), nullable=False, index=True)
    payload = Column(Text, nullable=False)
    attempts = Column(SmallInteger, nullable=False)
    reserved_at = Column(Integer)
    available_at = Column(Integer, nullable=False)
    created_at = Column(Integer, nullable=False)