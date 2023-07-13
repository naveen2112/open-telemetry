"""
Django test cases for updating the assessment details
"""
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from core.base_test import BaseTestCase


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
        sub_batch_task_timeline = baker.make(
            "hubble.SubBatchTaskTimeline",
            sub_batch=sub_batch,
            days=1,
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
        response = self.make_get_request(reverse(self.route_name, args=[self.trainee.user_id]))
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
        self.assert_database_has(
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
        self.assert_database_has(
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
