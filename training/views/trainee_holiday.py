"""
Django view and related functions for managing trainee holiday, 
including creating, updating, deleting, and displaying details of trainee holiday
"""
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, FormView

from core import template_utils
from core.utils import (
    CustomDatatable,
    schedule_timeline_for_sub_batch,
    validate_authorization,
)
from hubble.models import Batch, SubBatch, TraineeHoliday
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
            "title": "Action",
            "searchable": False,
            "orderable": False,
            "className": "text-center",
        },
    ]

    def get_initial_queryset(self, request=None):
        """
        The function returns an initial queryset of objects from a model, filtering out
        """
        return self.model.objects.filter(batch=request.POST.get("batch"))

    def customize_row(self, row, obj):
        """
        The function customize_row customizes a row by adding buttons based on the user's role.
        """
        buttons = "-"
        if self.request.user.is_admin_user:
            buttons = template_utils.holiday_edit_button(
                reverse("holiday.show", args=[obj.id])
            ) + template_utils.delete_button(
                "deleteHoliday('" + reverse("holiday.delete", args=[obj.id]) + "')"
            )
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        row["date_of_holiday"] = obj.date_of_holiday.strftime("%d %b %Y")
        row["days"] = obj.date_of_holiday.strftime("%A")
        return row


@method_decorator(login_required, name="dispatch")
@method_decorator(validate_authorization(), name="dispatch")
class TraineeHolidayCreateView(View):
    """
    Create Trainee Holiday View
    """

    http_method_names = ["post"]

    @method_decorator(require_http_methods(["POST"]))
    def dispatch(self, request, *args, **kwargs):
        """
        The function dispatches the request to the corresponding handler
        based on the request method.
        """
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        """
        The function creates a new holiday for a batch.
        """
        form = TraineeHolidayForm(request.POST)
        if form.is_valid():
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


@method_decorator(login_required, name="dispatch")
@method_decorator(validate_authorization(), name="dispatch")
class TraineeHolidayDataView(View):
    """
    Trainee Holiday Data View
    """

    def get(self, request, pk):  # pylint: disable=unused-argument
        """
        The function returns the data of a holiday for a batch.
        """
        try:
            data = {
                "holiday": model_to_dict(get_object_or_404(TraineeHoliday, id=pk))
            }  # Covert django queryset object to dict
            return JsonResponse(data, safe=False)
        except Exception as exception:
            logging.error("An error has occured while fetching the batch data \n%e", exception)
            return JsonResponse({"message": "Error while getting the data!"}, status=500)


@method_decorator(login_required, name="dispatch")
@method_decorator(validate_authorization(), name="dispatch")
class TraineeHolidayUpdateView(View):
    """
    Update Trainee Holiday View
    """

    http_method_names = ["post"]

    @method_decorator(require_http_methods(["POST"]))
    def dispatch(self, request, *args, **kwargs):
        """
        The function dispatches the request to the corresponding handler
        based on the request method.
        """
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        """
        The function updates the holiday of a batch.
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


@method_decorator(login_required, name="dispatch")
@method_decorator(validate_authorization(), name="dispatch")
class TraineeHolidayDeleteView(View):
    """
    Delete Trainee Holiday View
    """

    http_method_names = ["delete"]

    @method_decorator(require_http_methods(["DELETE"]))
    def dispatch(self, request, *args, **kwargs):
        """
        The function dispatches the request to the corresponding handler
        based on the request method.
        """
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, pk):  # pylint: disable=unused-argument
        """
        The function deletes the holiday of a batch.
        """
        try:
            trainee_holiday = get_object_or_404(TraineeHoliday, id=pk)
            trainee_holiday.delete()
            sub_batches = SubBatch.objects.filter(batch_id=trainee_holiday.batch_id)
            for sub_batch in sub_batches:
                schedule_timeline_for_sub_batch(sub_batch, is_create=False)
            return JsonResponse({"message": "Holiday deleted succcessfully"})
        except Exception as exception:
            logging.error(
                "An error has occured while deleting the trainee holiday \n%e", exception
            )
            return JsonResponse(
                {"message": "Error while deleting the trainee holiday!"}, status=500
            )
