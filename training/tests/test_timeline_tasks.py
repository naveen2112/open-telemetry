import random

from django.forms.models import model_to_dict
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import seq

from core.base_test import BaseTestCase
from core.constants import (PRESENT_TYPE_IN_PERSON, PRESENT_TYPE_REMOTE,
                            TASK_TYPE_ASSESSMENT, TASK_TYPE_CULTURAL_MEET,
                            TASK_TYPE_TASK)
from hubble.models import TimelineTask


class TimelineTaskCreateTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in timeline task module
    """

    create_route_name = "timeline-task.create"
    route_name = "timeline-template.detail"

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
        self.timeline = baker.make("hubble.Timeline")
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "days": 2,
            "present_type": PRESENT_TYPE_REMOTE,
            "task_type": TASK_TYPE_TASK,
            "timeline_id": self.timeline.id,
        }

    def validate_response(self, response, data):
        """
        To automate the assertion commands, where same logics are repeated
        """
        self.assertJSONEqual(
            self.decoded_json(response), {"status": "success"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "TimelineTask",
            {
                "name": data["name"],
                "days": data["days"],
                "present_type": data["present_type"],
                "task_type": data["task_type"],
                "timeline_id": data["timeline_id"],
            },
        )

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(
            reverse(self.route_name, args=[self.timeline.id])
        )
        self.assertTemplateUsed(
            response, "timeline_template_detail.html"
        )
        self.assertContains(response, self.timeline.name)

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(self.create_route_name), data=data
        )
        self.validate_response(response, data)

        # Check what happens when valid decimal data is given as input
        data = self.get_valid_inputs(
            {
                "days": 0.5,
                "present_type": PRESENT_TYPE_IN_PERSON,
                "task_type": TASK_TYPE_CULTURAL_MEET,
            }
        )
        response = self.make_post_request(
            reverse(self.create_route_name), data=data
        )
        self.validate_response(response, data)

        # Check whether the radio select options work correctly
        data = self.get_valid_inputs(
            {
                "days": 1.5,
                "present_type": PRESENT_TYPE_IN_PERSON,
                "task_type": TASK_TYPE_ASSESSMENT,
            }
        )
        response = self.make_post_request(
            reverse(self.create_route_name), data=data
        )
        self.validate_response(response, data)

    def test_minimum_length_validation(self):
        """
        To check what happens when name field fails MinlengthValidation
        """
        data = self.get_valid_inputs(
            {"name": self.faker.pystr(max_chars=2)}
        )
        response = self.make_post_request(
            reverse(self.create_route_name), data=data
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
        self.assertEqual(response.status_code, 200)

    def test_required_validation(self):
        """
        This function checks the required validation for the all the fields
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data={
                "timeline_id": self.timeline.id,
            },
        )
        field_errors = {
            "name": {"required"},
            "days": {"required"},
            "present_type": {"required"},
            "task_type": {"required"},
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)

    def test_validate_days_validation(self):
        """
        This function checks the validate days validation for the days field
        """
        # Check what happens when days field fails the validation is_not_divisible_by_0.5
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"days": 0.25}),
        )
        field_errors = {"days": {"is_not_divisible_by_0.5"}}
        error_message = {
            "is_not_divisible_by_0.5": "Value must be a multiple of 0.5"
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=error_message,
            ),
        )
        self.assertEqual(response.status_code, 200)

        # Check what happend when the days field fails value_cannot_be_zero
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"days": 0}),
        )
        field_errors = {"days": {"value_cannot_be_zero"}}
        error_message = {
            "value_cannot_be_zero": "Value must be greater than 0"
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=error_message,
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_choice_validations(self):
        """
        Check what happens when invalid data for present_type and task_type are given as input
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs(
                {
                    "present_type": self.faker.name(),
                    "task_type": self.faker.name(),
                }
            ),
        )
        field_errors = {
            "present_type": {"invalid_choice"},
            "task_type": {"invalid_choice"},
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)


class TimelineTaskShowTest(BaseTestCase):
    """
    This class is responsible for testing the SHOW process in timeline module
    """

    update_show_route_name = "timeline-task.show"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_success(self):
        """
        Checks what happens when valid inputs are given for all fields
        """
        timelinetask = baker.make(
            "hubble.TimelineTasK",
            timeline=baker.make("hubble.Timeline"),
            order=1,
        )
        response = self.make_get_request(
            reverse(self.update_show_route_name, args=[timelinetask.id])
        )
        self.assertJSONEqual(
            self.decoded_json(response),
            {
                "timeline_task": model_to_dict(
                    TimelineTask.objects.get(id=timelinetask.id)
                )
            },
        )

    def test_failure(self):
        """
        Checks what happens when we try to access invalid timeline task id in update
        """
        response = self.make_get_request(
            reverse(self.update_show_route_name, args=[0])
        )
        self.assertEqual(response.status_code, 500)


class TimelineTaskUpdateTest(BaseTestCase):
    """
    This class is responsible for testing the UPDATE feature in timeline module
    """

    update_edit_route_name = "timeline-task.edit"
    create_route_name = "timeline-task.create"

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
        timeline = baker.make("hubble.Timeline")
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "days": 2,
            "present_type": PRESENT_TYPE_REMOTE,
            "task_type": TASK_TYPE_TASK,
            "timeline_id": timeline.id,
        }
        task_timeline = baker.make(
            "hubble.TimelineTasK", timeline=timeline, order=1
        )
        self.timeline_task_id = task_timeline.id

    def validate_response(self, response, data):
        """
        To automate the assertion commands, where same logics are repeated
        """
        self.assertJSONEqual(
            self.decoded_json(response), {"status": "success"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "TimelineTask",
            {
                "name": data["name"],
                "days": data["days"],
                "present_type": data["present_type"],
                "task_type": data["task_type"],
                "timeline_id": data["timeline_id"],
            },
        )

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        # Valid scenario 1: Valid inputs for all fields
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name,
                args=[self.timeline_task_id],
            ),
            data=data,
        )
        self.validate_response(response, data)

        # Valid Scenario 2: Days can have decimal values, which satisfies the is_not_divisible_by_0.5 condition
        data = self.get_valid_inputs(
            {
                "days": 0.5,
                "present_type": PRESENT_TYPE_IN_PERSON,
                "task_type": TASK_TYPE_CULTURAL_MEET,
            }
        )
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name,
                args=[self.timeline_task_id],
            ),
            data=data,
        )
        self.validate_response(response, data)

        # Valid Scenario 3: Selecting Other options in Radio Select
        data = self.get_valid_inputs(
            {
                "days": 1.5,
                "present_type": PRESENT_TYPE_IN_PERSON,
                "task_type": TASK_TYPE_ASSESSMENT,
            }
        )
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name,
                args=[self.timeline_task_id],
            ),
            data=data,
        )
        self.validate_response(response, data)

    def test_minimum_length_validation(self):
        """
        To check what happens when name field fails MinlengthValidation
        """
        data = self.get_valid_inputs(
            {"name": self.faker.pystr(max_chars=2)}
        )
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name,
                args=[self.timeline_task_id],
            ),
            data=data,
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
        self.assertEqual(response.status_code, 200)

    def test_required_validation(self):
        """
        This function checks the required validation for the all the fields
        """
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name,
                args=[self.timeline_task_id],
            ),
            data={},
        )
        field_errors = {
            "name": {"required"},
            "days": {"required"},
            "present_type": {"required"},
            "task_type": {"required"},
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)

    def test_validate_days_validation(self):
        """
        This function checks the validate days validation for the days fields
        """
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name,
                args=[self.timeline_task_id],
            ),
            data=self.get_valid_inputs({"days": 0.25}),
        )
        field_errors = {"days": {"is_not_divisible_by_0.5"}}
        error_message = {
            "is_not_divisible_by_0.5": "Value must be a multiple of 0.5"
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=error_message,
            ),
        )
        self.assertEqual(response.status_code, 200)

        response = self.make_post_request(
            reverse(
                self.update_edit_route_name,
                args=[self.timeline_task_id],
            ),
            data=self.get_valid_inputs({"days": 0}),
        )
        field_errors = {"days": {"value_cannot_be_zero"}}
        error_message = {
            "value_cannot_be_zero": "Value must be greater than 0"
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=error_message,
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_choice_validations(self):
        """
        Check what happens when invalid data for team field is given as input
        """
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name,
                args=[self.timeline_task_id],
            ),
            data=self.get_valid_inputs(
                {
                    "present_type": self.faker.name(),
                    "task_type": self.faker.name(),
                }
            ),
        )
        field_errors = {
            "present_type": {"invalid_choice"},
            "task_type": {"invalid_choice"},
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)


class TimelineTaskDeleteTest(BaseTestCase):
    """
    This class is responsible for testing the DELETE feature in timeline module
    """

    delete_route_name = "timeline-task.delete"

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
        timelinetask = baker.make(
            "hubble.TimelineTasK",
            timeline=baker.make("hubble.Timeline"),
            order=1,
        )
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[timelinetask.id])
        )
        self.assertJSONEqual(
            response.content,
            {"message": "Timeline Template Task deleted successfully"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseNotHas(
            "TimelineTask", {"id": timelinetask.id}
        )

    def test_failure(self):
        """
        To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[0])
        )
        self.assertJSONEqual(
            response.content,
            {"message": "Error while deleting Timeline Template Task!"},
        )
        self.assertEqual(response.status_code, 500)


class TimelineTaskReOrderTest(BaseTestCase):
    """
    This class is responsible for testing the order of the tasks after changing the order in timeline task module
    """

    reorder_route_name = "timeline-task.reorder"

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
        self.timeline = baker.make("hubble.Timeline")
        baker.make(
            "hubble.TimelineTask",
            order=seq(0),
            timeline=self.timeline,
            _quantity=5,
        )
        self.timeline_task_ids = list(
            TimelineTask.objects.filter(
                timeline_id=self.timeline.id
            ).values_list("id", flat=True)
        )
        random.shuffle(self.timeline_task_ids)

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        self.timeline = baker.make("hubble.Timeline")
        baker.make(
            "hubble.TimelineTask",
            order=seq(0),
            timeline=self.timeline,
            _quantity=5,
        )
        self.timeline_task_ids = list(
            TimelineTask.objects.filter(
                timeline_id=self.timeline.id
            ).values_list("id", flat=True)
        )
        random.shuffle(self.timeline_task_ids)
        data = self.get_valid_inputs(
            {
                "data[]": self.timeline_task_ids,
                "timeline_id": self.timeline.id,
            }
        )
        response = self.make_post_request(
            reverse(self.reorder_route_name), data=data
        )
        self.assertJSONEqual(
            self.decoded_json(response), {"status": "success"}
        )
        self.assertEqual(response.status_code, 200)
        for order, task_id in enumerate(self.timeline_task_ids):
            self.assertDatabaseHas(
                "TimelineTask",
                {
                    "id": task_id,
                    "timeline_id": self.timeline.id,
                    "order": order + 1,
                },
            )

    def test_failure(self):
        """
        Check what happens when invalid timeline task ids are given as input
        """
        data = self.get_valid_inputs(
            {"data[]": [0] * 5, "timeline_id": self.timeline.id}
        )
        response = self.make_post_request(
            reverse(self.reorder_route_name), data=data
        )
        self.assertJSONEqual(
            response.content,
            {
                "message": "Some of the tasks doesn't belong to the current timeline",
                "status": "error",
            },
        )
        self.assertEqual(response.status_code, 200)


class TimelineTasksDatatableTest(BaseTestCase):
    """
    This class is responsible for testing the Datatables present in the Batch module
    """

    datatable_route_name = "timeline-task.datatable"
    route_name = "timeline-template.detail"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.timeline = baker.make("hubble.Timeline")

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(
            reverse(self.route_name, args=[self.timeline.id])
        )
        self.assertTemplateUsed(
            response, "timeline_template_detail.html"
        )
        self.assertContains(response, self.timeline.name)

    def test_datatable(self):
        """
        To check whether all columns are present in datatable and length of rows without any filter
        """
        timelinetasks = baker.make(
            "hubble.TimelineTasK",
            timeline_id=self.timeline.id,
            order=seq(0),
            days=2,
            _quantity=2,
        )

        payload = {
            "draw": 1,
            "start": 0,
            "length": 10,
            "timeline_id": self.timeline.id,
        }
        response = self.make_post_request(
            reverse(self.datatable_route_name), data=payload
        )
        self.assertEqual(response.status_code, 200)

        # Check whether row details are correct
        for row in range(len(timelinetasks)):
            expected_value = timelinetasks[row]
            received_value = response.json()["data"][row]
            self.assertEqual(
                expected_value.pk, int(received_value["pk"])
            )
            self.assertEqual(
                expected_value.name,
                received_value["name"].split(">")[1].split("<")[0],
            )
            self.assertEqual(
                expected_value.days, float(received_value["days"])
            )
            self.assertEqual(
                expected_value.present_type,
                received_value["present_type"],
            )
            self.assertEqual(
                expected_value.task_type, received_value["task_type"]
            )

        # Check whether all headers are present
        for row in response.json()["data"]:
            self.assertTrue("pk" in row)
            self.assertTrue("name" in row)
            self.assertTrue("days" in row)
            self.assertTrue("present_type" in row)
            self.assertTrue("task_type" in row)
            self.assertTrue("action" in row)

        # Check the numbers of rows received is equal to the number of expected rows
        self.assertTrue(
            response.json()["recordsTotal"], len(timelinetasks)
        )
