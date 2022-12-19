# coding: utf-8
from sqlalchemy import BigInteger, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(String(255), primary_key=True)
    user_id = Column(BigInteger, index=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    payload = Column(Text, nullable=False)
    last_activity = Column(Integer, nullable=False, index=True)