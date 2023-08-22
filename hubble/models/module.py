"""
The Module class represents a module in a project and is associated with a project
"""
from django.db import models

from core import db


class Module(db.SoftDeleteWithBaseModel):
    """
    Store the module name of the project
    """

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    project = models.ForeignKey("hubble.Project", models.CASCADE, related_name="modules")
    created_by = models.ForeignKey(
        "hubble.User",
        models.CASCADE,
        db_column="created_by",
        related_name="created_modules",
    )

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        managed = False
        db_table = "modules"
