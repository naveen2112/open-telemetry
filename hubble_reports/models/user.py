from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db
from .branch import Branch
from .designation import Designation
from .team import Team

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True)
    employee_id = db.Column(db.String(255))
    email = db.Column(db.String(255))
    email_verified_at = db.Column(TIMESTAMP())
    password = db.Column(db.String(255))
    username = db.Column(db.String(255))
    name = db.Column(db.String(255), nullable=False)
    is_employed = db.Column(db.Boolean)
    remember_token = db.Column(db.String(100))
    status = db.Column(db.String(255), nullable=False)
    team_id = db.Column(db.ForeignKey('teams.id', ondelete='CASCADE', onupdate='CASCADE'))
    branch_id = db.Column(db.ForeignKey('branches.id', ondelete='CASCADE', onupdate='CASCADE'))
    designation_id = db.Column(db.ForeignKey('designations.id', ondelete='CASCADE', onupdate='CASCADE'))
    created_at = db.Column(TIMESTAMP())
    updated_at = db.Column(TIMESTAMP())
    deleted_at = db.Column(TIMESTAMP())
    team_owner = db.Column(db.Boolean, server_default="false")

    branch = db.relationship('Branch')
    designation = db.relationship('Designation')
    team = db.relationship('Team')

    def is_active(self):
        return True
    
    def get_id(self):
        # user = User.query.filter(User.email==self.email).first()
        return self.id

    def is_authenticated(self):
        condtion = User.query.filter(User.email=='sharan@mallow-tech.com').first() is not None
        return True

    def is_anonymous(self):
        return False