from django.db import models

from core import db

from .extension import Extension
from .sub_batch import SubBatch
from .sub_batch_timeline_task import SubBatchTaskTimeline
from .user import User


class Assessment(db.SoftDeleteWithBaseModel):
    sub_batch = models.ForeignKey(SubBatch, on_delete=models.CASCADE)
    task = models.ForeignKey(
        SubBatchTaskTimeline,
        on_delete=models.CASCADE,
        null=True,
        related_name="assessments",
    )
    extension = models.ForeignKey(
        Extension, on_delete=models.CASCADE, null=True, related_name="assessments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assessments")
    score = models.IntegerField()
    is_retry = models.BooleanField(default=False)
    comment = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_assessments"
    )

    class Meta:
        db_table = "assessments"
