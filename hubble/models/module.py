from django.db import models
from hubble.models import User
from .project import Project


class Module(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, models.CASCADE, related_name="Modules_project")
    created_by = models.ForeignKey(
        User, models.CASCADE, db_column="created_by", related_name="Modules_created_by"
    )
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "modules"
