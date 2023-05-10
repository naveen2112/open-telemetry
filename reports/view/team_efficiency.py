from django.urls import reverse
from hubble.models import TimesheetEntry
from django.db.models import (
    F,
    Count,
)
from core.utils import CustomDatatable
from core import template_utils

default_values = [
    {
        "number": "-",
        "capacity": "-",
        "efficiency": "-",
        "productivity": "-",
        "efficiency_gap": "-",
        "productivity_gap": "-",
    }
]


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
            data = default_values
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


class TeamSummaryDatatable(CustomDatatable):
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
            data = default_values
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
