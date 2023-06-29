from django.urls import reverse
from model_bakery import baker
from django.utils import timezone

from core.base_test import BaseTestCase


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
        sub_batch = baker.make("hubble.SubBatch", start_date=(timezone.now() + timezone.timedelta(1)))
        sub_batch_task_timeline = baker.make("hubble.SubBatchTaskTimeline", sub_batch=sub_batch, days=1, order=1)
        self.intern = baker.make("hubble.InternDetail", sub_batch=sub_batch)
        # assessment = baker.make("hubble.Assessment", sub_batch=sub_batch, extension=None, score=50, task=sub_batch_task_timeline, _quantity=10)
        self.persisted_valid_inputs = {
            "score": 50,
            "comment": self.faker.name(),
            "task": sub_batch_task_timeline.id,
            "extension": "",
            "status": "true",
        }
    
    def test_success(self):
        data = self.get_valid_inputs()
        response = self.make_post_request(reverse(self.update_edit_route_name, args=[self.intern.user_id]), data=data)
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseHas(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry": True,
            },
        )

        data = self.get_valid_inputs({"status": "false"})
        response = self.make_post_request(reverse(self.update_edit_route_name, args=[self.intern.user_id]), data=data)
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseHas(
            "Assessment",
            {
                "score": data["score"],
                "comment": data["comment"],
                "task_id": data["task"],
                "is_retry": False,
            },
        )

    def test_required_validation(self):
        response = self.make_post_request(reverse(self.update_edit_route_name, args=[self.intern.user_id]), data=self.get_valid_inputs({"score": "", "comment": ""}))
        field_errors = {"score": {"required"}, "comment": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
