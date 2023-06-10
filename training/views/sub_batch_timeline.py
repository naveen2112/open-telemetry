import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView

from core import template_utils
from core.utils import CustomDatatable, calculate_duration
from hubble.models.holiday import Holiday
from hubble.models.sub_batch import SubBatch
from hubble.models.sub_batch_timeline_task import SubBatchTaskTimeline
from training.forms import SubBatchTimelineForm


class SubBatchTimeline(LoginRequiredMixin, DetailView):
    """
    Sub batch Timeline
    """

    extra_context = {"form": SubBatchTimelineForm()}
    model = SubBatch
    template_name = "sub_batch/timeline.html"


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
        return self.model.objects.filter(sub_batch=request.POST.get("sub_batch_id"))

    def customize_row(self, row, obj):
        if obj.can_editable():
            buttons = template_utils.edit_button(
                reverse("sub_batch.timeline.show", args=[obj.id])
            ) + template_utils.delete_button(
                "removeTimeline('"
                + reverse("sub_batch.timeline.remove", args=[obj.id])
                + "')"
            )
            row[
                "action"
            ] = f"<div class='form-inline justify-content-center'>{buttons}</div>"
        else:
            row["action"] = f"<div class='form-inline justify-content-center'>-</div>"
        row["start_date"] = obj.start_date.strftime("%d %b %Y")
        row["end_date"] = obj.end_date.strftime("%d %b %Y")
        row["order"] = f"<span data-id='{obj.id}'>{obj.order}</span>"
        return


@login_required()
def create_sub_batch_timeline(request, pk):
    """
    Create Task Timeline
    """
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
            if len(task_list) > 0 and task_list[0]:
                start_date = datetime.datetime.strptime(
                    str(task_list[0].start_date.date()), "%Y-%m-%d"
                )
            else:
                start_date = datetime.datetime.strptime(
                    str(sub_batch.start_date), "%Y-%m-%d"
                )

            duration = datetime.timedelta(
                hours=float(request.POST.get("days")) * 8
            )  # Working hours for a day

            holidays = Holiday.objects.values_list("date_of_holiday")
            values = calculate_duration(
                holidays,
                start_date,
                duration,
                number_of_days=float(request.POST.get("days")),
            )

            timeline_task.start_date = values[0]
            timeline_task.end_date = values[1]
            timeline_task.order = int(request.POST.get("order"))
            timeline_task.save()

            start_date = datetime.datetime.combine(values[2], values[3])
            order = int(request.POST.get("order"))
            for task in task_list:
                if task.id != timeline_task.id:
                    order += 1
                    task.order = order
                    duration = datetime.timedelta(
                        hours=task.days * 8
                    )  # Working hours for a day
                    values = calculate_duration(
                        holidays, start_date, duration, number_of_days=task.days
                    )
                    task.start_date = values[0]
                    task.end_date = values[1]
                    task.save()
                    start_date = datetime.datetime.combine(values[2], values[3])

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
def sub_batch_timeline_data(request, pk):
    """
    Sub batch timeline data
    """
    data = {
        "timeline": model_to_dict(get_object_or_404(SubBatchTaskTimeline, id=pk))
    }  # Covert django queryset object to dict,which can be easily serialized and sent as a JSON response
    return JsonResponse(data, safe=False)


@login_required()
def update_sub_batch_timeline(request, pk):
    current_task = get_object_or_404(SubBatchTaskTimeline, id=pk)
    if current_task.can_editable():
        form = SubBatchTimelineForm(request.POST, instance=current_task)
        if form.is_valid():
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
    return JsonResponse(
        {"message": "This task has been already started", "status": "error"}
    )


@login_required()
def update_task_sequence(request):
    task_order = request.POST.getlist("data[]")
    sub_batch_task = SubBatchTaskTimeline.objects.get(id=task_order[0])
    first_task = SubBatchTaskTimeline.objects.filter(
        sub_batch=sub_batch_task.sub_batch
    ).first()  # need to check
    start_date = datetime.datetime.strptime(
        str(first_task.start_date.date()), "%Y-%m-%d"
    )
    order = 0
    holidays = Holiday.objects.values_list("date_of_holiday")
    order = 0
    for task_id in task_order:
        task = SubBatchTaskTimeline.objects.get(id=task_id)
        duration = datetime.timedelta(hours=task.days * 8)
        order += 1
        task.order = order
        values = calculate_duration(
            holidays, start_date, duration, number_of_days=task.days
        )
        task.start_date = values[0]
        task.end_date = values[1]
        task.save()
        start_date = datetime.datetime.combine(values[2], values[3])
    return JsonResponse({"status": "success"})


@login_required()
@require_http_methods(
    ["DELETE"]
)  # This decorator ensures that the view function is only accessible through the DELETE HTTP method
def remove_sub_batch_timeline(request, pk):
    """
    Delete Sub Batch Task
    Soft delete the Sub Batch Task and record the deletion time in deleted_at field
    """
    try:
        timeline = get_object_or_404(SubBatchTaskTimeline, id=pk)
        if timeline.can_editable():
            timeline.delete()
            return JsonResponse({"message": "Task deleted succcessfully"})
        else:
            return JsonResponse(
                {"message": "This task has been already started!"}, status=500
            )
    except Exception as e:
        return JsonResponse({"message": "Error while deleting Task!"}, status=500)
