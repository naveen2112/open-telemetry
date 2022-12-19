# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, Date, Float, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class UserDetail(Base):
    __tablename__ = 'user_details'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('user_details_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, unique=True)
    profile_pic_path = Column(String(255))
    profile_pic_updated_at = Column(TIMESTAMP(precision=0))
    date_of_birth = Column(Date)
    date_of_joining_as_intern = Column(Date)
    intern_period = Column(Float(53))
    date_of_joining = Column(Date)
    aadhar_no = Column(String(255))
    blood_group = Column(String(255))
    gender = Column(String(255))
    religion = Column(String(255))
    notify_birthday = Column(Boolean)
    notify_joining_anniversary = Column(Boolean)
    notify_timesheet_entry = Column(Boolean)
    pan_no = Column(String(255))
    bank_account_no = Column(String(255))
    ifsc_code = Column(String(255))
    pf_account_no = Column(String(255))
    uan = Column(String(255))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))
    date_of_relieved = Column(Date)
    pan_proof = Column(String(255))
    aadhar_proof = Column(String(255))
    bank_name = Column(String(255))
    ctc = Column(ForeignKey('ctc_details.id', ondelete='CASCADE', onupdate='CASCADE'))
    date_of_end_as_intern = Column(Date)
    date_of_end_as_probation = Column(Date)

    ctc_detail = relationship('CtcDetail')
    user = relationship('User', uselist=False)