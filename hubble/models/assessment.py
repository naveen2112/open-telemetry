from django.db import models
from core import db
from .sub_batch import SubBatch
from .sub_batch_timeline_task import SubBatchTaskTimeline
from .user import User
from .week_extension import WeekExtension

class Assessment(db.SoftDeleteWithBaseModel):
    sub_batch = models.ForeignKey(SubBatch, on_delete=models.CASCADE)
    task = models.ForeignKey(SubBatchTaskTimeline, on_delete=models.CASCADE, null=True, related_name= 'assessments')
    week_extension = models.ForeignKey(WeekExtension, on_delete=models.CASCADE, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="trainee")
    score = models.IntegerField()
    is_retry = models.BooleanField()
    comment = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assessment_created_by")

    class Meta:
        db_table = "assessments"
