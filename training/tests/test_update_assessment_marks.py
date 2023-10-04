# pylint: disable=too-many-lines
"""
Django test cases for updating the assessment details
"""
import time_machine
from django.db.models import (
    Avg,
    BooleanField,
    Case,
    Count,
    F,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import seq

from core import constants
from core.base_test import BaseTestCase
from core.utils import schedule_timeline_for_sub_batch
from hubble.models import Assessment, InternDetail, SubBatchTaskTimeline


class TaskSummaryTest(BaseTestCase):
    """
    This class is responsible for testing the header stats in user journey page
    """

    route_name = "user_reports"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)),
        )
        baker.make(
            "hubble.SubBatchTaskTimeline",
            days=seq(1),
            task_type=constants.TASK_TYPE_ASSESSMENT,
            sub_batch=self.sub_batch,
            start_date=self.sub_batch.start_date,
            end_date=(timezone.now() + timezone.timedelta(10)).date(),
            order=seq(0),
            _quantity=5,
        )
        self.trainee = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)
        self.another_trainee = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)

    def test_assessment_summary(self):
        """
        To ensure correct scores and comments are received
        """
        latest_task_report = Assessment.objects.filter(
            task=OuterRef("id"), user_id=self.trainee.user_id
        ).order_by("-id")[:1]
        desired_output = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch=self.sub_batch, task_type=constants.TASK_TYPE_ASSESSMENT
            )
            .annotate(
                retries=Count(
                    "assessments__is_retry",
                    filter=Q(
                        Q(assessments__user=self.trainee.user_id) & Q(assessments__is_retry=True)
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
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        for row, value in enumerate(desired_output):
            self.assertEqual(
                value.last_entry,
                response.context["assessment_scores"][row].last_entry,
            )
            self.assertEqual(
                value.comment,
                response.context["assessment_scores"][row].comment,
            )
            self.assertEqual(
                value.is_retry,
                response.context["assessment_scores"][row].is_retry,
            )
            self.assertEqual(
                value.inactive_tasks,
                response.context["assessment_scores"][row].inactive_tasks,
            )
            self.assertEqual(
                value.is_retry_needed,
                response.context["assessment_scores"][row].is_retry_needed,
            )
            self.assertEqual(
                value.present_status,
                response.context["assessment_scores"][row].present_status,
            )
            self.assertEqual(
                value.assessment_id,
                response.context["assessment_scores"][row].assessment_id,
            )
            self.assertEqual(
                value.retries,
                response.context["assessment_scores"][row].retries,
            )

    def test_no_assignment(self):
        """
        Check what happens when there is no assignment
        """
        latest_task_report = Assessment.objects.filter(
            task=OuterRef("id"), user_id=self.another_trainee.user_id
        ).order_by("-id")[:1]
        desired_output = list(
            SubBatchTaskTimeline.objects.filter(
                sub_batch=self.sub_batch, task_type=constants.TASK_TYPE_ASSESSMENT
            )
            .annotate(
                retries=Count(
                    "assessments__is_retry",
                    filter=Q(
                        Q(assessments__user=self.another_trainee.user_id)
                        & Q(assessments__is_retry=True)
                    ),
                ),
                last_entry=Subquery(latest_task_report.values("score")),
                comment=Subquery(latest_task_report.values("comment")),
                is_retry=Subquery(latest_task_report.values("is_retry")),
                inactive_tasks=Case(
                    When(start_date__gt=timezone.now(), then=Value(False)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
            )
            .order_by("order")
        )
        response = self.make_get_request(
            reverse(self.route_name, args=[self.another_trainee.user_id])
        )
        self.assertListEqual(desired_output, list(response.context["assessment_scores"]))


class HeaderStatsTest(BaseTestCase):
    """
    This class is responsible for testing the header stats in user journey page
    """

    route_name = "user_reports"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)),
        )
        task = baker.make(
            "hubble.SubBatchTaskTimeline",
            days=10,
            task_type=constants.TASK_TYPE_ASSESSMENT,
            sub_batch=self.sub_batch,
            start_date=self.sub_batch.start_date,
            end_date=(timezone.now() + timezone.timedelta(10)).date(),
            order=1,
        )
        self.trainee = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)
        baker.make(
            "hubble.Assessment",
            user_id=self.trainee.user_id,
            task_id=task.id,
            sub_batch=self.sub_batch,
        )
        baker.make(
            "hubble.Assessment",
            user_id=self.trainee.user_id,
            task_id=task.id,
            is_retry=True,
            sub_batch=self.sub_batch,
        )

    def test_header_stats(self):
        """
        To check whether the received stats are right or wrong
        """
        task_count = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch=self.sub_batch, task_type=constants.TASK_TYPE_ASSESSMENT
            )
            .values("id")
            .count()
        )
        task_count = max(task_count, 1)
        last_attempt_score = SubBatchTaskTimeline.objects.filter(
            id=OuterRef("user__assessments__task_id"),
            assessments__user_id=OuterRef("user_id"),
            assessments__present_status=True,
            assessments__deleted_at__isnull=True,
        ).order_by("-assessments__id")[:1]

        desired_output = (
            InternDetail.objects.filter(sub_batch=self.sub_batch, user_id=self.trainee.user_id)
            .annotate(
                no_of_retries=Count(
                    "user__assessments__is_retry",
                    filter=Q(
                        user__assessments__is_retry=True,
                        user__assessments__extension__isnull=True,
                        user__assessments__task_id__deleted_at__isnull=True,
                        user__assessments__sub_batch_id=self.sub_batch.id,
                        user__assessments__deleted_at__isnull=True,
                    ),
                ),
                completion=Count(
                    "user__assessments__task_id",
                    filter=Q(
                        user__assessments__user_id=F("user_id"),
                        user__assessments__task_id__deleted_at__isnull=True,
                        user__assessments__sub_batch_id=self.sub_batch.id,
                        user__assessments__deleted_at__isnull=True,
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
                            distinct=True,
                        ),
                    ),
                    default=None,
                ),
            )
            .values(
                "average_marks",
                "no_of_retries",
                "completion",
            )
        )
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(list(desired_output)[0], response.context["performance_stats"])


class UpdateAssessmentTest(BaseTestCase):
    """
    This class is responsible for testing the updating the scores in
    asssesments in user journey page
    """

    route_name = "user_reports"
    update_edit_route_name = "user.update-score"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.update_valid_input()

    def update_valid_input(self):
        """
        This function is responsible for updating the valid inputs and creating
        data in databases as reqiured
        """
        sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)),
        )
        days = 1
        self.sub_batch_task_timeline = baker.make(
            "hubble.SubBatchTaskTimeline",
            days=days,
            task_type=constants.TASK_TYPE_ASSESSMENT,
            start_date=sub_batch.start_date,
            sub_batch=sub_batch,
            end_date=(timezone.now() + timezone.timedelta(days)).date(),
            order=1,
        )
        self.trainee = baker.make("hubble.InternDetail", sub_batch=sub_batch)
        self.persisted_valid_inputs = {
            "score": 50,
            "comment": self.faker.name(),
            "task": self.sub_batch_task_timeline.id,
            "extension": "",
            "present_status": "True",
            "is_retry_needed": "true",
            "is_retry": "false",
            "test_week": "true",
        }

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertTemplateUsed(response, "sub_batch/user_journey_page.html")
        self.assertContains(response, self.trainee.user.employee_id)

    def test_test_week_scenarios(self):
        """
        Check what happens when valid data is given as input for test week
        """
        # Check what happens when is_retry is True
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=data,
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_has(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry_needed": data["is_retry_needed"].capitalize(),
                "is_retry": data["is_retry"].capitalize(),
            },
        )

        assessment = Assessment.objects.get(score=data["score"], user_id=self.trainee.user_id)
        data = self.get_valid_inputs({"assessment_id": assessment.id})
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=data,
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_has(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry_needed": data["is_retry_needed"].capitalize(),
                "is_retry": data["is_retry"].capitalize(),
            },
        )

        data = self.get_valid_inputs(
            {
                "assessment_id": assessment.id,
                "is_retry": "true",
                "test_week": "false",
                "is_retry_needed": "false",
            }
        )
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=data,
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_has(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry_needed": data["is_retry_needed"].capitalize(),
                "is_retry": data["is_retry"].capitalize(),
            },
        )

        assessment.is_retry = True
        assessment.save()
        data = self.get_valid_inputs(
            {
                "assessment_id": assessment.id,
                "is_retry": "true",
                "test_week": "false",
                "is_retry_needed": "false",
            }
        )
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=data,
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_has(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry_needed": data["is_retry_needed"].capitalize(),
                "is_retry": data["is_retry"].capitalize(),
            },
        )

        data = self.get_valid_inputs({"score": 100})
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=data,
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_has(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry_needed": data["is_retry_needed"].capitalize(),
                "is_retry": data["is_retry"].capitalize(),
            },
        )

    def test_retry_week_success_scenarios(self):
        """
        Check what happens when valid data is given as input for retry week
        """
        # Check what happens when is_retry is True
        data = self.get_valid_inputs(
            {"is_retry": "true", "test_week": "false", "is_retry_needed": "false"}
        )
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=data,
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_has(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry_needed": data["is_retry_needed"].capitalize(),
                "is_retry": data["is_retry"].capitalize(),
            },
        )

        data = self.get_valid_inputs(
            {
                "score": 100,
                "is_retry": "true",
                "test_week": "false",
                "is_retry_needed": "false",
            }
        )
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=data,
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_has(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry_needed": data["is_retry_needed"].capitalize(),
                "is_retry": data["is_retry"].capitalize(),
            },
        )

    def test_required_validation(self):
        """
        This function checks the required validation for the score and comment fields
        """
        # Check the required validation for present status
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data={},
        )
        field_errors = {
            "present_status": {"required"},
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)

        # Check the required validation for score and comment
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data={"present_status": True},
        )
        field_errors = {"score": {"required"}, "comment": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_score_validation(self):
        """
        This function checks the invalid_score validation for the score field
        """
        # Check what happens when score is greater than 100
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=self.get_valid_inputs({"score": 101}),
        )
        field_errors = {"score": {"invalid_score"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)

        # Check what happens when score is negative
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=self.get_valid_inputs({"score": -100}),
        )
        field_errors = {"score": {"invalid_score"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)

    def test_retry_week_failure_scenarios(self):
        """
        Check what happens when valid data is given as input for retry week
        """
        # Check what happens when is_retry is True
        data = self.get_valid_inputs(
            {"is_retry": "true", "test_week": "false", "is_retry_needed": "true"}
        )
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=data,
        )
        field_errors = {"is_retry_needed": {"invalid_week"}}
        custom_validation_error_message = {
            "invalid_week": "You can not suggest retry needed during the retry week"
        }
        self.assertJSONEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=custom_validation_error_message,
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assert_database_not_has(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry_needed": data["is_retry_needed"].capitalize(),
                "is_retry": data["is_retry"].capitalize(),
            },
        )

    def test_test_week_failure_scenarios(self):
        """
        Check what happens when valid data is given as input for retry week
        """
        # Check what happens when is_retry is True
        data = self.get_valid_inputs({"is_retry": "true", "is_retry_needed": "true"})
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=data,
        )
        field_errors = {"is_retry": {"invalid_week"}}
        custom_validation_error_message = {
            "invalid_week": "You can not update retry score during the test week"
        }
        self.assertJSONEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=custom_validation_error_message,
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assert_database_not_has(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry_needed": data["is_retry_needed"].capitalize(),
                "is_retry": data["is_retry"].capitalize(),
            },
        )


class TaskScoreHistory(BaseTestCase):
    """
    This class is responsible for testing whether the rendered
    Score History table is correct or not
    """

    route_name = "score_history"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)),
        )
        self.sub_batch_task_timeline = baker.make(
            "hubble.SubBatchTaskTimeline",
            days=10,
            task_type=constants.TASK_TYPE_ASSESSMENT,
            sub_batch=self.sub_batch,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timezone.timedelta(10)).date(),
            order=1,
        )
        self.trainee = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)
        baker.make(
            "hubble.Assessment",
            task_id=self.sub_batch_task_timeline.id,
            user_id=self.trainee.user_id,
            sub_batch=self.sub_batch,
            score=50,
            is_retry_needed=True,
            is_retry=False,
        )
        self.another_sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)),
        )
        self.trainee = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)
        self.another_trainee = baker.make("hubble.InternDetail", sub_batch=self.another_sub_batch)

    def test_score_history(self):
        """
        This function will test whether the rendered score history table is correct or not
        """
        data = {
            "extension_id": "",
            "task_id": self.sub_batch_task_timeline.id,
            "user_id": self.trainee.user_id,
        }
        response = self.make_post_request(
            reverse(self.route_name),
            data=data,
        )
        data = Assessment.objects.filter(
            task_id=self.sub_batch_task_timeline.id,
            extension_id=None,
            user_id=self.trainee.user_id,
            sub_batch_id=InternDetail.objects.filter(user_id=self.trainee.user_id)
            .values("sub_batch_id")
            .last()["sub_batch_id"],
        ).order_by("-id")
        self.assertEqual(set(response.context["data"]), set(data))


class AssessmentUpdateShowTest(BaseTestCase):
    """
    This class is responsible for testing whether the rendered Assessment details is correct or not
    """

    route_name = "task.show_score"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)),
        )
        self.sub_batch_task_timeline = baker.make(
            "hubble.SubBatchTaskTimeline",
            days=10,
            task_type=constants.TASK_TYPE_ASSESSMENT,
            sub_batch=self.sub_batch,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timezone.timedelta(10)).date(),
            order=1,
        )
        self.trainee = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)
        baker.make(
            "hubble.Assessment",
            task_id=self.sub_batch_task_timeline.id,
            user_id=self.trainee.user_id,
            sub_batch=self.sub_batch,
            score=50,
            is_retry_needed=True,
            is_retry=False,
        )

    def test_success(self):
        """
        This function is responsible for testing the assessment details
        rendered in the Update Modal
        """
        data = {
            "extension_id": "",
            "task_id": self.sub_batch_task_timeline.id,
            "trainee_id": self.trainee.user_id,
            "sub_batch_id": self.sub_batch.id,
        }
        response = self.make_get_request(
            reverse(self.route_name),
            data=data,
        )
        desired_output = model_to_dict(
            Assessment.objects.filter(
                task_id=None if data["task_id"] == "" else data["task_id"],
                extension_id=None if data["extension_id"] == "" else data["extension_id"],
                sub_batch_id=data["sub_batch_id"],
                user_id=data["trainee_id"],
            )
            .order_by("-created_at")
            .first()
        )
        self.assertEqual(
            response.json()["task_details"],
            desired_output,
        )
        self.assertEqual(response.status_code, 200)

    def test_failure(self):
        """
        This function is responsible for testing the assessment details
        rendered in the Update Modal
        """
        data = {
            "extension_id": 0,
            "task_id": 0,
            "trainee_id": 0,
            "sub_batch_id": 0,
        }
        response = self.make_get_request(
            reverse(self.route_name),
            data=data,
        )
        self.assertJSONEqual(
            self.decoded_json(response),
            {"message": "This task/ extension doesn't have any history"},
        )
        self.assertEqual(response.status_code, 404)


class AssessmentRenderedTest(BaseTestCase):
    """
    This class is responsible for testing the anchor tags that is rendered
    """

    route_name = "user_reports"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(-1)).date(),
        )
        baker.make(
            "hubble.SubBatchTaskTimeline",
            days=seq(1),
            task_type=constants.TASK_TYPE_ASSESSMENT,
            sub_batch=self.sub_batch,
            start_date=self.sub_batch.start_date,
            end_date=(timezone.now() + timezone.timedelta(2)).date(),
            order=seq(0),
            _quantity=2,
        )
        schedule_timeline_for_sub_batch(self.sub_batch, is_create=False)
        self.task = SubBatchTaskTimeline.objects.filter(sub_batch=self.sub_batch)
        self.trainee = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)
        self.assessment = baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            is_retry_needed=True,
            present_status=True,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            _fill_optional=["comment"],
        )

    def test_test_week_scenarios(self):
        """
        This function is responsible for testing whether the
        Test Create model is rendered correctly
        """
        Assessment.objects.all().update(deleted_at=timezone.now())
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertTemplateUsed(response, "sub_batch/user_journey_page.html")
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status, constants.TEST_CREATE
        )

        baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            is_retry_needed=True,
            present_status=False,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            _fill_optional=["comment"],
        )
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status, constants.TEST_EDIT
        )

        baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            is_retry_needed=True,
            present_status=True,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            _fill_optional=["comment"],
        )
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status, constants.TEST_EDIT
        )

        Assessment.objects.all().update(deleted_at=timezone.now())
        baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            present_status=True,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            updated_at=timezone.now() + timezone.timedelta(-1),
            _fill_optional=["comment"],
        )

        traveller = time_machine.travel(self.task[1].start_date)
        traveller.start()
        baker.make(
            "hubble.SubBatchTaskTimeline",
            days=seq(1),
            task_type=constants.TASK_TYPE_ASSESSMENT,
            sub_batch=self.sub_batch,
            start_date=self.sub_batch.start_date,
            end_date=(timezone.now() + timezone.timedelta(2)).date(),
            order=3,
        )
        schedule_timeline_for_sub_batch(self.sub_batch, is_create=False)
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status, constants.TEST_COMPLETED
        )
        SubBatchTaskTimeline.objects.filter(sub_batch=self.sub_batch, order=3).delete()
        traveller.stop()

        traveller = time_machine.travel(self.task[1].start_date)
        traveller.start()
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status, constants.TEST_COMPLETED
        )
        Assessment.objects.all().update(deleted_at=timezone.now())
        baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            present_status=True,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            _fill_optional=["comment"],
        )
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status, constants.TEST_EDIT
        )

        Assessment.objects.all().update(deleted_at=timezone.now())

        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status,
            constants.INFINITE_TEST_CREATE,
        )

        baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            is_retry_needed=True,
            present_status=False,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            updated_at=timezone.now(),
            _fill_optional=["comment"],
        )
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status,
            constants.INFINITE_TEST_EDIT,
        )

        traveller.stop()

    def test_retest_week_scenarios(self):
        """
        This function is responsible for testing whether the
        retest scenarios are handled correctly or not
        """
        traveller = time_machine.travel(self.task[1].start_date)
        traveller.start()
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status,
            constants.INFINITE_RETEST_CREATE,
        )

        baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            is_retry=True,
            present_status=False,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            updated_at=timezone.now(),
            _fill_optional=["comment"],
        )
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status,
            constants.INFINITE_RETEST_EDIT,
        )

        baker.make(
            "hubble.SubBatchTaskTimeline",
            days=seq(1),
            task_type=constants.TASK_TYPE_ASSESSMENT,
            sub_batch=self.sub_batch,
            start_date=self.sub_batch.start_date,
            end_date=(timezone.now() + timezone.timedelta(2)).date(),
            order=3,
        )
        schedule_timeline_for_sub_batch(self.sub_batch, is_create=False)
        baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            is_retry=True,
            present_status=False,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            updated_at=timezone.now(),
            _fill_optional=["comment"],
        )
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status, constants.RETEST_EDIT
        )

        baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            is_retry=True,
            present_status=True,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            updated_at=timezone.now(),
            _fill_optional=["comment"],
        )
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status, constants.RETEST_EDIT
        )

        Assessment.objects.filter(is_retry=True).update(deleted_at=timezone.now())
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status, constants.RETEST_CREATE
        )

        baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            is_retry=True,
            present_status=True,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            updated_at=timezone.now(),
            _fill_optional=["comment"],
        )
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status, constants.RETEST_EDIT
        )
        traveller.stop()

        Assessment.objects.filter(is_retry=True).update(deleted_at=timezone.now())

        baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            is_retry=True,
            present_status=True,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            _fill_optional=["comment"],
        )
        traveller = time_machine.travel(self.task[1].start_date)
        traveller.start()
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status, constants.TEST_COMPLETED
        )
        SubBatchTaskTimeline.objects.filter(sub_batch=self.sub_batch, order=3).delete()

        Assessment.objects.filter(is_retry=True).update(deleted_at=timezone.now())
        traveller = time_machine.travel(self.task[1].start_date)
        traveller.start()
        baker.make(
            "hubble.Assessment",
            score=self.faker.random_int(1, 100),
            user_id=self.trainee.user_id,
            is_retry=True,
            present_status=True,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            _fill_optional=["comment"],
        )
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status,
            constants.INFINITE_RETEST_EDIT,
        )

        baker.make(
            "hubble.Assessment",
            user_id=self.trainee.user_id,
            is_retry=True,
            present_status=False,
            task_id=self.task[0].id,
            sub_batch_id=self.sub_batch.id,
            _fill_optional=["comment"],
        )
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
        self.assertEqual(
            response.context["assessment_scores"][0].assessment_status,
            constants.INFINITE_RETEST_EDIT,
        )

        traveller.stop()
