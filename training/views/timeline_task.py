"""
Django functions and classes related to managing timeline tasks in a Django 
web application, including creating, updating, and deleting tasks, 
as well as displaying them in a datatable
"""
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from core import template_utils
from core.utils import CustomDatatable, validate_authorization
from hubble.models import Timeline, TimelineTask
from training.forms import TimelineTaskForm


class TimelineTemplateTaskDataTable(
    LoginRequiredMixin, CustomDatatable
):
    """
    Timeline Template Task Datatable
    """

    model = TimelineTask

    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": False},
        {"name": "days", "visible": True, "searchable": False},
        {"name": "present_type", "visible": True, "searchable": False},
        {"name": "task_type", "visible": True, "searchable": False},
        {"name": "created_at", "visible": False, "searchable": False},
        {
            "name": "action",
            "title": "Action",
            "visible": True,
            "searchable": False,
            "orderable": False,
            "className": "text-center",
        },
    ]

    def get_initial_queryset(self, request=None):
        """
        The function returns an initial queryset filtered by the timeline ID
        obtained from the request's POST data.
        """
        return self.model.objects.filter(
            timeline=request.POST.get("timeline_id")
        )

    def customize_row(self, row, obj):
        """
        The function `customize_row` customizes a row by adding buttons
        for editing and deleting a task if the user is an admin, and adds a span
        element with the task name.
        """
        row[
            "action"
        ] = "<div class='form-inline justify-content-center'>-</div>"
        if self.request.user.is_admin_user:
            buttons = template_utils.edit_button(
                reverse("timeline-task.show", args=[obj.id])
            ) + template_utils.delete_button(
                "deleteTimeline('"
                + reverse("timeline-task.delete", args=[obj.id])
                + "')"
            )
            row[
                "action"
            ] = f"<div class='form-inline justify-content-center'>{buttons}</div>"
        row["name"] = f"<span data-id='{obj.id}'>{obj.name}</span>"
        return row


@login_required()
@validate_authorization()
def update_order(request):
    """
    The update_order function updates the order of tasks in a timeline based on the data received in
    the request
    """
    response_data = {}  # Initialize an empty dictionary
    data = request.POST.getlist("data[]")
    check_valid_tasks = TimelineTask.objects.filter(
        timeline_id=request.POST.get("timeline_id"), id__in=data
    ).count()
    if check_valid_tasks == len(data):
        for order, task_id in enumerate(data):
            task = TimelineTask.objects.get(id=task_id)
            task.order = order + 1
            task.save()
        response_data["status"] = "success"
    else:
        response_data = {
            "message": "Some of the tasks doesn't belong to the current timeline",
            "status": "error",
        }
    return JsonResponse(response_data)


@login_required()
@validate_authorization()
def create_timeline_task(request):
    """
    Create Timeline Template Task
    """
    response_data = {}  # Initialize an empty dictionary
    if request.method == "POST":
        form = TimelineTaskForm(request.POST)
        timeline = Timeline.objects.get(
            id=request.POST.get("timeline_id")
        )
        task = TimelineTask.objects.filter(
            timeline=request.POST.get("timeline_id")
        )
        if form.is_valid():  # Check if the valid or not
            timeline_task = form.save(commit=False)
            timeline_task.timeline = timeline
            timeline_task.created_by = request.user
            timeline_task.order = task.count() + 1
            timeline_task.save()
            response_data["status"] = "success"
        else:
            field_errors = form.errors.as_json()
            non_field_errors = form.non_field_errors().as_json()
            response_data = {
                "status": "error",
                "field_errors": field_errors,
                "non_field_errors": non_field_errors,
            }
    return JsonResponse(response_data)


@login_required()
@validate_authorization()
def timeline_task_data(request, primary_key):
    """
    Timeline Template Task Update Form Data
    """
    try:
        data = {
            "timeline_task": model_to_dict(
                get_object_or_404(TimelineTask, id=primary_key)
            )
        }  # Covert django queryset object to dict,which can be easily serialized
        # and sent as a JSON response
        return JsonResponse(data, safe=False)
    except Exception as exception:
        logging.error(
            "An error has occured while fetching the Timeline Task \n%s",
            exception,
        )
        return JsonResponse(
            {"message": "No timeline template task found"}, status=500
        )


@login_required()
@validate_authorization()
def update_timeline_task(request, primary_key):
    """
    Update Timeline Template Task
    """
    form = TimelineTaskForm(
        request.POST,
        instance=get_object_or_404(TimelineTask, id=primary_key),
    )
    if form.is_valid():  # Check if the valid or not
        form.save()
        return JsonResponse({"status": "success"})
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
@validate_authorization()
@require_http_methods(
    ["DELETE"]
)  # This decorator ensures that the view function is only accessible through the DELETE HTTP method
def delete_timeline_task(request, primary_key):
    """
    Delete Timeline Template Task
    Soft delete the template and record the deletion time in deleted_at field
    """
    try:
        timeline_task = get_object_or_404(TimelineTask, id=primary_key)
        timeline_task.delete()
        return JsonResponse(
            {"message": "Timeline Template Task deleted successfully"}
        )
    except Exception as exception:
        logging.error(
            "An error has occured while deleting the Timeline Task \n%s",
            exception,
        )
        return JsonResponse(
            {"message": "Error while deleting Timeline Template Task!"},
            status=500,
        )
