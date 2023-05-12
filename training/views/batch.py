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


def batch(request):
    context = {"form": BatchForm()}
    return render(request, "batch/batch_list.html", context)


class BatchDataTable(CustomDatatable):
    """
    Batch Datatable
    """

    model = Batch
    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": False},
        # {"name": "count", "visible": True, "searchable": False},
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
        buttons = (
            template_utils.show_btn(reverse("batch.detail", args=[obj.id]))
            + template_utils.edit_btn(
                obj.id,
            )
            + template_utils.delete_btn("deleteBatch(" + str(obj.id) + ")")
        )
        row[
            "action"
        ] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return
    

    # def get_initial_queryset(self, request=None):
    #     data = Batch.objects.annotate(count=Count(F("batch_id__intern")))
    #     return data


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


def batch_update_form(request):
    """
    Batch Update Form Data
    """
    id = request.GET.get("id")
    batch = Batch.objects.get(id=id)
    data = {
        "batch": model_to_dict(batch)
    }  # Covert django queryset object to dict,which can be easily serialized and sent as a JSON response
    return JsonResponse(data, safe=False)


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
def delete_batch(request):
    """
    Delete Batch
    Soft delete the batch and record the deletion time in deleted_at field
    """
    
    delete = QueryDict(
        request.body
    )  # Creates a QueryDict object from the request body
    id = delete.get("id")  # Get id from dictionary
    batch = get_object_or_404(Batch, id=id)
    batch.delete()
    return JsonResponse({"message": "Batch deleted succcessfully"})
    # except Exception as e:
    #     return JsonResponse({"message": "Error while deleting Batch!"}, status=500)


def batch_details(request, pk):
    batch = Batch.objects.get(id=pk)
    context = {
        "batch": batch,
        "batch_id": pk,
    }
    return render(request, "batch/sub_batch.html", context)