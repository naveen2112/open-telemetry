"""
The InternDetail class is a Django model that stores information about trainees
"""
from django.db import models
from django.db.models import Avg, Case, Count, OuterRef, Q, Subquery, When

from core import db
from hubble import models as hubble_models

from .user import User


class PerformanceManager(db.SoftDeleteManager):
    """
    Manager class for soft-deletable models that filters out
    deleted instances.Provides additional methods for querying deleted and
    non-deleted instances.
    """

    def get_performance_summary(self, sub_batch_id, task_count):
        """
        Returns a queryset that filters out deleted instances
        """
        last_attempt_score = (
            hubble_models.SubBatchTaskTimeline.objects.prefetch_related("assessments")
            .filter(
                id=OuterRef("sub_batch__task_timelines__id"),
                assessments__user_id=OuterRef("user_id"),
                sub_batch_id=sub_batch_id,
                assessments__present_status=True,
                assessments__deleted_at__isnull=True,
            )
            .order_by("-assessments__created_at")[:1]
        )

        return (
            super()
            .get_queryset()
            .select_related("user")
            .prefetch_related(
                "sub_batch",
                "user__assessments",
                "user__assessments__task",
                "user__assessments__extension",
            )
            .filter(
                sub_batch=sub_batch_id,
            )
            .annotate(
                no_of_retries=Count(
                    "user__assessments",
                    filter=Q(
                        user__assessments__sub_batch=sub_batch_id,
                        user__assessments__is_retry=True,
                        user__assessments__deleted_at__isnull=True,
                        user__assessments__present_status=True,
                        user__assessments__extension__isnull=True,
                        user__assessments__task__deleted_at__isnull=True,
                    ),
                    distinct=True,
                ),
                completion=Count(
                    "user__assessments__task__id",
                    filter=Q(
                        user__assessments__task__deleted_at__isnull=True,
                        user__assessments__sub_batch_id=sub_batch_id,
                        user__assessments__deleted_at__isnull=True,
                        user__assessments__present_status=True,
                    ),
                    distinct=True,
                )
                * 100.0
                / task_count,
                average_marks=Case(
                    When(
                        completion__gt=0,
                        then=Avg(
                            Subquery(last_attempt_score.values("assessments__score")),
                        ),
                    ),
                    default=None,
                ),
            )
        )


class InternDetail(db.SoftDeleteWithBaseModel):
    """
    Store the trainee detail and also the training completion date
    """

    sub_batch = models.ForeignKey(
        "SubBatch",
        on_delete=models.CASCADE,
        related_name="intern_details",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="intern_details")
    college = models.CharField(max_length=250)
    expected_completion = models.DateField(null=True)
    actual_completion = models.DateField(null=True)
    comment = models.TextField(null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_intern_details",
    )

    objects = PerformanceManager()

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        db_table = "intern_details"

    def __str__(self):
        return self.user.name
