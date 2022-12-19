# coding: utf-8
from sqlalchemy import BigInteger, Column, String, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class FailedJob(Base):
    __tablename__ = 'failed_jobs'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('failed_jobs_id_seq'::regclass)"))
    uuid = Column(String(255), nullable=False, unique=True)
    connection = Column(Text, nullable=False)
    queue = Column(Text, nullable=False)
    payload = Column(Text, nullable=False)
    exception = Column(Text, nullable=False)
    failed_at = Column(TIMESTAMP(precision=0), nullable=False, server_default=text("CURRENT_TIMESTAMP"))