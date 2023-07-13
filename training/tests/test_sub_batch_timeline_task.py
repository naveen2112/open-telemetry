"""
Django test cases for create, update and ordering the Sub batch task
"""
import random

from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import seq

from core.base_test import BaseTestCase
from core.constants import (PRESENT_TYPE_IN_PERSON, PRESENT_TYPE_REMOTE,
                            TASK_TYPE_ASSESSMENT, TASK_TYPE_CULTURAL_MEET,
                            TASK_TYPE_TASK)
from hubble.models import SubBatchTaskTimeline


class SubBatchTimelineTaskCreateTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in timeline task module
    """

    create_route_name = "sub_batch.timeline.create"
    route_name = "sub-batch.timeline"

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
        self.sub_batch = baker.make("hubble.SubBatch", start_date=timezone.now().date())
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "days": 2,
            "present_type": PRESENT_TYPE_REMOTE,
            "task_type": TASK_TYPE_TASK,
            "order": 1,
            "sub_batch_id": self.sub_batch.id,
        }

    def validate_response(self, response, data):
        """
        To automate the assertion commands, where same logic is repeated
        """
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_has(
            "SubBatchTaskTimeline",
            {
                "name": data["name"],
                "days": data["days"],
                "present_type": data["present_type"],
                "task_type": data["task_type"],
                "order": data["order"],
            },
        )

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name, args=[self.sub_batch.id]))
        self.assertTemplateUsed(response, "sub_batch/timeline.html")
        self.assertContains(response, self.sub_batch.name)

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.sub_batch.id]),
            data=data,
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
            reverse(self.create_route_name, args=[self.sub_batch.id]),
            data=data,
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
            reverse(self.create_route_name, args=[self.sub_batch.id]),
            data=data,
        )
        self.validate_response(response, data)

    def test_minimum_length_validation(self):
        """
        To check what happens when name field fails MinlengthValidation
        """
        data = self.get_valid_inputs({"name": self.faker.pystr(max_chars=2)})
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.sub_batch.id]),
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
            reverse(self.create_route_name, args=[self.sub_batch.id]),
            data={},
        )
        field_errors = {
            "name": {"required"},
            "days": {"required"},
            "present_type": {"required"},
            "task_type": {"required"},
            "order": {"required"},
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
            reverse(self.create_route_name, args=[self.sub_batch.id]),
            data=self.get_valid_inputs({"days": 0.25}),
        )
        field_errors = {"days": {"is_not_divisible_by_0.5"}}
        error_message = {"is_not_divisible_by_0.5": "Value must be a multiple of 0.5"}
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
            reverse(self.create_route_name, args=[self.sub_batch.id]),
            data=self.get_valid_inputs({"days": 0}),
        )
        field_errors = {"days": {"value_cannot_be_zero"}}
        error_message = {"value_cannot_be_zero": "Value must be greater than 0"}
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
        Check what happens when invalid data for present_type and
        task_type are given as input
        """
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.sub_batch.id]),
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

    def test_invalid_order_validation(self):
        """
        Check what happens when invalid order is given
        """
        # Check for zero_order_error
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.sub_batch.id]),
            data=self.get_valid_inputs({"order": 0}),
        )
        field_errors = {"order": {"zero_order_error"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)

        # check when there is gap between order input and the largest order in db
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.sub_batch.id]),
            data=self.get_valid_inputs({"order": 999}),
        )
        field_errors = {
            "order": {"invalid_order"},
        }
        validation_parameters = {
            "order": [
                SubBatchTaskTimeline.objects.filter(sub_batch_id=self.sub_batch.id)
                .values_list("order", flat=True)
                .last()
            ][0]
            or 0 + 1
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                validation_parameter=validation_parameters,
            ),
        )
        self.assertEqual(response.status_code, 200)


class SubBatchTaskTimelineShowTest(BaseTestCase):
    """
    This class is responsible for testing the SHOW process in timeline module
    """

    update_show_route_name = "sub_batch.timeline.show"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_success_show(self):
        """
        Checks what happens when valid inputs are given for all fields
        """
        sub_batch_task_timeline = baker.make("hubble.SubBatchTaskTimeline", order=1)
        response = self.make_get_request(
            reverse(
                self.update_show_route_name,
                args=[sub_batch_task_timeline.id],
            )
        )
        self.assertJSONEqual(
            self.decoded_json(response),
            {
                "timeline": model_to_dict(
                    SubBatchTaskTimeline.objects.get(id=sub_batch_task_timeline.id)
                )
            },
        )

    def test_failure_show(self):
        """
        Checks what happens when we try to access invalid timeline task id in update
        """
        response = self.make_get_request(reverse(self.update_show_route_name, args=[0]))
        self.assertEqual(response.status_code, 404)


class SubBatchTaskTimelineUpdateTest(BaseTestCase):
    """
    This class is responsible for testing the UPDATE feature in timeline module
    """

    update_edit_route_name = "sub_batch.timeline.edit"

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
        self.sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)).date(),
        )
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "days": 2,
            "present_type": PRESENT_TYPE_REMOTE,
            "task_type": TASK_TYPE_TASK,
            "order": 1,
        }
        sub_batch_task_timeline = baker.make(
            "hubble.SubBatchTaskTimeline",
            order=1,
            start_date=(timezone.now() + timezone.timedelta(1)).date(),
        )
        self.sub_batch_task_timeline_id = sub_batch_task_timeline.id

    def validate_response(self, response, data):
        """
        To automate the assertion commands, where same logic is repeated
        """
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_has(
            "SubBatchTaskTimeline",
            {
                "name": data["name"],
                "days": data["days"],
                "present_type": data["present_type"],
                "task_type": data["task_type"],
                "order": data["order"],
            },
        )

    def test_success_edit(self):
        """
        Check what happens when valid data is given as input
        """
        # Valid scenario 1: Valid inputs for all fields
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name,
                args=[self.sub_batch_task_timeline_id],
            ),
            data=data,
        )
        self.validate_response(response, data)

        # Valid Scenario 2: Days can have decimal values, which satisfies the
        # is_not_divisible_by_0.5 condition
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
                args=[self.sub_batch_task_timeline_id],
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
                args=[self.sub_batch_task_timeline_id],
            ),
            data=data,
        )
        self.validate_response(response, data)

    def test_minimum_length_validation(self):
        """
        To check what happens when name field fails MinlengthValidation
        """
        data = self.get_valid_inputs({"name": self.faker.pystr(max_chars=2)})
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name,
                args=[self.sub_batch_task_timeline_id],
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
                args=[self.sub_batch_task_timeline_id],
            ),
            data={},
        )
        field_errors = {
            "name": {"required"},
            "days": {"required"},
            "present_type": {"required"},
            "task_type": {"required"},
            "order": {"required"},
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
                args=[self.sub_batch_task_timeline_id],
            ),
            data=self.get_valid_inputs({"days": 0.25}),
        )
        field_errors = {"days": {"is_not_divisible_by_0.5"}}
        error_message = {"is_not_divisible_by_0.5": "Value must be a multiple of 0.5"}
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
                args=[self.sub_batch_task_timeline_id],
            ),
            data=self.get_valid_inputs({"days": 0}),
        )
        field_errors = {"days": {"value_cannot_be_zero"}}
        error_message = {"value_cannot_be_zero": "Value must be greater than 0"}
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
                args=[self.sub_batch_task_timeline_id],
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


class SubBatchTaskTimelineDeleteTest(BaseTestCase):
    """
    This class is responsible for testing the DELETE feature in timeline module
    """

    delete_route_name = "sub_batch.timeline.delete"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.sub_batch = baker.make(
            "hubble.SubBatch",
            start_date=(timezone.now() + timezone.timedelta(1)).date(),
        )

    def test_success(self):
        """
        To check what happens when valid id is given for delete
        """
        sub_batch_task_timeline = baker.make(
            "hubble.SubBatchTaskTimeline",
            sub_batch=self.sub_batch,
            order=seq(0),
            days=1,
            start_date=(timezone.now() + timezone.timedelta()).date(),
            _quantity=2,
        )
        self.assert_database_has(
            "SubBatchTaskTimeline",
            {"id": sub_batch_task_timeline[0].id},
        )
        response = self.make_delete_request(
            reverse(
                self.delete_route_name,
                args=[sub_batch_task_timeline[0].id],
            )
        )
        self.assertJSONEqual(
            self.decoded_json(response),
            {"message": "Task deleted succcessfully"},
        )
        self.assertEqual(response.status_code, 200)
        self.assert_database_not_has(
            "SubBatchTaskTimeline",
            {"id": sub_batch_task_timeline[0].id},
        )

    def test_deleting_last_task(self):
        """
        Check what happens when we try to delete the last task in timeline
        """
        sub_batch_task_timeline = baker.make(
            "hubble.SubBatchTaskTimeline",
            sub_batch=self.sub_batch,
            order=1,
            days=1,
            start_date=(timezone.now() + timezone.timedelta()).date(),
        )
        self.assert_database_has("SubBatchTaskTimeline", {"id": sub_batch_task_timeline.id})
        response = self.make_delete_request(
            reverse(
                self.delete_route_name,
                args=[sub_batch_task_timeline.id],
            )
        )
        self.assertJSONEqual(
            self.decoded_json(response),
            {"message": "This is the last task, Atleast one task should exist in the timeline"},
        )
        self.assertEqual(response.status_code, 500)

    def test_failure(self):
        """
        To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(reverse(self.delete_route_name, args=[0]))
        self.assertJSONEqual(
            response.content,
            {"message": "Error while deleting Task!"},
        )
        self.assertEqual(response.status_code, 500)


class SubBatchTaskTimelineReOrderTest(BaseTestCase):
    """
    This class is responsible for testing the order of the tasks after changing the
    order in timeline task module
    """

    reorder_route_name = "sub_batch.timeline.reorder"

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
        self.sub_batch = baker.make("hubble.SubBatch")
        baker.make(
            "hubble.SubBatchTaskTimeline",
            order=seq(0),
            days=1,
            sub_batch=self.sub_batch,
            _quantity=5,
        )
        self.sub_batch_task_timeline_ids = list(
            SubBatchTaskTimeline.objects.filter(sub_batch_id=self.sub_batch.id).values_list(
                "id", flat=True
            )
        )
        random.shuffle(self.sub_batch_task_timeline_ids)

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        response = self.make_post_request(
            reverse(self.reorder_route_name),
            data=self.get_valid_inputs(
                {
                    "data[]": self.sub_batch_task_timeline_ids,
                    "sub_batch_id": self.sub_batch.id,
                }
            ),
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        for order, task_id in enumerate(self.sub_batch_task_timeline_ids):
            self.assert_database_has(
                "SubBatchTaskTimeline",
                {
                    "id": task_id,
                    "sub_batch_id": self.sub_batch.id,
                    "order": order + 1,
                },
            )

    def test_failure(self):
        """
        Check what happens when invalid timeline task ids are given as input
        """
        data = self.get_valid_inputs({"data[]": [0] * 5, "sub_batch_id": self.sub_batch.id})
        response = self.make_post_request(reverse(self.reorder_route_name), data=data)
        self.assertJSONEqual(
            response.content,
            {
                "message": "Some of the tasks doesn't belong to the current timeline",
                "status": "error",
            },
        )
        self.assertEqual(response.status_code, 200)


class SubBatchTimelineDatatableTest(BaseTestCase):
    """
    This class is responsible for testing the Datatables present in the Batch module
    """

    datatable_route_name = "sub-batch.datatable"
    route_name = "sub-batch.timeline"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.sub_batch = baker.make("hubble.SubBatch", start_date=timezone.now().date())

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name, args=[self.sub_batch.id]))
        self.assertTemplateUsed(response, "sub_batch/timeline.html")
        self.assertContains(response, self.sub_batch.name)

    def test_datatable(self):
        """
        To check whether all columns are present in datatable and length of
        rows without any filter
        """
        sub_batch_task_timeline = baker.make(
            "hubble.SubBatchTaskTimeline",
            sub_batch=self.sub_batch,
            order=seq(0),
            days=1,
            start_date=(timezone.now() + timezone.timedelta(1)).date(),
            end_date=(timezone.now() + timezone.timedelta(2)).date(),
            _quantity=2,
        )
        payload = {
            "draw": 1,
            "start": 0,
            "length": 10,
            "sub_batch_id": self.sub_batch.id,
        }
        response = self.make_post_request(reverse(self.datatable_route_name), data=payload)
        self.assertEqual(response.status_code, 200)

        # Check whether row details are correct
        for index, expected_value in enumerate(sub_batch_task_timeline):
            received_value = response.json()["data"][index]
            self.assertEqual(expected_value.pk, int(received_value["pk"]))
            self.assertEqual(
                expected_value.order,
                int(float(received_value["order"].split(">")[1].split("<")[0])),
            )
            self.assertEqual(expected_value.name, received_value["name"])
            self.assertEqual(expected_value.days, float(received_value["days"]))
            self.assertEqual(
                expected_value.present_type,
                received_value["present_type"],
            )
            self.assertEqual(expected_value.task_type, received_value["task_type"])
            self.assertEqual(
                expected_value.start_date.strftime("%d %b %Y"),
                received_value["start_date"],
            )
            self.assertEqual(
                expected_value.end_date.strftime("%d %b %Y"),
                received_value["end_date"],
            )

        # Check whether all headers are present
        for row in response.json()["data"]:
            self.assertTrue("pk" in row)
            self.assertTrue("order" in row)
            self.assertTrue("name" in row)
            self.assertTrue("days" in row)
            self.assertTrue("present_type" in row)
            self.assertTrue("task_type" in row)
            self.assertTrue("start_date" in row)
            self.assertTrue("end_date" in row)

        # Check the numbers of rows received is equal to the number of expected rows
        self.assertTrue(
            response.json()["recordsTotal"],
            len(sub_batch_task_timeline),
        )
