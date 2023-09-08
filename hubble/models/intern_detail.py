"""
The InternDetail class is a Django model that stores information about trainees
"""
from django.db import models

from core import db

from .user import User


class InternDetail(db.SoftDeleteWithBaseModel):
    """
    Store the trainee detail and also the training completion date
    """

    sub_batch = models.ForeignKey(
        "SubBatch",
        on_delete=models.CASCADE,
        related_name="intern_details",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="intern_details")
    college = models.CharField(max_length=250)
    expected_completion = models.DateField(null=True)
    actual_completion = models.DateField(null=True)
    comment = models.TextField(null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_intern_details",
    )

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        db_table = "intern_details"

    def __str__(self):
        return self.user.name
