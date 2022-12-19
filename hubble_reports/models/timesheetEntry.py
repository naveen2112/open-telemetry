# coding: utf-8
from sqlalchemy import BigInteger, Column, Date, Float, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class TimesheetEntry(Base):
    __tablename__ = 'timesheet_entries'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('timesheet_entries_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    project_id = Column(ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    module_id = Column(ForeignKey('modules.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    task_id = Column(ForeignKey('tasks.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    description = Column(Text, nullable=False)
    entry_date = Column(Date, nullable=False)
    working_hours = Column(Float(53), nullable=False)
    approved_hours = Column(Float(53), nullable=False, server_default=text("'0'::double precision"))
    authorized_hours = Column(Float(53), nullable=False, server_default=text("'0'::double precision"))
    billed_hours = Column(Float(53), nullable=False, server_default=text("'0'::double precision"))
    team_id = Column(ForeignKey('teams.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    admin_comments = Column(Text)
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))

    module = relationship('Module')
    project = relationship('Project')
    task = relationship('Task')
    team = relationship('Team')
    user = relationship('User')