from sqlalchemy import text
from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class TimesheetEntry(db.Model):
    __tablename__ = 'timesheet_entries'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    project_id = db.Column(db.ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    module_id = db.Column(db.ForeignKey('modules.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    task_id = db.Column(db.ForeignKey('tasks.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    working_hours = db.Column(db.Float(53), nullable=False)
    approved_hours = db.Column(db.Float(53), nullable=False, server_default=text("'0'::double precision"))
    authorized_hours = db.Column(db.Float(53), nullable=False, server_default=text("'0'::double precision"))
    billed_hours = db.Column(db.Float(53), nullable=False, server_default=text("'0'::double precision"))
    team_id = db.Column(db.ForeignKey('teams.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    admin_comments = db.Column(db.Text)
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))

    module = db.relationship('Module')
    project = db.relationship('Project')
    task = db.relationship('Task')
    team = db.relationship('Team')
    user = db.relationship('User')