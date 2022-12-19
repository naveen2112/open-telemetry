# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class WorkDetail(Base):
    __tablename__ = 'work_details'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('work_details_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    mode_of_work = Column(String(255))
    work_schedule = Column(String(255))
    sunday = Column(Boolean, nullable=False, server_default=text("false"))
    monday = Column(Boolean, nullable=False, server_default=text("false"))
    tuesday = Column(Boolean, nullable=False, server_default=text("false"))
    wednesday = Column(Boolean, nullable=False, server_default=text("false"))
    thursday = Column(Boolean, nullable=False, server_default=text("false"))
    friday = Column(Boolean, nullable=False, server_default=text("false"))
    saturday = Column(Boolean, nullable=False, server_default=text("false"))
    deleted_at = Column(TIMESTAMP(precision=0))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))

    user = relationship('User')