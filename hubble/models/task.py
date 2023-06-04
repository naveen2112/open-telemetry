from django.db import models
from hubble.models import User, Module
from core import db


class Task(db.SoftDeleteWithBaseModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    module = models.ForeignKey(Module, models.CASCADE, related_name="tasks")
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, models.CASCADE, db_column="created_by", related_name="created_by"
    )

    class Meta:
        managed = False
        db_table = "tasks"