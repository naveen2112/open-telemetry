# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class UserContactDetail(Base):
    __tablename__ = 'user_contact_details'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('user_contact_details_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, unique=True)
    skype_id = Column(String(255))
    current_street = Column(String(255))
    current_city = Column(String(255))
    current_state = Column(String(255))
    current_pin_code = Column(Float(53))
    current_nationality = Column(String(255))
    permanent_street = Column(String(255))
    permanent_city = Column(String(255))
    permanent_state = Column(String(255))
    permanent_pin_code = Column(Float(53))
    permanent_nationality = Column(String(255))
    mobile_no = Column(String(255))
    contact_person = Column(String(255))
    contact_person_phone = Column(String(255))
    contact_person_alternate_phone = Column(String(255))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))
    contact_person_name = Column(String(255))

    user = relationship('User', uselist=False)