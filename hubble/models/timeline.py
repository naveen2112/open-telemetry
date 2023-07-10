"""
The Timeline class is a Django model that represents a timeline
"""
from django.db import models

from core import db


class Timeline(db.SoftDeleteWithBaseModel):
    """
    Store the timeline data
    """

    name = models.CharField(max_length=255)
    team = models.ForeignKey("hubble.Team", on_delete=models.CASCADE)
    is_active = models.BooleanField(
        default=False, blank=True, verbose_name="is_active"
    )
    created_by = models.ForeignKey(
        "hubble.User", on_delete=models.CASCADE
    )

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        db_table = "timelines"

    def __str__(self):
        return str(self.name)
