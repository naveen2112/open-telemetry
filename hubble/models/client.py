from django.db import models
from .currency import Currency


class Client(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    zip = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    currency = models.ForeignKey(Currency, models.CASCADE, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "clients"
