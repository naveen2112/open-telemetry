"""
Django view that handles the creation, update, and deletion of sub-batch 
timelines and tasks, and provides data for displaying the timelines in a datatable
"""
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView

from core import template_utils
from core.utils import (
    CustomDatatable,
    schedule_timeline_for_sub_batch,
    validate_authorization,
)
from hubble.models import SubBatch, SubBatchTaskTimeline
from training.forms import SubBatchTimelineForm


class SubBatchTimeline(LoginRequiredMixin, DetailView):
    """
    Sub batch Timeline is used to display the timeline for a sub batch
    """

    extra_context = {"form": SubBatchTimelineForm()}
    model = SubBatch
    template_name = "sub_batch/timeline.html"


# The `SubBatchTimelineDataTable` class is a custom datatable for displaying and managing timeline
# tasks associated with a sub-batch.
class SubBatchTimelineDataTable(LoginRequiredMixin, CustomDatatable):
    """
    Timeline Template Task Datatable
    """

    model = SubBatchTaskTimeline

    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "order", "visible": True, "searchable": False},
        {"name": "name", "visible": True, "searchable": False},
        {"name": "days", "visible": True, "searchable": False},
        {"name": "present_type", "visible": True, "searchable": False},
        {"name": "task_type", "visible": True, "searchable": False},
        {"name": "start_date", "visible": True, "searchable": False},
        {"name": "end_date", "visible": True, "searchable": False},
        {"name": "created_at", "visible": False, "searchable": False},
        {"name": "disabled", "visible": False, "searchable": False},
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
        The function returns a queryset of objects filtered by the "sub_batch_id" value from the
        request's POST data.
        """
        return self.model.objects.filter(sub_batch=request.POST.get("sub_batch_id"))

    def customize_row(self, row, obj):
        """
        The function customize_row customizes the values of certain fields in a row object based on
        the properties of an input object.
        """
        row["disabled"] = obj.start_date.date() <= timezone.now().date()
        row["action"] = "<div class='form-inline justify-content-center'>-</div>"
        if self.request.user.is_admin_user:
            row["action"] = "<div class='form-inline justify-content-center'>-</div>"
            if obj.can_editable():
                buttons = template_utils.edit_button(
                    reverse("sub_batch.timeline.show", args=[obj.id])
                ) + template_utils.delete_button(
                    "deleteTimeline('" + reverse("sub_batch.timeline.delete", args=[obj.id]) + "')"
                )
                row["action"] = f"<div class='form-inline justify-content-center'>{buttons}</div>"
        row["start_date"] = obj.start_date.strftime("%d %b %Y")
        row["end_date"] = obj.end_date.strftime("%d %b %Y")
        row["order"] = f"<span data-id='{obj.id}'>{obj.order}</span>"
        return row


@login_required()
@validate_authorization()
def create_sub_batch_timeline(request, pk):
    """
    Create Task Timeline
    """
    response_data = {}  # Initialize an empty dictionary
    if request.method == "POST":
        form = SubBatchTimelineForm(request.POST)
        sub_batch = SubBatch.objects.get(id=pk)
        if form.is_valid():  # Check if the valid or not
            task_list = SubBatchTaskTimeline.objects.filter(
                sub_batch=pk,
                order__gte=request.POST.get("order"),
            )  # Remaining task after the insertion of intermediate task
            timeline_task = form.save(commit=False)
            timeline_task.sub_batch = sub_batch
            timeline_task.created_by = request.user
            timeline_task.save()

            order = int(request.POST.get("order"))
            for task in task_list:
                if task.id != timeline_task.id:
                    order += 1
                    task.order = order
                    task.save()
            schedule_timeline_for_sub_batch(sub_batch, is_create=False)
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
def sub_batch_timeline_data(request, pk):  # pylint: disable=unused-argument
    """
    Sub batch timeline data
    """
    data = {
        "timeline": model_to_dict(get_object_or_404(SubBatchTaskTimeline, id=pk))
    }  # Covert django queryset object to dict,which can be easily serialized
    # and sent as a JSON response
    return JsonResponse(data, safe=False)


@login_required()
@validate_authorization()
def update_sub_batch_timeline(request, pk):
    """
    The function update_sub_batch_timeline updates the timeline of a sub-batch
    task based on user input, and returns a JSON response indicating the
    success or failure of the update.
    """
    current_task = get_object_or_404(SubBatchTaskTimeline, id=pk)
    previous_duration = current_task.days
    sub_batch = SubBatch.objects.get(id=current_task.sub_batch_id)
    if current_task.can_editable():
        form = SubBatchTimelineForm(request.POST, instance=current_task)
        if form.is_valid():
            if form.cleaned_data["days"] != previous_duration:
                timeline_task = form.save(commit=False)
                timeline_task.sub_batch = sub_batch
                timeline_task.created_by = request.user
            form.save()
            schedule_timeline_for_sub_batch(sub_batch=sub_batch, is_create=False)
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
    return JsonResponse(
        {
            "message": "This task has been already started",
            "status": "error",
        }
    )


@login_required()
@validate_authorization()
def update_task_sequence(request):
    """
    The update_task_sequence function updates the order of tasks in a
    timeline and schedules the timeline for a sub-batch if all the tasks
    belong to the current timeline.
    """
    task_order = request.POST.getlist("data[]")
    check_valid_tasks = SubBatchTaskTimeline.objects.filter(
        sub_batch_id=request.POST.get("sub_batch_id"), id__in=task_order
    ).count()
    if check_valid_tasks == len(task_order):
        sub_batch_task = SubBatchTaskTimeline.objects.get(id=task_order[0])
        order = 0
        for task_id in task_order:
            task = SubBatchTaskTimeline.objects.get(id=task_id)
            order += 1
            task.order = order
            task.save()
        schedule_timeline_for_sub_batch(sub_batch_task.sub_batch, is_create=False)
        return JsonResponse({"status": "success"})
    return JsonResponse(
        {
            "message": "Some of the tasks doesn't belong to the current timeline",
            "status": "error",
        }
    )


@login_required()
@validate_authorization()
@require_http_methods(
    ["DELETE"]
)  # This decorator ensures that the view function is only accessible
# through the DELETE HTTP method
def delete_sub_batch_timeline(request, pk):  # pylint: disable=unused-argument
    """
    Delete Sub Batch Task
    Soft delete the Sub Batch Task and record the deletion time in deleted_at field
    """
    try:
        timeline = get_object_or_404(SubBatchTaskTimeline, id=pk)
        if timeline.can_editable():
            sub_batch = SubBatch.objects.get(id=timeline.sub_batch_id)
            task_list = SubBatchTaskTimeline.objects.filter(
                sub_batch=sub_batch.id,
                order__gt=timeline.order,
            )  # Remaining task after the deletion of the task
            if (SubBatchTaskTimeline.objects.filter(sub_batch=sub_batch.id).count()) > 1:
                # Check whether multiple tasks are available before deleting
                order = timeline.order - 1
                timeline.delete()
                for task in task_list:
                    order += 1
                    task.order = order
                    task.save()
                schedule_timeline_for_sub_batch(sub_batch=sub_batch, is_create=False)
                return JsonResponse({"message": "Task deleted succcessfully"})
            return JsonResponse(
                {
                    "message": "This is the last task, Atleast one"
                    " task should exist in the timeline"
                },
                status=500,
            )
        return JsonResponse(
            {"message": "This task has been already started!"},
            status=500,
        )
    except Exception as exception:
        logging.error(
            "An error has occurred while deleting the data \n%s",
            exception,
        )

        return JsonResponse({"message": "Error while deleting Task!"}, status=500)
