from django.db import models


class Currency(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "currencies"
