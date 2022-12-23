from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User
from .project import Project

class ProjectComment(db.Model):
    __tablename__ = 'project_comments'

    id = db.Column(db.BigInteger, primary_key=True)
    comments = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())

    project = db.relationship('Project')
    user = db.relationship('User')