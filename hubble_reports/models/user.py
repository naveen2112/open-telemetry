from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from .core import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))

    # id = db.Column(BigInteger, primary_key=True, server_default=text("nextval('users_id_seq'::regclass)"))
    # employee_id = db.Column(String(255))
    # email = db.Column(String(255))
    # email_verified_at = db.Column(TIMESTAMP(precision=0))
    # password = db.Column(String(255))
    # username = db.Column(String(255))
    # name = db.Column(String(255), nullable=False)
    # is_employed = db.Column(Boolean)
    # remember_token = db.Column(String(100))
    # status = db.Column(String(255), nullable=False)
    # team_id = db.Column(ForeignKey('teams.id', ondelete='CASCADE', onupdate='CASCADE'))
    # branch_id = db.Column(ForeignKey('branches.id', ondelete='CASCADE', onupdate='CASCADE'))
    # designation_id = db.Column(ForeignKey('designations.id', ondelete='CASCADE', onupdate='CASCADE'))
    # created_at = db.Column(TIMESTAMP(precision=0))
    # updated_at = db.Column(TIMESTAMP(precision=0))
    # deleted_at = db.Column(TIMESTAMP(precision=0))
    # team_owner = db.Column(Boolean, server_default=text("false"))

    # branch = relationship('Branch')
    # designation = relationship('Designation')
    # team = relationship('Team')