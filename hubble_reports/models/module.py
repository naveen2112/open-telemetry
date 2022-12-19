# coding: utf-8
from sqlalchemy import BigInteger, Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Module(Base):
    __tablename__ = 'modules'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('modules_id_seq'::regclass)"))
    name = Column(String(255), nullable=False)
    project_id = Column(ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_by = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))

    user = relationship('User')
    project = relationship('Project')