"""
The Batch class is a Django model that represents a batch with a 
name and a reference to the user
"""
from django.db import models

from core import db


class Batch(db.SoftDeleteWithBaseModel):
    """
    Store the batch name
    """

    name = models.CharField(max_length=250)
    created_by = models.ForeignKey(
        "hubble.User", on_delete=models.CASCADE
    )

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        db_table = "batches"

    def __str__(self):
        return str(self.name)
