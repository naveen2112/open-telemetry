from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class ProjectResources(db.Model):
    __tablename__ = 'project_resources'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    project_id = db.Column(db.ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'))
    position = db.Column(db.String(255))
    reporting_person_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    resource_type = db.Column(db.String(255))
    utilisation = db.Column(db.Integer)
    charge_by_hour = db.Column(db.Float(53))
    primary_project = db.Column(db.Boolean, server_default="false")
    allotted_from = db.Column(db.Date)
    removed_on = db.Column(db.Date)
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))

    project = db.relationship('Project')
    reporting_person = db.relationship('User', primaryjoin='ProjectResources.reporting_person_id == User.id')
    user = db.relationship('User', primaryjoin='ProjectResources.user_id == User.id')

