from django.db import models

from core import db


class Currency(db.SoftDeleteWithBaseModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = "currencies"
