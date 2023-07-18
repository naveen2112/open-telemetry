from django.db.models import Count, FloatField, OuterRef, Q, Subquery, Sum
from django.db.models.functions import Coalesce
from django.forms.models import model_to_dict
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import seq

from core.base_test import BaseTestCase
from hubble.models import SubBatch, Timeline


class TimelineCreateTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in timeline module
    """

    route_name = "timeline-template"
    create_route_name = "timeline-template.create"
    update_edit_route_name = "timeline-template.edit"

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
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": self.create_team().id,
            "is_active": False,
        }
        self.timeline = baker.make(
            "hubble.Timeline",
            team_id=self.persisted_valid_inputs["team"],
        )
        baker.make(
            "hubble.TimelineTask",
            timeline_id=self.timeline.id,
            _fill_optional=["order"],
            _quantity=5,
        )

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name))
        self.assertTemplateUsed(response, "timeline_template.html")
        self.assertContains(response, "Timeline Template List")

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        # Valid scenario 1: Valid inputs for name and team fields and False for is_active field
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(self.create_route_name), data=data
        )
        self.assertJSONEqual(
            self.decoded_json(response), {"status": "success"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "Timeline",
            {
                "name": data["name"],
                "team_id": data["team"],
                "is_active": data["is_active"],
            },
        )

        # Valid scenario 2: Valid inputs for name and team fields and True for is_active field
        data = self.get_valid_inputs({"is_active": "true"})
        response = self.make_post_request(
            reverse(self.create_route_name), data=data
        )
        self.assertJSONEqual(
            self.decoded_json(response), {"status": "success"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "Timeline",
            {
                "name": data["name"],
                "team_id": data["team"],
                "is_active": data["is_active"].capitalize(),
            },
        )

        # Valid sceanrio 3: Valid inputs for all fields and is_active=False, along with duplicated timeline id
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"id": self.timeline.id}),
        )
        duplicated_timeline_id = Timeline.objects.order_by(
            "-id"
        ).first()
        self.assertJSONEqual(
            self.decoded_json(response), {"status": "success"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "Timeline", {"id": duplicated_timeline_id.id}
        )
        self.assertDatabaseCount(
            "TimelineTask", {"timeline": duplicated_timeline_id}, 5
        )

        # Valid sceanrio 4: Valid inputs for all fields and is_active=True, along with duplicated timeline id
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs(
                {
                    "id": self.timeline.id,
                    "is_active": "true",
                    "team": self.create_team().id,
                }
            ),
        )
        duplicated_timeline_id = Timeline.objects.order_by(
            "-id"
        ).first()
        self.assertJSONEqual(
            self.decoded_json(response), {"status": "success"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "Timeline", {"id": duplicated_timeline_id.id}
        )
        self.assertDatabaseCount(
            "TimelineTask", {"timeline": duplicated_timeline_id}, 5
        )

    def test_required_validation(self):
        """
        This function checks the required validation for the team and name fields
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"team": "", "name": ""}),
        )
        field_errors = {"name": {"required"}, "team": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )

    def test_minimum_length_failure(self):
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

    def test_invalid_template_id_validation(self):
        """
        What happens when the duplicated id is invalid
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"id": 0}),
        )
        field_errors = {"__all__": {""}}
        error_message = {
            "": "You are trying to duplicate invalid template"
        }
        non_field_errors = {
            "message": "You are trying to duplicate invalid template",
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

    def test_is_active_failure(self):
        """
        Check what happens when invalid data for is_active field is given as input
        """
        # What happens when is_active field is set True and the team selected currently already has a active teemplate
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name, args=[self.timeline.id]
            ),
            data=self.get_valid_inputs({"is_active": "true"}),
        )
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs(
                {"is_active": "true", "team": self.timeline.team_id}
            ),
        )
        field_errors = {"is_active": {"template_in_use"}}
        error_message = {
            "template_in_use": "Team already has an active template."
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=error_message,
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_choice_validation(self):
        """
        Check what happens when invalid data for team field is given as input
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"team": self.faker.name()}),
        )
        field_errors = {"team": {"invalid_choice"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)


class TimelineShowTest(BaseTestCase):
    """
    This class is responsible for testing the SHOW process in timeline module
    """

    update_show_route_name = "timeline-template.show"

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
        timeline = baker.make("hubble.Timeline")
        response = self.make_get_request(
            reverse(self.update_show_route_name, args=[timeline.id])
        )
        self.assertJSONEqual(
            self.decoded_json(response),
            {
                "timeline": model_to_dict(
                    Timeline.objects.get(id=timeline.id)
                )
            },
        )

    def test_failure(self):
        """
        Checks what happens when we try to access invalid arguments in update
        """
        response = self.make_get_request(
            reverse(self.update_show_route_name, args=[0])
        )
        self.assertEqual(response.status_code, 500)


class TimelineUpdateTest(BaseTestCase):
    """
    This class is responsible for testing the UPDATE feature in timeline module
    """

    update_edit_route_name = "timeline-template.edit"
    create_route_name = "timeline-template.create"

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
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": self.create_team().id,
            "is_active": False,
        }
        self.timeline = baker.make(
            "hubble.Timeline",
            team_id=self.persisted_valid_inputs["team"],
        )

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        # Valid scenario 1: Valid inputs for name and team fields and is_active=False
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name, args=[self.timeline.id]
            ),
            data=data,
        )
        self.assertJSONEqual(
            self.decoded_json(response), {"status": "success"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "Timeline",
            {
                "id": self.timeline.id,
                "name": data["name"],
                "team": data["team"],
                "is_active": data["is_active"],
            },
        )

        # Valid scenario 2: Valid inputs for name and team fields and is_active=True
        data = self.get_valid_inputs({"is_active": "true"})
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name, args=[self.timeline.id]
            ),
            data=data,
        )
        self.assertJSONEqual(
            self.decoded_json(response), {"status": "success"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "Timeline",
            {
                "id": self.timeline.id,
                "name": data["name"],
                "team": data["team"],
                "is_active": data["is_active"].capitalize(),
            },
        )

    def teat_required_validation(self):
        """
        This function checks the required field validations
        """
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name, args=[self.timeline.id]
            ),
            data=self.get_valid_inputs({"name": "", "team": ""}),
        )
        field_errors = {"name": {"required"}, "team": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_choice_validation(self):
        """
        Check what happens when invalid choice for the respective field is given as input
        """
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name, args=[self.timeline.id]
            ),
            data=self.get_valid_inputs({"team": self.faker.name()}),
        )
        field_errors = {"team": {"invalid_choice"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)

    def test_minimum_length_failure(self):
        """
        Check what happens when a field doesn't meet the limit value of MinlengthValidator
        """
        data = self.get_valid_inputs(
            {"name": self.faker.pystr(max_chars=2)}
        )
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name, args=[self.timeline.id]
            ),
            data=data,
        )
        field_errors = {"name": {"min_length"}}
        validation_paramters = {"name": 3}
        self.assertJSONEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                current_value=data,
                validation_parameter=validation_paramters,
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_is_active_failure(self):
        """
        Check what happens when invalid data for is_active field is given as input
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs(
                {"team": self.timeline.team_id, "is_active": "true"}
            ),
        )
        response = self.make_post_request(
            reverse(
                self.update_edit_route_name, args=[self.timeline.id]
            ),
            data=self.get_valid_inputs({"is_active": "true"}),
        )
        field_errors = {"is_active": {"template_in_use"}}
        custom_error = {
            "template_in_use": "Team already has an active template."
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=custom_error,
            ),
        )
        self.assertEqual(response.status_code, 200)


class TimelineDeleteTest(BaseTestCase):
    """
    This class is responsible for testing the DELETE feature in timeline module
    """

    delete_route_name = "timeline-template.delete"

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
        timeline = baker.make("hubble.Timeline")
        self.assertDatabaseHas("Timeline", {"id": timeline.id})
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[timeline.id])
        )
        self.assertJSONEqual(
            response.content,
            {"message": "Timeline Template deleted successfully"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseNotHas("Timeline", {"id": timeline.id})

    def test_failure(self):
        """
        To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[0])
        )
        self.assertJSONEqual(
            response.content,
            {"message": "Error while deleting Timeline Template!"},
        )
        self.assertEqual(response.status_code, 500)


class TimelineDatatableTest(BaseTestCase):
    """
    This class is responsible for testing the Datatables present in the Batch module
    """

    datatable_route_name = "timeline-template.datatable"
    route_name = "timeline-template"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name))
        self.assertTemplateUsed(response, "timeline_template.html")
        self.assertContains(response, "Timeline Template List")

    def test_datatable(self):
        """
        To check whether all columns are present in datatable and length of rows without any filter
        """
        name = self.faker.name()
        baker.make("hubble.Timeline", name=seq(name))
        no_of_sub_batches_subquery = (
            SubBatch.objects
            .filter(timeline_id=OuterRef('id'), deleted_at__isnull=True)
            .values('timeline')
            .annotate(no_of_sub_batches=Count('id', distinct=True))
            .values('no_of_sub_batches')
        )
        timeline = (
            Timeline.objects
            .filter(deleted_at__isnull=True)
            .annotate(
                Days=Coalesce(Sum('task_timeline__days', filter=Q(task_timeline__deleted_at__isnull=True)), 0, output_field=FloatField()),
                no_of_sub_batches=Coalesce(Subquery(no_of_sub_batches_subquery), 0)
            )
        )

        payload = {
            "draw": 1,
            "start": 0,
            "length": 10,
        }
        response = self.make_post_request(
            reverse(self.datatable_route_name), data=payload
        )
        self.assertEqual(response.status_code, 200)

        # Check whether row details are correct
        for row in range(len(timeline)):
            expected_value = timeline[row]
            received_value = response.json()["data"][row]
            self.assertEqual(
                expected_value.pk, int(received_value["pk"])
            )
            self.assertEqual(
                expected_value.name, received_value["name"]
            )
            if (
                received_value["is_active"].split(">")[1].split("<")[0]
                == "In Active"
            ):
                self.assertEqual(expected_value.is_active, False)
            else:
                self.assertEqual(expected_value.is_active, True)
            self.assertEqual(
                expected_value.team.name, received_value["team"]
            )
            self.assertEqual(
                expected_value.sub_batches.count(), int(received_value["no_of_sub_batches"])
            )

        # Check whether all headers are present
        for row in response.json()["data"]:
            self.assertTrue("pk" in row)
            self.assertTrue("name" in row)
            self.assertTrue("is_active" in row)
            self.assertTrue("team" in row)
            self.assertTrue("no_of_sub_batches" in row)
            self.assertTrue("action" in row)

        # Check the numbers of rows received is equal to the number of expected rows
        self.assertTrue(response.json()["recordsTotal"], len(timeline))
