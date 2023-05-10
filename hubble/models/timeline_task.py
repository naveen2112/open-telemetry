from django.db import models
from .user import User
from core import db
from .timeline import Timeline

class TimelineTask(db.SoftDeleteWithBaseModel):
    PRESENT_TYPE_REMOTE = "Remote"
    PRESENT_TYPE_IN_PERSON = "In-Person"
    PRESENT_TYPES = [
        (PRESENT_TYPE_REMOTE, PRESENT_TYPE_REMOTE),
        (PRESENT_TYPE_IN_PERSON, PRESENT_TYPE_IN_PERSON),
    ]

    TASK_TYPE_TASK = "Task"
    TASK_TYPE_ASSESSMENT = "Assessment"
    TASK_TYPE_CULTURAL_MEET = "Cultural Meet"
    TASK_TYPES = [
        (TASK_TYPE_TASK, TASK_TYPE_TASK),
        (TASK_TYPE_ASSESSMENT, TASK_TYPE_ASSESSMENT),
        (TASK_TYPE_CULTURAL_MEET, TASK_TYPE_CULTURAL_MEET),
    ]

    name = models.CharField(max_length=250)
    days = models.FloatField()
    timeline = models.ForeignKey(Timeline, on_delete=models.CASCADE)
    present_type = models.CharField(
        max_length=250, choices=PRESENT_TYPES, default=PRESENT_TYPE_REMOTE
    )
    task_type = models.CharField(max_length=250, choices=TASK_TYPES, default=TASK_TYPE_TASK)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'timeline_task'