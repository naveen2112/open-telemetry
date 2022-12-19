from sqlalchemy.dialects.postgresql import TIMESTAMP

from .core import db

class PersonalAccessToken(db.Model):
    __tablename__ = 'personal_access_tokens'
    __table_args__ = (
        db.Index('personal_access_tokens_tokenable_type_tokenable_id_index', 'tokenable_type', 'tokenable_id'),
    )

    id = db.Column(db.BigInteger, primary_key=True)
    tokenable_type = db.Column(db.String(255), nullable=False)
    tokenable_id = db.Column(db.BigInteger, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(64), nullable=False, unique=True)
    abilities = db.Column(db.Text)
    last_used_at = db.Column(TIMESTAMP(precision=0))
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))