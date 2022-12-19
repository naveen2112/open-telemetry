from .core import db

class Migration(db.Model):
    __tablename__ = 'migrations'

    id = db.Column(db.Integer, primary_key=True)
    migration = db.Column(db.String(255), nullable=False)
    batch = db.Column(db.Integer, nullable=False)

