from django.db import models

from core import db
from hubble.models import ProjectResourcePosition, User


class ProjectResource(db.SoftDeleteWithBaseModel):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="project_resource",
    )
    project = models.ForeignKey(
        "hubble.Project",
        models.CASCADE,
        blank=True,
        null=True,
        related_name="project_resources",
    )
    reporting_person = models.ForeignKey(
        User,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="resource_reporting_persons",
    )
    resource_type = models.CharField(
        max_length=255, blank=True, null=True
    )
    utilisation = models.IntegerField(blank=True, null=True)
    charge_by_hour = models.FloatField(blank=True, null=True)
    primary_project = models.BooleanField(blank=True, null=True)
    allotted_from = models.DateField(blank=True, null=True)
    removed_on = models.DateField(blank=True, null=True)
    position = models.ForeignKey(
        ProjectResourcePosition,
        models.DO_NOTHING,
        db_column="position",
        blank=True,
        null=True,
        related_name="resource_positions",
    )

    class Meta:
        managed = False
        db_table = "project_resources"
