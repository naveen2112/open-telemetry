from sqlalchemy import BigInteger, Column, String, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Currency(Base):
    __tablename__ = 'currencies'

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('currencies_id_seq'::regclass)"))
    name = Column(String(255), nullable=False)
    symbol = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(precision=0))
    updated_at = Column(TIMESTAMP(precision=0))
    deleted_at = Column(TIMESTAMP(precision=0))