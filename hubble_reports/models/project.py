from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User
from .client import Client
from .currency import Currency

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.BigInteger, primary_key=True)
    project_id = db.Column(db.Float(53), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    icon_path = db.Column(db.String(255))
    icon_updated_at = db.Column(TIMESTAMP(precision=0))
    status = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255))
    billing_frequency = db.Column(db.String(255))
    client_id = db.Column(db.ForeignKey('clients.id', ondelete='CASCADE', onupdate='CASCADE'))
    currency_id = db.Column(db.ForeignKey('currencies.id', ondelete='SET NULL', onupdate='CASCADE'))
    project_owner_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    project_manager_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))

    client = db.relationship('Client')
    currency = db.relationship('Currency')
    project_manager = db.relationship('User', primaryjoin='Project.project_manager_id == User.id')
    project_owner = db.relationship('User', primaryjoin='Project.project_owner_id == User.id')