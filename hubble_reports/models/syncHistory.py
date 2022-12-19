# coding: utf-8
from sqlalchemy import BigInteger, Column, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class SyncHistory(Base):
    __tablename__ = 'sync_histories'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('sync_histories_id_seq'::regclass)"))
    table = Column(String(255), nullable=False)
    type = Column(String(255))
    count = Column(BigInteger)
    start_time = Column(TIMESTAMP(precision=0))
    end_time = Column(TIMESTAMP(precision=0))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))