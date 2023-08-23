"""
The SubBatchTaskTimeline class is a Django model that stores data about
sub batch timelines and provides a method to check if the timeline
is editable based on its start date
"""
from django.db import models
from django.utils import timezone

from core import constants, db


class SubBatchTaskTimeline(db.SoftDeleteWithBaseModel):
    """
    Store the data of sub batch timeline
    """

    name = models.CharField(max_length=255)
    days = models.FloatField()
    sub_batch = models.ForeignKey(
        "hubble.SubBatch",
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
    created_by = models.ForeignKey("hubble.User", on_delete=models.CASCADE)

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        db_table = "sub_batch_timeline_tasks"
        ordering = ["order"]

    def can_editable(self):
        """
        Check if the timesheet is editable based on its start date
        """
        # It is used to ommit 'no-member' it tells that the '
        # DateTimeWithoutTZField has no date member
        # pylint: disable=no-member
        return self.start_date.date() >= timezone.now().date()
