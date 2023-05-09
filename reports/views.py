from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from hubble.models import TimesheetEntry, Team, Project
from datetime import datetime
from django.db.models.functions import Coalesce, Round
from django.db.models import (
    Avg,
    F,
    Q,
    Sum,
    Func,
    Value,
    CharField,
    Count,
)
from core.utils import CustomDatatable
from core import template_utils

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


@login_required()
def detailed_efficiency(request, pk):
    data = get_object_or_404(Team, pk=pk)
    context = {"data": data}
    return render(
        request=request,
        template_name="detailed_efficiency.html",
        context=context,
    )


@login_required()
def team_report(request):
    context = {}
    context["data"] = (
        TimesheetEntry.objects.values("team__name").distinct().order_by("team__name")
    )
    return render(
        request=request,
        template_name="team.html",
        context=context,
    )


@login_required()
def project_report(request):
    context = {}
    context["data"] = (
        TimesheetEntry.objects.values("project__name")
        .distinct()
        .order_by("project__name")
    )
    return render(
        request=request,
        template_name="project.html",
        context=context,
    )


@login_required()
def team_summary(request, pk, start, end):
    data = get_object_or_404(Team, pk=pk)
    context = {"data": data, "start": str(start), "end": str(end)}
    return render(
        request=request,
        template_name="team_summary.html",
        context=context,
    )


@login_required()
def project_summary(request, pk, start, end):
    data = get_object_or_404(Project, pk=pk)
    context = {"data": data, "start": str(start), "end": str(end)}
    return render(
        request=request,
        template_name="project_summary.html",
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
            .filter(
                Q(
                    entry_date__range=(
                        F("user__expected_user_efficiencies__effective_from"),
                        Coalesce(
                            F("user__expected_user_efficiencies__effective_to"), now
                        ),
                    )
                )
                & Q(
                    entry_date__range=(
                        request.REQUEST.get("datafrom"),
                        request.REQUEST.get("dateto"),
                    )
                )
            )
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


class TeamsDatatable(CustomDatatable):
    model = TimesheetEntry
    search_value_seperator = "+"
    show_column_filters = False
    initial_order = [
        ["efficiency_gap", "desc"],
        ["productivity_gap", "desc"],
    ]
    column_defs = [
        {
            "name": "team__name",
            "title": "<div class= 'text-center'>Team</div>",
            "visible": True,
            "className": "text-center",
            "searchable": True,
        },
        {
            "name": "capacity",
            "title": "<div class= 'text-center'>Capacity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency",
            "title": "<div class= 'text-center'>Efficiency</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity",
            "title": "<div class= 'text-center'>Productivity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency_gap",
            "title": "<div class= 'text-center'>Gap in Efficiency</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity_gap",
            "title": "<div class= 'text-center'>Gap in Productivity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "action",
            "title": "<div class= 'text-center'>Action</div>",
            "className": "text-center action",
            "visible": True,
            "orderable": False,
        },
    ]

    def get_response_dict(self, request, paginator, draw_idx, start_pos):
        response = super().get_response_dict(request, paginator, draw_idx, start_pos)
        data = list(
            TimesheetEntry.objects.select_related("user", "team")
            .date_range(
                datefrom=request.REQUEST.get("datafrom"),
                dateto=request.REQUEST.get("dateto"),
            )
            .annotate(number=Count("team__id", distinct=True))
            .values("number")
            .efficiency_fields()
        )
        if not data:
            data = [
                {
                    "number": "-",
                    "capacity": "-",
                    "efficiency": "-",
                    "productivity": "-",
                    "efficiency_gap": "-",
                    "productivity_gap": "-",
                }
            ]
        response["extra_data"] = data
        return response

    def customize_row(self, row, obj):
        start = self.request.POST.get("datafrom")
        end = self.request.POST.get("dateto")
        buttons = template_utils.show_btn(
            reverse(
                "team_summary",
                kwargs={"pk": obj["team__id"], "start": start, "end": end},
            )
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return

    def get_initial_queryset(self, request=None):
        data = (
            TimesheetEntry.objects.select_related("user", "team")
            .date_range(
                datefrom=request.REQUEST.get("datafrom"),
                dateto=request.REQUEST.get("dateto"),
            )
            .values("team__id")
            .efficiency_fields()
            .annotate(action=F("team__name"), team__name=F("team__name"))
        )
        dropdown_list = request.REQUEST.get("dropdown").split(",")
        if dropdown_list[0] != "":
            return data.filter(team__name__in=dropdown_list)
        else:
            return data

    def render_column(self, row, column):
        if column == "efficiency_gap":
            if int(row["efficiency_gap"]) <= 10:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            elif 10 < int(row["efficiency_gap"]) <= 20:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            elif 20 < int(row["efficiency_gap"]) <= 50:
                return f'<span class="bg-orange-100 text-orange-800 py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
        elif column == "productivity_gap":
            if int(row["productivity_gap"]) <= 10:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'
            elif 10 < int(row["productivity_gap"]) <= 25:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'

        return super().render_column(row, column)

class Organization(CustomDatatable):
    model = TimesheetEntry
    search_value_seperator = "+"
    show_column_filters = False
    initial_order = [
        ["efficiency_gap", "desc"],
        ["productivity_gap", "desc"],
    ]
    column_defs = [
        {
            "name": "user__name",
            "title": "<div class= 'text-center'>UserName</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "capacity",
            "title": "<div class= 'text-center'>Capacity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency",
            "title": "<div class= 'text-center'>Efficiency</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity",
            "title": "<div class= 'text-center'>Productivity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency_gap",
            "title": "<div class= 'text-center'>Gap in Efficiency</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity_gap",
            "title": "<div class= 'text-center'>Gap in Productivity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
    ]

    def get_initial_queryset(self, request=None):
        data = (
            TimesheetEntry.objects.select_related("user", "team")
            .date_range(
                datefrom=request.REQUEST.get("datafrom"),
                dateto=request.REQUEST.get("dateto"),
            )
            .filter(team__id=request.REQUEST.get("team_filter"))
            .values("user__name")
            .efficiency_fields()
        )
        return data

    def get_response_dict(self, request, paginator, draw_idx, start_pos):
        response = super().get_response_dict(request, paginator, draw_idx, start_pos)
        data = list(
            TimesheetEntry.objects.select_related("user", "team")
            .date_range(
                datefrom=request.REQUEST.get("datafrom"),
                dateto=request.REQUEST.get("dateto"),
            )
            .values("team__name")
            .annotate(members=Count(F("user__id"), distinct=True))
            .filter(team__id=request.REQUEST.get("team_filter"))
            .efficiency_fields()
        )
        if not data:
            data = [
                {
                    "members": "-",
                    "capacity": "-",
                    "efficiency": "-",
                    "productivity": "-",
                    "efficiency_gap": "-",
                    "productivity_gap": "-",
                }
            ]
        response["extra_data"] = data
        return response

    def render_column(self, row, column):
        if column == "efficiency_gap":
            if int(row["efficiency_gap"]) <= 10:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            elif 10 < int(row["efficiency_gap"]) <= 20:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            elif 20 < int(row["efficiency_gap"]) <= 50:
                return f'<span class="bg-orange-100 text-orange-800 py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
        elif column == "productivity_gap":
            if int(row["productivity_gap"]) <= 10:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'
            elif 10 < int(row["productivity_gap"]) <= 25:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'

        return super().render_column(row, column)


class ProjectsDatatable(CustomDatatable):
    model = TimesheetEntry
    search_value_seperator = "+"
    show_column_filters = False
    initial_order = [
        ["efficiency_gap", "desc"],
        ["productivity_gap", "desc"],
    ]
    column_defs = [
        {
            "name": "team__name",
            "title": "<div class= 'text-center'>Project</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "capacity",
            "title": "<div class= 'text-center'>Capacity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency",
            "title": "<div class= 'text-center'>Efficiency</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity",
            "title": "<div class= 'text-center'>Productivity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency_gap",
            "title": "<div class= 'text-center'>Gap in Efficiency</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity_gap",
            "title": "<div class= 'text-center'>Gap in Productivity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "action",
            "title": "<div class= 'text-center'>Action</div>",
            "className": "text-center",
            "visible": True,
            "orderable": False,
        },
    ]

    def get_response_dict(self, request, paginator, draw_idx, start_pos):
        response = super().get_response_dict(request, paginator, draw_idx, start_pos)
        data = list(
            TimesheetEntry.objects.select_related("user", "project")
            .date_range(
                datefrom=request.REQUEST.get("datafrom"),
                dateto=request.REQUEST.get("dateto"),
            )
            .annotate(number=Count("project__id", distinct=True))
            .values("number")
            .efficiency_fields()
        )
        if not data:
            data = [
                {
                    "number": "-",
                    "capacity": "-",
                    "efficiency": "-",
                    "productivity": "-",
                    "efficiency_gap": "-",
                    "productivity_gap": "-",
                }
            ]
        response["extra_data"] = data
        return response

    def customize_row(self, row, obj):
        start = self.request.POST.get("datafrom")
        end = self.request.POST.get("dateto")
        self.request.session["datefrom"] = start
        buttons = template_utils.show_btn(
            reverse(
                "project_summary",
                kwargs={"pk": obj["project__id"], "start": start, "end": end},
            )
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return

    def get_initial_queryset(self, request=None):
        data = (
            TimesheetEntry.objects.select_related("user", "project")
            .date_range(
                datefrom=request.REQUEST.get("datafrom"),
                dateto=request.REQUEST.get("dateto"),
            )
            .values("project__id")
            .efficiency_fields()
            .annotate(action=F("project__name"), team__name=F("project__name"))
        )
        dropdown_list = request.REQUEST.get("dropdown").split(",")
        if dropdown_list[0] != "":
            return data.filter(team__name__in=dropdown_list)
        else:
            return data

    def render_column(self, row, column):
        if column == "efficiency_gap":
            if int(row["efficiency_gap"]) <= 10:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            elif 10 < int(row["efficiency_gap"]) <= 20:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            elif 20 < int(row["efficiency_gap"]) <= 50:
                return f'<span class="bg-orange-100 text-orange-800 py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
        elif column == "productivity_gap":
            if int(row["productivity_gap"]) <= 10:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'
            elif 10 < int(row["productivity_gap"]) <= 25:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'

        return super().render_column(row, column)


class ProjectSummaryDatatable(CustomDatatable):
    model = TimesheetEntry
    search_value_seperator = "+"
    show_column_filters = False
    initial_order = [
        ["efficiency_gap", "desc"],
        ["productivity_gap", "desc"],
    ]
    column_defs = [
        {
            "name": "user__name",
            "title": "<div class= 'text-center'>UserName</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "role",
            "title": "<div class= 'text-center'>Role</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "capacity",
            "title": "<div class= 'text-center'>Capacity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency",
            "title": "<div class= 'text-center'>Efficiency</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity",
            "title": "<div class= 'text-center'>Productivity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency_gap",
            "title": "<div class= 'text-center'>Gap in Efficiency</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity_gap",
            "title": "<div class= 'text-center'>Gap in Productivity</div>",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
    ]

    def get_initial_queryset(self, request=None):
        data = (
            TimesheetEntry.objects.select_related("user", "project")
            .date_range(
                datefrom=request.REQUEST.get("datafrom"),
                dateto=request.REQUEST.get("dateto"),
            )
            .values("user__name")
            .efficiency_fields()
            .filter(project__id=request.REQUEST.get("team_filter"))
        )
        return data

    def get_response_dict(self, request, paginator, draw_idx, start_pos):
        response = super().get_response_dict(request, paginator, draw_idx, start_pos)
        data = list(
            TimesheetEntry.objects.select_related("user", "project")
            .date_range(
                datefrom=request.REQUEST.get("datafrom"),
                dateto=request.REQUEST.get("dateto"),
            )
            .values("project__name")
            .efficiency_fields()
            .annotate(members=Count(F("user__id"), distinct=True))
            .filter(project__id=request.REQUEST.get("team_filter"))
        )
        if not data:
            data = [
                {
                    "capacity": "-",
                    "efficiency": "-",
                    "productivity": "-",
                    "efficiency_gap": "-",
                    "productivity_gap": "-",
                    "members": "-"
                }
            ]
        response["extra_data"] = data
        return response

    def render_column(self, row, column):
        if column == "efficiency_gap":
            if int(row["efficiency_gap"]) <= 10:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            elif 10 < int(row["efficiency_gap"]) <= 20:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            elif 20 < int(row["efficiency_gap"]) <= 50:
                return f'<span class="bg-orange-100 text-orange-800 py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["efficiency_gap"]}</span>'
        elif column == "productivity_gap":
            if int(row["productivity_gap"]) <= 10:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'
            elif 10 < int(row["productivity_gap"]) <= 25:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["productivity_gap"]}</span>'

        return super().render_column(row, column)
