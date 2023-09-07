"""
Django view that handles the creation, update, deletion, and retrieval of
sub-batches and trainees within a batch management system
"""
import logging

import numpy as np
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Case, Count, F, OuterRef, Q, Subquery, Value, When
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView

from core import template_utils
from core.constants import (
    ABOVE_AVERAGE,
    AVERAGE,
    GOOD,
    MEET_EXPECTATION,
    NOT_YET_STARTED,
    POOR,
    TASK_TYPE_ASSESSMENT,
    USER_STATUS_INTERN,
)
from core.utils import (
    CustomDatatable,
    schedule_timeline_for_sub_batch,
    validate_authorization,
)
from hubble.models import (
    Batch,
    InternDetail,
    SubBatch,
    SubBatchTaskTimeline,
    Timeline,
    User,
)
from training.forms import AddInternForm, SubBatchForm


class SubBatchDataTable(LoginRequiredMixin, CustomDatatable):
    """
    Sub-Batch Datatable
    """

    model = SubBatch

    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": True},
        {
            "name": "team",
            "foreign_field": "team__name",
            "title": "Teams",
            "visible": True,
            "searchable": True,
        },
        {
            "name": "trainee_count",
            "title": "No. of Trainees",
            "visible": True,
            "searchable": False,
        },
        {
            "name": "primary_mentor",
            "title": "Reporting Persons",
            "visible": True,
            "searchable": False,
            "foreign_field": "primary_mentor__name",
        },
        {"name": "start_date", "visible": True, "searchable": False, "orderable": False},
        {
            "name": "timeline",
            "title": "Assigned Timeline Template",
            "visible": True,
            "searchable": True,
            "foreign_field": "timeline__name",
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

    def get_initial_queryset(self, request=None):
        """
        The function returns a queryset of model objects filtered by a batch ID
        and annotated with the count of related intern details that are not deleted.
        """
        return self.model.objects.filter(batch=request.POST.get("batch_id")).annotate(
            trainee_count=Count(
                "intern_details",
                filter=Q(intern_details__deleted_at__isnull=True),
            )
        )

    def customize_row(self, row, obj):
        """
        The function customize_row customizes a row in a table by
        adding buttons and formatting the start date.
        """
        buttons = template_utils.show_button(reverse("sub-batch.detail", args=[obj.id]))
        if self.request.user.is_admin_user:
            buttons += template_utils.edit_button_new_page(
                reverse("sub-batch.edit", args=[obj.id])
            ) + template_utils.delete_button(
                "deleteSubBatch('" + reverse("sub-batch.delete", args=[obj.id]) + "')"
            )
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        row["start_date"] = obj.start_date.strftime("%d %b %Y")
        return row

    def get_response_dict(self, request, paginator, draw_idx, start_pos):
        """
        The function `get_response_dict` adds extra data to the response
        dictionary by querying the database for the number of teams and
        trainees associated with a specific batch.
        """
        response = super().get_response_dict(request, paginator, draw_idx, start_pos)
        batch_id = request.POST.get("batch_id")
        extra_data = (
            Batch.objects.filter(id=batch_id)
            .annotate(
                no_of_teams=Coalesce(
                    Count(
                        "sub_batches__team",
                        distinct=True,
                        filter=Q(sub_batches__deleted_at__isnull=True),
                    ),
                    0,
                ),
                no_of_trainees=Count(
                    "sub_batches__intern_details",
                    filter=Q(sub_batches__intern_details__deleted_at__isnull=True),
                ),
            )
            .values("no_of_teams", "no_of_trainees")
        )
        response["extra_data"] = list(extra_data)
        return response


@login_required()
@validate_authorization()
def create_sub_batch(request, pk):
    """
    Create Sub-batch View
    """
    sub_batch_form = SubBatchForm()
    if request.method == "POST":
        sub_batch_form = SubBatchForm(request.POST)
        # Checking the trainee is already added in the other batch or not
        if "users_list_file" in request.FILES:
            excel_file = request.FILES["users_list_file"]
            data_frame = pd.read_excel(excel_file)
            data_frame.replace(chr(160), np.nan, inplace=True)
            data_frame = data_frame.dropna(how="all")
            if (data_frame.columns[0] == "employee_id") and (data_frame.columns[1] == "college"):
                data_frame["employee_id"] = data_frame["employee_id"].astype(int)
                if User.objects.filter(employee_id__in=data_frame["employee_id"]).count() == len(
                    data_frame["employee_id"]
                ):
                    if User.objects.filter(
                        employee_id__in=data_frame["employee_id"], status=USER_STATUS_INTERN
                    ).count() != len(data_frame["employee_id"]):
                        sub_batch_form.add_error(
                            None,
                            "Some of the users are not an intern",
                        )
                    elif InternDetail.objects.filter(
                        user__employee_id__in=data_frame["employee_id"]
                    ).exists():
                        sub_batch_form.add_error(
                            None,
                            "Some of the Users are already added in another sub-batch",
                        )  # Adding the non-field-error if the user aalready exists
                else:
                    sub_batch_form.add_error(
                        None,
                        "Some of the employee ids are not present in the "
                        "database, please check again",
                    )
            else:
                sub_batch_form.add_error(
                    None,
                    "Invalid keys are present in the file, please check the sample file",
                )
        else:
            sub_batch_form.add_error(
                None, "Please upload a file"
            )  # Adding the non-field-error if the file was not uploaded while submission
        if sub_batch_form.is_valid():  # Check if both the forms are valid or not
            sub_batch = sub_batch_form.save(commit=False)
            sub_batch.batch = Batch.objects.get(id=pk)
            sub_batch.created_by = request.user
            sub_batch.primary_mentor_id = request.POST.get("primary_mentor_id")
            sub_batch.save()
            sub_batch.secondary_mentors.set(request.POST.getlist("secondary_mentor_ids"))
            timeline_task_end_date = schedule_timeline_for_sub_batch(
                sub_batch=sub_batch, user=request.user
            )
            user_details = dict(
                User.objects.filter(employee_id__in=data_frame["employee_id"]).values_list(
                    "employee_id", "id"
                )
            )
            for row in range(len(data_frame)):  # Iterating over pandas dataframe
                InternDetail.objects.create(
                    sub_batch=sub_batch,
                    user_id=user_details[str(data_frame["employee_id"][row])],
                    expected_completion=timeline_task_end_date,
                    college=data_frame["college"][row],
                    created_by=request.user,
                )

            return redirect(reverse("batch.detail", args=[pk]))
    context = {
        "form": sub_batch_form,
        "sub_batch_id": pk,
    }
    return render(request, "sub_batch/create_sub_batch.html", context)


@login_required()
@validate_authorization()
def get_timelines(request):
    """
    This function retrieves an active timeline template for a given
    team and returns it as a JSON response, or returns an error message
    if no active template is found.
    """
    team_id = request.POST.get("team_id")
    timelines = list(Timeline.objects.filter(team_id=team_id).values("id", "name", "is_active"))
    if len(timelines) == 0:
        return JsonResponse({"message": "No timeline template found"}, status=404)
    return JsonResponse(timelines, safe=False)


@login_required()
@validate_authorization()
def update_sub_batch(request, pk):
    """
    Update Sub-batch View
    """
    try:
        sub_batch = SubBatch.objects.get(id=pk)
        old_timeline_id = sub_batch.timeline.id
    except Exception:
        return JsonResponse({"message": "Invalid SubBatch id", "status": "error"})
    if request.method == "POST":
        sub_batch_form = SubBatchForm(request.POST, instance=sub_batch)
        if sub_batch_form.is_valid():
            # validation start date
            sub_batch_form.save(commit=False)
            sub_batch.primary_mentor_id = request.POST.get("primary_mentor_id")
            sub_batch.secondary_mentors.set(request.POST.getlist("secondary_mentor_ids"))
            sub_batch_form.save()
            if int(request.POST.get("timeline")) != old_timeline_id:
                SubBatchTaskTimeline.bulk_delete({"sub_batch_id": pk})
                schedule_timeline_for_sub_batch(sub_batch, request.user)
            else:
                schedule_timeline_for_sub_batch(
                    sub_batch,
                    is_create=False,
                )
            return redirect(reverse("batch.detail", args=[sub_batch.batch.id]))
        context = {"form": sub_batch_form, "sub_batch": sub_batch}
        return render(request, "sub_batch/update_sub_batch.html", context)
    context = {
        "form": SubBatchForm(instance=sub_batch),
        "sub_batch": sub_batch,
    }
    return render(request, "sub_batch/update_sub_batch.html", context)


@login_required()
@validate_authorization()
@require_http_methods(
    ["DELETE"]
)  # This decorator ensures that the view function is only accessible
# through the DELETE HTTP method
def delete_sub_batch(request, pk):  # pylint: disable=unused-argument
    """
    Delete Batch
    Soft delete the batch and record the deletion time in deleted_at field
    """
    try:
        sub_batch = get_object_or_404(SubBatch, id=pk)
        InternDetail.bulk_delete({"sub_batch_id": pk})
        SubBatchTaskTimeline.bulk_delete({"sub_batch_id": pk})
        sub_batch.delete()
        return JsonResponse({"message": "Sub-Batch deleted succcessfully"})
    except Exception as exception:
        logging.error(
            "An error has occured while deleting the Sub-Batch \n%s",
            exception,
        )
        return JsonResponse({"message": "Error while deleting Sub-Batch!"}, status=500)


class SubBatchDetail(LoginRequiredMixin, DetailView):
    """
    Sub Batch detail view
    """

    model = SubBatch
    extra_context = {"form": AddInternForm()}
    template_name = "sub_batch/sub_batch_detail.html"


class SubBatchTraineesDataTable(LoginRequiredMixin, CustomDatatable):
    """
    Sub-Batch-Trainees Datatable
    """

    model = InternDetail

    column_defs = [
        {"name": "pk", "visible": False, "searchable": False},
        {
            "name": "user",
            "title": "Trainee's Name",
            "foreign_field": "user__name",
            "visible": True,
            "searchable": True,
        },
        {"name": "college", "title": "College", "visible": True, "searchable": False},
        {
            "name": "completion",
            "title": "Completion (%)",
            "visible": True,
            "searchable": False,
        },
        {
            "name": "no_of_retries",
            "title": "Total Retries",
            "visible": True,
            "searchable": False,
        },
        {
            "name": "average_marks",
            "title": "Average Score (%)",
            "visible": True,
            "searchable": False,
        },
        {
            "name": "performance",
            "title": "Performance",
            "visible": True,
            "searchable": False,
        },
        {
            "name": "expected_completion",
            "title": "Expected Completion",
            "visible": True,
            "searchable": False,
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

    def get_initial_queryset(self, request=None):
        """
        The function returns an initial queryset filtered by the sub_batch id obtained from the
        request's POST data.
        """
        task_count = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch_id=request.POST.get("sub_batch"),
                task_type=TASK_TYPE_ASSESSMENT,
            )
            .values("id")
            .count()
        )
        if task_count == 0:
            task_count = 1
        last_attempt_score = SubBatchTaskTimeline.objects.filter(
            id=OuterRef("sub_batch__task_timelines__id"),
            assessments__user_id=OuterRef("user_id"),
            sub_batch_id=OuterRef("sub_batch_id"),
        ).order_by("-assessments__id")[:1]
        query = (
            self.model.objects.filter(sub_batch__id=request.POST.get("sub_batch"))
            .select_related("user")
            .annotate(
                average_marks=Avg(
                    Subquery(last_attempt_score.values("assessments__score")),
                ),
                no_of_retries=Count(
                    "user__assessments__id",
                    filter=Q(
                        user__assessments__is_retry=True,
                        user__assessments__extension__isnull=True,
                        user__assessments__task_id__deleted_at__isnull=True,
                        user__assessments__sub_batch_id=request.POST.get("sub_batch"),
                    ),
                    distinct=True,
                ),
                completion=Count(
                    "user__assessments__task_id",
                    filter=Q(
                        user__assessments__user_id=F("user_id"),
                        user__assessments__task_id__deleted_at__isnull=True,
                        user__assessments__sub_batch_id=request.POST.get("sub_batch"),
                    ),
                    distinct=True,
                )
                * 100.0
                / task_count,
                performance=Case(
                    When(average_marks__gte=90, then=Value(GOOD)),
                    When(
                        average_marks__lt=90, average_marks__gte=75, then=Value(MEET_EXPECTATION)
                    ),
                    When(average_marks__lt=75, average_marks__gte=65, then=Value(ABOVE_AVERAGE)),
                    When(average_marks__lt=65, average_marks__gte=50, then=Value(AVERAGE)),
                    When(average_marks__lt=50, then=Value(POOR)),
                    default=Value(NOT_YET_STARTED),
                ),
            )
        )
        request.trainee_performance = query
        return query

    def customize_row(self, row, obj):
        """
        The function customize_row customizes a row in a table by adding buttons and formatting the
        expected completion date.
        """
        row["completion"] = round(obj.completion, 2)
        if obj.average_marks is not None:
            row["average_marks"] = round(obj.average_marks, 2)
        buttons = template_utils.show_button(reverse("user_reports", args=[obj.user.id]))
        if self.request.user.is_admin_user:
            buttons += (
                # template_utils.edit_button_new_page(reverse("batch")) +
                # #need to change in next PR
                template_utils.delete_button(
                    "removeIntern('" + reverse("trainee.remove", args=[obj.id]) + "')"
                )
            )
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        row["expected_completion"] = obj.expected_completion.strftime("%d %b %Y")
        if not row["average_marks"]:
            row["average_marks"] = "-"
        if obj.performance == GOOD:
            row[
                "performance"
            ] = f'<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 \
                rounded-xl text-sm">{GOOD}</span>'
        if obj.performance == MEET_EXPECTATION:
            row[
                "performance"
            ] = f'<span class="bg-dark-blue-10 text-dark-blue py-0.5 px-1.5 rounded-xl text-sm">{MEET_EXPECTATION}</span>'  # pylint: disable=C0301
        if obj.performance == ABOVE_AVERAGE:
            row[
                "performance"
            ] = f'<span style="background-color:#fefce8; color: #eab308;" \
            class="py-0.5 px-1.5 rounded-xl text-sm">{ABOVE_AVERAGE}</span>'
        if obj.performance == AVERAGE:
            row[
                "performance"
            ] = f'<span class="bg-orange-100 text-orange-700 py-0.5 px-1.5 \
                rounded-xl text-sm">{AVERAGE}</span>'
        if obj.performance == POOR:
            row[
                "performance"
            ] = f'<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 \
                rounded-xl text-sm">{POOR}</span>'
        if obj.performance == NOT_YET_STARTED:
            row[
                "performance"
            ] = f'<span class="bg-dark-black/10 text-dark-black py-0.5 px-1.5 \
                rounded-xl text-sm">{NOT_YET_STARTED}</span>'
        return row

    def get_response_dict(self, request, paginator, draw_idx, start_pos):
        """
        The function calculates a performance report based on average marks and adds it
        to the response dictionary.
        """
        response = super().get_response_dict(request, paginator, draw_idx, start_pos)
        performance_report = {
            GOOD: 0,
            MEET_EXPECTATION: 0,
            ABOVE_AVERAGE: 0,
            AVERAGE: 0,
            POOR: 0,
            NOT_YET_STARTED: 0,
        }
        for performance in request.trainee_performance:
            if performance.average_marks is not None:
                if float(performance.average_marks) >= 90:
                    performance_report[GOOD] += 1
                elif 90 > float(performance.average_marks) >= 75:
                    performance_report[MEET_EXPECTATION] += 1
                elif 75 > float(performance.average_marks) >= 65:
                    performance_report[ABOVE_AVERAGE] += 1
                elif 65 > float(performance.average_marks) >= 50:
                    performance_report[AVERAGE] += 1
                elif float(performance.average_marks) < 50:
                    performance_report[POOR] += 1
            else:
                performance_report[NOT_YET_STARTED] += 1
        response["extra_data"] = {
            "performance_report": performance_report,
            "no_of_trainees": len(request.trainee_performance),
        }
        return response


@login_required()
@validate_authorization()
# pylint: disable-next=R1710
def add_trainee(request):
    """
    Add trainee to sub batch
    """
    response_data = {}  # Initialize an empty dictionary
    if request.method == "POST":
        form = AddInternForm(request.POST)
        if form.is_valid():  # Check if form is valid or not
            try:
                sub_batch = SubBatch.objects.get(id=request.POST.get("sub_batch_id"))
                timeline_data = SubBatchTaskTimeline.objects.filter(sub_batch=sub_batch).last()
                trainee = form.save(commit=False)
                trainee.user_id = request.POST.get("user_id")
                trainee.sub_batch = sub_batch
                trainee.expected_completion = timeline_data.end_date
                trainee.created_by = request.user
                trainee.save()
                response_data["status"] = "success"
            except Exception:
                response_data = {
                    "message": "Invalid SubBatch id",
                    "status": "error",
                }
            return JsonResponse(response_data)
        field_errors = form.errors.as_json()
        non_field_errors = form.non_field_errors().as_json()
        return JsonResponse(
            {
                "status": "error",
                "field_errors": field_errors,
                "non_field_errors": non_field_errors,
            }
        )


@login_required
@validate_authorization()
@require_http_methods(["DELETE"])
def remove_trainee(request, pk):  # pylint: disable=unused-argument
    """
    The function remove_trainee deletes an intern from the database and returns a JSON response
    indicating the success or failure of the operation.
    """
    try:
        intern_detail = get_object_or_404(InternDetail, id=pk)
        intern_detail.delete()
        return JsonResponse({"message": "Intern has been deleted succssfully"})
    except Exception as exception:
        logging.error(
            "An error has occured while deleting an intern \n%s",
            exception,
        )
        return JsonResponse({"message": "Error while deleting Trainee!"}, status=500)
