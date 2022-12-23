from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User
from .module import Module

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    module_id = db.Column(db.ForeignKey('modules.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())

    user = db.relationship('User')
    module = db.relationship('Module')