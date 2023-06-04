import datetime

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView

from core import template_utils
from core.utils import CustomDatatable
from hubble.models import (Batch, Holiday, InternDetail, SubBatch,
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
        {"name": "trainee_count","title": "No. of Trainees", "visible": True, "searchable": False},
        {"name": "start_date", "visible": True, "searchable": False},
        {"name": "timeline", "title": "Assigned Timeline Template", "visible": True, "searchable": False, "foreign_field": "timeline__name"},
        {"name": "action", "title": "Action", "visible": True, "searchable": False, "orderable": False, "className": "text-center",},
    ]

    def get_initial_queryset(self, request=None):
        return self.model.objects.filter(batch=request.POST.get("batch_id")).annotate(trainee_count=Count("intern_sub_batch_details")) #TODO:what if the intern was deleted?

    def customize_row(self, row, obj):
        buttons = (
            template_utils.show_button(reverse("sub-batch.detail", args=[obj.id]))
            + template_utils.edit_button(reverse("sub-batch.edit", args=[self.request.POST.get("batch_id"), obj.id]))
            + template_utils.delete_button("deleteSubBatch('" + reverse("sub-batch.delete", args=[obj.id]) + "')")
        )
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        row["start_date"] = obj.start_date.strftime("%d %b %Y")
        return


holidays = Holiday.objects.values_list("date_of_holiday")
timeline_task_end_date = None


def create_sub_batch_timeline_task(sub_batch, user):
    start_date = datetime.datetime.strptime(str(sub_batch.start_date), "%Y-%m-%d")
    start_time = datetime.time(hour=9, minute=0)  # Day start time
    end_time = datetime.time(hour=18, minute=0)  # Day end time
    break_time = datetime.time(hour=13, minute=0)  # Day break time
    break_end_time = datetime.time(hour=14, minute=0)  # Day break end time
    order = 0
    for task in TimelineTask.objects.filter(timeline=sub_batch.timeline.id):
        task_start_date = None
        task_end_date = None

        duration = datetime.timedelta(hours=task.days * 8)  # Working hours for a day

        while duration != datetime.timedelta(0):
            temp_duration = datetime.timedelta(hours=4)
            end_datetime = (
                datetime.datetime.combine(start_date, start_time) + temp_duration
            )
            start_datetime = datetime.datetime.combine(start_date, start_time)

            # While the end date falls on a Sunday or holiday then it will increament the date 1
            while (
                end_datetime.date().weekday() == 6
            ) or end_datetime.date() in holidays:
                end_datetime += datetime.timedelta(days=1)

            total_start_hours = (duration.days * 24) + (
                duration.seconds / 3600
            )  # Calculating the hours required to complete the task

            # Check if total hours and hours required are the same
            if total_start_hours == task.days * 8:
                # While the end date falls on a Sunday or holiday then it will increament the date 1
                while (
                    start_datetime.date().weekday() == 6
                ) or end_datetime.date() in holidays:
                    start_datetime += datetime.timedelta(days=1)
                task_start_date = start_datetime.date()

            duration = duration - temp_duration
            total_hours = (duration.days * 24) + (
                duration.seconds / 3600
            )  # Calculating the remaining hours

            if total_hours == 0:
                task_end_date = end_datetime.date()

            # Check if the end_datetime.time() is equal to day end time
            if end_datetime.time() == end_time:
                end_datetime += datetime.timedelta(days=1)

            start_date = end_datetime
            start_time = end_datetime.time()

            # Check the end_datetime.time() is equal to break time
            # Exclide the 1hr breaktime
            if end_datetime.time() == break_time:
                start_time = break_end_time

            if end_datetime.time() == end_time:
                start_time = datetime.time(hour=9, minute=0)

        order += 1
        SubBatchTaskTimeline.objects.create(
            name=task.name,
            days=task.days,
            sub_batch=sub_batch,
            present_type=task.present_type,
            task_type=task.task_type,
            start_date=task_start_date,
            end_date=task_end_date,
            created_by=user,
            order=order,
        )

    global timeline_task_end_date
    timeline_task_end_date = task_end_date


def update_sub_batch_task(sub_batch):
    start_date = datetime.datetime.strptime(str(sub_batch.start_date), "%Y-%m-%d")
    start_time = datetime.time(hour=9, minute=0)  # Day start time
    end_time = datetime.time(hour=18, minute=0)  # Day end time
    break_time = datetime.time(hour=13, minute=0)  # Day break time
    break_end_time = datetime.time(hour=14, minute=0)  # Da break end time

    for task in SubBatchTaskTimeline.objects.filter(sub_batch=sub_batch):
        task_start_date = None
        task_end_date = None
        duration = datetime.timedelta(hours=task.days * 8)  # Working hours for a day

        while duration != datetime.timedelta(0):
            temp_duration = datetime.timedelta(hours=4)
            end_datetime = (
                datetime.datetime.combine(start_date, start_time) + temp_duration
            )
            start_datetime = datetime.datetime.combine(start_date, start_time)

            # While the end date falls on a Sunday or holiday then it will increament the date 1
            while (
                end_datetime.date().weekday() == 6
            ) or end_datetime.date() in holidays:
                end_datetime += datetime.timedelta(days=1)

            total_start_hours = (duration.days * 24) + (
                duration.seconds / 3600
            )  # Calculating the hours required to complete the task

            # Check if total hours and hours required are the same
            if total_start_hours == task.days * 8:
                # While the end date falls on a Sunday or holiday then it will increament the date 1
                while (
                    start_datetime.date().weekday() == 6
                ) or end_datetime.date() in holidays:
                    start_datetime += datetime.timedelta(days=1)
                task_start_date = start_datetime.date()

            duration = duration - temp_duration
            total_hours = (duration.days * 24) + (
                duration.seconds / 3600
            )  # Calculating the remaining hours

            if total_hours == 0:
                task_end_date = end_datetime.date()

            # Check if the end_datetime.time() is equal to day end time
            if end_datetime.time() == end_time:
                end_datetime += datetime.timedelta(days=1)

            start_date = end_datetime
            start_time = end_datetime.time()

            # Check the end_datetime.time() is equal to break time
            # Exclide the 1hr breaktime
            if end_datetime.time() == break_time:
                start_time = break_end_time

            if end_datetime.time() == end_time:
                start_time = datetime.time(hour=9, minute=0)
    global timeline_task_end_date
    timeline_task_end_date = task_end_date


@login_required()
def create_sub_batch(request, pk):
    """
    Create Sub-batch View
    """
    sub_batch_form = SubBatchForm()

    if request.method == "POST":
        sub_batch_form = SubBatchForm(request.POST)
        # Checking the trainie is already added in the other batch or not
        if "users_list_file" in request.FILES:
            excel_file = request.FILES["users_list_file"]
            df = pd.read_excel(excel_file)
            if InternDetail.objects.filter(user__in=df['user_id']).exists():
                sub_batch_form.add_error(None, "Some of the Users are already added in another sub-batch")  # Adding the non-field-error if the user aalready exists
        else:
            sub_batch_form.add_error(None, "Please upload the file")  # Adding the non-field-error if the file was not uploaded while submission

        if sub_batch_form.is_valid():  # Check if both the forms are valid or not
            sub_batch = sub_batch_form.save(commit=False)
            sub_batch.batch = Batch.objects.get(id=pk)
            sub_batch.created_by = request.user
            sub_batch.save()

            create_sub_batch_timeline_task(sub_batch, request.user)
            for row in range(len(df)): # Iterating over pandas dataframe
                InternDetail.objects.create(
                    sub_batch=sub_batch,
                    user=df['user_id'][row],
                    expected_completion=timeline_task_end_date,
                    college=df['college'][row],
                    created_by=request.user,
                )

            return redirect(reverse("batch.detail", args=[pk]))
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
    team_id = request.POST.get("team")
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
def update_sub_batch(request, batch, pk):
    """
    Update Sub-batch View
    """
    sub_batch_data = SubBatch.objects.get(id=pk)
    batch_start_date = sub_batch_data.start_date
    if request.method == "POST":
        sub_batch_form = SubBatchForm(request.POST, instance=sub_batch_data)
        if sub_batch_form.is_valid():
            sub_batch = sub_batch_form.save()

            if sub_batch.timeline.id != sub_batch_data.timeline.id:
                create_sub_batch_timeline_task(sub_batch, request.user)
            else:
                update_sub_batch_task(sub_batch)

            for trainee in InternDetail.objects.filter(sub_batch=sub_batch):
                if sub_batch.start_date != sub_batch_data.start_date:
                    trainee.expected_completion = timeline_task_end_date
                    trainee.save()
            return redirect(reverse("batch.detail", args=[batch]))

    sub_batch = SubBatch.objects.get(id=pk)
    context = {
        "form": SubBatchForm(instance=SubBatch.objects.get(id=pk)),
        "sub_batch": SubBatch.objects.get(id=pk),
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
        sub_batch.delete()
        return JsonResponse({"message": "Sub-Batch deleted succcessfully"})
    except Exception as e:
        return JsonResponse({"message": "Error while deleting Sub-Batch!"}, status=500)


class SubBatchDetail(LoginRequiredMixin, DetailView):
    model = SubBatch
    extra_context = {"form": AddInternForm()}
    template_name = "sub_batch/sub_batch_detail.html"


class SubBatchTrainiesDataTable(LoginRequiredMixin, CustomDatatable):
    """
    Sub-Batch-Trainies Datatable
    """

    model = InternDetail

    column_defs = [
        {"name": "pk", "visible": False, "searchable": False},
        {"name": "user", "title": "User", "visible": True, "searchable": False},
        {"name": "college", "title": "College", "visible": True, "searchable": False},
        {"name": "expected_completion", "title": "Expected Completion", "visible": True, "searchable": False},
        {"name": "action", "title": "Action", "visible": True, "searchable": False, "orderable": False, "className": "text-center",},
    ]

    def get_initial_queryset(self, request=None):
        return self.model.objects.filter(sub_batch__id=request.POST.get("sub_batch"))

    def customize_row(self, row, obj):
        buttons = template_utils.show_button(reverse("sub-batch.detail", args=[obj.user.id])) + template_utils.edit_button(reverse("batch"))
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return


@login_required()
def add_trainee(request):
    """
    Add tranie to sub batch
    """
    if request.method == "POST":
        form = AddInternForm(request.POST)
        if request.POST.get("user_id"):
            if InternDetail.objects.filter(user=request.POST.get("user_id")).exists():
                form.add_error(
                    "user", "Trainie already added in the another sub-batch"
                )  # Adding form error if the trainies is already added in another
        if form.is_valid():  # Check if form is valid or not
            sub_batch = SubBatch.objects.get(id=request.POST.get("sub_batch_id"))
            date = SubBatchTaskTimeline.objects.filter(sub_batch=sub_batch).last()
            trainie = form.save(commit=False)
            trainie.sub_batch = sub_batch
            trainie.expected_completion = date.start_date
            trainie.created_by = request.user
            trainie.save()
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
