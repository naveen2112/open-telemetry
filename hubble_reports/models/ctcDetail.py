# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class CtcDetail(Base):
    __tablename__ = 'ctc_details'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('ctc_details_id_seq'::regclass)"))
    name = Column(String(255))
    basic = Column(Float(53))
    house_rent_allowance = Column(Float(53))
    mobile_internet_allowance = Column(Float(53))
    special_allowance = Column(Float(53))
    company_contribution_of_pf = Column(Float(53))
    gratuity = Column(Float(53))
    health_insurance = Column(Float(53))
    company_contribution_of_esi = Column(Float(53))
    deleted_at = Column(TIMESTAMP(precision=0))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))