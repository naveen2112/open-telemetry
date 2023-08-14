"""
The Project class represents a model for storing project details in a Django application.
"""
from django.db import models

from core import db


class Project(db.SoftDeleteWithBaseModel):
    """
    Store the project name and its details
    """

    id = models.BigAutoField(primary_key=True)
    project_id = models.FloatField()
    name = models.CharField(max_length=255)
    icon_path = models.CharField(max_length=255, blank=True, null=True)
    icon_updated_at = db.DateTimeWithoutTZField(blank=True, null=True)
    status = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True, null=True)
    billing_frequency = models.CharField(max_length=255, blank=True, null=True)
    client = models.ForeignKey(
        "hubble.Client",
        models.CASCADE,
        blank=True,
        null=True,
        related_name="project_clients",
    )
    currency = models.ForeignKey(
        "hubble.Currency",
        models.CASCADE,
        blank=True,
        null=True,
        related_name="project_currencies",
    )
    project_owner = models.ForeignKey(
        "hubble.User",
        models.CASCADE,
        blank=True,
        null=True,
        related_name="project_owner",
    )
    project_manager = models.ForeignKey(
        "hubble.User",
        models.CASCADE,
        blank=True,
        null=True,
        related_name="project_managers",
    )

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        managed = False
        db_table = "projects"
