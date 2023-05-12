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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class TimelineTemplateTaskDataTable(CustomDatatable, LoginRequiredMixin):
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

    def customize_row(self, row, obj):
        buttons = template_utils.edit_btn(obj.id) + template_utils.delete_btn(
            "deleteTimeline(" + str(obj.id) + ")"
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        row["name"] = f'<span data-id="{obj.id}">{obj.name}</span>'
        return

    def get_initial_queryset(self, request=None):
        return TimelineTask.objects.filter(timeline=request.POST.get("timeline_id"))


@login_required()
def update_order(request):
    data = request.POST.getlist("data[]")
    for order, id in enumerate(data):
        task = TimelineTask.objects.get(id=id)
        task.order = order + 1
        task.save()
    return JsonResponse({"status": "success"})


@login_required()
def create_timelinetask_template(request):
    """
    Create Timeline Template Task
    """
    if request.method == "POST":
        form = TimelineTaskForm(request.POST)
        timeline = Timeline.objects.get(id=request.POST.get("timeline_id"))
        task = TimelineTask.objects.filter(timeline=request.POST.get("timeline_id"))
        if form.is_valid():  # Check if the valid or not
            timeline_task = form.save(commit=False)
            timeline_task.timeline = timeline
            timeline_task.created_by = request.user
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


@login_required()
def timelinetask_update_form(request):
    """
    Timeline Template Task Update Form Data
    """
    id = request.GET.get("id")
    timeline_task = TimelineTask.objects.get(id=id)
    data = {
        "timeline_task": model_to_dict(timeline_task)
    }  # Covert django queryset object to dict,which can be easily serialized and sent as a JSON response
    return JsonResponse(data, safe=False)


@login_required()
def update_timelinetask_template(request):
    """
    Update Timeline Template Task
    """
    id = request.POST.get("id")
    timeline_task = TimelineTask.objects.get(id=id)
    form = TimelineTaskForm(request.POST, instance=timeline_task)
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


@login_required()
@require_http_methods(
    ["DELETE"]
)  # This decorator ensures that the view function is only accessible through the DELETE HTTP method
def delete_timelinetask_template(request):
    """
    Delete Timeline Template Task
    Soft delete the template and record the deletion time in deleted_at field
    """
    try:
        delete = QueryDict(
            request.body
        )  # Creates a QueryDict object from the request body
        id = delete.get("id")  # Get id from dictionary
        timeline_task = get_object_or_404(TimelineTask, id=id)
        timeline_task.delete()
        return JsonResponse({"message": "Timeline Template Task deleted succcessfully"})
    except Exception as e:
        return JsonResponse(
            {"message": "Error while deleting Timeline Template Task!"}, status=500
        )
