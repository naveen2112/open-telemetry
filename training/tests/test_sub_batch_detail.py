from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from core.base_test import BaseTestCase


class AddInternTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in SubBatchDetail module
    """

    route_name = "sub-batch.detail"
    create_route_name = "trainees.add"

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
        intern = baker.make("hubble.User", is_employed=False, _fill_optional=["email"])
        self.sub_batch = baker.make("hubble.SubBatch", start_date=timezone.now().date())
        baker.make(
            "hubble.SubBatchTaskTimeline",
            days=10,
            sub_batch=self.sub_batch,
            end_date=(timezone.now() + timezone.timedelta(10)).date(),
            order=1,
        )
        self.persisted_valid_inputs = {
            "user_id": intern.id,
            "college": self.faker.name(),
            "sub_batch_id": self.sub_batch.id,
        }

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(
            reverse(self.route_name, args=[self.sub_batch.id])
        )
        self.assertTemplateUsed(response, "sub_batch/sub_batch_detail.html")
        self.assertContains(response, self.sub_batch.name)

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        data = self.get_valid_inputs()
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseHas(
            "InternDetail",
            {
                "user_id": data["user_id"],
                "college": data["college"],
                "sub_batch_id": data["sub_batch_id"],
            },
        )

    def test_required_validation(self):
        """
        This function checks the required validation for the team and name fields
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs(
                {"user_id": "", "college": "", "sub_batch_id": ""}
            ),
        )
        field_errors = {"user_id": {"required"}, "college": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )

    def test_minimim_length_validation(self):
        """
        To check what happens when college field fails MinlengthValidation
        """
        data = self.get_valid_inputs({"college": self.faker.pystr(max_chars=2)})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"college": {"min_length"}}
        validation_paramters = {"college": 3}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                current_value=data,
                validation_parameter=validation_paramters,
            ),
        )
        self.assertTrue(response.status_code, 200)

    def test_invalid_choice_validation(self):
        """
        Check what happens when invalid data for user_id field is given as input
        """
        response = self.make_post_request(
            reverse(self.create_route_name), data=self.get_valid_inputs({"user_id": 0})
        )
        field_errors = {"user_id": {"invalid_choice"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertTrue(response.status_code, 200)

    def test_invalid_sub_batch_id(self):
        """
        Check what happens when invalid sub_batch id is given as input
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"sub_batch_id": 0}),
        )
        field_errors = {"__all__": {""}}
        error_message = {"": "You are trying to add trainees to an invalid SubBatch"}
        non_field_errors = {
            "message": "You are trying to add trainees to an invalid SubBatch",
            "code": "",
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                non_field_errors=non_field_errors,
                custom_validation_error_message=error_message,
            ),
        )


class DeleteInternTest(BaseTestCase):
    """
    This class is responsible for testing the DELETE feature in timeline module
    """

    delete_route_name = "trainee.remove"

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
        trainee = baker.make("hubble.InternDetail")
        self.assertDatabaseHas("InternDetail", {"id": trainee.id})
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[trainee.id])
        )
        self.assertJSONEqual(
            response.content, {"message": "Intern has been deleted succssfully"}
        )
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseNotHas("InternDetail", {"id": trainee.id})

    def test_failure(self):
        """
        To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(reverse(self.delete_route_name, args=[0]))
        self.assertJSONEqual(
            response.content, {"message": "Error while deleting Timeline Template!"}
        )
        self.assertTrue(response.status_code, 200)
