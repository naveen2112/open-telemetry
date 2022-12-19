# coding: utf-8
from sqlalchemy import BigInteger, Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class UserEmployeeId(Base):
    __tablename__ = 'user_employee_ids'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('user_employee_ids_id_seq'::regclass)"))
    unique_id = Column(String(255), nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    type = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))

    user = relationship('User')