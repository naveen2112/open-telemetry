from django.db import models
from hubble.models import User, Team
from . import ExpectedUserEfficiency, Project, Module, Task
from datetime import datetime
from django.db.models.functions import Coalesce, Round
from django.db.models import (
    Avg,
    F,
    Q,
    Sum,
    Case,
    When,
    FloatField,
    Func,
    Value,
    CharField,
    Count,
)


now = datetime.now()

class DatatableManager(models.QuerySet):


    # def custom_group_by(self, number):
    #     return self.


    def join(self, *related_models):
        return self.select_related(*related_models)


    def date_range(self, datefrom, dateto):
        return (self
                .filter(
                Q(
                    entry_date__range=(
                        F("user__expected_user_efficiencies__effective_from"),
                        Coalesce(
                            F("user__expected_user_efficiencies__effective_to"), now
                        ),
                    )
                )
                & Q(entry_date__range=(datefrom, dateto))
                )
        )
    

    def group(self, group_by):
        return self.values(group_by)
    

    def efficiency_fields(self):
        return (self.annotate(capacity = Sum(F('user__expected_user_efficiencies__expected_efficiency')),
                    efficiency = Sum(F('authorized_hours')),
                    productivity = Sum(F('billed_hours')),
                    efficiency_gap = Round(
                        100
                        * (
                            (
                                Sum(
                                    F(
                                        "user__expected_user_efficiencies__expected_efficiency"
                                    )
                                )
                                - Sum(F("authorized_hours"))
                            )
                            / Sum("user__expected_user_efficiencies__expected_efficiency")
                        ), 2
                    ),
                    productivity_gap = Round(
                        100
                        * (
                            (
                                Sum(
                                    F(
                                        "user__expected_user_efficiencies__expected_efficiency"
                                    )
                                )
                                - Sum(F("billed_hours"))
                            )
                            / Sum("user__expected_user_efficiencies__expected_efficiency")
                        ), 2
                    )))

    
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
    objects = models.Manager()
    datatable = DatatableManager.as_manager()

    class Meta:
        managed = False
        db_table = 'timesheet_entries'



