# coding: utf-8
from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class RoleUser(Base):
    __tablename__ = 'role_user'

    role_id = Column(ForeignKey('roles.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    user_id = Column(BigInteger, primary_key=True, nullable=False)
    user_type = Column(String(255), primary_key=True, nullable=False)

    role = relationship('Role')