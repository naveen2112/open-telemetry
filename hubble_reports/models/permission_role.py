from .core import db

class PermissionRole(db.Model):
    __tablename__ = 'permission_role'
    permission_id = db.Column('permission_id', db.ForeignKey('permissions.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    role_id = db.Column('role_id', db.ForeignKey('roles.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
