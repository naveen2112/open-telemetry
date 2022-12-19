# coding: utf-8
from sqlalchemy import BigInteger, Column, Date, ForeignKey, Numeric, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Leaf(Base):
    __tablename__ = 'leaves'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('leaves_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    date_of_leave = Column(Date, nullable=False)
    session = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False)
    days = Column(Numeric(8, 2), nullable=False)
    month_year = Column(String(255), nullable=False)
    updated_by = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))

    user = relationship('User', primaryjoin='Leaf.updated_by == User.id')
    user1 = relationship('User', primaryjoin='Leaf.user_id == User.id')