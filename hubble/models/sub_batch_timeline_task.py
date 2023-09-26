"""
The SubBatchTaskTimeline class is a Django model that stores data about
sub batch timelines and provides a method to check if the timeline
is editable based on its start date
"""
from django.db import models
from django.utils import timezone

from core import constants, db
from core.assessment_status import (
    first_assessment_entry,
    second_assessment_entry,
    zeroth_assessment_entry,
)


class SubBatchTaskTimeline(db.SoftDeleteWithBaseModel):
    """
    Store the data of sub batch timeline
    """

    name = models.CharField(max_length=255)
    days = models.FloatField()
    sub_batch = models.ForeignKey(
        "hubble.SubBatch",
        on_delete=models.CASCADE,
        related_name="task_timelines",
    )
    present_type = models.CharField(
        max_length=255,
        choices=constants.PRESENT_TYPES,
        default=constants.PRESENT_TYPE_REMOTE,
    )
    task_type = models.CharField(
        max_length=255,
        choices=constants.TASK_TYPES,
        default=constants.TASK_TYPE_TASK,
    )
    start_date = db.DateTimeWithoutTZField(null=True)
    end_date = db.DateTimeWithoutTZField(null=True)
    order = models.IntegerField(blank=True)
    created_by = models.ForeignKey("hubble.User", on_delete=models.CASCADE)

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        db_table = "sub_batch_timeline_tasks"
        ordering = ["order"]

    def can_editable(self):
        """
        Check if the timesheet is editable based on its start date
        """
        # It is used to ommit 'no-member' it tells that the '
        # DateTimeWithoutTZField has no date member
        # pylint: disable=no-member
        return self.start_date.date() > timezone.now().date()

    def update_assessment(self, order, user, sub_batch_tasks):
        """
        This function is responsible for telling the current assessment to be taken
        """
        tasks = [tasks for tasks in sub_batch_tasks if tasks["order"] >= order]
        try:
            current_week_start_date = [
                cur["start_date"] for cur in tasks if cur["start_date"] < timezone.now()
            ][-1]
        except IndexError:
            current_week_start_date = (
                constants.NO_START_DATE
            )  # TODO :: Not Considering this right now...
        try:
            current_week_end_date = [
                cur["start_date"] for cur in tasks if cur["start_date"] > timezone.now()
            ][0]
        except IndexError:
            current_week_end_date = constants.NO_END_DATE
        current_task = tasks[0]
        assessments_completed = [
            assessment
            for assessment in current_task["assessments"]
            if assessment["user_id"] == user
        ]
        assessment_attended = [
            assessment_attended
            for assessment_attended in current_task["assessments"]
            if (
                (assessment_attended["user_id"] == user)
                and (assessment_attended["present_status"] is not False)
            )
        ]
        current_task_assessments = len(assessment_attended)
        try:
            last_assessment_with_absent_record = assessments_completed[-1]
        except IndexError:
            last_assessment_with_absent_record = []
        try:
            last_assessment_record = assessment_attended[-1]
        except IndexError:
            last_assessment_record = []

        arguments = (
            current_week_end_date,
            current_week_start_date,
            last_assessment_with_absent_record,
        )

        if current_task_assessments == 0:
            return zeroth_assessment_entry(*arguments, current_task, user)

        if current_task_assessments == 1:
            return first_assessment_entry(*arguments, last_assessment_record)

        if current_task_assessments == 2:
            return second_assessment_entry(*arguments, last_assessment_record)
        return constants.TEST_COMPLETED
