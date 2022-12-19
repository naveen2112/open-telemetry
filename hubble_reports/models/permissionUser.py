# coding: utf-8
from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class PermissionUser(Base):
    __tablename__ = 'permission_user'

    permission_id = Column(ForeignKey('permissions.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    user_id = Column(BigInteger, primary_key=True, nullable=False)
    user_type = Column(String(255), primary_key=True, nullable=False)

    permission = relationship('Permission')