"""
The Assessment class is used to store the assessment report of a trainee
"""
from django.db import models

from core import db

from .extension import Extension
from .sub_batch import SubBatch
from .sub_batch_timeline_task import SubBatchTaskTimeline
from .user import User


class Assessment(db.SoftDeleteWithBaseModel):
    """
    Store the assessment report of the trainee
    """

    sub_batch = models.ForeignKey(SubBatch, on_delete=models.CASCADE, related_name="assessments")
    task = models.ForeignKey(
        SubBatchTaskTimeline,
        on_delete=models.CASCADE,
        null=True,
        related_name="assessments",
    )
    extension = models.ForeignKey(
        Extension,
        on_delete=models.CASCADE,
        null=True,
        related_name="assessments",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assessments")
    score = models.IntegerField(null=True, blank=True)
    is_retry = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_assessments",
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="updated_assessments", null=True
    )
    is_retry_needed = models.BooleanField(default=False, verbose_name="Is retry needed")
    present_status = models.BooleanField(default=True, verbose_name="Present status")

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        db_table = "assessments"
