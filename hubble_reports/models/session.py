from .core import db

class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.BigInteger, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    payload = db.Column(db.Text, nullable=False)
    last_activity = db.Column(db.Integer, nullable=False, index=True)