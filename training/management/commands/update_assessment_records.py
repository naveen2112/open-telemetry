"""
This module is responsible for the management command for updating the 
User Assessment records as per the new requirements
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from core.constants import TASK_TYPE_ASSESSMENT
from hubble.models import Assessment, SubBatch


class Command(BaseCommand):
    """
    Creates a custom command for updating the previous assessment records
    """

    help = "Updates the assessments recordes in a SubBatch"

    def add_arguments(self, parser):
        """
        This function is responsible for adding arguments to the command
        """
        parser.add_argument("--sub_batch_id", nargs="*", type=int)
        parser.add_argument("--days_to_be_reduced", type=int, default=0)

    # pylint: disable=too-many-arguments
    def create_absent_record(
        self, task, trainee, sub_batch, is_retry_needed=False, is_retry_score=False
    ):
        """
        Create a record with Present Status as False
        """
        assessment = Assessment.objects.create(
            present_status=False,
            task_id=task.id,
            user_id=trainee.user_id,
            sub_batch_id=sub_batch.id,
            score=None,
            comment=None,
            is_retry_needed=is_retry_needed,
            is_retry=is_retry_score,
            created_by=sub_batch.primary_mentor,
            updated_by=sub_batch.primary_mentor,
        )
        Assessment.objects.filter(id=assessment.id).update(
            created_at=task.start_date + timezone.timedelta(1),
            updated_at=task.start_date + timezone.timedelta(1),
        )
        return assessment

    # pylint: disable=too-many-nested-blocks, unused-argument, too-many-locals
    def handle(self, *args, **kwargs):
        """
        Create records based on the given scenario
        """
        for sub_batch_id in kwargs["sub_batch_id"]:
            try:
                sub_batch = SubBatch.objects.prefetch_related(
                    "task_timelines", "intern_details", "assessments"
                ).get(pk=sub_batch_id)
                sub_batch_tasks = sub_batch.task_timelines.filter(
                    task_type=TASK_TYPE_ASSESSMENT,
                    start_date__date__lte=timezone.now().date()
                    - timezone.timedelta(kwargs["days_to_be_reduced"]),
                )
                intern_details = sub_batch.intern_details.all()
                for task in sub_batch_tasks:
                    for intern in intern_details:
                        assessment_queryset = sub_batch.assessments.filter(
                            task_id=task.id, user_id=intern.user_id
                        ).order_by("created_at")
                        if assessment_queryset.count() > 0:
                            for counter, assessment in enumerate(assessment_queryset):
                                if counter == 0:
                                    if assessment.is_retry:
                                        self.create_absent_record(
                                            task,
                                            intern,
                                            sub_batch,
                                            is_retry_needed=True,
                                        )
                                    previous_assessment = assessment
                                else:
                                    if assessment.is_retry:
                                        previous_assessment.is_retry_needed = True
                                        previous_assessment.save()
                                        previous_assessment = assessment
                        else:
                            self.create_absent_record(
                                task, intern, sub_batch, is_retry_needed=True
                            )

            except SubBatch.DoesNotExist as exc:
                raise CommandError(f'SubBatch "{sub_batch}" does not exist') from exc
