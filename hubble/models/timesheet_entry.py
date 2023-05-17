from django.db import models
from hubble.models import User, Team
from . import ExpectedUserEfficiency, Project, Module, Task
from django.utils import timezone
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


class DatatableQuery(models.QuerySet):
    def date_range(self, from_date, to_date):
        return self.filter(
            Q(
                entry_date__range=(
                    F("user__expected_user_efficiencies__effective_from"),
                    Coalesce(F("user__expected_user_efficiencies__effective_to"), timezone.now()),
                )
            )
            & Q(entry_date__range=(from_date, to_date))
        )


    def efficiency_fields(self):
        return self.annotate(
            capacity=Coalesce(
                Sum(F("user__expected_user_efficiencies__expected_efficiency")),
                0,
                output_field=FloatField(),
            ),
            efficiency=Coalesce(
                Sum(F("authorized_hours")), 0, output_field=FloatField()
            ),
            productivity=Coalesce(Sum(F("billed_hours")), 0, output_field=FloatField()),
            efficiency_gap=Coalesce(
                Round(
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
                    ),
                    2,
                ),
                0,
                output_field=FloatField(),
            ),
            productivity_gap=Coalesce(
                Round(
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
                    ),
                    2,
                ),
                0,
                output_field=FloatField(),
            ),
            role = Coalesce(F('user__project_resource__position__name'), Value('TBA'), output_field=CharField())
        )


    def kpi_fields(self):
        return (
            self.annotate(
                Project=F("project__name"),
                Working_hours=Sum("working_hours"),
                expected_efficiency=F(
                    "user__expected_user_efficiencies__expected_efficiency"
                ),
                Authorized_sum=Sum("authorized_hours"),
                Billed_sum=Sum("billed_hours"),
                User_name=F("user__name"),
                Team_name=F("team__name"),
            )
            .values(
                "Project",
                "User_name",
                "Team_name",
                "Billed_sum",
                "Authorized_sum",
                "Working_hours",
                "expected_efficiency",
            )
            .order_by("-Authorized_sum", "Billed_sum")
        )


    def monetization_fields(self):
        return (
            self.annotate(a_sum=Sum("authorized_hours"))
            .annotate(
                day=Func(
                    F("entry_date"),
                    Value("Month YYYY"),
                    function="to_char",
                    output_field=CharField(),
                ),
            )
            .values("day", "team__name")
            .annotate(
                gap=Case(
                    When(a_sum=0, then=0),
                    default=Round(
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
                            / Sum(
                                "user__expected_user_efficiencies__expected_efficiency"
                            )
                        ),
                        2,
                    ),
                    output_field=FloatField(),
                ),
                efficiency_capacity=Sum(F("authorized_hours")),
                monetization_capacity=Sum(
                    F("user__expected_user_efficiencies__expected_efficiency")
                ),
                ratings=Sum(F("authorized_hours")),
            )
        )


class TableManager(models.Manager):
    
    def get_queryset(self):
        return DatatableQuery(self.model, using=self._db)


    def date_range(self, datefrom, dateto):
        return self.get_queryset.date_range(datefrom, dateto)


    def efficiency_fields(self):
        return self.get_queryset.efficiency_fields()


    def monetization_fields(self):
        return self.get_queryset.monetization_fields()


class TimesheetEntry(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User, models.CASCADE, related_name="timesheet_entries", db_column="user_id"
    )
    project = models.ForeignKey(
        Project, models.CASCADE, related_name="timesheet_entries"
    )
    module = models.ForeignKey(Module, models.CASCADE, related_name="timesheet_entries")
    task = models.ForeignKey(Task, models.CASCADE, related_name="timesheet_entries")
    team = models.ForeignKey(
        Team, models.CASCADE, related_name="timesheet_entries", db_column="team_id"
    )
    description = models.TextField()
    entry_date = models.DateField()
    working_hours = models.FloatField()
    approved_hours = models.FloatField()
    authorized_hours = models.FloatField()
    billed_hours = models.FloatField()
    admin_comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    objects = TableManager()


    class Meta:
        managed = False
        db_table = "timesheet_entries"
