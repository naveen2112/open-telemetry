import json

from model_bakery import baker

from hubble.models import Team, Timeline, User
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
        # self.maxDiff = None
    
    def update_valid_input(self):
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": baker.make("hubble.Team").id,
            "is_active": False,
        }
        create_timeline = baker.make(
            "hubble.Timeline", team_id=self.persisted_valid_inputs["team"]
        )
        self.timeline_id = create_timeline.id
        self.team_id = create_timeline.team_id

    def test_templates(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(self.route_name)
        self.assertTemplateUsed(response, "timeline_template.html")
        # TODO :: Add wordings check like Timeline Template

    def test_success_scenarios(self):
        """
        Check what happens when valid data is given as input
        """
        #Valid scenario 1: Valid inputs for name and team fields and False for is_active field 
        data = self.get_valid_inputs()
        response = self.make_post_request(self.create_route_name, data=data)
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

        #Valid scenario 2: Valid inputs for name and team fields and True for is_active field 
        data = self.get_valid_inputs({"is_active": "true"})
        response = self.make_post_request(self.create_route_name, data=data)
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

        # Scenario Duplicate invalid id, Success duplicate check timeline and timeline_task, Active and inactive duplicated template

    def test_all_failure_scenario(self):
        """
        Check what happens when multiple invalid inputs are given at once
        """
        #What happens when name fails MinValidator and team is empty
        data = self.get_valid_inputs(
            {
                "name": self.faker.pystr(min_chars=1, max_chars=1),
                "team": "",
                "is_active": "true",
            }
        )
        response = self.make_post_request(self.create_route_name, data=data)
        field_errors = {"name": {"min_length"}, "team": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )

        #What happens when 
        data = self.get_valid_inputs({"is_active": "true", "team": "", "name": ""})
        response = self.make_post_request(self.create_route_name, data=data)
        field_errors = {"name": {"required"}, "team": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )

    def test_is_active_failure_scenarios(self):
        """
        Check what happens when invalid data for is_active field is given as input
        """
        #Invalid scenario 1: What happens when is_active field is set True and the team selected currently already has a active teemplate
        data = self.get_valid_inputs({"is_active": "true"})
        response = self.make_post_request_with_argument(
            self.update_edit_route_name, self.timeline_id, data=data
        )
        data = self.get_valid_inputs({"is_active": "true", "team": self.team_id})
        response = self.make_post_request(self.create_route_name, data=data)
        field_errors = {"is_active": {""}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)

    def test_team_failure_scenarios(self):
        """
        Check what happens when invalid data for team field is given as input
        """
        #Invalid scenario 1: What happens when team field is left empty
        data = self.get_valid_inputs({"team": ""})
        response = self.make_post_request(self.create_route_name, data=data)
        field_errors = {"team": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)

        #Invalid scenario 2: What happens when invalid choice is selected for team
        data = self.get_valid_inputs({"team": self.faker.name()})
        response = self.make_post_request(self.create_route_name, data=data)
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
        data = self.get_valid_inputs({"name": ""})
        response = self.make_post_request(self.create_route_name, data=data)
        field_errors = {"name": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)
        data = self.get_valid_inputs({"name": self.faker.pystr(max_chars=2)})
        response = self.make_post_request(self.create_route_name, data=data)
        field_errors = {"name": {"min_length"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)


class TimelineUpdate(BaseTestCase):
    update_show_route_name = "timeline-template.show"
    update_edit_route_name = "timeline-template.edit"
    create_route_name = "timeline-template.create"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
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
        response = self.make_get_request_with_argument(
            self.update_show_route_name, self.timeline_id
        )
        self.assertEqual(
            response.json()["timeline"]["id"], self.timeline_id
        )  # TODO :: Need new method?

    def test_failure_scenario_show(self):
        """
        Checks what happens when we try to access invalid arguments in update
        """
        response = self.make_get_request_with_argument(self.update_show_route_name, 9)
        self.assertEqual(response.status_code, 500)

    def test_success_scenarios_edit(self):
        """
        Check what happens when valid data is given as input
        """
        data = self.get_valid_inputs()
        response = self.make_post_request_with_argument(
            self.update_edit_route_name, self.timeline_id, data=data
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

        data = self.get_valid_inputs({"is_active": "true"})
        response = self.make_post_request_with_argument(
            self.update_edit_route_name, self.timeline_id, data=data
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
        response = self.make_post_request(self.create_route_name, data=data)
        data = self.get_valid_inputs({"is_active": "true"})
        response = self.make_post_request_with_argument(
            self.update_edit_route_name, self.timeline_id, data=data
        )
        field_errors = {"is_active": {""}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)

    def test_team_failure_scenarios(self):
        """
        Check what happens when invalid data for team field is given as input
        """
        data = self.get_valid_inputs({"team": ""})
        response = self.make_post_request(self.create_route_name, data=data)
        field_errors = {"team": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)
        data = self.get_valid_inputs({"team": self.faker.name()})
        response = self.make_post_request(self.create_route_name, data=data)
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
        data = self.get_valid_inputs({"name": ""})
        response = self.make_post_request(self.create_route_name, data=data)
        field_errors = {"name": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)
        data = self.get_valid_inputs({"name": self.faker.pystr(max_chars=2)})
        response = self.make_post_request(self.create_route_name, data=data)
        field_errors = {"name": {"min_length"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)


class TimelineDelete(BaseTestCase):
    delete_route_name = "timeline-template.delete"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
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
        response = self.make_delete_request(self.delete_route_name, self.timeline_id)
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
        response = self.make_delete_request(self.delete_route_name, 99)
        self.assertJSONEqual(
            response.content, {"message": "Error while deleting Timeline Template!"}
        )
        self.assertTrue(response.status_code, 200)


class TimelineDuplicate(BaseTestCase):
    duplicate_route_name = "timeline-template.create"
    update_edit_route_name = "timeline-template.edit"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
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
        Check what happens when valid data is given as input
        """
        data = self.get_valid_inputs(
            {"name": self.faker.name(), "id": self.timeline_id}
        )
        response = self.make_post_request(self.duplicate_route_name, data=data)
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code)
        self.assertDatabaseHas(
            "Timeline",
            {
                "name": data["name"],
                "team_id": data["team"],
                "is_active": data["is_active"],
            },
        )

        data = self.get_valid_inputs(
            {"name": self.faker.name(), "id": self.timeline_id, "is_active": "true"}
        )
        response = self.make_post_request(self.duplicate_route_name, data=data)
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertTrue(response.status_code)
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
        data = self.get_valid_inputs({"is_active": "true"})
        response = self.make_post_request_with_argument(
            self.update_edit_route_name, self.timeline_id, data=data
        )
        data = self.get_valid_inputs({"is_active": "true", "id": self.timeline_id})
        response = self.make_post_request(self.duplicate_route_name, data=data)
        field_errors = {"is_active": {""}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)

    def test_team_failure_scenarios(self):
        """
        Check what happens when invalid data for team field is given as input
        """
        data = self.get_valid_inputs({"team": ""})
        response = self.make_post_request(self.duplicate_route_name, data=data)
        field_errors = {"team": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)
        data = self.get_valid_inputs({"team": self.faker.name()})
        response = self.make_post_request(self.duplicate_route_name, data=data)
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
        data = self.get_valid_inputs({"name": ""})
        response = self.make_post_request(self.duplicate_route_name, data=data)
        field_errors = {"name": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)
        data = self.get_valid_inputs({"name": self.faker.pystr(max_chars=2)})
        response = self.make_post_request(self.duplicate_route_name, data=data)
        field_errors = {"name": {"min_length"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors, current_value=data),
        )
        self.assertTrue(response.status_code, 200)
