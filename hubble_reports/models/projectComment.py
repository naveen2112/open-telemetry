# coding: utf-8
from sqlalchemy import BigInteger, Column, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class ProjectComment(Base):
    __tablename__ = 'project_comments'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('project_comments_id_seq'::regclass)"))
    comments = Column(Text, nullable=False)
    project_id = Column(ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))

    project = relationship('Project')
    user = relationship('User')