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
    Case,
    When,
    FloatField,
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
    data = get_object_or_404(Team, pk = pk)
    context = {"data" : data}
    return render(
        request=request,
        template_name="detailed_efficiency.html",
        context=context,
    )


@login_required()
def team_report(request):
    context = {}
    return render(
        request=request,
        template_name="team.html",
        context=context,
    )


@login_required()
def project_report(request):
    context = {}
    return render(
        request=request,
        template_name="project.html",
        context=context,
    )


@login_required()
def team_summary(request, pk):
    data = get_object_or_404(Team, pk = pk)
    # data = Team.objects.get(id = name)
    context = {"data" : data}
    return render(
        request=request,
        template_name="team_summary.html",
        context=context,
    )


@login_required()
def project_summary(request, pk):
    data = get_object_or_404(Project, pk = pk)
    context = {"data" : data}
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
            "className" : "text-center"
        },
    ]


    def customize_row(self, row, obj):
        buttons = template_utils.show_btn(reverse("detailed_efficiency", args=[obj['pk']]))
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return


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
                & Q(entry_date__range=(request.REQUEST.get('datafrom'), request.REQUEST.get('dateto')))
            )
            .values("team__name")
            .annotate(
                capacity=Round(Avg(
                    100
                    * (F("authorized_hours"))
                    / (F("user__expected_user_efficiencies__expected_efficiency"))
                ), 2),
                pk=F("team__id"),
                action = F("team__id")
            )
            .order_by("team__id")
        )
        return data
    

    def render_column(self, row, column):
        if column == 'capacity':
            if int(row["capacity"])>=75:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'
            elif 50<int(row['capacity'])<75:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["capacity"]}</span>'
        return super().render_column(row, column)


    # def render_row_details(self, pk, request=None):
    #     data = (
    #         TimesheetEntry.objects.select_related("user", "team")
    #         .filter(
    #             Q(
    #                 entry_date__range=(
    #                     F("user__expected_user_efficiencies__effective_from"),
    #                     Coalesce(
    #                         F("user__expected_user_efficiencies__effective_to"), now
    #                     ),
    #                 )
    #             )
    #             & Q(entry_date__range=("2022-01-01", "2023-01-01"))
    #         )
    #         .annotate(
    #             Month=Func(
    #                 F("entry_date"),
    #                 Value("MonthYYYY"),
    #                 function="to_char",
    #                 output_field=CharField(),
    #             ),
    #         )
    #         .values("Month")
    #         .filter(team__id=pk)
    #         .annotate(
    #             Team_Name=F("team__name"),
    #             Expected_hours=Sum(
    #                 "user__expected_user_efficiencies__expected_efficiency"
    #             ),
    #             Actual_hours=Sum("authorized_hours"),
    #             Capacity=Avg(
    #                 100
    #                 * (F("authorized_hours"))
    #                 / (F("user__expected_user_efficiencies__expected_efficiency"))
    #             ),
    #         )
    #     )
    #     html = '<table class="display border-0 table-with-no-border dataTable no-footer"><tr><thead>'
    #     for header in list(data)[0].keys():
    #         html += "<td>%s</td>" % (header)
    #     html += "</thead><tbody>"
    #     for field in list(data):
    #         html += "<tr>"
    #         for value in field.values():
    #             html += "<td>%s</td>" % (value)
    #         html += "</tr>"
    #     html += "</tbody></table>"
    #     return html


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
            "className" : "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "day",
            "title": "<div class= 'text-center'>Date</div>",
            "className" : "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency_capacity",
            "title": "<div class= 'text-center'>Efficiency Capacity <br> (Accomplishment)</div>",
            "className" : "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "monetization_capacity",
            "title": "<div class= 'text-center'>Monetization Capacity</div>",
            "className" : "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "gap",
            "title": "<div class= 'text-center'>Gap</div>",
            "className" : "text-center",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "ratings",
            "title": "<div class= 'text-center'>Ratings</div>",
            "className" : "text-center",
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
                            / Sum("user__expected_user_efficiencies__expected_efficiency")
                        ), 2
                    ),
                    output_field=FloatField(),
                ), 
                efficiency_capacity = Sum(F('authorized_hours')),
                monetization_capacity = Sum(F('user__expected_user_efficiencies__expected_efficiency')),
                ratings = Sum(F('authorized_hours'))
            )
            .filter(entry_date__year = request.REQUEST.get('year_filter'), 
                    entry_date__month = request.REQUEST.get('month_filter'))
        )
        return data
    

    def render_column(self, row, column):
        if column == "gap":
            return f'{row["gap"]}%'
        if column == "ratings":
            if int(row["gap"])<=15:
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
            .filter(team__id=int(request.REQUEST.get('team_filter')))
            .annotate(
                Team_Name=F("team__name"),
                Expected_hours=Sum(
                    "user__expected_user_efficiencies__expected_efficiency"
                ),
                Actual_hours=Sum("authorized_hours"),
                Capacity=Round(Avg(
                    100
                    * (F("authorized_hours"))
                    / (F("user__expected_user_efficiencies__expected_efficiency"))
                )),
            )
        )
        return data
    

    def render_column(self, row, column):
        if column == 'Capacity':
            if int(row["Capacity"])>=75:
                return f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'
            elif 50<int(row['Capacity'])<75:
                return f'<span class="bg-yellow-100 text-yellow-800 py-0.5 px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'
            else:
                return f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">{row["Capacity"]}</span>'
        return super().render_column(row, column)


class TeamsDatatable(CustomDatatable):
    model = TimesheetEntry
    search_value_seperator = "+"
    show_column_filters = False
    initial_order = [['team__name', 'asc'],]
    column_defs = [
        {
            "name": "team__name",
            "title": "Team",
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
            "name": "efficiency",
            "title": "Efficiency",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity",
            "title": "Productivity",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency_gap",
            "title": "Gap in Efficiency",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity_gap",
            "title": "Gap in Productivity",
            "visible": True,
            "searchable": True,
        },
        {
            "name" : "action",
            "title" : "Action",
            "visible" : True,
            "orderable" : False
        }
    ]


    def get_response_dict(self, request, paginator, draw_idx, start_pos):
        response = super().get_response_dict(request, paginator, draw_idx, start_pos) 
        data = list(TimesheetEntry.objects.select_related('user', 'team')
                .filter(
                Q(
                    entry_date__range=(
                        F("user__expected_user_efficiencies__effective_from"),
                        Coalesce(
                            F("user__expected_user_efficiencies__effective_to"), now
                        ),
                    )
                )
                & Q(entry_date__range=(request.REQUEST.get('datafrom'), request.REQUEST.get('dateto')))
                )
                .annotate(number = Count('team__id', distinct=True))
                .values('number')
                .annotate(
                    capacity = Sum(F('user__expected_user_efficiencies__expected_efficiency')),
                    efficiency = Sum(F('authorized_hours')),
                    productivity = Sum(F('billed_hours')),
                    efficiency_gap = Round(
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
                        ), 2
                    ),
                    productivity_gap = Round(
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
                        ), 2
                    )
                )
            )
        response['extra_data'] = data
        return response


    def customize_row(self, row, obj):
        buttons = template_utils.show_btn(reverse("team_summary", args=[obj['team__id']]))
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return


    def get_initial_queryset(self, request=None):
        data = (TimesheetEntry.objects.select_related('user', 'team')
                .filter(
                Q(
                    entry_date__range=(
                        F("user__expected_user_efficiencies__effective_from"),
                        Coalesce(
                            F("user__expected_user_efficiencies__effective_to"), now
                        ),
                    )
                )
                & Q(entry_date__range=(request.REQUEST.get('datafrom'), request.REQUEST.get('dateto')))
                )
                .values('team__id')
                .annotate(
                    capacity = Sum(F('user__expected_user_efficiencies__expected_efficiency')),
                    efficiency = Sum(F('authorized_hours')),
                    productivity = Sum(F('billed_hours')),
                )
                .annotate(
                    efficiency_gap = Round(
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
                        ), 2
                    ),
                    productivity_gap = Round(
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
                        ), 2
                    ),
                    action = F('team__name'),
                    team__name = F('team__name')
                )
            )

        return data
    

class Organization(CustomDatatable):
    model = TimesheetEntry
    search_value_seperator = "+"
    show_column_filters = False
    column_defs = [
        {
            "name": "user__name",
            "title": "UserName",
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
            "name": "efficiency",
            "title": "Efficiency",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity",
            "title": "Productivity",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency_gap",
            "title": "Gap in Efficiency",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity_gap",
            "title": "Gap in Efficiency",
            "visible": True,
            "searchable": True,
        },
    ]


    def get_initial_queryset(self, request=None):
        sample = TimesheetEntry.datatable.join('user', 'team').date_range(datefrom=request.REQUEST.get('datafrom'), dateto= request.REQUEST.get('dateto')).group(group_by = 'user__name').efficiency_fields().filter(team__id = request.REQUEST.get('team_filter'))
        return sample
    

    def get_response_dict(self, request, paginator, draw_idx, start_pos):
        response =  super().get_response_dict(request, paginator, draw_idx, start_pos)
        data = list(TimesheetEntry.datatable.join('user', 'team').date_range(datefrom=request.REQUEST.get('datafrom'), dateto= request.REQUEST.get('dateto')).group(group_by = 'team__name').efficiency_fields().filter(team__id = request.REQUEST.get('team_filter')))
        response['extra_data'] = data
        return response
    

class ProjectSummaryDatatable(CustomDatatable):
    model = TimesheetEntry
    search_value_seperator = "+"
    show_column_filters = False
    column_defs = [
        {
            "name": "user__name",
            "title": "UserName",
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
            "name": "efficiency",
            "title": "Efficiency",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity",
            "title": "Productivity",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency_gap",
            "title": "Gap in Efficiency",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity_gap",
            "title": "Gap in Efficiency",
            "visible": True,
            "searchable": True,
        },
    ]


    def get_initial_queryset(self, request=None):
        data = TimesheetEntry.datatable.join('user', 'project').date_range(datefrom=request.REQUEST.get('datafrom'), dateto= request.REQUEST.get('dateto')).group(group_by = 'user__name').efficiency_fields().filter(project__id = request.REQUEST.get('team_filter'))
        return data
    

    def get_response_dict(self, request, paginator, draw_idx, start_pos):
        response =  super().get_response_dict(request, paginator, draw_idx, start_pos)
        data = list(TimesheetEntry.datatable.join('user', 'project').date_range(datefrom=request.REQUEST.get('datafrom'), dateto= request.REQUEST.get('dateto')).group(group_by = 'project__name').efficiency_fields().filter(project__id = request.REQUEST.get('team_filter')))
        response['extra_data'] = data
        return response    

class ProjectsDatatable(CustomDatatable):
    model = TimesheetEntry
    search_value_seperator = "+"
    show_column_filters = False
    initial_order = [['team__name', 'asc'],]
    column_defs = [
        {
            "name": "team__name",
            "title": "Team",
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
            "name": "efficiency",
            "title": "Efficiency",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity",
            "title": "Productivity",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "efficiency_gap",
            "title": "Gap in Efficiency",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "productivity_gap",
            "title": "Gap in Productivity",
            "visible": True,
            "searchable": True,
        },
        {
            "name" : "action",
            "title" : "Action",
            "visible" : True,
            "orderable" : False
        }
    ]


    def get_response_dict(self, request, paginator, draw_idx, start_pos):
        response = super().get_response_dict(request, paginator, draw_idx, start_pos) 
        data = list(TimesheetEntry.objects.select_related('user', 'project')
                .filter(
                Q(
                    entry_date__range=(
                        F("user__expected_user_efficiencies__effective_from"),
                        Coalesce(
                            F("user__expected_user_efficiencies__effective_to"), now
                        ),
                    )
                )
                & Q(entry_date__range=(request.REQUEST.get('datafrom'), request.REQUEST.get('dateto')))
                )
                .annotate(number = Count('project__id', distinct=True))
                .values('number')
                .annotate(
                    capacity = Sum(F('user__expected_user_efficiencies__expected_efficiency')),
                    efficiency = Sum(F('authorized_hours')),
                    productivity = Sum(F('billed_hours')),
                    efficiency_gap = Round(
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
                        ), 2
                    ),
                    productivity_gap = Round(
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
                        ), 2
                    )
                )
            )
        response['extra_data'] = data
        return response


    def customize_row(self, row, obj):
        buttons = template_utils.show_btn(reverse("project_summary", args=[obj['project__id']]))
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return


    def get_initial_queryset(self, request=None):
        data = (TimesheetEntry.objects.select_related('user', 'project')
                .filter(
                Q(
                    entry_date__range=(
                        F("user__expected_user_efficiencies__effective_from"),
                        Coalesce(
                            F("user__expected_user_efficiencies__effective_to"), now
                        ),
                    )
                )
                & Q(entry_date__range=(request.REQUEST.get('datafrom'), request.REQUEST.get('dateto')))
                )
                .values('project__id')
                .annotate(
                    capacity = Sum(F('user__expected_user_efficiencies__expected_efficiency')),
                    efficiency = Sum(F('authorized_hours')),
                    productivity = Sum(F('billed_hours')),
                )
                .annotate(
                    efficiency_gap = Round(
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
                        ), 2
                    ),
                    productivity_gap = Round(
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
                        ), 2
                    ),
                    action = F('project__name'),
                    team__name = F('project__name')
                )
            )
        # data = TimesheetEntry.datatable.join('user', 'project').date_range(datefrom=request.REQUEST.get('datafrom'), dateto= request.REQUEST.get('dateto')).group(group_by = 'project__id').efficiency_fields()
        return data

