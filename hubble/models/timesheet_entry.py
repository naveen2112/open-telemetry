from django.db import models
from hubble.models import User, Team
from . import ExpectedUserEfficiency, Project, Module, Task

class TimesheetEntry(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, models.CASCADE, related_name= 'timesheet_entries', db_column = 'user_id')
    project = models.ForeignKey(Project, models.CASCADE, related_name= 'timesheet_entries')
    module = models.ForeignKey(Module, models.CASCADE, related_name= 'timesheet_entries')
    task = models.ForeignKey(Task, models.CASCADE, related_name= 'timesheet_entries')
    team = models.ForeignKey(Team, models.CASCADE, related_name= 'timesheet_entries', db_column= 'team_id')
    description = models.TextField()
    entry_date = models.DateField()
    working_hours = models.FloatField()
    approved_hours = models.FloatField() 
    authorized_hours = models.FloatField()
    billed_hours = models.FloatField()
    admin_comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'timesheet_entries'



