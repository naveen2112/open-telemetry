"""
Django views and datatables for generating efficiency, monetization, and KPI reports
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, CharField, F, Func, Sum, Value
from django.db.models.functions import Round
from django.urls import reverse
from django.views.generic import DetailView, TemplateView

from core import template_utils
from core.utils import CustomDatatable
from hubble.models import Team, TimesheetEntry


class Index(LoginRequiredMixin, TemplateView):
    """
    This Class is responsible for checking whether user is authenticated or not,
    and redirects the user to Efficiency report
    """

    template_name = "report.html"


class MonetizationReport(LoginRequiredMixin, TemplateView):
    """
    This Class is responsible for checking whether user is authenticated or not,
    and redirects the user to MOnetization Gap report
    """

    template_name = "monetization.html"


class KpiReport(LoginRequiredMixin, TemplateView):
    """This Class is responsible for checking whether user is authenticated
    or not, and redirects the user to KPI report
    """

    template_name = "kpi.html"


class DetailedEfficiency(LoginRequiredMixin, DetailView):
    """This Class is responsible for checking whether user is authenticated
    or not, and redirects the user to Team specific report
    """

    model = Team
    template_name = "detailed_efficiency.html"


class EfficiencyDatatable(CustomDatatable):
    """
    This class is responsible for Datatable corresponding to Overall efficiency
    """

    model = TimesheetEntry
    initial_order = (["team__name", "asc"],)
    search_value_seperator = "+"

    column_defs = [
        {
            "name": "pk",
            "title": "Team ID",
            "className": "text-center",
            "visible": False,
            "searchable": False,
        },
        {
            "name": "team__name",
            "title": "Team Name",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "capacity",
            "title": "Capacity",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "action",
            "title": "Action",
            "className": "text-center",
            "visible": True,
            "searchable": False,
            "orderable": False,
        },
    ]

    def customize_row(self, row, obj):
        """This is responsible for adding the view action button"""
        buttons = template_utils.show_btn(  # pylint: disable=no-member
            reverse("detailed_efficiency", args=[obj["pk"]])
        )
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return row

    def get_initial_queryset(self, request=None):
        """To load a queryset into the datatable"""
        return (
            TimesheetEntry.objects.select_related("user", "team")
            .date_range(
                request.REQUEST.get("from_date"),
                request.REQUEST.get("to_date"),
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
            )
            .order_by("team__id")
        )

    def render_dict_column(self, row, column):
        # Used to differnetiate the data through various colors
        if column == "capacity":
            if int(row["capacity"]) >= 75:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 \
                    px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'
            if 50 < int(row["capacity"]) < 75:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 \
                    px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'

            return f'<span class="bg-dark-red-10 text-dark-red py-0.5 \
                    px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'
        return super().render_dict_column(row, column)


class MonetizationDatatable(CustomDatatable):
    """
    This class is responsible for Datatable corresponding to Monetization Gap report
    """

    model = TimesheetEntry
    initial_order = (["team__name", "asc"],)

    column_defs = [
        {
            "name": "team__name",
            "title": "Team Name",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "day",
            "title": "Date",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency_capacity",
            "title": "Efficiency Capacity <br> (Accomplishment)",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "monetization_capacity",
            "title": "Monetization Capacity",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "gap",
            "title": "Gap",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "ratings",
            "title": "Ratings",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
    ]

    def get_initial_queryset(self, request=None):
        """To load a queryset into the datatable"""
        return (
            TimesheetEntry.objects.select_related("user", "project")
            .monetization_fields()
            .filter(
                entry_date__year=request.REQUEST.get("year_filter"),
                entry_date__month=request.REQUEST.get("month_filter"),
            )
        )

    def render_dict_column(self, row, column):
        # This is responsible for percentage symbol and data tag colors
        if column == "gap":
            return f'{row["gap"]}%'
        if column == "ratings":
            if int(row["gap"]) <= 15:
                return (
                    '<span class="bg-mild-green-10 text-mild-green py-0.5 '
                    'px-1.5 rounded-xl text-sm">Good</span>'
                )
            return (
                '<span class="bg-dark-red-10 text-dark-red py-0.5 '
                'px-1.5 rounded-xl text-sm">Need Improvements</span>'
            )
        return super().render_dict_column(row, column)


class KPIDatatable(CustomDatatable):
    """
    This class is responsible for Datatable corresponding to KPI report
    """

    model = TimesheetEntry
    search_value_seperator = "+"

    column_defs = [
        {
            "name": "project_name",
            "title": "Project",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "user_name",
            "title": "User Name",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "team_name",
            "title": "Team Name",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "billed_sum",
            "title": "Billed sum",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "authorized_sum",
            "title": "Authorized sum",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "worked_hours",
            "title": "Working hours",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "expected_efficiency",
            "title": "Expected Efficiency",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
    ]

    def get_initial_queryset(self, request=None):
        """To load a queryset into the datatable"""
        return (
            TimesheetEntry.objects.select_related("user", "project")
            .date_range(
                request.REQUEST.get("from_date"),
                request.REQUEST.get("to_date"),
            )
            .kpi_fields()
        )


class DetaileEfficiencyDatatable(CustomDatatable):
    """
    This class is responsible for Datatable corresponding to Team specific Efficiency
    """

    model = TimesheetEntry
    search_value_seperator = "+"

    column_defs = [
        {
            "name": "month",
            "title": "Month",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "expected_hours",
            "title": "Expected hours",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "actual_hours",
            "title": "Actual hours",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "capacity",
            "title": "Capacity",
            "className": "text-center",
            "visible": True,
            "searchable": True,
        },
    ]

    def get_initial_queryset(self, request=None):
        """To load a queryset into the datatable"""
        return (
            TimesheetEntry.objects.select_related("user", "team")
            .date_range(
                request.REQUEST.get("from_date"),
                request.REQUEST.get("to_date"),
            )
            .annotate(
                month=Func(
                    F("entry_date"),
                    Value("Month-YYYY"),
                    function="to_char",
                    output_field=CharField(),
                ),
            )
            .values("month")
            .filter(team__id=int(request.REQUEST.get("team_id")))
            .annotate(
                expected_hours=Sum("user__expected_user_efficiencies__expected_efficiency"),
                actual_hours=Sum("authorized_hours"),
                capacity=Round(
                    Avg(
                        100
                        * (F("authorized_hours"))
                        / (F("user__expected_user_efficiencies__expected_efficiency"))
                    )
                ),
            )
        )

    def render_dict_column(self, row, column):
        # This is responsible for updating the capacity data with various colors based on the value
        if column == "Capacity":
            if int(row["Capacity"]) >= 75:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 \
                    px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'
            if 50 < int(row["Capacity"]) < 75:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 \
                    px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'

            return f'<span class="bg-dark-red-10 text-dark-red py-0.5 \
                    px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'
        return super().render_dict_column(row, column)
