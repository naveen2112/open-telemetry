from django.db import models
from django.utils import timezone

from core import constants, db
from hubble.models import SubBatch, User


class SubBatchTaskTimeline(db.SoftDeleteWithBaseModel):
    name = models.CharField(max_length=255)
    days = models.FloatField()
    sub_batch = models.ForeignKey(
        SubBatch,
        on_delete=models.CASCADE,
        related_name="task_timelines",
    )
    present_type = models.CharField(
        max_length=255,
        choices=constants.PRESENT_TYPES,
        default=constants.PRESENT_TYPE_REMOTE,
    )
    task_type = models.CharField(
        max_length=255,
        choices=constants.TASK_TYPES,
        default=constants.TASK_TYPE_TASK,
    )
    start_date = db.DateTimeWithoutTZField(null=True)
    end_date = db.DateTimeWithoutTZField(null=True)
    order = models.IntegerField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "sub_batch_timeline_tasks"
        ordering = ["order"]

    def can_editable(self):
        return self.start_date.date() >= timezone.now().date()

    @property
    def is_test_week(self):
        return  self.start_date.date() <= timezone.now().date() <= self.start_date.date() + timezone.timedelta(days=7)
    
    @property
    def is_retry_week(self):
        return self.start_date.date() + timezone.timedelta(days=7) <= timezone.now().date() <= self.start_date.date() + timezone.timedelta(days=14)
