"""
The ProjectResource class is a Django model that represents project 
resources and their attributes
"""
from django.db import models

from core import db


class ProjectResource(db.SoftDeleteWithBaseModel):
    """
    Store the project resource data
    """

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        "hubble.User",
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
        "hubble.User",
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
        "hubble.ProjectResourcePosition",
        models.DO_NOTHING,
        db_column="position",
        blank=True,
        null=True,
        related_name="resource_positions",
    )

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        managed = False
        db_table = "project_resources"
