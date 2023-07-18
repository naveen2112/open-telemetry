import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (Avg, BooleanField, Case, Count, F, OuterRef, Q,
                              Subquery, Value, When)
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView

from core.constants import TASK_TYPE_ASSESSMENT
from core.utils import validate_authorization
from hubble.models import (Assessment, Extension, InternDetail, SubBatch,
                           SubBatchTaskTimeline, User)
from training.forms import InternScoreForm


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

        task_count = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch_id=sub_batch_id, task_type=TASK_TYPE_ASSESSMENT
            )
            .values("id")
            .count()
        )
        if task_count == 0:
            task_count = 1 

        last_attempt_score = SubBatchTaskTimeline.objects.filter(
            id=OuterRef("user__assessments__task_id"),
            assessments__user_id=OuterRef("user_id"),
        ).order_by("-assessments__id")[:1]

        performance = (
            InternDetail.objects.filter(
                sub_batch=sub_batch_id, user_id=self.kwargs["pk"]
            )
            .annotate(
                average_marks=Case(
                    When(
                        user_id=F("user__assessments__user_id"),
                        then=Coalesce(
                            Avg(
                                Subquery(
                                    last_attempt_score.values("assessments__score")
                                ),
                                distinct=True,
                            ),
                            0.0,
                        ),
                    ),
                    default=None,
                ),
                no_of_retries=Coalesce(
                    Count(
                        "user__assessments__is_retry",
                        filter=Q(Q(user__assessments__is_retry=True) & Q(user__assessments__extension__isnull=True)),
                    ),
                    0,
                ),
                completion=Coalesce(
                    (
                        Count(
                            "user__assessments__task_id",
                            filter=Q(user__assessments__user_id=F("user_id")),
                            distinct=True,
                        )
                        / float(task_count)
                    )
                    * 100,
                    0.0,
                ),
            )
            .values("average_marks", "no_of_retries", "completion")
        )

        task_summary = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch=sub_batch_id, task_type=TASK_TYPE_ASSESSMENT
            )
            .annotate(
                retries=Count(
                    "assessments__is_retry",
                    filter=Q(
                        Q(assessments__user=self.object) & Q(assessments__is_retry=True)
                    ),
                ),
                last_entry=Subquery(latest_task_report.values("score")),
                comment=Subquery(latest_task_report.values("comment")),
                is_retry=Subquery(latest_task_report.values("is_retry")),
                inactive_tasks=Case(
                    When(
                        start_date__gt=timezone.now(), then=Value(False)
                    ),  # TODO :: Temporarily changed to False, need to update in future
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
            .order_by("order")
        )

        extended_task_summary = Extension.objects.filter(
            sub_batch=sub_batch_id, user=self.object
        ).annotate(
            retries=Count(
                "assessments__is_retry", filter=Q(assessments__is_retry=True)
            ),
            last_entry=Subquery(latest_extended_task_report.values("score")),
            comment=Subquery(latest_extended_task_report.values("comment")),
            is_retry=Subquery(latest_extended_task_report.values("is_retry")),
        )

        context = super().get_context_data(**kwargs)
        context["assessment_scores"] = task_summary
        context["sub_batch"] = sub_batch_id
        context["form"] = InternScoreForm()
        context["extension_tasks"] = extended_task_summary
        context["performance_stats"] = performance[0]
        return context


@login_required()
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
            report.sub_batch = SubBatch.objects.filter(intern_details__user=pk).first()
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
def add_extension(request, pk):
    try:
        Extension.objects.create(
            sub_batch=SubBatch.objects.filter(intern_details__user=pk).first(),
            user_id=pk,
            created_by=request.user,
        )
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error"})


@login_required()
def delete_extension(request, pk):
    """
    Delete Timeline Template
    Soft delete the template and record the deletion time in deleted_at field
    """
    try:
        extension = get_object_or_404(Extension, id=pk)
        extension.delete()
        Assessment.bulk_delete({"extension": extension})
        return JsonResponse(
            {
                "message": "Week extension deleted succcessfully",
                "status": "success",
            }
        )
    except Exception as e:
        logging.error(f"An error has occured while deleting an Extension task \n{e}")
        return JsonResponse(
            {"message": "Error while deleting week extension!"},
            status=500,
        )
