from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User

class FamilyDetail(db.Model):
    __tablename__ = 'family_details'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    marital_status = db.Column(db.String(255))
    anniversary_date = db.Column(db.Date)
    spouse_name = db.Column(db.String(255))
    kids = db.Column(db.JSON)
    deleted_at = db.Column(TIMESTAMP(precision=0))
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))

    user = db.relationship('User')