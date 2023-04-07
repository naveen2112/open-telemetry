from django.db import models
from hubble.models import User, Team
from . import ExpectedUserEfficiency, Project, Module, Task

class TimesheetEntry(models.Model):
    id = models.BigAutoField(primary_key=True)
    # user_id = models.ForeignKey(ExpectedUserEfficiency, models.CASCADE, to_field="user_id",unique = False, db_column='user_id', related_name= 'timesheet_user_id')
    user_id = models.ManyToManyField(ExpectedUserEfficiency,through= 'TimesheetUser',  related_name='timesheetuser')
    project = models.ForeignKey(Project, models.CASCADE, related_name= 'TimesheetEntries_project_id')
    module = models.ForeignKey(Module, models.CASCADE, related_name= 'TimesheetEntries_module_id')
    task = models.ForeignKey(Task, models.CASCADE, related_name= 'TimesheetEntries_task_id')
    team = models.ForeignKey(Team, models.CASCADE, related_name= 'TimesheetEntries_team_id', db_column= 'team_id')
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
        # constraints = [models.UniqueConstraint(fields=['user_id'], name='unique_user_id')]
        managed = False
        db_table = 'timesheet_entries'

    
class TimesheetUser(models.Model):
    # pass
    t_user = models.ForeignKey(ExpectedUserEfficiency, on_delete = models.CASCADE, related_name='t_user', to_field= 'user_id')
    e_user = models.ForeignKey(TimesheetEntry, on_delete = models.CASCADE, related_name= 'e_user', to_field= 'user_id')

    class Meta:
        unique_together = ['t_user', 'e_user']
        managed = False
        db_table = 'timesheet_user'



