"""
The ProjectResourcePosition class is a Django model that represents a
project resource position
"""
from django.db import models

from core import db


class ProjectResourcePosition(db.BaseModel):
    """
    Store the project resource position
    """

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    required_reporting_person = models.BooleanField(blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        managed = False
        db_table = "project_resource_positions"
