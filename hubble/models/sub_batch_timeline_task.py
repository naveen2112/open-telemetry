from django.db import models
from core import db
from hubble.models import SubBatch, User
from core import constants


class SubBatchTaskTimeline(db.SoftDeleteWithBaseModel):

    name = models.CharField(max_length=255)
    days = models.FloatField()
    sub_batch = models.ForeignKey(SubBatch, on_delete=models.CASCADE, related_name="task_timelines")
    present_type = models.CharField(max_length=255, choices=constants.PRESENT_TYPES, default=constants.PRESENT_TYPE_REMOTE)
    task_type = models.CharField(max_length=255, choices=constants.TASK_TYPES, default=constants.TASK_TYPE_TASK)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    order = models.IntegerField(blank=True) 
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "sub_batch_timeline_tasks"
        ordering = ["order"]

