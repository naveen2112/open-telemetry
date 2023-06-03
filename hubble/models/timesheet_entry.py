from django.db import models
from hubble.models import User, Team
from . import Project, Module, Task
from django.utils import timezone
from django.db.models.functions import Coalesce, Round
from core import db
from django.db.models import (
    F,
    Q,
    Sum,
    Case,
    When,
    FloatField,
    Func,
    Value,
    CharField,
)


class TimesheetCustomQuerySet(models.QuerySet):
    def date_range(self, from_date, to_date):
        return self.filter(
            Q(
                entry_date__range=(
                    F("user__expected_user_efficiencies__effective_from"),
                    Coalesce(
                        F("user__expected_user_efficiencies__effective_to"),
                        timezone.now(),
                    ),
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
            role=Coalesce(
                F("user__project_resource__position__name"),
                Value("TBA"),
                output_field=CharField(),
            ),
        )

    def kpi_fields(self):
        return (
            self.annotate(
                project_name=F("project__name"),
                worked_hours=Sum("working_hours"),
                expected_efficiency=F(
                    "user__expected_user_efficiencies__expected_efficiency"
                ),
                authorized_sum=Sum("authorized_hours"),
                billed_sum=Sum("billed_hours"),
                user_name=F("user__name"),
                team_name=F("team__name"),
            )
            .values(
                "project_name",
                "user_name",
                "team_name",
                "billed_sum",
                "authorized_sum",
                "worked_hours",
                "expected_efficiency",
            )
            .order_by("-authorized_sum", "billed_sum")
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


class TimesheetManager(models.Manager):
    def get_queryset(self):
        return TimesheetCustomQuerySet(self.model, using=self._db)

    def date_range(self, from_date, to_date):
        return self.get_queryset.date_range(from_date, to_date)

    def efficiency_fields(self):
        return self.get_queryset.efficiency_fields()

    def monetization_fields(self):
        return self.get_queryset.monetization_fields()

    def kpi_fields(self):
        return self.get_queryset.kpi_fields()


class TimesheetEntry(db.BaseModel):
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
    objects = TimesheetManager()

    class Meta:
        managed = False
        db_table = "timesheet_entries"
