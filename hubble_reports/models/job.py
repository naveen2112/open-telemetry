from .core import db
class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.BigInteger, primary_key=True)
    queue = db.Column(db.String(255), nullable=False, index=True)
    payload = db.Column(db.Text, nullable=False)
    attempts = db.Column(db.SmallInteger, nullable=False)
    reserved_at = db.Column(db.Integer)
    available_at = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.Integer, nullable=False)