import datetime
from django.forms import model_to_dict
from django.http import JsonResponse, QueryDict
import pandas as pd
import pytz
from core.utils import CustomDatatable
from hubble.models.batch import Batch
from hubble.models.holiday import Holiday
from hubble.models.intern_detail import InternDetail
from hubble.models.sub_batch import SubBatch
from core import template_utils
from django.db.models import Count, F
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from hubble.models.task_timeline import Task_Timeline
from hubble.models.timeline import Timeline
from hubble.models.timeline_task import TimelineTask
from hubble.models.user import User
from training.forms import AddInternForm, InternDetailForm, SubBatchForm
from django.views.decorators.http import require_http_methods


class SubBatchDataTable(CustomDatatable):
    """
    Sub-Batch Datatable
    """

    model = SubBatch
    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": False},
        {"name": "team", "visible": True, "searchable": False},
        {"name": "start_date", "visible": True, "searchable": False},
        {
            "name": "traines",
            "title": "No of Trainies",
            "visible": True,
            "searchable": False,
        },
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
        return SubBatch.objects.filter(batch=request.POST.get("batch_id")).annotate(
            traines=Count("intern")
        )


    def customize_row(self, row, obj):
        buttons = (
            template_utils.show_btn(reverse("sub-batch.detail", args=[obj.id]))
            + template_utils.edit_btn(
                f"/batch/{self.request.POST.get('batch_id')}/sub-batch/{obj.id}",
            )
            + template_utils.delete_btn("deleteSubBatch(" + str(obj.id) + ")")
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        row["start_date"] = obj.start_date.strftime("%d %b %Y")
        return


def create_sub_batch(request, pk):
    usr = User.objects.get(id=58)
    sub_batch_form = SubBatchForm()
    intern_detail = InternDetailForm()

    if request.method == "POST":
        sub_batch_form = SubBatchForm(request.POST)
        intern_detail = InternDetailForm(request.POST)

        # Checking the trainie is already added in the other batch or not
        if "users_list_file" in request.FILES:
            excel_file = request.FILES["users_list_file"]
            df = pd.read_excel(excel_file, skiprows=1)
            for index, row in df.iterrows():
                data = list(row)
                user = User.objects.get(id=data[0])
                if InternDetail.objects.filter(id=user.id).exists():
                    intern_detail.add_error(
                        None, f"{user.name} is already added in the another sub-batch."
                    )  # Adding the non-form-field error if the trainie is already is added in another branch
        else:
            intern_detail.add_error(
                None, "Please upload the file"
            )  # Adding the non-field-error if the file was not uploaded while submission

        if (
            sub_batch_form.is_valid() or intern_detail.is_valid()
        ):  # Check if both the forms are valid or not
            primary_mentor = request.POST.get("primary_mentor")
            secondary_mentor = request.POST.get("secondary_mentor")
            sub_batch = sub_batch_form.save(commit=False)
            sub_batch.batch = Batch.objects.get(id=pk)
            sub_batch.created_by = usr
            sub_batch.save()

            start_date = datetime.datetime.strptime(
                str(sub_batch.start_date), "%Y-%m-%d"
            )
            start_time = datetime.time(hour=9, minute=0)  # Day start time
            end_time = datetime.time(hour=18, minute=0)  # Day end time
            break_time = datetime.time(hour=13, minute=0)  # Day break time
            break_end_time = datetime.time(hour=14, minute=0)  # Day break end time
            order = 0
            for task in TimelineTask.objects.filter(timeline=sub_batch.timeline.id):
                order += 1
                task_timeline = Task_Timeline.objects.create(
                    name=task.name,
                    days=task.days,
                    sub_batch=sub_batch,
                    present_type=task.present_type,
                    task_type=task.task_type,
                    created_by=usr,
                    order=order,
                )

                duration = datetime.timedelta(
                    hours=task.days * 8
                )  # Working hours for a day

                while duration != datetime.timedelta(0):
                    temp_duration = datetime.timedelta(hours=4)
                    end_datetime = (
                        datetime.datetime.combine(start_date, start_time)
                        + temp_duration
                    )
                    start_datetime = datetime.datetime.combine(start_date, start_time)

                    # While the end date falls on a Sunday or holiday then it will increament the date 1
                    while (
                        end_datetime.date().weekday() == 6
                    ) or Holiday.objects.filter(
                        date_of_holiday=end_datetime.date()
                    ).exists():
                        end_datetime += datetime.timedelta(days=1)

                    total_start_hours = (duration.days * 24) + (
                        duration.seconds / 3600
                    )  # Calculating the hours required to complete the task

                    # Check if total hours and hours required are the same
                    if total_start_hours == task.days * 8:
                        # While the end date falls on a Sunday or holiday then it will increament the date 1
                        while (
                            start_datetime.date().weekday() == 6
                        ) or Holiday.objects.filter(
                            date_of_holiday=start_datetime.date()
                        ).exists():
                            start_datetime += datetime.timedelta(days=1)
                        task_timeline.start_date = start_datetime.date()
                        task_timeline.save()

                    duration = duration - temp_duration
                    total_hours = (duration.days * 24) + (
                        duration.seconds / 3600
                    )  # Calculating the remaining hours

                    if total_hours == 0:
                        task_timeline.end_date = end_datetime.date()
                        task_timeline.save()

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

            sub_batch_intern = SubBatch.objects.get(id=sub_batch.id)
            for index, row in df.iterrows():  # Iterating over pandas dataframe
                data = list(row)
                user = User.objects.get(id=data[0])
                trainie_detail = InternDetail.objects.create(
                    user=user,
                    primary_mentor=User.objects.get(id=primary_mentor),
                    secondary_mentor=User.objects.get(id=secondary_mentor),
                    expected_completion=end_datetime.date(),
                    college=data[1],
                    created_by=usr,
                )
                sub_batch_intern.intern.add(
                    trainie_detail.id
                )  # Adding the trainies to sub-batch

            return redirect(f"/batch/{pk}/details")
    context = {
        "form": sub_batch_form,
        "sub_batch_id": pk,
        "intern_detail": intern_detail,
    }
    return render(request, "batch/create_sub_batch.html", context)


def get_team(request):
    """
    This function retrieves an active timeline template for a given team and returns it as a JSON
    response, or returns an error message if no active template is found.
    """
    team = request.POST.get("team")
    try:
        timeline = Timeline.objects.get(team=team, is_active=True)
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


def update_sub_batch(request, batch, pk):
    usr = User.objects.get(id=58)
    sub_batch_1 = SubBatch.objects.get(id=pk)
    batch_start_date = sub_batch_1.start_date
    if request.method == "POST":
        sub_batch_form = SubBatchForm(request.POST, instance=sub_batch_1)
        intern_detail = InternDetailForm(request.POST)
        if sub_batch_form.is_valid() or intern_detail.is_valid():
            primary_mentor = request.POST.get("primary_mentor")
            secondary_mentor = request.POST.get("secondary_mentor")
            sub_batch = sub_batch_form.save(commit=False)
            sub_batch.save()

            start_date = datetime.datetime.strptime(
                str(request.POST.get("start_date")), "%Y-%m-%d"
            )
            start_time = datetime.time(hour=9, minute=0)  # Day start time
            end_time = datetime.time(hour=18, minute=0)  # Day end time
            break_time = datetime.time(hour=13, minute=0)  # Day break time
            break_end_time = datetime.time(hour=14, minute=0)  # Da break end time
            order = 0

            expected_date = ""
            if sub_batch.timeline.id != sub_batch_1.timeline.id:
                for task in TimelineTask.objects.filter(timeline=sub_batch.timeline.id):
                    order += 1
                    task_timeline = Task_Timeline.objects.create(
                        name=task.name,
                        days=task.days,
                        sub_batch=sub_batch,
                        present_type=task.present_type,
                        task_type=task.task_type,
                        created_by=usr,
                        order=order,
                    )

                    duration = datetime.timedelta(
                        hours=task.days * 8
                    )  # Working hours for a day

                    while duration != datetime.timedelta(0):
                        temp_duration = datetime.timedelta(hours=4)
                        end_datetime = (
                            datetime.datetime.combine(start_date, start_time)
                            + temp_duration
                        )
                        start_datetime = datetime.datetime.combine(
                            start_date, start_time
                        )

                        # While the end date falls on a Sunday or holiday then it will increament the date 1
                        while (
                            end_datetime.date().weekday() == 6
                        ) or Holiday.objects.filter(
                            date_of_holiday=end_datetime.date()
                        ).exists():
                            end_datetime += datetime.timedelta(days=1)

                        total_start_hours = (duration.days * 24) + (
                            duration.seconds / 3600
                        )  # Calculating the hours required to complete the task

                        # Check if total hours and hours required are the same
                        if total_start_hours == task.days * 8:
                            # While the end date falls on a Sunday or holiday then it will increament the date 1
                            while (
                                start_datetime.date().weekday() == 6
                            ) or Holiday.objects.filter(
                                date_of_holiday=start_datetime.date()
                            ).exists():
                                start_datetime += datetime.timedelta(days=1)
                            task_timeline.start_date = start_datetime.date()
                            task_timeline.save()

                        duration = duration - temp_duration
                        total_hours = (duration.days * 24) + (
                            duration.seconds / 3600
                        )  # Calculating the remaining hours
                        # Check if the end_datetime.time() is equal to day end time
                        if total_hours == 0:
                            task_timeline.end_date = end_datetime.date()
                            task_timeline.save()

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
                    expected_date = end_datetime
            elif sub_batch.start_date != sub_batch_1.start_date:
                for task in Task_Timeline.objects.filter(sub_batch=sub_batch.id):
                    duration = datetime.timedelta(
                        hours=task.days * 8
                    )  # Working hours for a day

                    while duration != datetime.timedelta(0):
                        temp_duration = datetime.timedelta(hours=4)
                        end_datetime = (
                            datetime.datetime.combine(start_date, start_time)
                            + temp_duration
                        )
                        start_datetime = datetime.datetime.combine(
                            start_date, start_time
                        )

                        # While the end date falls on a Sunday or holiday then it will increament the date 1
                        while (
                            end_datetime.date().weekday() == 6
                        ) or Holiday.objects.filter(
                            date_of_holiday=end_datetime.date()
                        ).exists():
                            end_datetime += datetime.timedelta(days=1)

                        total_start_hours = (duration.days * 24) + (
                            duration.seconds / 3600
                        )  # Calculating the hours required to complete the task

                        # Check if total hours and hours required are the same
                        if total_start_hours == task.days * 8:
                            # While the end date falls on a Sunday or holiday then it will increament the date 1
                            while (
                                start_datetime.date().weekday() == 6
                            ) or Holiday.objects.filter(
                                date_of_holiday=start_datetime.date()
                            ).exists():
                                start_datetime += datetime.timedelta(days=1)
                            task.start_date = start_datetime.date()
                            task.save()

                        duration = duration - temp_duration
                        total_hours = (duration.days * 24) + (
                            duration.seconds / 3600
                        )  # Calculating the remaining hours
                        if total_hours == 0:
                            task.end_date = end_datetime.date()
                            task.save()

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

                    expected_date = end_datetime
            for user in sub_batch_1.intern.all():
                trainie = InternDetail.objects.get(user=user.user.id)
                trainie.primary_mentor = User.objects.get(id=primary_mentor)
                trainie.secondary_mentor = User.objects.get(id=secondary_mentor)
                if sub_batch.start_date != sub_batch_1.start_date:
                    trainie.expected_completion = expected_date.date()
                trainie.save()
        return redirect(f"/batch/{batch}/details")

    sub_batch = SubBatch.objects.get(id=pk)
    sub_batch_detail = sub_batch.intern.all().first()
    context = {
        "form": SubBatchForm(instance=SubBatch.objects.get(id=pk)),
        "mentor_form": InternDetailForm(),
        "sub_batch": SubBatch.objects.get(id=pk),
        "intern_detail": InternDetailForm(),
        "sub_batch_detail": sub_batch_detail,
        "batch_id": batch,
    }
    return render(request, "batch/update_sub_batch.html", context)


@require_http_methods(
    ["DELETE"]
)  # This decorator ensures that the view function is only accessible through the DELETE HTTP method
def delete_sub_batch(request):
    """
    Delete Batch
    Soft delete the batch and record the deletion time in deleted_at field
    """
    try:
        delete = QueryDict(
            request.body
        )  # Creates a QueryDict object from the request body
        id = delete.get("id")  # Get id from dictionary
        sub_batch = get_object_or_404(SubBatch, id=id)
        sub_batch.delete()
        return JsonResponse({"message": "Sub-Batch deleted succcessfully"})
    except Exception as e:
        return JsonResponse({"message": "Error while deleting Sub-Batch!"}, status=500)


def sub_batch_details(request, pk):
    """
    Sub Batch Detail View
    Display all information about the sub-batch trainies
    """
    sub_batch = SubBatch.objects.get(id=pk)
    context = {"sub_batch": sub_batch, "form": AddInternForm()}
    return render(request, "batch/sub_batch_detail.html", context)


class SubBatchTrainiesDataTable(CustomDatatable):
    """
    Sub-Batch-Trainies Datatable
    """

    model = SubBatch
    column_defs = [
        {"name": "pk", "visible": False, "searchable": False},
        {
            "name": "intern__user__name",
            "title": "User",
            "visible": True,
            "searchable": False,
        },
        {"name": "intern__user_id", "visible": False, "searchable": False},
        {
            "name": "intern__primary_mentor__name",
            "title": "Primary mentor",
            "visible": True,
            "searchable": False,
        },
        {
            "name": "intern__secondary_mentor__name",
            "title": "Secondary mentor",
            "visible": True,
            "searchable": False,
        },
        {
            "name": "intern__college",
            "title": "College",
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


    def customize_row(self, row, obj):
        buttons = template_utils.show_btn(
            reverse("bsub-batch.detail", args=[obj["intern__user_id"]])
        ) + template_utils.edit_btn(
            f"/batch",
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return


    def get_initial_queryset(self, request=None):
        data = (
            SubBatch.objects.filter(id=request.POST.get("sub_batch"))
            .prefetch_related("intern")
            .values(
                "id",
                "intern__user_id",
                "intern__user__name",
                "intern__primary_mentor__name",
                "intern__secondary_mentor__name",
                "intern__college",
            )
            .annotate(action=F("intern__user__name"), pk=F("id"))
        )
        return data


def add_trainies(request):
    """
    Create Timeline Template
    """
    if request.method == "POST":
        user = User.objects.get(id=58)
        form = AddInternForm(request.POST)
        sub_batch_id = request.POST.get("sub_batch")
        if request.POST.get("user"):
            if InternDetail.objects.filter(user=request.POST.get("user")).exists():
                form.add_error(
                    "user", "Trainie already added in the another sub-batch"
                )  # Adding form error if the trainies is already added in another
        if form.is_valid():  # Check if form is valid or not
            sub_batch = SubBatch.objects.get(id=sub_batch_id)
            sub_batch_detail = sub_batch.intern.all().first()
            trainie = form.save(commit=False)
            trainie.primary_mentor = sub_batch_detail.primary_mentor
            trainie.secondary_mentor = sub_batch_detail.secondary_mentor
            trainie.created_by = user
            trainie.save()
            sub_batch.intern.add(trainie.id)
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