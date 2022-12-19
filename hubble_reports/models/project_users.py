from .core import db

class ProjectUsers(db.Model):
    __tablename__ = 'project_users'
    user_id = db.Column('user_id', db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, primary_key=True)
    project_id = db.Column('project_id', db.ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    role_type = db.Column('role_type', db.String(255))
