from django.db import models
from hubble.models import User, Currency, Client
from core import db


class Project(db.SoftDeleteWithBaseModel):
    id = models.BigAutoField(primary_key=True)
    project_id = models.FloatField()
    name = models.CharField(max_length=255)
    icon_path = models.CharField(max_length=255, blank=True, null=True)
    icon_updated_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True, null=True)
    billing_frequency = models.CharField(max_length=255, blank=True, null=True)
    client = models.ForeignKey(
        Client, models.CASCADE, blank=True, null=True, related_name="project_clients"
    )
    currency = models.ForeignKey(
        Currency,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="project_currencies",
    )
    project_owner = models.ForeignKey(
        User,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="project_owner",
    )
    project_manager = models.ForeignKey(
        User,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="project_managers",
    )

    class Meta:
        managed = False
        db_table = "projects"
