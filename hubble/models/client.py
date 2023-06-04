from django.db import models
from .currency import Currency
from core import db


class Client(db.SoftDeleteWithBaseModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    zip = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    currency = models.ForeignKey(Currency, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "clients"
