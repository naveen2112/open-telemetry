from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import (BooleanField, Case, Count, OuterRef, Q, Subquery,
                              Value, When)
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView
from django.utils.decorators import method_decorator

from core.constants import TASK_TYPE_ASSESSMENT
from core.utils import validate_authorization
from hubble.models import (Assessment, Extension, SubBatch,
                           SubBatchTaskTimeline, User)
from training.forms import InternScoreForm


@method_decorator(validate_authorization(), name="dispatch")
class TraineeJourneyView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "sub_batch/user_journey_page.html"

    def get_context_data(self, **kwargs):
        latest_task_report = Assessment.objects.filter(
            task=OuterRef("id"), user_id=self.object.id
        ).order_by("-id")[:1]
        latest_extended_task_report = Assessment.objects.filter(
            extension=OuterRef("id")
        ).order_by("-id")[:1]
        sub_batch_id = SubBatch.objects.filter(
            intern_details__user=self.object.id
        ).first()

        task_summary = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch=sub_batch_id, task_type=TASK_TYPE_ASSESSMENT
            )
            .annotate(
                retries=Count(
                    "assessments__is_retry", filter=Q(assessments__user=self.object)
                )
                - 1,
                last_entry=Subquery(latest_task_report.values("score")),
                comment=Subquery(latest_task_report.values("comment")),
                is_retry=Subquery(latest_task_report.values("is_retry")),
                inactive_tasks=Case(
                    When(start_date__gt=timezone.now(), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
            )
            .values(
                "id",
                "last_entry",
                "retries",
                "comment",
                "name",
                "is_retry",
                "inactive_tasks",
            )
            .order_by(
            "order"
            )
        )

        extended_task_summary = (
            Extension.objects.filter(sub_batch=sub_batch_id, user=self.object)
            .annotate(
                retries=Count("assessments__is_retry") - 1,
                last_entry=Subquery(latest_extended_task_report.values("score")),
                comment=Subquery(latest_extended_task_report.values("comment")),
                is_retry=Subquery(latest_extended_task_report.values("is_retry")),
            )
            .values("id", "last_entry", "retries", "comment", "is_retry")
        )

        context = super().get_context_data(**kwargs)
        context["assessment_scores"] = task_summary
        context["sub_batch"] = sub_batch_id
        context["form"] = InternScoreForm()
        context["extension_tasks"] = extended_task_summary
        return context


@login_required()
@validate_authorization()
def update_task_score(request, pk):
    """
    Create User report
    """
    if request.method == "POST":
        form = InternScoreForm(request.POST)
        if form.is_valid():  # Check if form is valid or not
            report = form.save(commit=False)
            report.user_id = pk
            report.task_id = request.POST.get("task")
            report.extension_id = request.POST.get("extension")
            report.sub_batch = SubBatch.objects.filter(
                intern_details__user=pk
            ).first()
            report.is_retry = True if request.POST.get("status") == "true" else False
            report.created_by = request.user
            report.save()
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
def add_extension(request, pk):
    Extension.objects.create(
        sub_batch=SubBatch.objects.filter(intern_details__user=pk).first(),
        user_id=pk,
        created_by=request.user,
    )
    return JsonResponse({"status": "success"})


@login_required()
@validate_authorization()
def delete_extension(request, pk):
    """
    Delete Timeline Template
    Soft delete the template and record the deletion time in deleted_at field
    """
    try:
        extension = get_object_or_404(Extension, id=pk)
        extension.delete()
        Assessment.bulk_delete({"extension":extension})
        return JsonResponse(
            {"message": "Week extension deleted succcessfully", "status": "success"}
        )
    except Exception as e:
        return JsonResponse(
            {"message": "Error while deleting week extension!"}, status=500
        )
