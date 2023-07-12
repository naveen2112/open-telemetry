"""
The TimesheetEntry class is a model that represents a timesheet entry
"""
from django.db import models
from django.db.models import (Case, CharField, F, FloatField, Func, Q, Sum,
                              Value, When)
from django.db.models.functions import Coalesce, Round
from django.utils import timezone

from core import db

from . import Module, Project, Task


class TimesheetCustomQuerySet(models.QuerySet):
    """
    Provide custom query method for the model
    """

    def date_range(self, from_date, to_date):
        """
        Filters the timesheets based on the given date range and the
        effective date range of the user's expected efficiency
        """
        return self.filter(
            Q(
                entry_date__range=(
                    F(
                        "user__expected_user_efficiencies__effective_from"
                    ),
                    Coalesce(
                        F(
                            "user__expected_user_efficiencies__effective_to"
                        ),
                        timezone.now(),
                    ),
                )
            )
            & Q(entry_date__range=(from_date, to_date))
        )

    def efficiency_fields(self):
        """
        Annotates the timesheets with efficiency-related fields
        """
        return self.annotate(
            capacity=Coalesce(
                Sum(
                    F(
                        "user__expected_user_efficiencies__expected_efficiency"
                    )
                ),
                0,
                output_field=FloatField(),
            ),
            efficiency=Coalesce(
                Sum(F("authorized_hours")), 0, output_field=FloatField()
            ),
            productivity=Coalesce(
                Sum(F("billed_hours")), 0, output_field=FloatField()
            ),
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
                        / Sum(
                            "user__expected_user_efficiencies__expected_efficiency"
                        )
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
                        / Sum(
                            "user__expected_user_efficiencies__expected_efficiency"
                        )
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
        """
        Annotates the timesheets with KPI-related fields.The results are ordered
        by authorized sum in descending order and then by billed sum in ascending order
        """
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
        """
        Annotates the timesheets with monetization-related fields
        """
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
                gap=Coalesce(
                    Case(
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
                    0,
                    output_field=FloatField(),
                ),
                efficiency_capacity=Sum(F("authorized_hours")),
                monetization_capacity=Sum(
                    F(
                        "user__expected_user_efficiencies__expected_efficiency"
                    )
                ),
                ratings=Sum(F("authorized_hours")),
            )
        )


class TimesheetManager(models.Manager):
    """
    Custom manager for the Timesheet model
    """

    def get_queryset(self):
        """
        Get the custom query set for Timesheet model
        """
        return TimesheetCustomQuerySet(self.model, using=self._db)

    def date_range(self, from_date, to_date):
        """
        Filter timesheets based on a date range
        """
        return (
            self.get_queryset.date_range(  # pylint: disable=no-member
                from_date, to_date
            )
        )

    def efficiency_fields(self):
        """
        Get the efficiency fields of timesheets
        """
        return (
            self.get_queryset.efficiency_fields()  # pylint: disable=no-member
        )

    def monetization_fields(self):
        """
        Get the monetization fields of timesheets
        """
        return (
            self.get_queryset.monetization_fields()  # pylint: disable=no-member
        )

    def kpi_fields(self):
        """
        Get the KPI (Key Performance Indicator) fields of timesheets
        """
        return (
            self.get_queryset.kpi_fields()  # pylint: disable=no-member
        )


class TimesheetEntry(db.BaseModel):
    """
    Store the timesheet entry data along with projct and module
    as a foreign key field
    """

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        "hubble.User",
        models.CASCADE,
        related_name="timesheet_entries",
        db_column="user_id",
    )
    project = models.ForeignKey(
        Project, models.CASCADE, related_name="timesheet_entries"
    )
    module = models.ForeignKey(
        Module, models.CASCADE, related_name="timesheet_entries"
    )
    task = models.ForeignKey(
        Task, models.CASCADE, related_name="timesheet_entries"
    )
    team = models.ForeignKey(
        "hubble.Team",
        models.CASCADE,
        related_name="timesheet_entries",
        db_column="team_id",
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
        """
        Meta class for defining class behavior and properties.
        """

        managed = False
        db_table = "timesheet_entries"
