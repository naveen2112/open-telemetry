from django.db.models import (Avg, BooleanField, Case, Count, F, OuterRef, Q,
                              Subquery, Value, When)
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import seq

from core.base_test import BaseTestCase
from core.constants import TASK_TYPE_ASSESSMENT
from hubble.models import Assessment, InternDetail, SubBatchTaskTimeline


class UpdateAssessmentTest(BaseTestCase):
    """
    This class is responsible for testing the updating the scores in asssesments in user journey page
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
        This function is responsible for updating the valid inputs and creating data in databases as reqiured
        """
        sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)),
        )
        sub_batch_task_timeline = baker.make(
            "hubble.SubBatchTaskTimeline",
            days=10,
            task_type=TASK_TYPE_ASSESSMENT,
            sub_batch=sub_batch,
            end_date=(timezone.now() + timezone.timedelta(10)).date(),
            order=1,
        )
        self.trainee = baker.make("hubble.InternDetail", sub_batch=sub_batch)
        self.persisted_valid_inputs = {
            "score": 50,
            "comment": self.faker.name(),
            "task": sub_batch_task_timeline.id,
            "extension": "",
            "status": "true",
        }

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(
            reverse(self.route_name, args=[self.trainee.user_id])
        )
        self.assertTemplateUsed(response, "sub_batch/user_journey_page.html")
        self.assertContains(response, self.trainee.user.employee_id)

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        # Check what happens when is_retry is True
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=data,
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry": data["status"].capitalize(),
            },
        )

        # Check what happens when is_retry is False
        data = self.get_valid_inputs({"status": "false"})
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data=data,
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry": data["status"].capitalize(),
            },
        )

    def test_required_validation(self):
        """
        This function checks the required validation for the score and comment fields
        """
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.trainee.user_id]),
            data={},
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
            task_type=TASK_TYPE_ASSESSMENT,
            sub_batch=self.sub_batch,
            end_date=(timezone.now() + timezone.timedelta(10)).date(),
            order=seq(0),
            _quantity=5,
        )
        self.another_sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)),
        )
        self.trainee = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)
        self.another_trainee = baker.make("hubble.InternDetail", sub_batch=self.another_sub_batch)

    def test_assessment_summary(self):
        """
        To ensure correct scores and comments are received
        """
        latest_task_report = Assessment.objects.filter(
            task=OuterRef("id"), user_id=self.trainee.user_id
        ).order_by("-id")[:1]
        desired_output = list(
            SubBatchTaskTimeline.objects.filter(
                sub_batch=self.sub_batch, task_type=TASK_TYPE_ASSESSMENT
            )
            .annotate(
                retries=Count(
                    "assessments__is_retry",
                    filter=Q(
                        Q(assessments__user=self.trainee.user_id)
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
        response = self.make_get_request(
            reverse(self.route_name, args=[self.trainee.user_id])
        )
        for row in range(len(desired_output)):
            self.assertEqual(
                desired_output[row], response.context["assessment_scores"][row]
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
                sub_batch=self.another_sub_batch, task_type=TASK_TYPE_ASSESSMENT
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
        baker.make(
            "hubble.SubBatchTaskTimeline",
            days=10,
            task_type=TASK_TYPE_ASSESSMENT,
            sub_batch=self.sub_batch,
            end_date=(timezone.now() + timezone.timedelta(10)).date(),
            order=1,
        )
        self.trainee = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)

    def test_header_stats(self):
        """
        To check whether the received stats are right or wrong
        """
        task_count = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch=self.sub_batch, task_type=TASK_TYPE_ASSESSMENT
            )
            .values("id")
            .count()
        )
        last_attempt_score = SubBatchTaskTimeline.objects.filter(
            id=OuterRef("user__assessments__task_id"),
            assessments__user_id=OuterRef("user_id"),
        ).order_by("-assessments__id")[:1]

        desired_output = (
            InternDetail.objects.filter(
                sub_batch=self.sub_batch, user_id=self.trainee.user_id
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
        response = self.make_get_request(
            reverse(self.route_name, args=[self.trainee.user_id])
        )
        self.assertEqual(list(desired_output)[0], response.context["performance_stats"])
