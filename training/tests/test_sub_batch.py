"""
Django test cases for create, update, delete and django datatable for the Sub batch
"""

import io

import pandas as pd
from django.db.models import Count, Q
from django.http.request import QueryDict
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from model_bakery import baker
from model_bakery.recipe import seq

from core.base_test import BaseTestCase
from core.constants import USER_STATUS_INTERN, USER_STATUS_PROBATIONER
from hubble.models import Batch, SubBatch, Timeline, User
from training.forms import SubBatchForm


class SubBatchCreateTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in sub_batch module
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

    def update_valid_input(self):  # pragma: no cover
        """
        This function is responsible for updating the valid inputs and creating
        data in databases as reqiured
        """
        self.batch_id = baker.make("hubble.Batch", start_date=timezone.now().date).id
        baker.make(
            "hubble.User",
            is_employed=True,
            _fill_optional=["email"],
            status=USER_STATUS_PROBATIONER,
            employee_id=seq(0),
            _quantity=5,
        )
        self.users = baker.make(
            "hubble.User",
            is_employed=False,
            _fill_optional=["email"],
            status=USER_STATUS_INTERN,
            employee_id=seq(5),
            _quantity=5,
        )
        primary_mentor_id = User.objects.get(employee_id=1).id
        secondary_mentor_ids = User.objects.get(employee_id=2).id
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
            "hubble.Holiday",
            date_of_holiday=timezone.now().date() + timezone.timedelta(days=2),
        )
        start_date = timezone.now().date()
        if start_date.weekday() == 6:
            start_date = timezone.now().date() + timezone.timedelta(days=1)
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": team_id,
            "start_date": start_date,
            "timeline": timeline.id,
            "primary_mentor_id": primary_mentor_id,
            "secondary_mentor_ids": secondary_mentor_ids,
        }
        self.query_dict = QueryDict("", mutable=True)

    def create_memory_file(self, data):
        """
        This function is responsible for creating valid file input
        """
        memory_file = io.BytesIO()
        dataframe = pd.DataFrame(data)
        dataframe.to_excel(memory_file, index=False)
        memory_file.seek(0)
        return memory_file

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        file_values = {
            "employee_id": [self.users[1].employee_id, self.users[2].employee_id],
            "college": [self.faker.name(), self.faker.name()],
        }
        valid_file = self.create_memory_file(file_values)
        data = self.get_valid_inputs({"users_list_file": valid_file})
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        self.assertRedirects(response, reverse(self.route_name, args=[self.batch_id]))
        self.assertEqual(response.status_code, 302)
        self.assert_database_has(
            "SubBatch",
            {
                "name": data["name"],
                "team_id": data["team"],
                "timeline_id": data["timeline"],
                "start_date": data["start_date"],
            },
        )

    def test_multiple_mentors(self):
        """
        Check what happens when valid data is given as input with multiple secondary mentor
        """
        file_values = {
            "employee_id": [self.users[1].employee_id, self.users[2].employee_id],
            "college": [self.faker.name(), self.faker.name()],
        }
        valid_file = self.create_memory_file(file_values)
        secondary_mentor1 = self.create_user().id
        secondary_mentor2 = self.create_user().id
        data = self.get_valid_inputs(
            {
                "users_list_file": valid_file,
                "secondary_mentor_ids": [secondary_mentor1, secondary_mentor2],
            }
        )
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        self.assertRedirects(response, reverse(self.route_name, args=[self.batch_id]))
        self.assertEqual(response.status_code, 302)
        self.assert_database_has(
            "SubBatch",
            {
                "name": data["name"],
                "team_id": data["team"],
                "timeline_id": data["timeline"],
                "start_date": data["start_date"],
                "secondary_mentors__in": [secondary_mentor1, secondary_mentor2],
            },
        )

    def test_required_validation(self):
        """
        This function checks the required validation for the team and name fields
        """
        file_values = {
            "employee_id": [self.users[1].employee_id, self.users[2].employee_id],
            "college": [self.faker.name(), self.faker.name()],
        }
        valid_file = self.create_memory_file(file_values)
        self.query_dict.update({"users_list_file": valid_file})
        data = self.query_dict
        self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        field_errors = {
            "name": {"required"},
            "team": {"required"},
            "timeline": {"required"},
            "primary_mentor_id": {"required"},
            "secondary_mentor_ids": {"required"},
        }
        self.validate_form_errors(
            field_errors=field_errors,
            form=SubBatchForm(data=data, initial={"batch": self.batch_id}),
        )

    def test_invalid_choice_validation(self):
        """
        Check what happens when invalid data for team field is given as input
        """
        file_values = {
            "employee_id": [self.users[1].employee_id, self.users[2].employee_id],
            "college": [self.faker.name(), self.faker.name()],
        }
        valid_file = self.create_memory_file(file_values)
        secondary_mentors = [0, 0]
        data = self.get_valid_inputs(
            {
                "users_list_file": valid_file,
                "team": self.faker.name(),
                "timeline": self.faker.name(),
                "primary_mentor_id": self.faker.name(),
                "secondary_mentor_ids": secondary_mentors,
            }
        )
        data.setlist("secondary_mentor_ids", secondary_mentors)
        self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        field_errors = {
            "team": {"invalid_choice"},
            "timeline": {"invalid_choice"},
            "primary_mentor_id": {"invalid_choice"},
            "secondary_mentor_ids": {"invalid_choice"},
        }
        self.validate_form_errors(
            field_errors=field_errors,
            form=SubBatchForm(data=data, initial={"batch": self.batch_id}),
        )

    def test_minimum_length_validation(self):
        """
        To check what happens when name field fails MinlengthValidation
        """
        file_values = {
            "employee_id": [self.users[1].employee_id, self.users[2].employee_id],
            "college": [self.faker.name(), self.faker.name()],
        }
        valid_file = self.create_memory_file(file_values)
        data = self.get_valid_inputs(
            {
                "users_list_file": valid_file,
                "name": self.faker.pystr(max_chars=2),
            }
        )
        self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        field_errors = {"name": {"min_length"}}
        self.validate_form_errors(
            field_errors=field_errors,
            current_value=data,
            validation_parameter={"name": 3},
            form=SubBatchForm(data=data, initial={"batch": self.batch_id}),
        )

    def test_invalid_start_date(self):
        """
        To check what happens when start_date is invalid
        """
        file_values = {
            "employee_id": [self.users[1].employee_id, self.users[2].employee_id],
            "college": [self.faker.name(), self.faker.name()],
        }
        # Check what happens when start_date is empty
        valid_file = self.create_memory_file(file_values)
        data = self.get_valid_inputs({"users_list_file": valid_file, "start_date": ""})
        self.assertFormError(
            SubBatchForm(data=data, initial={"batch": self.batch_id}),
            "start_date",
            "This field is required.",
        )
        # Check what happens when start_date is on Holiday
        valid_file = self.create_memory_file(file_values)
        baker.make(
            "hubble.TraineeHoliday", batch_id=self.batch_id, date_of_holiday=timezone.now().date()
        )
        data = self.get_valid_inputs(
            {
                "users_list_file": valid_file,
            }
        )
        self.assertFormError(
            SubBatchForm(data=data, initial={"batch": self.batch_id}),
            "start_date",
            "The Selected date falls on a holiday, please reconsider the start date",
        )
        # Check what happens when start_date is before the batch start date
        valid_file = self.create_memory_file(file_values)
        data = self.get_valid_inputs(
            {
                "users_list_file": valid_file,
                "start_date": timezone.now().date() - timezone.timedelta(days=1),
            }
        )
        self.assertFormError(
            SubBatchForm(data=data, initial={"batch": self.batch_id}),
            "start_date",
            "The Selected date is before the batch start date",
        )

    def test_validate_no_timeline_task(self):
        """
        Check what happpens when a timeline with no task is selected
        """
        team_id = self.create_team().id
        timeline = baker.make("hubble.Timeline", team_id=team_id, is_active=True)
        file_values = {
            "employee_id": [self.users[1].employee_id, self.users[2].employee_id],
            "college": [self.faker.name(), self.faker.name()],
        }
        valid_file = self.create_memory_file(file_values)
        data = self.get_valid_inputs(
            {
                "users_list_file": valid_file,
                "team": team_id,
                "timeline": timeline.id,
            }
        )
        self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        field_errors = {
            "timeline": {"timeline_has_no_tasks"},
        }
        self.validate_form_errors(
            field_errors=field_errors,
            form=SubBatchForm(data=data, initial={"batch": self.batch_id}),
        )

    def test_inactive_timeline_has_no_tasks(self):
        """
        Check what happpens when a timeline with no task is selected
        """
        team_id = self.create_team().id
        timeline = baker.make("hubble.Timeline", team_id=team_id)
        file_values = {
            "employee_id": [self.users[1].employee_id, self.users[2].employee_id],
            "college": [self.faker.name(), self.faker.name()],
        }
        valid_file = self.create_memory_file(file_values)
        data = self.get_valid_inputs(
            {
                "users_list_file": valid_file,
                "team": team_id,
                "timeline": timeline.id,
            }
        )
        self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        field_errors = {
            "timeline": {"timeline_has_no_tasks"},
        }
        error_message = {
            "timeline_has_no_tasks": "The Selected Team's In Active Timeline"
            " doesn't have any tasks."
        }
        custom_validation_error_message = error_message
        self.validate_form_errors(
            field_errors=field_errors,
            custom_validation_error_message=custom_validation_error_message,
            form=SubBatchForm(data=data, initial={"batch": self.batch_id}),
        )

    def test_file_validation(self):
        """
        To check what happens when file input isn't valid
        """
        # When file is not uploaded
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        self.assertEqual(
            strip_tags(response.context["errors"]),
            "Please upload a file",
        )

        # Invalid data in file interns should be a type of intern
        file_values = {
            "employee_id": list(
                User.objects.filter(employee_id__in=[1, 2]).values_list("employee_id", flat=True)
            ),
            "college": [self.faker.name(), self.faker.name()],
        }
        valid_file = self.create_memory_file(file_values)
        data = self.get_valid_inputs({"users_list_file": valid_file})
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        self.assertEqual(
            strip_tags(response.context["errors"]),
            "Some of the users are not an intern",
        )

        # Invalid data in file interns belong to another sub-batch
        file_values = {
            "employee_id": [self.users[1].employee_id, self.users[2].employee_id],
            "college": [self.faker.name(), self.faker.name()],
        }
        valid_file = self.create_memory_file(file_values)
        data = self.get_valid_inputs({"users_list_file": valid_file})
        self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        valid_file = self.create_memory_file(file_values)
        data = self.get_valid_inputs({"users_list_file": valid_file})
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        self.assertEqual(
            strip_tags(response.context["errors"]),
            "Some of the Users are already added in another sub-batch",
        )

        # Invalid data in file, employee_id doesn't match with any employee_id in db
        file_values = {
            "employee_id": [self.faker.random_int(10, 20), self.faker.random_int(10, 20)],
            "college": [self.faker.name(), self.faker.name()],
        }
        invalid_file = self.create_memory_file(file_values)
        data = self.get_valid_inputs({"users_list_file": invalid_file})
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        self.assertEqual(
            strip_tags(response.context["errors"]),
            "Some of the employee ids are not present in the database, please check again",
        )

        # Invalid column names are present
        file_values = {
            "employee_ids": [self.users[1].employee_id, self.users[2].employee_id],
            "colleges": [self.faker.name(), self.faker.name()],
        }
        invalid_file = self.create_memory_file(file_values)
        data = self.get_valid_inputs({"users_list_file": invalid_file})
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]),
            data=data,
        )
        self.assertEqual(
            strip_tags(response.context["errors"]),
            "Invalid keys are present in the file, please check the sample file",
        )


class SubBatchUpdateTest(BaseTestCase):
    """
    This class is responsible for testing the Edit feature in sub_batch module
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

    def update_valid_input(self):  # pragma: no cover
        """
        This function is responsible for updating the valid inputs and creating
        data in databases as reqiured
        """
        self.batch_id = baker.make("hubble.Batch", start_date=timezone.now().date).id
        self.sub_batch_id = baker.make("hubble.SubBatch", batch_id=self.batch_id).id
        baker.make(
            "hubble.User",
            is_employed=True,
            _fill_optional=["email"],
            status=USER_STATUS_PROBATIONER,
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
        secondary_mentor_ids = User.objects.get(employee_id=2).id
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
        baker.make(
            "hubble.Holiday",
            date_of_holiday=timezone.now().date() + timezone.timedelta(days=2),
        )
        start_date = timezone.now().date()
        if start_date.weekday() == 6:
            start_date = timezone.now().date() + timezone.timedelta(days=1)
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": team_id,
            "start_date": start_date,
            "timeline": timeline.id,
            "primary_mentor_id": primary_mentor_id,
            "secondary_mentor_ids": secondary_mentor_ids,
        }
        self.query_dict = QueryDict("", mutable=True)

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]),
            data=data,
        )
        self.assertRedirects(response, reverse(self.route_name, args=[self.batch_id]))
        self.assertEqual(response.status_code, 302)
        self.assert_database_has(
            "SubBatch",
            {
                "name": data["name"],
                "team_id": data["team"],
                "timeline_id": data["timeline"],
                "start_date": data["start_date"],
            },
        )

        # Check whether multiple secondary mentors are added
        secondary_mentor1 = self.create_user().id
        secondary_mentor2 = self.create_user().id
        data = self.get_valid_inputs(
            {"secondary_mentor_ids": [secondary_mentor1, secondary_mentor2]}
        )
        response = self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]),
            data=data,
        )
        self.assertRedirects(response, reverse(self.route_name, args=[self.batch_id]))
        self.assertEqual(response.status_code, 302)
        self.assert_database_has(
            "SubBatch",
            {
                "name": data["name"],
                "team_id": data["team"],
                "timeline_id": data["timeline"],
                "start_date": data["start_date"],
                "secondary_mentors__in": [secondary_mentor1, secondary_mentor2],
            },
        )

        # check what happens when a timeline is not updated
        data = self.get_valid_inputs({"name": self.faker.name()})
        response = self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]),
            data=data,
        )
        self.assertRedirects(response, reverse(self.route_name, args=[self.batch_id]))
        self.assertEqual(response.status_code, 302)
        self.assert_database_has(
            "SubBatch",
            {
                "name": data["name"],
                "team_id": data["team"],
                "timeline_id": data["timeline"],
                "start_date": data["start_date"],
            },
        )

    def test_required_validation(self):
        """
        This function checks the required validation for the team and name fields
        """
        self.query_dict.update({})
        data = self.query_dict
        self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]),
            data=data,
        )
        field_errors = {
            "name": {"required"},
            "team": {"required"},
            "timeline": {"required"},
            "primary_mentor_id": {"required"},
            "secondary_mentor_ids": {"required"},
        }
        self.validate_form_errors(
            field_errors=field_errors,
            form=SubBatchForm(data=data, instance=SubBatch.objects.get(id=self.sub_batch_id)),
        )

    def test_invalid_choice_validation(self):
        """
        Check what happens when invalid data for team field is given as input
        """
        data = self.get_valid_inputs(
            {
                "team": self.faker.name(),
                "timeline": self.faker.name(),
                "primary_mentor_id": self.faker.name(),
                "secondary_mentor_ids": self.faker.unique.random_int(1, 10),
            }
        )
        self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]),
            data=data,
        )
        field_errors = {
            "team": {"invalid_choice"},
            "timeline": {"invalid_choice"},
            "primary_mentor_id": {"invalid_choice"},
            "secondary_mentor_ids": {"invalid_choice"},
        }
        self.validate_form_errors(
            field_errors=field_errors,
            form=SubBatchForm(data=data, instance=SubBatch.objects.get(id=self.sub_batch_id)),
        )

    def test_minimum_length_validation(self):
        """
        To check what happens when name field fails MinlengthValidation
        """
        data = self.get_valid_inputs({"name": self.faker.pystr(max_chars=2)})
        self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]),
            data=data,
        )
        field_errors = {"name": {"min_length"}}
        self.validate_form_errors(
            field_errors=field_errors,
            current_value=data,
            validation_parameter={"name": 3},
            form=SubBatchForm(data=data, instance=SubBatch.objects.get(id=self.sub_batch_id)),
        )

    def test_invalid_start_date(self):
        """
        To check what happens when start_date is invalid
        """
        # Check what happens when start_date is empty
        data = self.get_valid_inputs({"start_date": ""})
        self.assertFormError(
            SubBatchForm(data=data, instance=SubBatch.objects.get(id=self.sub_batch_id)),
            "start_date",
            "This field is required.",
        )
        # Check what happens when start_date is on Holiday
        data = self.get_valid_inputs()
        baker.make(
            "hubble.TraineeHoliday", batch_id=self.batch_id, date_of_holiday=timezone.now().date()
        )
        self.assertFormError(
            SubBatchForm(data=data, instance=SubBatch.objects.get(id=self.sub_batch_id)),
            "start_date",
            "The Selected date falls on a holiday, please reconsider the start date",
        )
        # Check what happens when start_date is before the batch start date
        data = self.get_valid_inputs(
            {
                "start_date": timezone.now().date() - timezone.timedelta(days=1),
            }
        )
        self.assertFormError(
            SubBatchForm(data=data, instance=SubBatch.objects.get(id=self.sub_batch_id)),
            "start_date",
            "The Selected date is before the batch start date",
        )

    def test_active_timeline_has_no_tasks(self):
        """
        Check what happpens when a timeline with no task is selected
        """
        team_id = self.create_team().id
        timeline = baker.make("hubble.Timeline", team_id=team_id, is_active=True)
        data = self.get_valid_inputs({"team": team_id, "timeline": timeline.id})
        self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]),
            data=data,
        )
        field_errors = {
            "timeline": {"timeline_has_no_tasks"},
        }
        self.validate_form_errors(
            field_errors=field_errors,
            form=SubBatchForm(data=data, instance=SubBatch.objects.get(id=self.sub_batch_id)),
        )

    def test_inactive_timeline_has_no_tasks(self):
        """
        Check what happpens when a timeline with no task is selected
        """
        team_id = self.create_team().id
        timeline = baker.make("hubble.Timeline", team_id=team_id)
        data = self.get_valid_inputs({"team": team_id, "timeline": timeline.id})
        self.make_post_request(
            reverse(self.update_route_name, args=[self.sub_batch_id]),
            data=data,
        )
        field_errors = {
            "timeline": {"timeline_has_no_tasks"},
        }
        error_message = {
            "timeline_has_no_tasks": "The Selected Team's In Active Timeline"
            " doesn't have any tasks."
        }
        custom_validation_error_message = error_message
        self.validate_form_errors(
            field_errors=field_errors,
            custom_validation_error_message=custom_validation_error_message,
            form=SubBatchForm(data=data, instance=SubBatch.objects.get(id=self.sub_batch_id)),
        )


class SubBatchShowTest(BaseTestCase):
    """
    This class is responsible for testing the Show feature in sub_batch module
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
        """
        Check what happens when valid data is given as input
        """
        sub_batch = baker.make("hubble.SubBatch")
        response = self.make_get_request(reverse(self.update_route_name, args=[sub_batch.id]))
        self.assertIsInstance(response.context.get("form"), SubBatchForm)
        self.assertEqual(response.context.get("form").instance, sub_batch)

    def test_failure(self):
        """
        Check what happens when invalid data is given as input
        """
        response = self.make_get_request(reverse(self.update_route_name, args=[0]))
        self.assertEqual(
            self.bytes_cleaner(response.content),
            '{"message": "Invalid SubBatch id", "status": "error"}',
        )


class GetTimelineTest(BaseTestCase):
    """
    This class is responsible for testing whether correct timeline is fetched or not
    """

    get_timeline_route_name = "sub-batch.get_timelines"

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
        team_id = baker.make("hubble.Team").id
        baker.make("hubble.Timeline", team_id=team_id, is_active=True)
        timeline_template = list(
            Timeline.objects.filter(team_id=team_id).values("id", "name", "is_active")
        )
        response = self.make_post_request(
            reverse(self.get_timeline_route_name),
            data={"team_id": team_id},
        )
        self.assertJSONEqual((response.content), timeline_template)
        self.assertEqual(response.status_code, 200)

    def test_failure(self):
        """
        Check what happens when invalid data is given as input
        """
        response = self.make_post_request(
            reverse(self.get_timeline_route_name), data={"team_id": 0}
        )
        self.assertJSONEqual(
            self.decoded_json(response),
            {
                "message": "No timeline template found",
            },
        )
        self.assertEqual(response.status_code, 404)


class SubBatchDeleteTest(BaseTestCase):
    """
    This class is responsible for testing the DELETE feature in sub_batch module
    """

    delete_route_name = "sub-batch.delete"

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
        sub_batch = baker.make("hubble.SubBatch")
        self.assert_database_has("SubBatch", {"id": sub_batch.id})
        response = self.make_delete_request(reverse(self.delete_route_name, args=[sub_batch.id]))
        self.assertJSONEqual(
            self.decoded_json(response),
            {"message": "Sub-Batch deleted succcessfully"},
        )
        self.assert_database_not_has("SubBatch", {"id": sub_batch.id})

    def test_failure(self):
        """
        Check what happens when invalid data is given as input
        """
        response = self.make_delete_request(reverse(self.delete_route_name, args=[0]))
        self.assertJSONEqual(
            self.decoded_json(response),
            {"message": "Error while deleting Sub-Batch!"},
        )


class SubBatchDatatableTest(BaseTestCase):
    """
    This class is responsible for testing the Datatables present in the Batch module
    """

    datatable_route_name = "sub-batch-datatable"
    route_name = "batch.detail"

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
        self.batch = baker.make("hubble.Batch")
        self.team = baker.make("hubble.Team")
        self.name = self.faker.name()
        self.sub_batch = baker.make(
            "hubble.SubBatch",
            name=seq(self.name),
            team_id=self.team.id,
            batch_id=self.batch.id,
            _quantity=2,
        )
        self.persisted_valid_inputs = {
            "draw": 1,
            "start": 0,
            "length": 10,
            "search[value]": "",
            "batch_id": self.batch.id,
        }

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name, args=[self.batch.id]))
        self.assertTemplateUsed(response, "sub_batch/sub_batch.html")
        self.assertContains(response, "Sub Batch List")

    def test_datatable(self):
        """
        To check whether all columns are present in datatable and length of rows without any filter
        """
        no_of_teams = (
            Batch.objects.filter(id=self.batch.id).values("sub_batches__team").distinct().count()
        )
        no_of_trainees = (
            Batch.objects.filter(id=self.batch.id)
            .annotate(
                no_of_trainees=Count(
                    "sub_batches__intern_details",
                    filter=Q(sub_batches__intern_details__deleted_at__isnull=True),
                ),
            )
            .values("no_of_trainees")
        )[0]["no_of_trainees"]
        sub_batches = SubBatch.objects.filter(batch=self.batch.id).annotate(
            trainee_count=Count(
                "intern_details",
                filter=Q(intern_details__deleted_at__isnull=True),
            )
        )
        response = self.make_post_request(
            reverse(self.datatable_route_name),
            data=self.get_valid_inputs(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("extra_data" in response.json())
        self.assertTrue("no_of_teams" in response.json()["extra_data"][0])
        self.assertTrue("no_of_trainees" in response.json()["extra_data"][0])
        self.assertEqual(response.json()["extra_data"][0]["no_of_teams"], no_of_teams)
        self.assertEqual(response.json()["extra_data"][0]["no_of_trainees"], no_of_trainees)
        for index, expected_value in enumerate(sub_batches):
            received_value = response.json()["data"][index]
            self.assertEqual(expected_value.pk, int(received_value["pk"]))
            self.assertEqual(expected_value.name, received_value["name"])
            self.assertEqual(
                expected_value.trainee_count,
                int(received_value["trainee_count"]),
            )
            self.assertEqual(expected_value.timeline.name, received_value["timeline"])
            self.assertEqual(
                expected_value.primary_mentor.name,
                received_value["primary_mentor"],
            )
            self.assertEqual(
                expected_value.start_date.strftime("%d %b %Y"),
                received_value["start_date"],
            )
        for row in response.json()["data"]:
            self.assertTrue("pk" in row)
            self.assertTrue("name" in row)
            self.assertTrue("team" in row)
            self.assertTrue("trainee_count" in row)
            self.assertTrue("primary_mentor" in row)
            self.assertTrue("timeline" in row)
            self.assertTrue("start_date" in row)
            self.assertTrue("action" in row)
        self.assertTrue(response.json()["recordsTotal"], len(self.sub_batch))

    def test_datatable_search(self):
        """
        To check what happens when search value is given
        """
        name_to_be_searched = self.name + "1"
        response = self.make_post_request(
            reverse(self.datatable_route_name),
            data=self.get_valid_inputs({"search[value]": name_to_be_searched}),
        )
        self.assertTrue(
            response.json()["recordsTotal"],
            SubBatch.objects.filter(name__icontains=name_to_be_searched).count(),
        )
