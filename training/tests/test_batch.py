from django.forms.models import model_to_dict
from django.urls import reverse
from model_bakery import baker

from core.base_test import BaseTestCase
from hubble.models import Batch


class BatchCreateTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in batch module
    """

    create_route_name = "batch.create"
    route_name = "batch"

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
        self.persisted_valid_inputs = {"name": self.faker.name()}

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name))
        self.assertTemplateUsed(response, "batch/batch_list.html")
        self.assertContains(response, "Batch List")

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        data = self.get_valid_inputs()
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseHas("Batch", {"name": data["name"]})

    def test_required_validation(self):
        """
        This function checks the required validation for the name field
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"name": ""}),
        )
        field_errors = {"name": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )

    def test_min_length_validation(self):
        """
        Check what happens when name field fails MinlengthValidation
        """
        data = self.get_valid_inputs({"name": self.faker.pystr(max_chars=2)})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"name": {"min_length"}}
        validation_paramters = {"name": 3}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                current_value=data,
                validation_parameter=validation_paramters,
            ),
        )
        self.assertTrue(response.status_code, 200)


class BatchShowTest(BaseTestCase):
    """
    This class is responsible for testing the SHOW process in timeline module
    """

    update_show_route_name = "batch.show"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        batch = baker.make("hubble.Batch")
        response = self.make_get_request(
            reverse(self.update_show_route_name, args=[batch.id])
        )
        self.assertJSONEqual(
            self.decoded_json(response),
            {"batch": model_to_dict(Batch.objects.get(id=batch.id))},
        )

    def test_failure(self):
        """
        To check what happens when invalid id is given as argument for batch update
        """
        response = self.make_get_request(reverse(self.update_show_route_name, args=[0]))
        self.assertEqual(response.status_code, 500)


class BatchUpdateTest(BaseTestCase):
    """
    This class is responsible for testing the UPDATE feature in timeline module
    """

    update_edit_route_name = "batch.edit"

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
        self.persisted_valid_inputs = {"name": self.faker.name()}
        self.batch_id = baker.make("hubble.Batch").id

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.batch_id]), data=data
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseHas("Batch", {"name": data["name"]})

    def test_required_validation(self):
        """
        This function checks the required validation for the name field
        """
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.batch_id]),
            data=self.get_valid_inputs({"name": ""}),
        )
        field_errors = {"name": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )

    def test_min_length_validation(self):
        """
        To check what happens when name field fails MinlengthValidation
        """
        data = self.get_valid_inputs({"name": self.faker.pystr(max_chars=2)})
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.batch_id]), data=data
        )
        field_errors = {"name": {"min_length"}}
        validation_paramters = {"name": 3}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                current_value=data,
                validation_parameter=validation_paramters,
            ),
        )
        self.assertTrue(response.status_code, 200)


class BatchDeleteTest(BaseTestCase):
    """
    This class is responsible for testing the DELETE feature in timeline module
    """

    delete_route_name = "batch.delete"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        batch = baker.make("hubble.Batch")
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[batch.id])
        )
        self.assertJSONEqual(
            response.content, {"message": "Batch deleted succcessfully"}
        )
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseNotHas("Batch", {"id": batch.id})

    def test_failure(self):
        """
        To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(reverse(self.delete_route_name, args=[0]))
        self.assertEqual(response.status_code, 500)
