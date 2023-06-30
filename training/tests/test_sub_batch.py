from django.conf import settings
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import seq

from core.base_test import BaseTestCase
from hubble.models import SubBatch, User
from training.forms import SubBatchForm
import json
from django.utils.html import strip_tags


class SubBatchCreateTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in batch module
    """

    create_route_name = "sub-batch.create"
    route_name = "batch.detail"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.update_valid_input()

    def update_valid_input(self):
        self.batch_id = baker.make("hubble.Batch").id
        baker.make(
            "hubble.User",
            is_employed=True,
            _fill_optional=["email"],
            employee_id=seq(0),
            _quantity=5,
        )
        baker.make(
            "hubble.User",
            is_employed=False,
            _fill_optional=["email"],
            employee_id=seq(5),
            _quantity=5,
        )
        primary_mentor_id = User.objects.get(employee_id=1).id
        secondary_mentor_id = User.objects.get(employee_id=2).id
        team_id = self.create_team().id
        timeline = baker.make("hubble.Timeline", team_id=team_id)
        baker.make(
            "hubble.TimelineTask",
            timeline_id=timeline.id,
            _fill_optional=["order"],
            _quantity=5,
            days=2,
        )
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": team_id,
            "start_date": timezone.now().date(),
            "timeline": timeline.id,
            "primary_mentor_id": primary_mentor_id,
            "secondary_mentor_id": secondary_mentor_id,
        }

    def get_file_path(self):
        static_path = list(settings.STATICFILES_DIRS)
        return f"{static_path[0]}/training/pdf/"

    def test_success(self):
        with open(self.get_file_path() + "Sample_Intern_Upload.xlsx", "rb") as sample_file:
            data = self.get_valid_inputs({"users_list_file": sample_file})
            response = self.make_post_request(
                reverse(self.create_route_name, args=[self.batch_id]), data=data
            )
            self.assertRedirects(
                response, reverse(self.route_name, args=[self.batch_id])
            )
            self.assertEqual(response.status_code, 302)
            self.assertDatabaseHas(
                "SubBatch",
                {
                    "name": data["name"],
                    "team_id": data["team"],
                    "timeline_id": data["timeline"],
                    "start_date": data["start_date"],
                },
            )

    def test_required_validation(self):
        with open(self.get_file_path() + "Sample_Intern_Upload.xlsx", "rb") as sample_file:
            data = self.get_valid_inputs(
                {
                    "users_list_file": sample_file,
                    "name": "",
                    "team": "",
                    "timeline": "",
                    "primary_mentor_id": "",
                    "secondary_mentor_id": "",
                }
            )
            self.make_post_request(
                reverse(self.create_route_name, args=[self.batch_id]), data=data
            )
            field_errors = {
                "name": {"required"},
                "team": {"required"},
                "timeline": {"required"},
                "primary_mentor_id": {"required"},
                "secondary_mentor_id": {"required"},
            }
            self.validate_form_errors(
                field_errors=field_errors, form=SubBatchForm(data=data)
            )

    def test_invalid_choice_validation(self):
        with open(self.get_file_path() + "Sample_Intern_Upload.xlsx", "rb") as sample_file:
            data = self.get_valid_inputs(
                {
                    "users_list_file": sample_file,
                    "team": self.faker.name(),
                    "timeline": self.faker.name(),
                    "primary_mentor_id": self.faker.name(),
                    "secondary_mentor_id": self.faker.name(),
                }
            )
            self.make_post_request(
                reverse(self.create_route_name, args=[self.batch_id]), data=data
            )
            field_errors = {
                "team": {"invalid_choice"},
                "timeline": {"invalid_choice"},
                "primary_mentor_id": {"invalid_choice"},
                "secondary_mentor_id": {"invalid_choice"},
            }
            self.validate_form_errors(
                field_errors=field_errors, form=SubBatchForm(data=data)
            )

    def test_minimum_length_validation(self):
        with open(self.get_file_path() + "Sample_Intern_Upload.xlsx", "rb") as sample_file:
            data = self.get_valid_inputs(
                {"users_list_file": sample_file, "name": self.faker.pystr(max_chars=2)}
            )
            self.make_post_request(
                reverse(self.create_route_name, args=[self.batch_id]), data=data
            )
            field_errors = {"name": {"min_length"}}
            self.validate_form_errors(
                field_errors=field_errors,
                current_value=data,
                validation_parameter={"name": 3},
                form=SubBatchForm(data=data),
            )

    def test_file_validation(self):
        data = self.get_valid_inputs()
        response = self.make_post_request(reverse(self.create_route_name, args=[self.batch_id]), data=data)
        self.assertEqual(strip_tags(response.context["errors"]), "Please upload a file")

        with open(self.get_file_path() + "Sample_Intern_Upload.xlsx", "rb") as sample_file:
            data = self.get_valid_inputs({"users_list_file": sample_file})
            self.make_post_request(
                reverse(self.create_route_name, args=[self.batch_id]), data=data
            )
        with open(self.get_file_path() + "Sample_Intern_Upload.xlsx", "rb") as sample_file:
            data = self.get_valid_inputs({"users_list_file": sample_file})
            response = self.make_post_request(
                reverse(self.create_route_name, args=[self.batch_id]), data=data
            )
            self.assertEqual(strip_tags(response.context["errors"]), "Some of the Users are already added in another sub-batch")
        with open(self.get_file_path() + "invalid_file_upload1.xlsx", "rb") as sample_file:
            data = self.get_valid_inputs({"users_list_file": sample_file})
            response = self.make_post_request(
                reverse(self.create_route_name, args=[self.batch_id]), data=data
            )
            self.assertEqual(strip_tags(response.context["errors"]), "Some of the employee ids are not present in the database, please check again")
        with open(self.get_file_path() + "invalid_file_upload2.xlsx", "rb") as sample_file:
            data = self.get_valid_inputs({"users_list_file": sample_file})
            response = self.make_post_request(
                reverse(self.create_route_name, args=[self.batch_id]), data=data
            )
            self.assertEqual(strip_tags(response.context["errors"]), "Invalid keys are present in the file, please check the sample file")




class SubBatchUpdateTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in batch module
    """

    update_route_name = "sub-batch.edit"
    route_name = "batch.detail"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.update_valid_input()

    def update_valid_input(self):
        self.batch_id = baker.make("hubble.Batch").id
        self.sub_batch_id = baker.make("hubble.SubBatch", batch_id=self.batch_id).id
        baker.make(
            "hubble.User",
            is_employed=True,
            _fill_optional=["email"],
            employee_id=seq(0),
            _quantity=5,
        )
        baker.make(
            "hubble.User",
            is_employed=False,
            _fill_optional=["email"],
            employee_id=seq(5),
            _quantity=5,
        )
        primary_mentor_id = User.objects.get(employee_id=1).id
        secondary_mentor_id = User.objects.get(employee_id=2).id
        team_id = self.create_team().id
        timeline = baker.make("hubble.Timeline", team_id=team_id)
        baker.make(
            "hubble.TimelineTask",
            timeline_id=timeline.id,
            _fill_optional=["order"],
            _quantity=5,
            days=2,
        )
        baker.make(
            "hubble.SubBatchTaskTimeline",
            days=2,
            order=1,
            sub_batch_id=self.sub_batch_id,
        )
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": team_id,
            "start_date": timezone.now().date(),
            "timeline": timeline.id,
            "primary_mentor_id": primary_mentor_id,
            "secondary_mentor_id": secondary_mentor_id,
        }

    def test_success(self):
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]), data=data
        )
        self.assertRedirects(response, reverse(self.route_name, args=[self.batch_id]))
        self.assertEqual(response.status_code, 302)
        self.assertDatabaseHas(
            "SubBatch",
            {
                "name": data["name"],
                "team_id": data["team"],
                "timeline_id": data["timeline"],
                "start_date": data["start_date"],
            },
        )

    def test_required_validation(self):
        data = self.get_valid_inputs(
            {
                "name": "",
                "team": "",
                "timeline": "",
                "primary_mentor_id": "",
                "secondary_mentor_id": "",
            }
        )
        self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]), data=data
        )
        field_errors = {
            "name": {"required"},
            "team": {"required"},
            "timeline": {"required"},
            "primary_mentor_id": {"required"},
            "secondary_mentor_id": {"required"},
        }
        self.validate_form_errors(field_errors=field_errors, form=SubBatchForm(data=data))

    def test_invalid_choice_validation(self):
        data = self.get_valid_inputs(
            {
                "team": self.faker.name(),
                "timeline": self.faker.name(),
                "primary_mentor_id": self.faker.name(),
                "secondary_mentor_id": self.faker.name(),
            }
        )
        self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]), data=data
        )
        field_errors = {
            "team": {"invalid_choice"},
            "timeline": {"invalid_choice"},
            "primary_mentor_id": {"invalid_choice"},
            "secondary_mentor_id": {"invalid_choice"},
        }
        self.validate_form_errors(field_errors=field_errors, form=SubBatchForm(data=data))

    def test_minimum_length_validation(self):
        data = self.get_valid_inputs({"name": self.faker.pystr(max_chars=2)})
        self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]), data=data
        )
        field_errors = {"name": {"min_length"}}
        self.validate_form_errors(
            field_errors=field_errors,
            current_value=data,
            validation_parameter={"name": 3},
            form=SubBatchForm(data=data),
        )

    def test_timeline_with_no_tasks(self):
        team_id = self.create_team().id
        timeline = baker.make("hubble.Timeline", team_id=team_id)
        data = self.get_valid_inputs({"team": team_id, "timeline": timeline.id})
        self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]), data=data
        )
        field_errors = {
            "timeline": {"timeline_with_no_tasks"},
        }
        self.validate_form_errors(field_errors=field_errors, form=SubBatchForm(data=data))




class SubBatchShowTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in batch module
    """

    update_route_name = "sub-batch.edit"
    route_name = "batch.detail"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_success(self):
        sub_batch = baker.make("hubble.SubBatch")
        response = self.make_get_request(
            reverse(self.update_route_name, args=[sub_batch.id])
        )
        self.assertIsInstance(response.context.get("form"), SubBatchForm)
        self.assertEqual(response.context.get("form").instance, sub_batch)

    def test_failure(self):
        response = self.make_get_request(reverse(self.update_route_name, args=[0]))
        self.assertEqual(
            self.bytes_cleaner(response.content),
            '{"message": "Invalid SubBatch id", "status": "error"}',
        )


class GetTimelineTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in batch module
    """

    get_timeline_route_name = "sub-batch.get_timeline"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_success(self):
        team_id = baker.make("hubble.Team").id
        timeline = baker.make("hubble.Timeline", team_id=team_id, is_active=True)
        response = self.make_post_request(
            reverse(self.get_timeline_route_name), data={"team_id": team_id}
        )
        expected_message = {'timeline': model_to_dict(timeline)}
        self.assertEqual(
            (response.content.decode()), json.dumps(expected_message)
        )
        self.assertEqual(response.status_code, 200)

    def test_failure(self):
        response = self.make_post_request(
            reverse(self.get_timeline_route_name), data={"team_id": 0}
        )
        self.assertEqual(
            self.decoded_json(response).decode(),
            json.dumps({
                "message": "No active timeline template found",
            }),
        )
        self.assertEqual(response.status_code, 404)


class SubBatchDeleteTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in batch module
    """

    delete_route_name = "sub-batch.delete"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_success(self):
        sub_batch = baker.make("hubble.SubBatch")
        self.assertDatabaseHas("SubBatch", {"id": sub_batch.id})
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[sub_batch.id])
        )
        self.assertEqual(
            self.decoded_json(response).decode(), json.dumps({"message": "Sub-Batch deleted succcessfully"})
        )
        self.assertDatabaseNotHas("SubBatch", {"id": sub_batch.id})

    def test_failure(self):
        response = self.make_delete_request(reverse(self.delete_route_name, args=[0]))
        self.assertEqual(
            self.decoded_json(response).decode(), json.dumps({"message": "Error while deleting Sub-Batch!"})
        )
