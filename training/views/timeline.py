"""
Django view and related functions for managing timeline templates, 
including creating, updating, deleting, and displaying details of timeline templates
"""
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, FloatField, Sum
from django.db.models.functions import Coalesce
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, FormView

from core import template_utils
from core.utils import CustomDatatable, validate_authorization
from hubble.models import Timeline, TimelineTask
from training.forms import TimelineForm, TimelineTaskForm


class TimelineTemplate(LoginRequiredMixin, FormView):
    """
    Timeline Template
    """

    form_class = TimelineForm
    template_name = "timeline_template.html"


class TimelineTemplateDataTable(LoginRequiredMixin, CustomDatatable):
    """
    Timeline Template Datatable
    """

    model = Timeline

    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": True},
        {"name": "Days", "visible": True, "searchable": True},
        {
            "name": "is_active",
            "title": "Is Active",
            "visible": True,
            "searchable": True,
        },
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

    def get_initial_queryset(self, request=None):  # pylint: disable=unused-argument
        """
        The function returns an initial queryset of objects from a model, filtering out
        those with a non-null "deleted_at" field in the related "task_timeline" model.
        """
        return self.model.objects.filter(task_timeline__deleted_at__isnull=True).annotate(
            Days=Coalesce(
                Sum(F("task_timeline__days")),
                0,
                output_field=FloatField(),
            )
        )  # TODO :: should we need '-' incase we need to CAST here

    def customize_row(self, row, obj):
        """
        The function customize_row customizes a row by adding buttons based on the user's role.
        """
        buttons = template_utils.show_button(reverse("timeline-template.detail", args=[obj.id]))
        if self.request.user.is_admin_user:
            buttons += (
                template_utils.edit_button(reverse("timeline-template.show", args=[obj.id]))
                + template_utils.delete_button(
                    "deleteTimeline('" + reverse("timeline-template.delete", args=[obj.id]) + "')"
                )
                + template_utils.duplicate_button(reverse("timeline-template.show", args=[obj.id]))
            )
        row["action"] = f"<div class='form-inline justify-content-center'>{buttons}</div>"
        return row

    def render_column(self, row, column):
        """
        The function render_column takes a row and column as input and returns a HTML span element
        with a specific class and text based on the value of the column in the row
        """
        if column == "is_active":
            if row.is_active:
                return "<span class='bg-mild-green-10 text-mild-green py-0.5 \
                    px-1.5 rounded-xl text-sm'>Active</span>"
            return "<span class='bg-dark-red-10 text-dark-red py-0.5 \
                px-1.5 rounded-xl text-sm'>In Active</span>"
        return super().render_column(row, column)


@login_required()
@validate_authorization()
def create_timeline_template(request):
    """
    Create Timeline Template
    """
    response_data = {}  # Initialize an empty dictionary
    if request.method == "POST":
        form = TimelineForm(request.POST)
        if form.is_valid():  # Check if form is valid or not
            timeline = form.save(commit=False)
            timeline.is_active = request.POST.get("is_active") == "true"  # Set is_active to true
            # if the input is checked else it will be false
            timeline.created_by = request.user
            timeline.save()

            if request.POST.get("id"):
                timeline_task = TimelineTask.objects.filter(timeline=request.POST.get("id"))
                order = 0
                for task in timeline_task:
                    order += 1
                    TimelineTask.objects.create(
                        name=task.name,
                        days=task.days,
                        timeline=timeline,
                        present_type=task.present_type,
                        task_type=task.task_type,
                        order=order,
                        created_by=task.created_by,
                    )
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
def timeline_template_data(request, pk):  # pylint: disable=unused-argument
    """
    Timeline Template Update Form Data
    """
    try:
        data = {
            "timeline": model_to_dict(get_object_or_404(Timeline, id=pk))
        }  # Covert django queryset object to dict,which can be easily
        # serialized and sent as a JSON response
        return JsonResponse(data, safe=False)
    except Exception as exception:
        logging.error(
            "An error has occured while fetching the Timeline \n%s",
            exception,
        )
        return JsonResponse({"message": "No timeline template found"}, status=500)


@login_required()
@validate_authorization()
def update_timeline_template(request, pk):
    """
    Update Timeline Template
    """
    form = TimelineForm(
        request.POST,
        instance=get_object_or_404(Timeline, id=pk),
    )
    if form.is_valid():  # check if form is valid or not
        timeline = form.save(commit=False)
        timeline.is_active = request.POST.get("is_active") == "true"  # Set is_active to true
        # if the input is checked else it will be false
        timeline.save()
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


@validate_authorization()
@require_http_methods(
    ["DELETE"]
)  # This decorator ensures that the view function is only accessible
# through the DELETE HTTP method
def delete_timeline_template(request, pk):  # pylint: disable=unused-argument
    """
    Delete Timeline Template
    Soft delete the template and record the deletion time in deleted_at field
    """
    try:
        timeline = get_object_or_404(Timeline, id=pk)
        TimelineTask.bulk_delete({"timeline_id": pk})
        timeline.delete()
        return JsonResponse({"message": "Timeline Template deleted successfully"})
    except Exception as exception:
        logging.error(
            "An error has occured while deleting the Timeline \n%s",
            exception,
        )
        return JsonResponse(
            {"message": "Error while deleting Timeline Template!"},
            status=500,
        )


class TimelineTemplateDetails(LoginRequiredMixin, DetailView):
    """
    Timeline Template Detail
    Display the timeline template tasks for the current template
    """

    model = Timeline
    extra_context = {"form": TimelineTaskForm()}
    template_name = "timeline_template_detail.html"
