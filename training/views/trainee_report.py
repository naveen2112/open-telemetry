from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from hubble.models import (
    SubBatchTaskTimeline,
    User,
    SubBatch,
    Assessment,
    WeekExtension,
)
from training.forms import AddReportForm
from django.http import JsonResponse
from django.db.models import Count, Subquery, OuterRef
from django.db.models import BooleanField, Case, When, Value, Q
from django.utils import timezone
from core.constants import TASK_TYPE_ASSESSMENT

class UserProfile(LoginRequiredMixin, DetailView):
    model = User
    template_name = "sub_batch/user_report.html"

    def get_context_data(self, **kwargs):
        
        latest_task_report = Assessment.objects.filter(task=OuterRef("id"),user_id=self.object.id).order_by("-id")[:1]
        latest_extended_task_report = Assessment.objects.filter(week_extension=OuterRef("id")).order_by("-id")[:1]
        subBatchId = SubBatch.objects.filter(intern_sub_batch_details__user = self.object.id).first()

        task_summary = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch=subBatchId, task_type=TASK_TYPE_ASSESSMENT
            )
            .annotate(
                retries=Count("assessments__is_retry", filter=Q(assessments__user = self.object.id)) - 1,
                last_entry=Subquery(latest_task_report.values("score")),
                comment=Subquery(latest_task_report.values("comment")),
                is_retry=Subquery(latest_task_report.values("is_retry")),
                inactive_tasks = Case(
                    When(start_date__gt=timezone.now(), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                    ),
                )
                .values("id", "last_entry", "retries", "comment", "name", "is_retry", "inactive_tasks")
            )
        
        extended_task_summary = (
            WeekExtension.objects.filter(sub_batch=subBatchId, user=self.object.id).annotate(
                retries=Count("assessment__is_retry") - 1,
                last_entry=Subquery(latest_extended_task_report.values("score")),
                comment=Subquery(latest_extended_task_report.values("comment")),
                is_retry=Subquery(latest_extended_task_report.values("is_retry")),
            )
            .values("id", "last_entry", "retries", "comment", "is_retry")
        )
        
        context = super().get_context_data(**kwargs)
        context["assessment_scores"] = task_summary
        context["sub_batch"] = subBatchId
        context["form"] = AddReportForm()
        context["extension_tasks"] = extended_task_summary
        return context


def user_journey_page(request, pk):
    """
    Create User report
    """
    if request.method == "POST":
        form = AddReportForm(request.POST)
        if form.is_valid():  # Check if form is valid or not
            report = form.save(commit=False)
            report.user_id = pk 
            report.task_id = request.POST.get("task")
            report.week_extension_id = request.POST.get("extension")
            report.sub_batch = SubBatch.objects.filter(intern_sub_batch_details__user = pk).first()
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


def add_extension(request, pk):
    extension = WeekExtension.objects.create(
            sub_batch=SubBatch.objects.filter(intern_sub_batch_details__user = pk).first(),
            user=User.objects.get(id=pk),
            created_by=request.user,
        )
    return JsonResponse({"status": "success"})


def delete_extension(request, pk):
    """
    Delete Timeline Template
    Soft delete the template and record the deletion time in deleted_at field
    """
    try:
        extension = get_object_or_404(WeekExtension, id=pk)
        extension.delete()
        return JsonResponse(
            {"message": "Week extension deleted succcessfully", "status": "success"}
        )
    except Exception as e:
        return JsonResponse(
            {"message": "Error while deleting week extension!"}, status=500
        )
