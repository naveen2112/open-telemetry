from django.forms.models import model_to_dict
from django.urls import reverse
from model_bakery import baker

from hubble.models import Timeline
from training.tests.base import BaseTestCase


class TimelineCreate(BaseTestCase):
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
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": self.create_team().id,
            "is_active": False,
        }
        create_timeline = baker.make(
            "hubble.Timeline", team_id=self.persisted_valid_inputs["team"]
        )
        baker.make(
            "hubble.TimelineTask",
            timeline_id=create_timeline.id,
            _fill_optional=["order"],
            _quantity=5,
        )
        self.timeline_id = create_timeline.id
        self.team_id = create_timeline.team_id

    def test_templates(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name))
        self.assertTemplateUsed(response, "timeline_template.html")
        self.assertContains(response, "Timeline Template List")

    def test_success_scenarios(self):
        """
        Check what happens when valid data is given as input
        """
        # Valid scenario 1: Valid inputs for name and team fields and False for is_active field
        data = self.get_valid_inputs()
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
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
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseHas(
            "Timeline",
            {
                "name": data["name"],
                "team_id": data["team"],
                "is_active": data["is_active"].capitalize(),
            },
        )

        # Valid sceanrio 3: Valid inputs for all fields and is_active=False, along with duplicated timeline id
        data = self.get_valid_inputs({"id": self.timeline_id})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        duplicated_timeline_id = Timeline.objects.order_by("-id").first()
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseHas(
            "Timeline",
            {
                "name": data["name"],
                "team_id": data["team"],
                "is_active": data["is_active"],
            },
        )
        self.assertDatabaseCount(
            "TimelineTask", {"timeline": duplicated_timeline_id}, 5
        )

        # Valid sceanrio 3: Valid inputs for all fields and is_active=True, along with duplicated timeline id
        data = self.get_valid_inputs(
            {"id": self.timeline_id, "is_active": "true", "team": self.create_team().id}
        )
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        duplicated_timeline_id = Timeline.objects.order_by("-id").first()
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseHas(
            "Timeline",
            {
                "name": data["name"],
                "team_id": data["team"],
                "is_active": data["is_active"].capitalize(),
            },
        )
        self.assertDatabaseCount(
            "TimelineTask", {"timeline": duplicated_timeline_id}, 5
        )

    def test_required_validation_scenario(self):
        """
        This function checks the required validation for the team and name fields
        """
        data = self.get_valid_inputs({"is_active": "true", "team": "", "name": ""})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"name": {"required"}, "team": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )

    def test_multiple_invalid_input_scenario(self):
        """
        Check what happens when multiple invalid inputs are given at once
        """
        # What happens when name fails MinValidator and team is empty
        data = self.get_valid_inputs(
            {
                "name": self.faker.pystr(min_chars=1, max_chars=1),
                "team": "",
                "is_active": "true",
            }
        )
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"name": {"min_length"}, "team": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors, current_value=data, validation_parameter=3
            ),
        )

        # What happens when the duplicated id is invalid
        data = self.get_valid_inputs({"id": 99})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"__all__": {""}}
        error_message = {"": "You are trying to duplicate invalid template"}
        non_field_errors = {
            "message": "You are trying to duplicate invalid template",
            "code": "",
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                non_field_errors=non_field_errors,
                current_value=data,
                custom_validation_error_message=error_message,
            ),
        )

    def test_is_active_failure_scenarios(self):
        """
        Check what happens when invalid data for is_active field is given as input
        """
        # What happens when is_active field is set True and the team selected currently already has a active teemplate
        data = self.get_valid_inputs({"is_active": "true"})
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.timeline_id]), data=data
        )
        data = self.get_valid_inputs({"is_active": "true", "team": self.team_id})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"is_active": {"template_in_use"}}
        error_message = {"template_in_use": "Team already has an active template."}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                current_value=data,
                custom_validation_error_message=error_message,
            ),
        )
        self.assertTrue(response.status_code, 200)

    def test_team_failure_scenarios(self):
        """
        Check what happens when invalid data for team field is given as input
        """
        # Invalid scenario 1: What happens when team field is left empty
        data = self.get_valid_inputs({"team": ""})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"team": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)

        # Invalid scenario 2: What happens when invalid choice is selected for team
        data = self.get_valid_inputs({"team": self.faker.name()})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"team": {"invalid_choice"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)

    def test_name_failure_scenarios(self):
        """
        Check what happens when invalid data for name field is given as input
        """
        # Invalid scenario 1: What happens when name field is left empty
        data = self.get_valid_inputs({"name": ""})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"name": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)

        # Invalid scenario 2: What happens when name field fails MinlengthValidation
        data = self.get_valid_inputs({"name": self.faker.pystr(max_chars=2)})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"name": {"min_length"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors, current_value=data, validation_parameter=3
            ),
        )
        self.assertTrue(response.status_code, 200)


class TimelineUpdateShow(BaseTestCase):
    update_show_route_name = "timeline-template.show"
    create_route_name = "timeline-template.create"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.update_valid_input()

    def update_valid_input(self):
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": self.create_team().id,
            "is_active": False,
        }
        create_timeline = baker.make(
            "hubble.Timeline", team_id=self.persisted_valid_inputs["team"]
        )
        self.timeline_id = create_timeline.id
        self.team_id = create_timeline.team_id

    def test_success_scenarios_show(self):
        """
        Checks what happens when valid inputs are given for all fields
        """
        response = self.make_get_request(
            reverse(self.update_show_route_name, args=[self.timeline_id])
        )
        self.assertJSONEqual(
            self.decoded_json(response),
            {"timeline": model_to_dict(Timeline.objects.get(id=self.timeline_id))},
        )

    def test_failure_scenario_show(self):
        """
        Checks what happens when we try to access invalid arguments in update
        """
        response = self.make_get_request(reverse(self.update_show_route_name, args=[9]))
        self.assertEqual(response.status_code, 500)


class TimelineUpdateEdit(BaseTestCase):
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
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": self.create_team().id,
            "is_active": False,
        }
        create_timeline = baker.make(
            "hubble.Timeline", team_id=self.persisted_valid_inputs["team"]
        )
        self.timeline_id = create_timeline.id
        self.team_id = create_timeline.team_id

    def test_success_scenarios_edit(self):
        """
        Check what happens when valid data is given as input
        """
        # Valid scenario 1: Valid inputs for name and team fields and is_active=False
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.timeline_id]), data=data
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseHas(
            "Timeline",
            {
                "name": data["name"],
                "team_id": data["team"],
                "is_active": data["is_active"],
            },
        )

        # Valid scenario 2: Valid inputs for name and team fields and is_active=True
        data = self.get_valid_inputs({"is_active": "true"})
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.timeline_id]), data=data
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseHas(
            "Timeline",
            {
                "name": data["name"],
                "team_id": data["team"],
                "is_active": data["is_active"].capitalize(),
            },
        )

    def test_is_active_failure_scenarios(self):
        """
        Check what happens when invalid data for is_active field is given as input
        """
        data = self.get_valid_inputs({"team": self.team_id, "is_active": "true"})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        data = self.get_valid_inputs({"is_active": "true"})
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.timeline_id]), data=data
        )
        field_errors = {"is_active": {"template_in_use"}}
        custom_error = {"template_in_use": "Team already has an active template."}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                current_value=data,
                custom_validation_error_message=custom_error,
            ),
        )
        self.assertTrue(response.status_code, 200)

    def test_team_failure_scenarios(self):
        """
        Check what happens when invalid data for team field is given as input
        """
        # Invalid scenario 1: What happens when team field is left empty
        data = self.get_valid_inputs({"team": ""})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"team": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)

        # Invalid scenario 2: What happens when invalid choice is selected for team
        data = self.get_valid_inputs({"team": self.faker.name()})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"team": {"invalid_choice"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)

    def test_name_failure_scenarios(self):
        """
        Check what happens when invalid data for name field is given as input
        """
        # Invalid scenario 1: What happens when name field is left empty
        data = self.get_valid_inputs({"name": ""})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"name": {"required"}}
        self.assertJSONEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)

        # Invalid scenario 2: What happens when name field fails MinlengthValidation
        data = self.get_valid_inputs({"name": self.faker.pystr(max_chars=2)})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"name": {"min_length"}}
        self.assertJSONEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors, current_value=data, validation_parameter=3
            ),
        )
        self.assertTrue(response.status_code, 200)


class TimelineDelete(BaseTestCase):
    delete_route_name = "timeline-template.delete"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.update_valid_inputs()

    def update_valid_inputs(self):
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": self.create_team().id,
            "is_active": False,
        }
        create_timeline = baker.make(
            "hubble.Timeline",
            name=self.persisted_valid_inputs["name"],
            team_id=self.persisted_valid_inputs["team"],
        )
        self.timeline_id = create_timeline.id

    def test_success_scenarios(self):
        """
        To check what happens when valid id is given for delete
        """
        self.assertDatabaseHas(
            "Timeline",
            {
                "name": self.persisted_valid_inputs["name"],
                "team_id": self.persisted_valid_inputs["team"],
                "is_active": self.persisted_valid_inputs["is_active"],
            },
        )
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[self.timeline_id])
        )
        self.assertJSONEqual(
            response.content, {"message": "Timeline Template deleted succcessfully"}
        )
        self.assertTrue(response.status_code, 200)
        self.assertDatabaseNotHas(
            "Timeline",
            {
                "name": self.persisted_valid_inputs["name"],
                "team_id": self.persisted_valid_inputs["team"],
                "is_active": self.persisted_valid_inputs["is_active"],
            },
        )

    def test_failure_scenarios(self):
        """
        To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(reverse(self.delete_route_name, args=[99]))
        self.assertJSONEqual(
            response.content, {"message": "Error while deleting Timeline Template!"}
        )
        self.assertTrue(response.status_code, 200)
