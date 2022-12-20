from .core import db
from .permission import Permissions

class PermissionUser(db.Model):
    __tablename__ = 'permission_user'

    permission_id = db.Column(db.ForeignKey('permissions.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    user_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    user_type = db.Column(db.String(255), primary_key=True, nullable=False)

    permission = db.relationship('Permissions')