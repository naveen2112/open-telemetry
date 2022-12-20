from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User

class UserContactDetail(db.Model):
    __tablename__ = 'user_contact_details'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, unique=True)
    skype_id = db.Column(db.String(255))
    current_street = db.Column(db.String(255))
    current_city = db.Column(db.String(255))
    current_state = db.Column(db.String(255))
    current_pin_code = db.Column(db.Float(53))
    current_nationality = db.Column(db.String(255))
    permanent_street = db.Column(db.String(255))
    permanent_city = db.Column(db.String(255))
    permanent_state = db.Column(db.String(255))
    permanent_pin_code = db.Column(db.Float(53))
    permanent_nationality = db.Column(db.String(255))
    mobile_no = db.Column(db.String(255))
    contact_person = db.Column(db.String(255))
    contact_person_phone = db.Column(db.String(255))
    contact_person_alternate_phone = db.Column(db.String(255))
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())
    contact_person_name = db.Column(db.String(255))

    user = db.relationship('User', uselist=False)