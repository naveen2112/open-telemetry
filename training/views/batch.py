import logging

from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, FormView

from core import template_utils
from core.constants import BATCH_DURATION
from core.utils import CustomDatatable, validate_authorization
from hubble.models import Batch, Holiday, InternDetail, SubBatch, TraineeHoliday
from training.forms import BatchForm


class BatchList(LoginRequiredMixin, FormView):
    """
    Timeline Template
    """

    form_class = BatchForm
    template_name = "batch/batch_list.html"


class BatchDataTable(LoginRequiredMixin, CustomDatatable):
    """
    Batch Datatable
    """

    model = Batch

    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": True},
        {
            "name": "number_of_sub_batches",
            "title": "Number of Sub-Batches",
            "searchable": False,
        },
        {
            "name": "total_trainee",
            "title": "No. of Trainee",
            "visible": True,
            "searchable": False,
        },
        {
            "name": "start_date",
            "title": "Start Date",
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
        return self.model.objects.annotate(
            total_trainee=Count(
                "sub_batches__intern_details",
                filter=Q(sub_batches__intern_details__deleted_at__isnull=True),
            ),
            number_of_sub_batches=Coalesce(
                Subquery(
                    self.model.objects.filter(sub_batches__batch_id=OuterRef("id"))
                    .annotate(
                        number_of_sub_batches=Count(
                            "sub_batches__id",
                            filter=Q(sub_batches__deleted_at__isnull=True),
                        )
                    )
                    .values("number_of_sub_batches")
                ),
                0,
            ),
        )

    def customize_row(self, row, obj):
        buttons = template_utils.show_button(reverse("batch.detail", args=[obj.id]))
        if self.request.user.is_admin_user:
            buttons += template_utils.edit_button(
                reverse("batch.show", args=[obj.id])
            ) + template_utils.delete_button(
                "deleteBatch('" + reverse("batch.delete", args=[obj.id]) + "')"
            )
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        row["start_date"] = obj.start_date.strftime("%d %b %Y")
        return


@login_required()
@validate_authorization()
def create_batch(request):
    """
    Create Batch
    """
    if request.method == "POST":
        form = BatchForm(request.POST)
        if form.is_valid():  # Check if the valid or not
            batch = form.save(commit=False)
            batch.created_by = request.user
            batch.save()
            start_date = batch.start_date
            end_date = start_date + relativedelta(months=BATCH_DURATION)
            holidays = Holiday.objects.filter(date_of_holiday__range=(start_date, end_date))
            trainee_holidays = [
                TraineeHoliday(
                    batch_id=batch.id,
                    date_of_holiday=holiday.date_of_holiday,
                    month_year=holiday.month_year,
                    updated_by=request.user,
                    reason=holiday.reason,
                    allow_check_in=holiday.allow_check_in,
                    national_holiday=holiday.national_holiday,
                )
                for holiday in holidays
            ]
            TraineeHoliday.objects.bulk_create(trainee_holidays)
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
@validate_authorization()
def batch_data(request, pk):
    """
    Batch Update Form Data
    """
    try:
        data = {
            "batch": model_to_dict(get_object_or_404(Batch, id=pk))
        }  # Covert django queryset object to dict,which can be easily serialized and sent as a JSON response
        return JsonResponse(data, safe=False)
    except Exception as e:
        logging.error(f"An error has occured while fetching the batch data \n{e}")
        return JsonResponse({"message": "Error while getting the data!"}, status=500)


@login_required()
@validate_authorization()
def update_batch(request, pk):
    """
    Update Batch
    """
    batch = get_object_or_404(Batch, id=pk)
    form = BatchForm(request.POST, instance=batch)
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
@validate_authorization()
@require_http_methods(
    ["DELETE"]
)  # This decorator ensures that the view function is only accessible through the DELETE HTTP method
def delete_batch(request, pk):
    """
    Delete Batch
    Soft delete the batch and record the deletion time in deleted_at field
    """
    try:
        batch = get_object_or_404(Batch, id=pk)
        intern_details = list(batch.sub_batches.all().values_list("id", flat=True))
        TraineeHoliday.bulk_delete({"batch_id": pk})
        SubBatch.bulk_delete({"batch_id": pk})
        InternDetail.bulk_delete({"sub_batch_id__in": intern_details})
        batch.delete()
        return JsonResponse({"message": "Batch deleted succcessfully"})
    except Exception as e:
        logging.error(f"An error has occured while deleting the batch data \n{e}")
        return JsonResponse({"message": "Error while deleting Batch!"}, status=500)


class BatchDetails(LoginRequiredMixin, DetailView):
    model = Batch
    template_name = "sub_batch/sub_batch.html"
