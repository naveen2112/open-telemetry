from django.db.models import Count, OuterRef, Q, Subquery
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import seq

from core.base_test import BaseTestCase
from core.constants import TASK_TYPE_ASSESSMENT
from hubble.models import Assessment, Extension


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
        self.sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)),
        )
        self.trainee = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(
            reverse(self.route_name, args=[self.trainee.user_id])
        )
        self.assertTemplateUsed(response, "sub_batch/user_journey_page.html")
        self.assertContains(response, self.trainee.user_id)

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        desired_extension_name = Extension.objects.filter(user_id=self.trainee.user_id, sub_batch=self.sub_batch).count() + 1
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.trainee.user_id]),
            data={},
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "Extension",
            {
                "name": f"Extension Week {desired_extension_name}",
                "user_id": self.trainee.user_id,
                "sub_batch": self.sub_batch,
            },
        )

    def test_failure(self):
        """
        Check what happens when invalid data is given as input
        """
        response = self.make_post_request(
            reverse(self.create_route_name, args=[0]), data={}
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "error"})
        self.assertEqual(response.status_code, 200)


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
        sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)),
        )
        self.extension_task = baker.make("hubble.Extension", sub_batch=sub_batch)
        self.trainee = baker.make("hubble.InternDetail", sub_batch=sub_batch)
        self.persisted_valid_inputs = {
            "score": 50,
            "comment": self.faker.name(),
            "task": "",
            "extension": self.extension_task.id,
            "status": "true",
        }

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
                "extension_id": data["extension"],
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
                "extension_id": data["extension"],
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
        trainee = baker.make("hubble.User")
        sub_batch = baker.make("hubble.SubBatch")
        extension = baker.make("hubble.Extension", user_id=trainee.id, sub_batch=sub_batch, name=seq("Extension Week "), _quantity=2)
        self.assertDatabaseHas("Extension", {"id": extension[0].id})
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[extension[0].id])
        )
        self.assertJSONEqual(
            response.content,
            {
                "message": "Week extension deleted succcessfully",
                "status": "success",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseNotHas("Extension", {"id": extension[0].id})
        self.assertDatabaseHas("Extension", {"id": extension[1].id, "name": extension[0].name})

    def test_failure(self):
        """
        To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(reverse(self.delete_route_name, args=[0]))
        self.assertJSONEqual(
            response.content,
            {"message": "Error while deleting week extension!"},
        )
        self.assertEqual(response.status_code, 500)


class ExtensionSummaryTest(BaseTestCase):
    """
    This class is responsible for testing the contents of extension cards in user journey page
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
        self.trainee = baker.make("hubble.InternDetail", sub_batch=self.sub_batch)
        extension_task = baker.make(
            "hubble.Extension", sub_batch=self.sub_batch, user_id=self.trainee.user_id
        )
        baker.make(
            "hubble.Assessment",
            extension_id=extension_task.id,
            user_id=self.trainee.user_id,
            _quantity=2,
        )

    def test_assessment_summary(self):
        """
        To ensure correct scores and comments are received
        """
        latest_extended_task_report = Assessment.objects.filter(
            extension=OuterRef("id")
        ).order_by("-id")[:1]
        desired_output = (
            Extension.objects.filter(
                sub_batch=self.sub_batch.id, user=self.trainee.user
            )
            .annotate(
                retries=Count(
                    "assessments__is_retry", filter=Q(assessments__is_retry=True)
                ),
                last_entry=Subquery(latest_extended_task_report.values("score")),
                comment=Subquery(latest_extended_task_report.values("comment")),
                is_retry=Subquery(latest_extended_task_report.values("is_retry")),
            )
            .order_by("id")
        )
        response = self.make_get_request(
            reverse(self.route_name, args=[self.trainee.user_id])
        )
        for row in range(len(desired_output)):
            self.assertEqual(
                desired_output[row], response.context["extension_tasks"][row]
            )
