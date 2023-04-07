from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from hubble.models import TimesheetEntry, TimesheetUser
from datetime import date
from django.db.models.functions import Coalesce
from django.db.models import (
    Avg,
    F,
    Q,
    Sum
)
from core.utils import CustomDatatable

data = TimesheetEntry.objects.prefetch_related('user_id').values('user_id__user_id')
print(data.query)

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
    initial_order = [["team__name", "asc"],]
    search_value_seperator = "+"
    show_column_filters = False
    # table_row_id_fieldname = 'team__id'
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

    def render_column(self, row, column):
        if column == 'team__name' and row[column] == 'Python':
            return '<span class="bg-green-100 text-green-800 text-sm font-medium mr-2 px-2.5 py-0.5 rounded dark:bg-green-900 dark:text-green-300">Python</span>'
        return super().render_column(row, column)


    def get_initial_queryset(self, request=None):
        ''' Please rename anyone of the fields in the query to `pk`,
          so that it would be useful to render_row_details '''
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
            .values("team__name")
            .annotate(
                capacity=Avg(
                    100 * (F("authorized_hours")) / (F("user_id__expected_efficiency"))
                ),
                pk = F('team__id')
            )
            .order_by("team__id")
        )
        if 'team_filter' in request.REQUEST :
            team_filter = int(request.REQUEST.get('team_filter'))
            if team_filter != 0:
                data=data.filter(team__id = team_filter)
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