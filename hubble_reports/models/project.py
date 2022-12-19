# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Project(Base):
    __tablename__ = 'projects'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('projects_id_seq'::regclass)"))
    project_id = Column(Float(53), nullable=False)
    name = Column(String(255), nullable=False)
    icon_path = Column(String(255))
    icon_updated_at = Column(TIMESTAMP(precision=0))
    status = Column(String(255), nullable=False)
    version = Column(String(255))
    billing_frequency = Column(String(255))
    client_id = Column(ForeignKey('clients.id', ondelete='CASCADE', onupdate='CASCADE'))
    currency_id = Column(ForeignKey('currencies.id', ondelete='SET NULL', onupdate='CASCADE'))
    project_owner_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    project_manager_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))

    client = relationship('Client')
    currency = relationship('Currency')
    project_manager = relationship('User', primaryjoin='Project.project_manager_id == User.id')
    project_owner = relationship('User', primaryjoin='Project.project_owner_id == User.id')