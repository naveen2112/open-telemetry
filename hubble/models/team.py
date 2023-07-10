"""
The Team class is a Django model that represents a team in an organization
"""
from django.db import models

from core import db


class Team(db.SoftDeleteWithBaseModel):
    """
    Store the team data in the organization
    """

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True, null=True)
    started_at = models.DateField(blank=True, null=True)

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        managed = False
        db_table = "teams"

    def __str__(self):
        return self.name
