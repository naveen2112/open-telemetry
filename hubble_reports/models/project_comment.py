from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class ProjectComment(db.Model):
    __tablename__ = 'project_comments'

    id = db.Column(db.BigInteger, primary_key=True)
    comments = db.Column(db.Text, nullable=False)
    project_id = db.Column(db.ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))

    project = db.relationship('Project')
    user = db.relationship('User')