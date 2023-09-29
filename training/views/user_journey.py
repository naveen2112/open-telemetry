"""
Django view and related functions for managing trainee journey and task 
scores in a training application
"""
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    BooleanField,
    Case,
    Count,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.generic import DetailView

from core.constants import TASK_TYPE_ASSESSMENT
from hubble.models import (
    Assessment,
    Extension,
    InternDetail,
    SubBatch,
    SubBatchTaskTimeline,
    User,
)
from training.forms import InternScoreForm


class TraineeJourneyView(LoginRequiredMixin, DetailView):
    """
    TraineeJourneyView class is a Django view that displays a user's journey page, including their
    assessment scores and extension tasks
    """

    model = User
    template_name = "sub_batch/user_journey_page.html"

    def get_context_data(self, **kwargs):  # TODO :: Need to add custom Managers and querysets
        """
        The `get_context_data` function retrieves data related to assessments, task timelines
        and performance statistics for a given user.
        """
        sub_batch_id = SubBatch.objects.filter(intern_details__user=self.object.id).last()

        latest_task_report = Assessment.objects.filter(
            task=OuterRef("id"), user_id=self.object.id, sub_batch=sub_batch_id
        ).order_by("-created_at")[:1]
        latest_extended_task_report = Assessment.objects.filter(extension=OuterRef("id")).order_by(
            "-id"
        )[:1]

        task_count = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch_id=sub_batch_id, task_type=TASK_TYPE_ASSESSMENT
            )
            .values("id")
            .count()
        )
        task_count = max(task_count, 1)

        performance = (
            InternDetail.objects.get_performance_summary(sub_batch_id, task_count)
            .filter(user_id=self.kwargs["pk"])
            .values(
                "average_marks",
                "no_of_retries",
                "completion",
            )
        )

        task_summary = (
            SubBatchTaskTimeline.objects.prefetch_related("assessments")
            .filter(
                sub_batch=sub_batch_id,
                task_type=TASK_TYPE_ASSESSMENT,
            )
            .annotate(
                retries=Count(
                    "assessments__id",
                    filter=Q(
                        assessments__is_retry=True,
                        assessments__present_status=True,
                        assessments__user=self.object,
                        assessments__deleted_at__isnull=True,
                    ),
                    distinct=True,
                ),
                assessment_id=Subquery(latest_task_report.values("id")),
                last_entry=Subquery(latest_task_report.values("score")),
                comment=Subquery(latest_task_report.values("comment")),
                is_retry=Subquery(latest_task_report.values("is_retry")),
                is_retry_needed=Subquery(latest_task_report.values("is_retry_needed")),
                present_status=Subquery(latest_task_report.values("present_status")),
                inactive_tasks=Case(
                    When(
                        start_date__gt=timezone.now(), then=Value(False)
                    ),  # TODO :: Temporarily changed to False, need to update in future
                    default=Value(False),
                    output_field=BooleanField(),
                ),
            )
            .order_by("order")
        )

        tasks = SubBatchTaskTimeline.objects.prefetch_related("assessments").filter(
            sub_batch_id=sub_batch_id, task_type=TASK_TYPE_ASSESSMENT
        )

        task_details = list(tasks.values())

        for task in range(tasks.count()):
            task_details[task]["assessments"] = list(tasks[task].assessments.all().values())

        for task in task_summary:
            task.assessment_status = task.update_assessment(
                task.order, self.object.id, task_details
            )

        extended_task_summary = (
            Extension.objects.prefetch_related("assessments")
            .filter(sub_batch=sub_batch_id, user=self.object)
            .annotate(
                retries=Count("assessments__is_retry", filter=Q(assessments__is_retry=True)),
                last_entry=Subquery(latest_extended_task_report.values("score")),
                comment=Subquery(latest_extended_task_report.values("comment")),
                present_status=Subquery(latest_extended_task_report.values("present_status")),
                assessment_id=Subquery(latest_extended_task_report.values("id")),
            )
            .order_by("id")
        )

        context = super().get_context_data(**kwargs)
        context["assessment_scores"] = task_summary
        context["sub_batch"] = sub_batch_id
        context["form"] = InternScoreForm()
        context["extension_tasks"] = extended_task_summary
        try:
            context["performance_stats"] = performance[0]
        except IndexError:
            context["performance_stats"] = performance
        return context


@login_required
def show_task_score(request):
    """
    This function helps us to render the scores for a specific task
    """
    extension_id = (
        None if request.GET.get("extension_id") == "" else request.GET.get("extension_id")
    )
    task_id = None if request.GET.get("task_id") == "" else request.GET.get("task_id")
    try:
        task_last_attempt_details = model_to_dict(
            Assessment.objects.filter(
                task_id=task_id,
                extension_id=extension_id,
                sub_batch_id=request.GET.get("sub_batch_id"),
                user_id=request.GET.get("trainee_id"),
            )
            .order_by("-created_at")
            .first()
        )
        return JsonResponse({"task_details": task_last_attempt_details, "status": "success"})
    except Exception:
        return JsonResponse(
            {"message": "This task/ extension doesn't have any history"}, status=404
        )


def create_assessment(request, report, pk):
    """
    This function helps us to create assessments
    """
    report.created_by = request.user
    report.updated_by = request.user
    report.present_status = request.POST.get("present_status") == "True"
    report.task_id = request.POST.get("task")
    report.extension_id = request.POST.get("extension")
    if report.task_id != "":
        if request.POST.get("test_week") == "true":
            report.is_retry_needed = request.POST.get("is_retry_needed") == "true"
            report.is_retry = False
        else:
            report.is_retry_needed = False
            report.is_retry = True
    report.user_id = pk
    report.sub_batch = SubBatch.objects.filter(intern_details__user=pk).last()
    report.save()


@login_required()
# pylint: disable=too-many-nested-blocks
def update_task_score(request, pk):
    """
    Update task score
    """
    response_data = {}  # Initialize an empty dictionary
    if request.method == "POST":
        form = InternScoreForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            if request.POST.get("assessment_id"):
                assessment = Assessment.objects.get(id=request.POST.get("assessment_id"))
                assessment.present_status = request.POST.get("present_status") == "True"
                assessment.score = report.score
                assessment.comment = report.comment
                assessment.updated_by = request.user
                if assessment.task_id is not None:
                    if request.POST.get("test_week") == "true":
                        assessment.is_retry_needed = request.POST.get("is_retry_needed") == "true"
                        assessment.is_retry = False
                        assessment.save()
                    else:
                        if assessment.is_retry:
                            assessment.is_retry_needed = False
                            assessment.is_retry = True
                            assessment.save()
                        else:
                            create_assessment(request, report, pk)
                else:
                    assessment.save()
            else:
                create_assessment(request, report, pk)
            return JsonResponse({"status": "success"})
        field_errors = form.errors.as_json()
        non_field_errors = form.non_field_errors().as_json()
        response_data = {
            "status": "error",
            "field_errors": field_errors,
            "non_field_errors": non_field_errors,
        }
    return JsonResponse(response_data)


@login_required()
def add_extension(request, pk):
    """
    The function add_extension creates a new Extension object with the given
    primary key and request information.
    """
    try:
        extension_name = Extension.objects.filter(
            sub_batch=SubBatch.objects.filter(intern_details__user=pk).last(), user_id=pk
        ).count()
        Extension.objects.create(
            name=f"Extension Week {extension_name+1}",
            sub_batch=SubBatch.objects.filter(intern_details__user=pk).last(),
            user_id=pk,
            created_by=request.user,
        )
        return JsonResponse({"status": "success"})
    except Exception:
        return JsonResponse({"status": "error"})


@login_required()
def delete_extension(request, pk):  # pylint: disable=unused-argument
    """
    Delete Timeline Template
    Soft delete the template and record the deletion time in deleted_at field
    """
    try:
        extension = get_object_or_404(Extension, id=pk)
        extension_names_to_be_changed = Extension.objects.filter(
            sub_batch=extension.sub_batch, id__gt=pk, user_id=extension.user_id
        )
        extension.delete()
        Assessment.bulk_delete({"extension": extension})
        for extension_week in extension_names_to_be_changed:
            extension_week.name = "Extension Week " + str(int(extension_week.name.split()[2]) - 1)
            extension_week.save()
        return JsonResponse(
            {
                "message": "Week extension deleted succcessfully",
                "status": "success",
            }
        )
    except Exception as exception:
        logging.error(
            "An error has occured while deleting an Extension task \n%s",
            exception,
        )
        return JsonResponse(
            {"message": "Error while deleting week extension!"},
            status=500,
        )


@login_required()
def get_mark_history(request):
    """
    Returns a JsonResponse, which renders the score history of an assessment
    """
    extension_id = (
        None if request.POST.get("extension_id") == "" else request.POST.get("extension_id")
    )
    task_id = None if request.POST.get("task_id") == "" else request.POST.get("task_id")
    user_id = request.POST.get("user_id")
    data = Assessment.objects.filter(
        task_id=task_id,
        extension_id=extension_id,
        user_id=user_id,
        sub_batch_id=InternDetail.objects.filter(user_id=user_id)
        .values("sub_batch_id")
        .last()["sub_batch_id"],
    ).order_by("-created_at")
    return JsonResponse(render_to_string("sub_batch/score_table.html", {"data": data}), safe=False)
