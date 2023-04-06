from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ajax_datatable import AjaxDatatableView
from hubble.models import TimesheetEntry
from datetime import date
from django.db.models.functions import Coalesce
from django.db.models import (
    Avg,
    F,
    Q,
    Sum
)
from core.utils import CustomDatatable

now = date.today()


@login_required()
def index(request):
    context = {}
    return render(
        request=request,
        template_name="report.html",
        context=context,
    )


class datatable(CustomDatatable):
    model = TimesheetEntry
    initial_order = [["team__id", "asc"],]
    search_value_seperator = "+"
    show_column_filters = False
    column_defs = [
        {   
            "name": "team__id",
            "title": "Team-ID",
            "visible": True,
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
        data = (
            TimesheetEntry.objects.prefetch_related("user_id", "team")
            .filter(
                Q(
                    entry_date__range=(
                        F("user_id__effective_from"),
                        Coalesce(F("user_id__effective_to"), now),
                    )
                )
                & Q(entry_date__range=("2022-01-01", "2023-01-01"))
            )
            .values("team__id", "team__name")
            .annotate(
                capacity=Avg(
                    100 * (F("authorized_hours")) / (F("user_id__expected_efficiency"))
                ),
            )
            .order_by("team__id")
        )
        return data


    def render_row_details(self, pk, request=None):
        data = (
            TimesheetEntry.objects.select_related("user_id", "team")
            .filter(
                Q(
                    entry_date__range=(
                        F("user_id__effective_from"),
                        Coalesce(F("user_id__effective_to"), now),
                    )
                )
                & Q(entry_date__range=("2022-01-01", "2023-01-01"))
            )
            .values("team__name")
            .filter(team__id=pk)
            .annotate(
                capacity=Avg(
                    100 * (F("authorized_hours")) / (F("user_id__expected_efficiency"))
                ),
                actual_hours=Sum("authorized_hours"),
                expected_hours=Sum("user_id__expected_efficiency"),
            )
        )
        html = '<table class="row-details">'
        for tag, value in list(data)[0].items():
            html += "<tr><td>%s</td><td>%s</td></tr>" % (tag, value)
        html += "</table>"
        return html