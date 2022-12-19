# coding: utf-8
from sqlalchemy import BigInteger, Column, JSON, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class SyncFailure(Base):
    __tablename__ = 'sync_failures'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('sync_failures_id_seq'::regclass)"))
    table_name = Column(String(255))
    type = Column(String(255))
    sync_start_time = Column(TIMESTAMP(precision=0))
    sync_end_time = Column(TIMESTAMP(precision=0))
    old_data = Column(JSON)
    new_data = Column(JSON)
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))