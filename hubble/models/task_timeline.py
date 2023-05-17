from django.db import models
from core import db
from .sub_batch import SubBatch
from .user import User

class Task_Timeline(db.SoftDeleteWithBaseModel):
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

    name = models.CharField(max_length=255)
    days = models.FloatField()
    sub_batch = models.ForeignKey(SubBatch, on_delete=models.CASCADE)
    present_type = models.CharField(max_length=255, choices=PRESENT_TYPES, default=PRESENT_TYPE_REMOTE)
    task_type = models.CharField(max_length=255, choices=TASK_TYPES, default=TASK_TYPE_TASK)
    start_date = models.DateTimeField(null=True, blank=True, auto_now_add=False, auto_now=False)
    end_date = models.DateTimeField(null=True, blank=True, auto_now_add=False, auto_now=False)
    order = models.IntegerField(blank=True) 
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    

    class Meta:
        db_table = 'task_timeline'
        ordering = ['order']

