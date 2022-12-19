from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class UserReportingPerson(db.Model):
    __tablename__ = 'user_reporting_persons'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    reporting_person_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))

    reporting_person = db.relationship('User', primaryjoin='UserReportingPerson.reporting_person_id == User.id')
    user = db.relationship('User', primaryjoin='UserReportingPerson.user_id == User.id')