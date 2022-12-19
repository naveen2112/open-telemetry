from sqlalchemy import text
from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class TaskEffort(db.Model):
    __tablename__ = 'task_efforts'

    id = db.Column(db.BigInteger, primary_key=True)
    efforts = db.Column(db.Float(53), nullable=False, server_default=text("'0'::double precision"))
    learning = db.Column(db.Float(53))
    assumption = db.Column(db.Text)
    task_id = db.Column(db.ForeignKey('tasks.id', ondelete='SET NULL', onupdate='CASCADE'))
    module_id = db.Column(db.ForeignKey('modules.id', ondelete='SET NULL', onupdate='CASCADE'))
    team_id = db.Column(db.ForeignKey('teams.id', ondelete='SET NULL', onupdate='CASCADE'))
    created_by = db.Column(db.BigInteger)
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))
    deleted_at = db.Column(TIMESTAMP(precision=0))

    module = db.relationship('Module')
    task = db.relationship('Task')
    team = db.relationship('Team')