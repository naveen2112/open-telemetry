# coding: utf-8
from sqlalchemy import BigInteger, Column, Date, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class TeamHistory(Base):
    __tablename__ = 'team_histories'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('team_histories_id_seq'::regclass)"))
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    team_id = Column(ForeignKey('teams.id', ondelete='CASCADE', onupdate='CASCADE'))
    from_date = Column(Date)
    to_date = Column(Date)
    status = Column(String(255))
    deleted_at = Column(TIMESTAMP(precision=0))
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))

    team = relationship('Team')
    user = relationship('User')