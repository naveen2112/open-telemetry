from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from hubble.models import TimesheetEntry
from datetime import datetime
from django.db.models.functions import Coalesce
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
)
from core.utils import CustomDatatable

now = datetime.now()


@login_required()
def index(request):
    context = {}
    return render(
        request=request,
        template_name="report.html",
        context=context,
    )


@login_required()
def monetization_report(request):
    context = {}
    return render(
        request=request,
        template_name="monetization.html",
        context=context,
    )


@login_required()
def kpi_report(request):
    context = {}
    return render(
        request=request,
        template_name="kpi.html",
        context=context,
    )


class datatable(CustomDatatable):
    model = TimesheetEntry
    initial_order = [
        ["team__name", "asc"],
    ]
    search_value_seperator = "+"
    show_column_filters = False
    column_defs = [
        {
            "name": "pk",
            "title": "Team-ID",
            "visible": False,
            "searchable": True,
        },
        {
            "name": "team__name",
            "title": "Team-Name",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "capacity",
            "title": "Capacity",
            "visible": True,
            "searchable": True,
        },
    ]


    def get_initial_queryset(self, request=None):
        """Please rename anyone of the fields in the query to `pk`,
        so that it would be useful to render_row_details"""
        data = (
            TimesheetEntry.objects.prefetch_related("user", "team")
            .filter(
                Q(
                    entry_date__range=(
                        F("user__expected_user_efficiencies__effective_from"),
                        Coalesce(
                            F("user__expected_user_efficiencies__effective_to"), now
                        ),
                    )
                )
                & Q(entry_date__range=("2022-01-01", "2023-01-01"))
            )
            .values("team__name")
            .annotate(
                capacity=Avg(
                    100
                    * (F("authorized_hours"))
                    / (F("user__expected_user_efficiencies__expected_efficiency"))
                ),
                pk=F("team__id"),
            )
            .order_by("team__id")
        )
        return data


    def render_row_details(self, pk, request=None):
        data = (
            TimesheetEntry.objects.select_related("user", "team")
            .filter(
                Q(
                    entry_date__range=(
                        F("user__expected_user_efficiencies__effective_from"),
                        Coalesce(
                            F("user__expected_user_efficiencies__effective_to"), now
                        ),
                    )
                )
                & Q(entry_date__range=("2022-01-01", "2023-01-01"))
            )
            .annotate(
                Month=Func(
                    F("entry_date"),
                    Value("MonthYYYY"),
                    function="to_char",
                    output_field=CharField(),
                ),
            )
            .values("Month")
            .filter(team__id=pk)
            .annotate(
                Team_Name=F("team__name"),
                Expected_hours=Sum(
                    "user__expected_user_efficiencies__expected_efficiency"
                ),
                Actual_hours=Sum("authorized_hours"),
                Capacity=Avg(
                    100
                    * (F("authorized_hours"))
                    / (F("user__expected_user_efficiencies__expected_efficiency"))
                ),
            )
        )
        html = '<table class="display border-0 table-with-no-border dataTable no-footer"><tr><thead>'
        for header in list(data)[0].keys():
            html += "<td>%s</td>" % (header)
        html += "</thead><tbody>"
        for field in list(data):
            html += "<tr>"
            for value in field.values():
                html += "<td>%s</td>" % (value)
            html += "</tr>"
        html += "</tbody></table>"
        return html


class monetization_datatable(CustomDatatable):
    model = TimesheetEntry
    initial_order = [
        ["team__name", "asc"],
    ]
    show_column_filters = False
    column_defs = [
        {
            "name": "team__name",
            "title": "Team-Name",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "gap",
            "title": "Gap",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "day",
            "title": "Date",
            "visible": True,
            "searchable": True,
        },
    ]


    def get_initial_queryset(self, request=None):
        data = (
            TimesheetEntry.objects.select_related("user", "team")
            .filter(
                Q(
                    entry_date__range=(
                        F("user__expected_user_efficiencies__effective_from"),
                        Coalesce(
                            F("user__expected_user_efficiencies__effective_to"), now
                        ),
                    )
                )
                & Q(entry_date__range=("2022-01-01", "2023-01-01"))
            )
            .annotate(a_sum=Sum("authorized_hours"))
            .annotate(
                day=Func(
                    F("entry_date"),
                    Value("MonthYYYY"),
                    function="to_char",
                    output_field=CharField(),
                ),
            )
            .values("day", "team__name")
            .annotate(
                gap=Case(
                    When(a_sum=0, then=0),
                    default=(
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
                            / Sum("authorized_hours")
                        )
                    ),
                    output_field=FloatField(),
                )
            )
        )
        return data


class kpi_datatable(CustomDatatable):
    model = TimesheetEntry
    show_column_filters = False
    column_defs = [
        {
            "name": "Project",
            "title": "Project",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "User_name",
            "title": "User-Name",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "Team_name",
            "title": "Team-Name",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "Billed_sum",
            "title": "Billed-sum",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "Authorized_sum",
            "title": "Authorized_sum",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "Working_hours",
            "title": "Working_hours",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "expected_efficiency",
            "title": "Expected_Efficiency",
            "visible": True,
            "searchable": True,
        },
    ]


    def get_initial_queryset(self, request=None):
        data = (
            TimesheetEntry.objects.select_related("project", "user")
            .filter(
                Q(
                    entry_date__range=(
                        F("user__expected_user_efficiencies__effective_from"),
                        Coalesce(
                            F("user__expected_user_efficiencies__effective_to"), now
                        ),
                    )
                )
            )
            # .filter(project__project_id=1514)
            .filter(Q(entry_date__range=("2022-01-01", "2023-01-01")))
            .annotate(
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
        return data
