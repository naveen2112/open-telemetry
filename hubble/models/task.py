"""
The Task class is a Django model that represents a task with various fields
"""
from django.db import models

from core import db


class Task(db.SoftDeleteWithBaseModel):
    """
    Store the task data and it related module name as one to many field
    """

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    module = models.ForeignKey(
        "hubble.Module", models.CASCADE, related_name="tasks"
    )
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        "hubble.User",
        models.CASCADE,
        db_column="created_by",
        related_name="created_by",
    )

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        managed = False
        db_table = "tasks"
