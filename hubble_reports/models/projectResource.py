# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, Date, Float, ForeignKey, Integer, String, Table, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class ProjectResource(Base):
    __tablename__ = 'project_resources'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('project_resources_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    project_id = Column(ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'))
    position = Column(String(255))
    reporting_person_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    resource_type = Column(String(255))
    utilisation = Column(Integer)
    charge_by_hour = Column(Float(53))
    primary_project = Column(Boolean, server_default=text("false"))
    allotted_from = Column(Date)
    removed_on = Column(Date)
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))

    project = relationship('Project')
    reporting_person = relationship('User', primaryjoin='ProjectResource.reporting_person_id == User.id')
    user = relationship('User', primaryjoin='ProjectResource.user_id == User.id')


t_project_users = Table(
    'project_users', metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False),
    Column('project_id', ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False),
    Column('role_type', String(255))
)