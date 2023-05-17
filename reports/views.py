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
    #To render the initial or home page, also efficiency report
    context = {}
    return render(
        request=request,
        template_name="report.html",
        context=context,
    )


@login_required()
def monetization_report(request):
    #To render the monetization gap report
    context = {}
    return render(
        request=request,
        template_name="monetization.html",
        context=context,
    )


@login_required()
def kpi_report(request):
    #To render KPI report 
    context = {}
    return render(
        request=request,
        template_name="kpi.html",
        context=context,
    )


@login_required()
def detailed_efficiency(request, pk):
    #This function is responsible for the detailed efficiency for respective teams
    data = get_object_or_404(Team, pk=pk)
    context = {"data": data}
    return render(
        request=request,
        template_name="detailed_efficiency.html",
        context=context,
    )


class EfficiencyDatatable(CustomDatatable):
    """
    Datatable for overall efficiency
    """
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
            "title": "Team Name",
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


    def customize_row(self, row, obj): #This is responsible for adding the view action button
        buttons = template_utils.show_btn(
            reverse("detailed_efficiency", args=[obj["pk"]])
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return


    def get_initial_queryset(self, request=None):
        """
        To load a queryset into the datatable
        """
        data = (
            TimesheetEntry.objects.select_related("user", "team")
            .date_range(from_date = request.REQUEST.get("from_date"), to_date = request.REQUEST.get("to_date"))
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


    def render_column(self, row, column): #Used to differnetiate the data through various colors
        if column == "capacity":
            if int(row["capacity"]) >= 75:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'
            elif 50 < int(row["capacity"]) < 75:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'
        return super().render_column(row, column)


class MonetizationDatatable(CustomDatatable):
    """
    Monetization Gap report
    """
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
        """
            To load a queryset into the datatable
        """
        data = (
            TimesheetEntry.objects.select_related("user", "project")
            .date_range(
                from_date="2022-01-01",
                to_date="2023-01-01",
            )
            .monetization_fields()
            .filter(
                entry_date__year=request.REQUEST.get("year_filter"),
                entry_date__month=request.REQUEST.get("month_filter"),
            )
        )
        return data


    def render_column(self, row, column): #This is responsible for percentage symbol and data tag colors
        if column == "gap":
            return f'{row["gap"]}%'
        if column == "ratings":
            if int(row["gap"]) <= 15:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">Good</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">Need Improvements</span>'
        return super().render_column(row, column)


class KPIDatatable(CustomDatatable):
    """
    Datatable for KPI report
    """
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
        """
            To load a queryset into the datatable
        """
        data = (
            TimesheetEntry.objects.select_related("user", "project")
            .date_range(
                from_date="2022-01-01",
                to_date="2023-01-01",
            )
            .kpi_fields()
        )
        return data


class DetaileEfficiencyDatatable(CustomDatatable):
    """
        Datatable for detailed efficiency report
    """
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
        """
            To load a queryset into the datatable
        """ 
        data = (
            TimesheetEntry.objects.select_related("user", "team")
            .date_range(from_date = "2022-01-01", to_date = "2023-01-01")
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


    def render_column(self, row, column): #This is responsible for updating the capacity data with various colors based on the value
        if column == "Capacity":
            if int(row["Capacity"]) >= 75:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'
            elif 50 < int(row["Capacity"]) < 75:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'
        return super().render_column(row, column)
