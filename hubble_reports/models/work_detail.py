from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User

class WorkDetail(db.Model):
    __tablename__ = 'work_details'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    mode_of_work = db.Column(db.String(255))
    work_schedule = db.Column(db.String(255))
    sunday = db.Column(db.Boolean, nullable=False, server_default="false")
    monday = db.Column(db.Boolean, nullable=False, server_default="false")
    tuesday = db.Column(db.Boolean, nullable=False, server_default="false")
    wednesday = db.Column(db.Boolean, nullable=False, server_default="false")
    thursday = db.Column(db.Boolean, nullable=False, server_default="false")
    friday = db.Column(db.Boolean, nullable=False, server_default="false")
    saturday = db.Column(db.Boolean, nullable=False, server_default="false")
    deleted_at = db.Column(TIMESTAMP())
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())

    user = db.relationship('User')