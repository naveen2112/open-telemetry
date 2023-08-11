import json
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, FormView

from core import template_utils
from core.utils import CustomDatatable, validate_authorization, schedule_timeline_for_sub_batch
from hubble.models import Batch, TraineeHoliday, SubBatch
from training.forms import TraineeHolidayForm


class TraineeHolidayList(LoginRequiredMixin, FormView, DetailView):
    """
    Timeline Template
    """

    form_class = TraineeHolidayForm
    model = Batch
    template_name = "trainee_holiday/trainee_holiday.html"


class TraineeHolidayDataTable(LoginRequiredMixin, CustomDatatable):
    """
    Batch Datatable
    """

    model = TraineeHoliday

    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {
            "name": "date_of_holiday",
            "title": "Date",
        },
        {
            "name": "days",
            "title": "Days",
            "searchable": False,
            "orderable": False,
        },
        {
            "name": "reason",
            "searchable": True,
        },
        {
            "name": "national_holiday",
        },
        {
            "name": "allow_check_in",
        },
        {
            "name": "action",
            "searchable": False,
            "orderable": False,
            "className": "text-center",
        },
    ]

    def get_initial_queryset(self, request=None):
        return self.model.objects.filter(batch=request.POST.get("batch"))
    
    def customize_row(self, row, obj):
        if self.request.user.is_admin_user:
            buttons = template_utils.holiday_edit_button(
                reverse("holiday.show", args=[obj.id])
            ) + template_utils.delete_button(
                "deleteHoliday('"
                + reverse("holiday.delete", args=[obj.id])
                + "')"
            )
            row[
                "action"
            ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        row["date_of_holiday"] = obj.date_of_holiday.strftime("%d %b %Y")
        row["days"] = obj.date_of_holiday.strftime("%A")
        return


@login_required
@validate_authorization()
@require_http_methods(["POST"])
def create_trainee_holiday(request, pk):
    """
    Create Trainee Holiday
    """
    form = TraineeHolidayForm(request.POST)
    if form.is_valid():
        print(form.cleaned_data)
        holiday = form.save(commit=False)
        holiday.batch_id = pk
        holiday.updated_by_id = request.user.id
        try:
            holiday.save()
            sub_batches = SubBatch.objects.filter(batch_id=pk)
            for sub_batch in sub_batches:
                schedule_timeline_for_sub_batch(sub_batch, is_create=False)
            return JsonResponse({"status": "success"})
        except IntegrityError:
            form.add_error("date_of_holiday", "Holiday already exists")
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
def trainee_holiday_data(request, pk):
    """
    Trainee Holiday Data
    """
    try:
        data = {
            "holiday": model_to_dict(get_object_or_404(TraineeHoliday, id=pk))
        }  # Covert django queryset object to dict,which can be easily serialized and sent as a JSON response
        return JsonResponse(data, safe=False)
    except Exception as e:
        logging.error(
            f"An error has occured while fetching the batch data \n{e}"
        )
        return JsonResponse(
            {"message": "Error while getting the data!"}, status=500
        )
    

@login_required
@validate_authorization()
@require_http_methods(["POST"])
def update_trainee_holiday(request, pk):
    """
    Update Trainee Holiday
    """
    trainee_holiday = get_object_or_404(TraineeHoliday, id=pk)
    form = TraineeHolidayForm(request.POST, instance=trainee_holiday)
    if form.is_valid():
        holiday = form.save(commit=False)
        holiday.updated_by_id = request.user.id
        holiday.save()
        sub_batches = SubBatch.objects.filter(batch_id=trainee_holiday.batch_id)
        for sub_batch in sub_batches:
            schedule_timeline_for_sub_batch(sub_batch, is_create=False)
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


@login_required
@validate_authorization()
@require_http_methods(["DELETE"])
def delete_trainee_holiday(request, pk):
    """
    Delete Trainee Holiday
    """
    try:
        trainee_holiday = get_object_or_404(TraineeHoliday, id=pk)
        trainee_holiday.delete()
        sub_batches = SubBatch.objects.filter(batch_id=trainee_holiday.batch_id)
        for sub_batch in sub_batches:
            schedule_timeline_for_sub_batch(sub_batch, is_create=False)
        return JsonResponse({"message": "Holiday deleted succcessfully"})
    except Exception as e:
        logging.error(
            f"An error has occured while deleting the trainee holiday \n{e}"
        )
        return JsonResponse(
            {"message": "Error while deleting the trainee holiday!"}, status=500
        )