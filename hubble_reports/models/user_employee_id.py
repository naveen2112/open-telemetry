from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User

class UserEmployeeId(db.Model):
    __tablename__ = 'user_employee_ids'

    id = db.Column(db.BigInteger, primary_key=True)
    unique_id = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    type = db.Column(db.String(255), nullable=False)
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))

    user = db.relationship('User')