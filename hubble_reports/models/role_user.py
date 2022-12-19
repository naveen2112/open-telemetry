from .core import db

class RoleUser(db.Model):
    __tablename__ = 'role_user'

    role_id = db.Column(db.ForeignKey('roles.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    user_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    user_type = db.Column(db.String(255), primary_key=True, nullable=False)

    role = db.relationship('Role')