# coding: utf-8
from sqlalchemy import BigInteger, Column, Date, Float, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class ExpectedUserEfficiencies(Base):
    __tablename__ = 'expected_user_efficiencies'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('expected_user_efficiencies_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    expected_efficiency = Column(Float(53), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    updated_by = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))

    user = relationship('User', primaryjoin='ExpectedUserEfficiency.updated_by == User.id')
    user1 = relationship('User', primaryjoin='ExpectedUserEfficiency.user_id == User.id')