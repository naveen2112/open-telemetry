from django.db import models
from hubble.models import User
from . import Currency, Client


class Project(models.Model):
    id = models.BigAutoField(primary_key=True)
    project_id = models.FloatField()
    name = models.CharField(max_length=255)
    icon_path = models.CharField(max_length=255, blank=True, null=True)
    icon_updated_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True, null=True)
    billing_frequency = models.CharField(max_length=255, blank=True, null=True)
    client = models.ForeignKey(
        Client, models.CASCADE, blank=True, null=True, related_name="Projects_client"
    )
    currency = models.ForeignKey(
        Currency,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="Projects_currency",
    )
    project_owner = models.ForeignKey(
        User,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="Projects_project_owner",
    )
    project_manager = models.ForeignKey(
        User,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="Projects_project_manager",
    )
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "projects"
