from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True)
    employee_id = db.Column(db.String(255))
    email = db.Column(db.String(255))
    email_verified_at = db.Column(TIMESTAMP(precision=0))
    password = db.Column(db.String(255))
    username = db.Column(db.String(255))
    name = db.Column(db.String(255), nullable=False)
    is_employed = db.Column(db.Boolean)
    remember_token = db.Column(db.String(100))
    status = db.Column(db.String(255), nullable=False)
    team_id = db.Column(db.ForeignKey('teams.id', ondelete='CASCADE', onupdate='CASCADE'))
    branch_id = db.Column(db.ForeignKey('branches.id', ondelete='CASCADE', onupdate='CASCADE'))
    designation_id = db.Column(db.ForeignKey('designations.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))
    team_owner = db.Column(db.Boolean, server_default="false")

    branch = db.relationship('Branch')
    designation = db.relationship('Designation')
    team = db.relationship('Team')