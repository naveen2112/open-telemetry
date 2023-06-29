from django.forms.models import model_to_dict
from django.urls import reverse
from model_bakery import baker
from django.utils import timezone

from core.base_test import BaseTestCase
from hubble.models import Timeline, User, InternDetail


class ExtensionCreateTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in timeline module
    """
    route_name = "user_reports"
    create_route_name = "extension.create"

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
        self.sub_batch = baker.make("hubble.SubBatch", start_date=(timezone.now() + timezone.timedelta(1)))
        sub_batch_task_timeline = baker.make("hubble.SubBatchTaskTimeline", sub_batch=self.sub_batch, days=1, order=1)
        self.intern = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)
        # print(InternDetail.objects.all().values("id", "user_id"))
        # print(self.intern.user_id, self.intern.sub_batch)


    def test_success(self):
        response = self.make_post_request(reverse(self.create_route_name, args=[self.intern.user_id]), data={})
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseHas(
            "Extension",
            {
                "user_id": self.intern.user_id,
                "sub_batch": self.sub_batch
            },
        )

    def test_failure(self):
        response = self.make_post_request(reverse(self.create_route_name, args=[0]), data={})
        self.assertJSONEqual(self.decoded_json(response), {"status": "error"})
        self.assertTrue(response.status_code, 200)

class ExtensionUpdateTest(BaseTestCase):
    """
    This class is responsible for testing the updating the scores in asssesments in user journey page
    """
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
        extension_task = baker.make("hubble.Extension", sub_batch=sub_batch)
        self.intern = baker.make("hubble.InternDetail", sub_batch=sub_batch)
        # assessment = baker.make("hubble.Assessment", sub_batch=sub_batch, extension=None, score=50, task=sub_batch_task_timeline, _quantity=10)
        self.persisted_valid_inputs = {
            "score": 50,
            "comment": self.faker.name(),
            "task": "",
            "extension": extension_task.id,
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
                "extension_id": data["extension"],
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
                "extension_id": data["extension"],
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


class ExtensionWeekTaskDelete(BaseTestCase):
    """
    This class is responsible for testing the DELETE feature in timeline module
    """

    delete_route_name = "extension.delete"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_success(self):
        """
        To check what happens when valid id is given for delete
        """
        extension = baker.make("hubble.Extension")
        self.assertDatabaseHas("Extension", {"id": extension.id})
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[extension.id])
        )
        self.assertJSONEqual(
            response.content, {"message": "Week extension deleted succcessfully", "status": "success"}
        )
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseNotHas("Extension", {"id": extension.id})

    def test_failure(self):
        """
        To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(reverse(self.delete_route_name, args=[0]))
        self.assertJSONEqual(
            response.content, {"message": "Error while deleting week extension!"}
        )
        self.assertTrue(response.status_code, 500)