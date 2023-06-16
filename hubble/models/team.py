from django.db import models

from core import db


class Team(db.SoftDeleteWithBaseModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True, null=True)
    started_at = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "teams"

    def __str__(self):
        return self.name
