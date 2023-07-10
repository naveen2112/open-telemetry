"""
The Currency class is a Django model that represents a currency with 
its name and symbol.
"""
from django.db import models

from core import db


class Currency(db.SoftDeleteWithBaseModel):
    """
    Store the currency name and their symbol
    """

    id = models.BigAutoField(primary_key=True)

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        managed = False
        db_table = "currencies"
