"""
Django view for managing batches, including creating, updating, and 
deleting batches, as well as displaying batch details
"""
import logging

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
from core.utils import CustomDatatable, validate_authorization
from hubble.models import Batch, InternDetail, SubBatch
from training.forms import BatchForm


class BatchList(LoginRequiredMixin, FormView):
    """
    Timeline Template
    """

    form_class = BatchForm
    template_name = "batch/batch_list.html"


class BatchDataTable(LoginRequiredMixin, CustomDatatable):
    """
    Batch Datatable class is used for display the batch data with defined column
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
            "title": "No. of Trainees",
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

    def get_initial_queryset(self, request=None):  # pylint: disable=unused-argument
        """
        The function returns an annotated queryset with the total number of
        trainees and the number of sub-batches for each object in the model.
        """
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
        """
        The function customize_row customizes a row by adding buttons for
        viewing, editing, and deleting a batch object, based on the user's permissions.
        """
        buttons = template_utils.show_button(reverse("batch.detail", args=[obj.id]))
        if self.request.user.is_admin_user:
            buttons += template_utils.edit_button(
                reverse("batch.show", args=[obj.id])
            ) + template_utils.delete_button(
                "deleteBatch('" + reverse("batch.delete", args=[obj.id]) + "')"
            )
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return row


@login_required()
@validate_authorization()
def create_batch(request):
    """
    Create Batch
    """
    response_data = {}  # Initialize an empty dictionary
    if request.method == "POST":
        form = BatchForm(request.POST)
        if form.is_valid():  # Check if the valid or not
            batch = form.save(commit=False)
            batch.created_by = request.user
            batch.save()
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
def batch_data(request, pk):  # pylint: disable=unused-argument
    """
    The function batch_data retrieves batch data from the database and
    returns it as a JSON response.
    """
    try:
        data = {
            "batch": model_to_dict(get_object_or_404(Batch, id=pk))
        }  # Covert django queryset object to dict,which can be easily
        # serialized and sent as a JSON response
        return JsonResponse(data, safe=False)
    except Exception as exception:
        logging.error(
            "An error has occurred while fetching the batch data \n%s",
            exception,
        )

        return JsonResponse({"message": "Error while getting the data!"}, status=500)


@login_required()
@validate_authorization()
def update_batch(request, pk):
    """
    The function update_batch updates a batch object with the data provided
    in the request and returns a JSON response indicating the success or
    failure of the update operation.
    """
    batch = get_object_or_404(Batch, id=pk)
    form = BatchForm(request.POST, instance=batch)
    if form.is_valid():  # Check if the valid or not
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


@login_required()
@validate_authorization()
@require_http_methods(
    ["DELETE"]
)  # This decorator ensures that the view function is only accessible through the
# DELETE HTTP method
def delete_batch(request, pk):  # pylint: disable=unused-argument
    """
    Delete Batch
    Soft delete the batch and record the deletion time in deleted_at field
    """
    try:
        batch = get_object_or_404(Batch, id=pk)
        intern_details = list(batch.sub_batches.all().values_list("id", flat=True))
        SubBatch.bulk_delete({"batch_id": pk})
        InternDetail.bulk_delete({"sub_batch_id__in": intern_details})
        batch.delete()
        return JsonResponse({"message": "Batch deleted succcessfully"})
    except Exception as exception:
        logging.error(
            "An error has occurred while deleting the batch data \n%s",
            exception,
        )
        return JsonResponse({"message": "Error while deleting Batch!"}, status=500)


class BatchDetails(LoginRequiredMixin, DetailView):
    """
    BatchDetails class is a Django view that displays the details of a Batch model object
    """

    model = Batch
    template_name = "sub_batch/sub_batch.html"
