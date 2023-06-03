from django.db import models
from hubble.models import User
from .project import Project
from core import db


class Module(db.SoftDeleteWithBaseModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, models.CASCADE, related_name="modules")
    created_by = models.ForeignKey(
        User, models.CASCADE, db_column="created_by", related_name="created_modules"
    )

    class Meta:
        managed = False
        db_table = "modules"
