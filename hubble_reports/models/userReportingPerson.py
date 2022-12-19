# coding: utf-8
from sqlalchemy import BigInteger, Column, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class UserReportingPerson(Base):
    __tablename__ = 'user_reporting_persons'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('user_reporting_persons_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    reporting_person_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    deleted_at = Column(TIMESTAMP(precision=0))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))

    reporting_person = relationship('User', primaryjoin='UserReportingPerson.reporting_person_id == User.id')
    user = relationship('User', primaryjoin='UserReportingPerson.user_id == User.id')