from django.db import models
from core import db


class ProjectResourcePosition(db.BaseModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    required_reporting_person = models.BooleanField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "project_resource_positions"
