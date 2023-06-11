from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView, FormView

from core import template_utils
from core.utils import CustomDatatable
from hubble.models import Batch
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
        {"name": "name", "visible": True, "searchable": False},
        {
            "name": "total_trainee",
            "title": "No. of Trainee",
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
        return self.model.objects.all().annotate(
            total_trainee=Count(
                "sub_batches__intern_sub_batch_details",
                filter=Q(
                    sub_batches__intern_sub_batch_details__deleted_at__isnull=True
                ),
            )
        )

    def customize_row(self, row, obj):
        buttons = (
            template_utils.show_button(reverse("batch.detail", args=[obj.id]))
            + template_utils.edit_button(reverse("batch.show", args=[obj.id]))
            + template_utils.delete_button("deleteBatch('" + reverse("batch.delete", args=[obj.id]) + "')")
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return


@login_required()
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
        return JsonResponse({"message": "Error while getting the data!"}, status=500)


@login_required()
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
@require_http_methods(["DELETE"])  # This decorator ensures that the view function is only accessible through the DELETE HTTP method
def delete_batch(request, pk):
    """
    Delete Batch
    Soft delete the batch and record the deletion time in deleted_at field
    """
    try:
        batch = get_object_or_404(Batch, id=pk)
        batch.delete()
        return JsonResponse({"message": "Batch deleted succcessfully"})
    except Exception as e:
        return JsonResponse({"message": "Error while deleting Batch!"}, status=500)


class BatchDetails(LoginRequiredMixin, DetailView):
    model = Batch
    template_name = "sub_batch/sub_batch.html"
