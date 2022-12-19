from sqlalchemy.dialects.postgresql import TIMESTAMP


from .core import db


class CtcDetail(db.Model):
    __tablename__ = 'ctc_details'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255))
    basic = db.Column(db.Float(53))
    house_rent_allowance = db.Column(db.Float(53))
    mobile_internet_allowance = db.Column(db.Float(53))
    special_allowance = db.Column(db.Float(53))
    company_contribution_of_pf = db.Column(db.Float(53))
    gratuity = db.Column(db.Float(53))
    health_insurance = db.Column(db.Float(53))
    company_contribution_of_esi = db.Column(db.Float(53))
    deleted_at = db.Column(TIMESTAMP(precision=0))
    created_at = db.Column(TIMESTAMP(precision=0))
    updated_at = db.Column(TIMESTAMP(precision=0))