from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from hubble.models import TimesheetEntry, Team
from django.db.models.functions import Round
from django.db.models import (
    Avg,
    F,
    Sum,
    Func,
    Value,
    CharField,
)
from core.utils import CustomDatatable
from core import template_utils


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


@login_required()
def detailed_efficiency(request, pk):
    data = get_object_or_404(Team, pk=pk)
    context = {"data": data}
    return render(
        request=request,
        template_name="detailed_efficiency.html",
        context=context,
    )


class Datatable(CustomDatatable):
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
            "searchable": False,
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
        {
            "name": "action",
            "title": "Action",
            "visible": True,
            "searchable": False,
            "orderable": False,
            "className": "text-center",
        },
    ]


    def customize_row(self, row, obj):
        buttons = template_utils.show_btn(
            reverse("detailed_efficiency", args=[obj["pk"]])
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return


    def get_initial_queryset(self, request=None):
        """Please rename anyone of the fields in the query to `pk`,
        so that it would be useful to render_row_details"""
        data = (
            TimesheetEntry.objects.select_related("user", "team")
            .date_range(datefrom = request.REQUEST.get("datafrom"), dateto = request.REQUEST.get("dateto"))
            .values("team__name")
            .annotate(
                capacity=Round(
                    Avg(
                        100
                        * (F("authorized_hours"))
                        / (F("user__expected_user_efficiencies__expected_efficiency"))
                    ),
                    2,
                ),
                pk=F("team__id"),
                action=F("team__id"),
            )
            .order_by("team__id")
        )
        return data


    def render_column(self, row, column):
        if column == "capacity":
            if int(row["capacity"]) >= 75:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'
            elif 50 < int(row["capacity"]) < 75:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'
        return super().render_column(row, column)


class MonetizationDatatable(CustomDatatable):
    model = TimesheetEntry
    initial_order = [
        ["team__name", "asc"],
    ]
    show_column_filters = False
    column_defs = [
        {
            "name": "team__name",
            "title": "<div class= 'text-center'>Team-Name</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "day",
            "title": "<div class= 'text-center'>Date</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency_capacity",
            "title": "<div class= 'text-center'>Efficiency Capacity <br> (Accomplishment)</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "monetization_capacity",
            "title": "<div class= 'text-center'>Monetization Capacity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "gap",
            "title": "<div class= 'text-center'>Gap</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "ratings",
            "title": "<div class= 'text-center'>Ratings</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
    ]


    def get_initial_queryset(self, request=None):
        data = (
            TimesheetEntry.objects.select_related("user", "project")
            .date_range(
                datefrom="2022-01-01",
                dateto="2023-01-01",
            )
            .monetization_fields()
            .filter(
                entry_date__year=request.REQUEST.get("year_filter"),
                entry_date__month=request.REQUEST.get("month_filter"),
            )
        )
        return data


    def render_column(self, row, column):
        if column == "gap":
            return f'{row["gap"]}%'
        if column == "ratings":
            if int(row["gap"]) <= 15:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">Good</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">Need Improvements</span>'
        return super().render_column(row, column)


class KPIDatatable(CustomDatatable):
    model = TimesheetEntry
    show_column_filters = False
    column_defs = [
        {
            "name": "Project",
            "title": "<div class= 'text-center'>Project</div>",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "User_name",
            "title": "<div class= 'text-center'>User-Name</div>",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "Team_name",
            "title": "<div class= 'text-center'>Team-Name</div>",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "Billed_sum",
            "title": "<div class= 'text-center'>Billed-sum</div>",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "Authorized_sum",
            "title": "<div class= 'text-center'>Authorized_sum</div>",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "Working_hours",
            "title": "<div class= 'text-center'>Working_hours</div>",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "expected_efficiency",
            "title": "<div class= 'text-center'>Expected_Efficiency</div>",
            "visible": True,
            "searchable": True,
        },
    ]


    def get_initial_queryset(self, request=None):
        data = (
            TimesheetEntry.objects.select_related("user", "project")
            .date_range(
                datefrom="2022-01-01",
                dateto="2023-01-01",
            )
            .kpi_fields()
        )
        return data


class DetaileEfficiencyDatatable(CustomDatatable):
    model = TimesheetEntry
    search_value_seperator = "+"
    show_column_filters = False
    column_defs = [
        {
            "name": "Month",
            "title": "Month",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "Expected_hours",
            "title": "Expected hours",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "Actual_hours",
            "title": "Actual hours",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "Capacity",
            "title": "Capacity",
            "visible": True,
            "searchable": True,
        },
    ]


    def get_initial_queryset(self, request=None):
        data = (
            TimesheetEntry.objects.select_related("user", "team")
            .date_range(datefrom = "2022-01-01", dateto = "2023-01-01")
            .annotate(
                Month=Func(
                    F("entry_date"),
                    Value("Month-YYYY"),
                    function="to_char",
                    output_field=CharField(),
                ),
            )
            .values("Month")
            .filter(team__id=int(request.REQUEST.get("team_filter")))
            .annotate(
                Team_Name=F("team__name"),
                Expected_hours=Sum(
                    "user__expected_user_efficiencies__expected_efficiency"
                ),
                Actual_hours=Sum("authorized_hours"),
                Capacity=Round(
                    Avg(
                        100
                        * (F("authorized_hours"))
                        / (F("user__expected_user_efficiencies__expected_efficiency"))
                    )
                ),
            )
        )
        return data


    def render_column(self, row, column):
        if column == "Capacity":
            if int(row["Capacity"]) >= 75:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'
            elif 50 < int(row["Capacity"]) < 75:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'
        return super().render_column(row, column)
