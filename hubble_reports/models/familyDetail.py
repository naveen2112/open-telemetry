# coding: utf-8
from sqlalchemy import BigInteger, Column, Date, ForeignKey, JSON, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class FamilyDetail(Base):
    __tablename__ = 'family_details'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('family_details_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    marital_status = Column(String(255))
    anniversary_date = Column(Date)
    spouse_name = Column(String(255))
    kids = Column(JSON)
    deleted_at = Column(TIMESTAMP(precision=0))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))

    user = relationship('User')