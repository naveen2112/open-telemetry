from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .user import User
from .ctc_detail import CtcDetail

class UserDetail(db.Model):
    __tablename__ = 'user_details'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, unique=True)
    profile_pic_path = db.Column(db.String(255))
    profile_pic_updated_at = db.Column(TIMESTAMP())
    date_of_birth = db.Column(db.Date)
    date_of_joining_as_intern = db.Column(db.Date)
    intern_period = db.Column(db.Float(53))
    date_of_joining = db.Column(db.Date)
    aadhar_no = db.Column(db.String(255))
    blood_group = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    religion = db.Column(db.String(255))
    notify_birthday = db.Column(db.Boolean)
    notify_joining_anniversary = db.Column(db.Boolean)
    notify_timesheet_entry = db.Column(db.Boolean)
    pan_no = db.Column(db.String(255))
    bank_account_no = db.Column(db.String(255))
    ifsc_code = db.Column(db.String(255))
    pf_account_no = db.Column(db.String(255))
    uan = db.Column(db.String(255))
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())
    date_of_relieved = db.Column(db.Date)
    pan_proof = db.Column(db.String(255))
    aadhar_proof = db.Column(db.String(255))
    bank_name = db.Column(db.String(255))
    ctc = db.Column(db.ForeignKey('ctc_details.id', ondelete='CASCADE', onupdate='CASCADE'))
    date_of_end_as_intern = db.Column(db.Date)
    date_of_end_as_probation = db.Column(db.Date)

    ctc_detail = db.relationship('CtcDetail')
    user = db.relationship('User', uselist=False)