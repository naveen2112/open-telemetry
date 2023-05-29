from django.forms import model_to_dict
from django.http import JsonResponse, QueryDict
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from core import template_utils
from core.utils import CustomDatatable
from hubble.models.timeline import Timeline
from hubble.models.timeline_task import TimelineTask
from hubble.models.user import User
from training.forms import TimelineTaskForm
from django.urls import reverse

class TimelineTemplateTaskDataTable(CustomDatatable):
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
        {"name": "action", "title": "Action", "visible": True, "searchable": False, "orderable": False, "className": "text-center"},
    ]

    def customize_row(self, row, obj):
        buttons = (
            template_utils.edit_button(reverse("timeline-task.show", args=[obj.id]))
            + template_utils.delete_button("deleteTimeline('" + reverse("timeline-task.delete", args=[obj.id]) + "')"))
        row[
            "action"
        ] = f"<div class='form-inline justify-content-center'>{buttons}</div>"
        row["name"] = f"<span data-id='{obj.id}'>{obj.name}</span>"
        return

    def get_initial_queryset(self, request=None):
        return TimelineTask.objects.filter(timeline=request.POST.get("timeline_id"))


def update_order(request):
    data = request.POST.getlist("data[]")
    for order, id in enumerate(data):
        task = TimelineTask.objects.get(id=id)
        task.order = order + 1
        task.save()
    return JsonResponse({"status": "success"})


def create_timeline_task(request):
    """
    Create Timeline Template Task
    """
    if request.method == "POST":
        form = TimelineTaskForm(request.POST)
        timeline = Timeline.objects.get(id=request.POST.get("timeline_id"))
        user = User.objects.get(id=58)
        # TODO :: Need to remove the user after adding the authentication logic
        task = TimelineTask.objects.filter(timeline=request.POST.get("timeline_id"))
        if form.is_valid():  # Check if the valid or not
            timeline_task = form.save(commit=False)
            timeline_task.timeline = timeline
            timeline_task.created_by = user
            timeline_task.order = task.count() + 1
            timeline_task.save()
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


def timeline_task_data(request, pk):
    """
    Timeline Template Task Update Form Data
    """
    try:
        data = {
            "timeline_task": model_to_dict(get_object_or_404(TimelineTask, id=pk))
        }  # Covert django queryset object to dict,which can be easily serialized and sent as a JSON response
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse(
            {"message": "No timeline template task found"}, status=500
        )


def update_timeline_task(request, pk):
    """
    Update Timeline Template Task
    """
    form = TimelineTaskForm(request.POST, instance=get_object_or_404(TimelineTask, id=pk))
    if form.is_valid():  # Check if the valid or not
        form.save()
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


@require_http_methods(["DELETE"])  # This decorator ensures that the view function is only accessible through the DELETE HTTP method
def delete_timeline_task(request, pk):
    """
    Delete Timeline Template Task
    Soft delete the template and record the deletion time in deleted_at field
    """
    try:
        timeline_task = get_object_or_404(TimelineTask, id=pk)
        timeline_task.delete()
        return JsonResponse({"message": "Timeline Template Task deleted succcessfully"})
    except Exception as e:
        return JsonResponse(
            {"message": "Error while deleting Timeline Template Task!"}, status=500
        )