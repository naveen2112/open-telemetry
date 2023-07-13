"""
The TimelineTask class is a Django model that represents a task in a timeline
"""
from django.db import models

from core import constants, db


class TimelineTask(db.SoftDeleteWithBaseModel):
    """
    Store the task data and it timeline id
    """

    name = models.CharField(max_length=250)
    days = models.FloatField()
    timeline = models.ForeignKey(
        "hubble.Timeline",
        on_delete=models.CASCADE,
        related_name="task_timeline",
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
    order = models.IntegerField(blank=True)
    created_by = models.ForeignKey("hubble.User", on_delete=models.CASCADE)

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        db_table = "timeline_tasks"
        ordering = ["order"]

    def __str__(self):
        return str(self.name)
