from django.db import models
from .users import Users
from core import db
from .timeline import Timeline

class TimelineTask(db.BaseModel):
    PRESENT_TYPE_REMOTE = "Remote"
    PRESENT_TYPE_IN_PERSON = "In-Person"
    PRESENT_TYPE = [
        (PRESENT_TYPE_REMOTE, PRESENT_TYPE_REMOTE),
        (PRESENT_TYPE_IN_PERSON, PRESENT_TYPE_IN_PERSON),
    ]

    TASK_TYPE_NONE = "None"
    TASK_TYPE_WEEKLY_TASK = "Weekly Task"
    TASK_TYPE_REAL_TIME_PROJECT = "Realtime Project"
    TASK_TYPE = [
        (TASK_TYPE_NONE, TASK_TYPE_NONE),
        (TASK_TYPE_WEEKLY_TASK, TASK_TYPE_WEEKLY_TASK),
        (TASK_TYPE_REAL_TIME_PROJECT, TASK_TYPE_REAL_TIME_PROJECT),
    ]

    name = models.CharField(max_length=255)
    days = models.FloatField()
    timeline_id = models.ForeignKey(Timeline, on_delete=models.CASCADE)
    present_type = models.CharField(
        max_length=255, choices=PRESENT_TYPE, default=PRESENT_TYPE_REMOTE
    )
    type = models.CharField(max_length=255, choices=TASK_TYPE, default=TASK_TYPE_NONE)
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        db_table = 'timeline_task'