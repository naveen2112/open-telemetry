# coding: utf-8
from sqlalchemy import BigInteger, Column, Float, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class TaskEffort(Base):
    __tablename__ = 'task_efforts'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('task_efforts_id_seq'::regclass)"))
    efforts = Column(Float(53), nullable=False, server_default=text("'0'::double precision"))
    learning = Column(Float(53))
    assumption = Column(Text)
    task_id = Column(ForeignKey('tasks.id', ondelete='SET NULL', onupdate='CASCADE'))
    module_id = Column(ForeignKey('modules.id', ondelete='SET NULL', onupdate='CASCADE'))
    team_id = Column(ForeignKey('teams.id', ondelete='SET NULL', onupdate='CASCADE'))
    created_by = Column(BigInteger)
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))

    module = relationship('Module')
    task = relationship('Task')
    team = relationship('Team')