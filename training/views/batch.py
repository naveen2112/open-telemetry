from django.forms.models import model_to_dict
from django.http import JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from core import template_utils
from core.utils import CustomDatatable
from hubble.models.batch import Batch
from hubble.models.user import User
from training.forms import BatchForm
from django.db.models import F, Count
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView, FormView

class BatchList(FormView):
    """
    Timeline Template
    """
    form_class = BatchForm
    template_name = "batch/batch_list.html"

class BatchDataTable(CustomDatatable):
    """
    Batch Datatable
    """
    model = Batch
    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": False},
        {"name": "action","title": "Action","visible": True,"searchable": False,"orderable": False,"className": "text-center"},
    ]

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


def create_batch(request):
    """
    Create Batch
    """
    if request.method == "POST":
        form = BatchForm(request.POST)
        user = User.objects.get(id=58)
        if form.is_valid():  # Check if the valid or not
            batch = form.save(commit=False)
            batch.created_by = user
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


def update_batch(request):
    """
    Update Batch
    """
    id = request.POST.get("id")
    batch = Batch.objects.get(id=id)
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
        batch.delete()
        return JsonResponse({"message": "Batch deleted succcessfully"})
    except Exception as e:
        return JsonResponse({"message": "Error while deleting Batch!"}, status=500)


def batch_details(request, pk):
    batch = Batch.objects.get(id=pk)
    context = {
        "batch": batch,
        "batch_id": pk,
    }
    return render(request, "batch/sub_batch.html", context)