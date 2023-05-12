from django.forms.models import model_to_dict
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse, QueryDict
from hubble.models.timeline import Timeline
from training import forms
from django.views.generic import TemplateView, FormView, DetailView
from core.utils import CustomDatatable
from hubble import models
from core import template_utils
from django.db.models import Q, Sum, F, Count, FloatField
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class TimelineTemplate(FormView, LoginRequiredMixin):
    """
    Timeline Template
    """
    form_class = forms.TimelineForm
    template_name = "timeline_template.html"


class TimelineTemplateDataTable(CustomDatatable, LoginRequiredMixin):
    """
    Timeline Template Datatable
    """

    model = models.Timeline
    show_column_filters = False
    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": True},
        {"name": "Days", "visible": True, "searchable": True},
        {"name": "is_active", "visible": True, "searchable": True},
        {
            "name": "team",
            "visible": True,
            "searchable": True,
            "foreign_field": "team__name",
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
        buttons = (
            template_utils.show_btn(reverse("timeline-template.detail", args=[obj.id]))
            + template_utils.edit_btn(obj.id)
            + template_utils.delete_btn("deleteTimeline(" + str(obj.id) + ")")
            + template_utils.duplicate_btn(obj.id)
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return


    def render_column(self, row, column):
        if column == "is_active":
            if row.is_active:
                return '<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">Active</span>'
            else:
                return '<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">In Active</span>'
        return super().render_column(row, column)


    def get_initial_queryset(self, request=None):
        data = models.Timeline.objects.annotate(Days=Sum(F("task_timeline__days")))
        return data


@login_required()
def create_timeline_template(request):
    """
    Create Timeline Template
    """
    if request.method == "POST":
        print(f'Requested user {request.user}')
        form = forms.TimelineForm(request.POST)
        if form.is_valid():  # Check if form is valid or not
            timeline = form.save(commit=False)
            timeline.is_active = (
                True if request.POST.get("is_active") == "true" else False
            )  # Set is_active to true if the input is checked else it will be false
            timeline.created_by = request.user
            timeline.save()
            return JsonResponse({"status": "success"})
        else:
            field_errors = form.errors.as_json()
            non_field_errors = form.non_field_errors().as_json()
            return JsonResponse(
                {
                    "status": "error",
                    "field_errors": field_errors,
                    "non_field_errors": non_field_errors,
                }
            )


@login_required()
def timeline_update_form(request):
    """
    Timeline Template Update Form Data
    """
    id = request.GET.get("id")
    timeline = models.Timeline.objects.get(id=id)
    data = {
        "timeline": model_to_dict(timeline)
    }  # Covert django queryset object to dict,which can be easily serialized and sent as a JSON response
    return JsonResponse(data, safe=False)


@login_required()
def update_timeline_template(request):
    """
    Update Timeline Template
    """
    id = request.POST.get("id")
    timeline = models.Timeline.objects.get(id=id)
    form = forms.TimelineForm(request.POST, instance=timeline)
    if form.is_valid():  # check if form is valid or not
        timeline = form.save(commit=False)
        timeline.is_active = (
            True if request.POST.get("is_active") == "true" else False
        )  # Set is_active to true if the input is checked else it will be false
        timeline.save()
        return JsonResponse({"status": "success"})
    else:
        field_errors = form.errors.as_json()
        non_field_errors = form.non_field_errors().as_json()
        return JsonResponse(
            {
                "status": "error",
                "field_errors": field_errors,
                "non_field_errors": non_field_errors,
            }
        )


@login_required()
@require_http_methods(
    ["DELETE"]
)  # This decorator ensures that the view function is only accessible through the DELETE HTTP method
def delete_timeline_template(request):
    """
    Delete Timeline Template
    Soft delete the template and record the deletion time in deleted_at field
    """
    try:
        delete = QueryDict(
            request.body
        )  # Creates a QueryDict object from the request body
        id = delete.get("id")  # Get id from dictionary
        timeline = get_object_or_404(models.Timeline, id=id)
        timeline.delete()
        return JsonResponse({"message": "Timeline Template deleted succcessfully"})
    except Exception as e:
        return JsonResponse(
            {"message": "Error while deleting Timeline Template!"}, status=500
        )


@login_required()
def timeline_duplicate_form(request):
    """
    Timeline Template Form Data
    """
    id = request.GET.get("id")
    timeline = models.Timeline.objects.get(id=id)
    data = {
        "timeline": model_to_dict(timeline)
    }  # Covert django queryset object to dict,which can be easily serialized and sent as a JSON response
    return JsonResponse(data, safe=False)


@login_required()
def duplicate_timeline_template(request):
    """
    Duplicate Timeline Template
    """
    id = request.POST.get("id")
    timeline = models.Timeline.objects.get(id=id)
    form = forms.TimelineForm(request.POST)
    if form.is_valid():  # Check the form is valid or not
        timeline = form.save(commit=False)
        timeline.is_active = (
            True if request.POST.get("is_active") == "true" else False
        )  # Set is_active to true if the input is checked else it will be false
        timeline.created_by = request.user
        timeline.save()
        timeline_task = models.TimelineTask.objects.filter(timeline=id)
        order = 0
        for task in timeline_task:
            order += 1
            timetask = models.TimelineTask.objects.create(
                name=task.name,
                days=task.days,
                timeline=timeline,
                present_type=task.present_type,
                task_type=task.task_type,
                order=order,
                created_by=task.created_by,
            )
        return JsonResponse({"status": "success"})
    else:
        field_errors = form.errors.as_json()
        non_field_errors = form.non_field_errors().as_json()
        return JsonResponse(
            {
                "status": "error",
                "field_errors": field_errors,
                "non_field_errors": non_field_errors,
            }
        )


@login_required()
def timeline_template_details(request, pk):
    """
    Timeline Template Detail
    Display the timeline template tasks for the current template
    """
    timeline = Timeline.objects.get(id=pk)
    form = forms.TimelineTaskForm()
    context = {"timeline": timeline, "form": form, "timeline_id": pk}
    return render(request, "timeline_template_detail.html", context)
