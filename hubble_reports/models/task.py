# coding: utf-8
from sqlalchemy import BigInteger, Column, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('tasks_id_seq'::regclass)"))
    name = Column(Text, nullable=False)
    module_id = Column(ForeignKey('modules.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    description = Column(Text)
    created_by = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))

    user = relationship('User')
    module = relationship('Module')