"""
The Designation class is a Django model that represents a designation
and stores its name and type.
"""
from django.db import models

from core import db


class Designation(db.SoftDeleteWithBaseModel):
    """
    Store the designation
    """

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        managed = False
        db_table = "designations"
