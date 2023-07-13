"""
The SubBatch class represents a sub-batch of data with various details
"""
from django.db import models

from core import db


class SubBatch(db.SoftDeleteWithBaseModel):
    """
    Store the sub-batch data and it details
    """

    name = models.CharField(max_length=250)
    batch = models.ForeignKey(
        "hubble.Batch",
        on_delete=models.CASCADE,
        related_name="sub_batches",
    )
    team = models.ForeignKey("hubble.Team", on_delete=models.CASCADE)
    primary_mentor = models.ForeignKey(
        "hubble.User",
        on_delete=models.CASCADE,
        related_name="primary_sub_batches",
    )
    secondary_mentor = models.ForeignKey(
        "hubble.User",
        on_delete=models.CASCADE,
        related_name="secondary_sub_batches",
    )
    start_date = models.DateField()
    timeline = models.ForeignKey("hubble.Timeline", on_delete=models.CASCADE)
    created_by = models.ForeignKey("hubble.User", on_delete=models.CASCADE)

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        db_table = "sub_batches"

    def __str__(self):
        return str(self.name)

    @property
    def reporting_persons(self):
        """
        Get the names of the primary and secondary mentors as a string
        """
        return " / ".join([self.primary_mentor.name, self.secondary_mentor.name])
