# coding: utf-8
from sqlalchemy import BigInteger, Column, Date, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Holiday(Base):
    __tablename__ = 'holidays'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('holidays_id_seq'::regclass)"))
    date_of_holiday = Column(Date, nullable=False)
    month_year = Column(String(255), nullable=False)
    updated_by = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))

    user = relationship('User')