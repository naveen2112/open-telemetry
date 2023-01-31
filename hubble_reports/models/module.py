from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User
from .project import Project

class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    project_id = db.Column(db.ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_by = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())

    user = db.relationship('User')
    project = db.relationship('Project')