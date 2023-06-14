import datetime

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView

from core import template_utils
from core.utils import CustomDatatable, create_and_update_sub_batch, update_expected_end_date_of_intern_details
from hubble.models import (Batch, InternDetail, SubBatch,
                           SubBatchTaskTimeline, Timeline, TimelineTask, User)
from training.forms import AddInternForm, SubBatchForm


class SubBatchDataTable(LoginRequiredMixin, CustomDatatable):
    """
    Sub-Batch Datatable
    """

    model = SubBatch

    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": False},
        {"name": "team", "visible": True, "searchable": False},
        {
            "name": "trainee_count",
            "title": "No. of Trainees",
            "visible": True,
            "searchable": False,
        },
        {"name": "start_date", "visible": True, "searchable": False},
        {
            "name": "timeline",
            "title": "Assigned Timeline Template",
            "visible": True,
            "searchable": False,
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
        return self.model.objects.filter(batch=request.POST.get("batch_id")).annotate(
            trainee_count=Count(
                "intern_details",
                filter=Q(intern_details__deleted_at__isnull=True),
            )
        )

    def customize_row(self, row, obj):
        buttons = (
            template_utils.show_button(reverse("sub-batch.detail", args=[obj.id]))
            + template_utils.edit_button_new_page(reverse("sub-batch.edit", args=[obj.id]))
            + template_utils.delete_button("deleteSubBatch('" + reverse("sub-batch.delete", args=[obj.id]) + "')")
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        row["start_date"] = obj.start_date.strftime("%d %b %Y")
        return


@login_required()
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
            df = pd.read_excel(excel_file)
            if (df.columns[0] == "employee_id") and (df.columns[1] == "college"):
                if User.objects.filter(employee_id__in=df["employee_id"]).count()==len(df["employee_id"]):
                    if InternDetail.objects.filter(
                        user__employee_id__in=df["employee_id"]
                    ).exists():
                        sub_batch_form.add_error(
                            None, "Some of the Users are already added in another sub-batch"
                        )  # Adding the non-field-error if the user aalready exists
                else:
                    sub_batch_form.add_error(None, "Some of the employee ids are not present in the database, please check again")
            else:
                sub_batch_form.add_error(None, "Invalid keys are present in the file, please check the sample file")
        else:
            sub_batch_form.add_error(
                None, "Please upload a file"
            )  # Adding the non-field-error if the file was not uploaded while submission
        if sub_batch_form.is_valid():  # Check if both the forms are valid or not
            sub_batch = sub_batch_form.save(commit=False)
            if TimelineTask.objects.filter(timeline=sub_batch.timeline.id):
                sub_batch.batch = Batch.objects.get(id=pk)
                sub_batch.created_by = request.user
                sub_batch.primary_mentor_id = request.POST.get("primary_mentor_id")
                sub_batch.secondary_mentor_id = request.POST.get("secondary_mentor_id")
                sub_batch.save()
                timeline_task_end_date = create_and_update_sub_batch(
                    sub_batch=sub_batch, user=request.user
                )
                user_details = dict(
                    User.objects.filter(employee_id__in=df["employee_id"]).values_list(
                        "employee_id", "id"
                    )
                )
                for row in range(len(df)):  # Iterating over pandas dataframe
                    InternDetail.objects.create(
                        sub_batch=sub_batch,
                        user_id=user_details[str(df["employee_id"][row])],
                        expected_completion=timeline_task_end_date,
                        college=df["college"][row],
                        created_by=request.user,
                    )

                return redirect(reverse("batch.detail", args=[pk]))
            else:
                sub_batch_form.add_error(
                    None, "The Selected Team's Active Timeline doesn't have any tasks"
                )
    context = {
        "form": sub_batch_form,
        "sub_batch_id": pk,
    }
    return render(request, "sub_batch/create_sub_batch.html", context)


@login_required()
def get_timeline(request):
    """
    This function retrieves an active timeline template for a given team and returns it as a JSON
    response, or returns an error message if no active template is found.
    """
    team_id = request.POST.get("team_id")
    try:
        timeline = Timeline.objects.get(team=team_id, is_active=True)
        return JsonResponse(
            {"timeline": model_to_dict(timeline)}
        )  # Return the response with active template for a team
    except Exception as e:
        return JsonResponse(
            {
                "message": "No active timeline template found",
            },
            status=404,
        )


@login_required()
def update_sub_batch(request, pk):
    """
    Update Sub-batch View
    """
    sub_batch = SubBatch.objects.get(id=pk)
    if request.method == "POST":
        sub_batch_form = SubBatchForm(request.POST, instance=sub_batch)
        if sub_batch_form.is_valid():
            # validation start date
            active_form = sub_batch_form.save(commit=False)
            if TimelineTask.objects.filter(timeline=active_form.timeline.id):
                sub_batch.primary_mentor_id = request.POST.get("primary_mentor_id")
                sub_batch.secondary_mentor_id = request.POST.get("secondary_mentor_id")
                active_form = sub_batch_form.save()
                if request.POST.get("timeline") != sub_batch.timeline.id:
                    create_and_update_sub_batch(
                        sub_batch, request.user
                    )  # TODO need to delete old one before new one
                else:
                    timeline_task_end_date = create_and_update_sub_batch(
                        sub_batch,
                        is_create=False,
                    )
                update_expected_end_date_of_intern_details(sub_batch.id)
                return redirect(reverse("batch.detail", args=[sub_batch.batch.id]))
            else:
                sub_batch_form.add_error(
                    None, "The Selected Team's Active Timeline doesn't have any tasks"
                )
        context = {"form": sub_batch_form, "sub_batch": sub_batch}
        return render(request, "sub_batch/update_sub_batch.html", context)
    sub_batch = SubBatch.objects.get(id=pk)
    context = {
        "form": SubBatchForm(instance=sub_batch),
        "sub_batch": sub_batch,
    }
    return render(request, "sub_batch/update_sub_batch.html", context)


@login_required()
@require_http_methods(
    ["DELETE"]
)  # This decorator ensures that the view function is only accessible through the DELETE HTTP method
def delete_sub_batch(request, pk):
    """
    Delete Batch
    Soft delete the batch and record the deletion time in deleted_at field
    """
    try:
        sub_batch = get_object_or_404(SubBatch, id=pk)
        InternDetail.bulk_delete({"sub_batch_id":pk})
        SubBatchTaskTimeline.bulk_delete({"sub_batch_id":pk})
        sub_batch.delete()
        return JsonResponse({"message": "Sub-Batch deleted succcessfully"})
    except Exception as e:
        return JsonResponse({"message": "Error while deleting Sub-Batch!"}, status=500)


class SubBatchDetail(LoginRequiredMixin, DetailView):
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
        {"name": "user", "title": "User", "visible": True, "searchable": False},
        {"name": "college", "title": "College", "visible": True, "searchable": False},
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
        return self.model.objects.filter(sub_batch__id=request.POST.get("sub_batch"))

    def customize_row(self, row, obj):
        buttons = (
            template_utils.show_button(reverse("user_reports", args=[obj.user.id]))
            +
            # template_utils.edit_button_new_page(reverse("batch")) + #need to change in next PR
            template_utils.delete_button(
                "removeIntern('" + reverse("trainee.remove", args=[obj.id]) + "')"
            )
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        row["expected_completion"] = obj.expected_completion.strftime("%d %b %Y")
        return


@login_required()
def add_trainee(request):
    """
    Add tranie to sub batch
    """
    if request.method == "POST":
        modify_data = request.POST.copy()
        modify_data["user"] = modify_data["user_id"]
        form = AddInternForm(modify_data)
        if request.POST.get("user_id"):
            if InternDetail.objects.filter(user=request.POST.get("user_id")).exists():
                form.add_error(
                    "user", "Trainee already added in the another sub-batch"
                )  # Adding form error if the trainees is already added in another
        if form.is_valid():  # Check if form is valid or not
            sub_batch = SubBatch.objects.get(id=request.POST.get("sub_batch_id"))
            timeline_data = SubBatchTaskTimeline.objects.filter(
                sub_batch=sub_batch
            ).last()
            trainee = form.save(commit=False)
            trainee.sub_batch = sub_batch
            trainee.expected_completion = timeline_data.end_date
            trainee.created_by = request.user
            trainee.save()
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


@login_required
@require_http_methods(["DELETE"])
def remove_trainee(request, pk):
    try:
        intern_detail = get_object_or_404(InternDetail, id=pk)
        intern_detail.delete()
        return JsonResponse({"message": "Intern has been deleted succssfully"})
    except Exception as e:
        return JsonResponse(
            {"message": "Error while deleting Timeline Template!"}, status=500
        )
