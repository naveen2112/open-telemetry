"""
Django application basic testcase configuration and test runner for
the unmanaged models
"""
import datetime
import json

from django.apps import apps
from django.conf import settings
from django.db.models import Q
from django.http import QueryDict
from django.test import Client, TestCase
from django.test.runner import DiscoverRunner
from django.utils import timezone
from django.utils.translation import ngettext_lazy
from faker import Faker
from model_bakery import baker
from model_bakery.recipe import seq

from core.constants import ADMIN_EMAILS
from core.utils import calculate_duration_for_task, schedule_timeline_for_sub_batch
from hubble.models import TraineeHoliday, User
from hubble_report.settings import env


# It is used to disable the 'potected access error', the protected member
# is not intended to access it from outside the class or subclass
# pylint: disable=protected-access
class UnManagedModelTestRunner(DiscoverRunner):
    """
    Test runner that automatically makes all unmanaged models in your Django
    project managed for the duration of the test run, so that one doesn't need
    to execute the SQL manually to create them.
    Test runner that automatically makes all unmanaged models in your Django
    project managed for the duration of the test run, so that one doesn't need
    to execute the SQL manually to create them.
    """

    def setup_test_environment(self, *args, **kwargs):
        """
        The function sets up the test environment by setting a flag and calling
        the parent class's setup_test_environment method.
        """
        settings.IS_TEST_CASE = True
        super().setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        """
        The function `teardown_test_environment` sets the `IS_TEST_CASE` setting
        to `False` after calling the parent class's `teardown_test_environment` method.
        """
        super().teardown_test_environment(*args, **kwargs)
        settings.IS_TEST_CASE = False


class BaseTestCase(TestCase):  # pylint:disable=R0902,R0904
    """
    This class helps us to follow DRY principles in Training module testing
    """

    persisted_valid_inputs = {}
    testcase_server_name = env("TRAINING_TESTCASE_SERVER_NAME")

    def setUp(self):
        """
        This function will be called before the start of every test
        """
        settings.ROOT_URLCONF = "training.urls"
        self.client = Client()
        self.faker = Faker()

    def create_user(self):
        """
        This function is responsible for creating an user and giving
        them admin access
        """
        user = baker.make(User, is_employed=True, _fill_optional=["email"])
        ADMIN_EMAILS.append(
            user.email
        )  # TODO :: Need to remove this logic after roles and permission
        return user

    def create_team(self):
        """
        Creates and returns an instance of the 'hubble.Team' model
        """
        return baker.make("hubble.Team")

    def create_holidays(self):
        """
        This function is responsible for create Holidays for the next 12 weeks
        """
        current_date = datetime.datetime.now().date()
        end_date = current_date + datetime.timedelta(weeks=12)
        while current_date <= end_date:
            if current_date.weekday() == 5:
                holiday = baker.make(
                    "hubble.Holiday",
                    date_of_holiday=current_date,
                    reason=self.faker.sentence(),
                )
            current_date += datetime.timedelta(1)

        return holiday

    def create_trinee_holidays(self, batch_id):
        """
        This function is responsible for create Trinee Holidays for the next 12 weeks
        """
        current_date = datetime.datetime.now().date()
        end_date = current_date + datetime.timedelta(weeks=12)
        while current_date <= end_date:
            if current_date.weekday() == 5:
                holiday = baker.make(
                    "hubble.TraineeHoliday",
                    date_of_holiday=current_date,
                    reason=self.faker.sentence(),
                    batch_id=batch_id,
                )
            current_date += datetime.timedelta(1)
        return holiday

    def setup_timline_tasks(self):
        """
        This function is responsible for creating the timeline tasks
        """
        self.batch_id = baker.make(  # pylint:disable=W0201
            "hubble.Batch", start_date=(timezone.now() + timezone.timedelta(1)).date()
        ).id
        self.create_trinee_holidays(self.batch_id)
        self.timeline = baker.make(  # pylint:disable=W0201
            "hubble.Timeline",
            is_active=True,
        )
        self.days_list = [  # pylint:disable=W0201
            self.faker.random_number(1, 20) / 2 for _ in range(4)
        ]
        self.timeline_task = baker.make(  # pylint:disable=W0201
            "hubble.TimelineTask",
            timeline=self.timeline,
            days=self.days_list.__iter__(),  # pylint:disable=C2801
            order=seq(0),
            _quantity=4,
        )
        self.sub_batch = baker.make(  # pylint:disable=W0201
            "hubble.SubBatch",
            start_date=(timezone.now().date() + timezone.timedelta(1)),
            batch_id=self.batch_id,
            timeline=self.timeline,
        )
        schedule_timeline_for_sub_batch(sub_batch=self.sub_batch, user=self.user)

    def check_start_end_date(self):
        """
        This function is responsible for checking the start and end date
        """
        self.holidays = TraineeHoliday.objects.filter(  # pylint:disable=W0201
            batch_id=self.batch_id
        ).values_list("date_of_holiday", flat=True)
        cur_date = timezone.now() + timezone.timedelta(1)
        is_half_day = False
        for task in self.timeline_task:
            data = calculate_duration_for_task(self.holidays, cur_date, is_half_day, task.days)
            cur_date = end_date = data["end_date_time"]
            is_half_day = data["ends_afternoon"]
        timeline_task_end_date = schedule_timeline_for_sub_batch(
            sub_batch=self.sub_batch, user=self.user
        )
        self.assertEqual(end_date, timeline_task_end_date)

    def authenticate(self, user=None):
        """
        This function is responsible for authenticating the created user
        """
        if not user:
            user = self.create_user()
        self.client.force_login(user)

    def make_get_request(self, url_pattern, data=None):
        """
        This function is responsible for handling the GET requests
        """
        return self.client.get(url_pattern, data=data, SERVER_NAME=self.testcase_server_name)

    def make_post_request(self, url_pattern, data):
        """
        This function is responsible for handling the POST requests
        """
        return self.client.post(url_pattern, data, SERVER_NAME=self.testcase_server_name)

    def make_delete_request(self, url_pattern):
        """
        This function is responsible for handling DELETE requests}
        """
        return self.client.delete(url_pattern, SERVER_NAME=self.testcase_server_name)

    # It isn used to disable 'dangerous-default-value'.By default, pylint
    # warns against using mutable objects as default values for function
    # parameters because they can lead to unexpected behavior
    # pylint: disable=dangerous-default-value
    def get_valid_inputs(self, override={}):
        """
        This function is responsible for getting the valid inputs for
        testcases and updating it as per need
        """
        query_dict = QueryDict("", mutable=True)
        query_dict.update({**self.persisted_valid_inputs, **override})
        return query_dict

    def decoded_json(self, response):
        """
        This function is responsible getting the response and converting
        into bytes
        """
        return response.content

    def get_model_instance(self, model_name):
        """
        This function is responsible for getting the correct model
        for DB testcases
        """
        return apps.get_model(app_label="hubble", model_name=model_name)

    def get_queryset_instance(self, model_name, filters):
        """
        This function is responsible for filtering the model
        as per the need
        """
        model = self.get_model_instance(model_name)
        query_filters = Q(**filters)
        return model.objects.filter(query_filters)

    def assert_database_has(self, model_name, filters):
        """
        This function checks whether the DB has the data which
        we have created or manipulated
        """
        queryset = self.get_queryset_instance(model_name, filters)
        self.assertTrue(queryset.exists())

    def assert_database_count(self, model_name, filters, count):
        """
        Gives the number of rows present in a table
        """
        queryset = self.get_queryset_instance(model_name, filters)
        self.assertEqual(queryset.count(), count)

    def assert_database_not_has(self, model_name, filters):
        """
        This function checks whether the data we desired to delete,
        has been deleted ot not
        """
        queryset = self.get_queryset_instance(model_name, filters)
        self.assertFalse(queryset.exists())

    def bytes_cleaner(self, response):
        """
        This function cleans the unwanted slashes and mismatches in the quotes
        """
        return str(response.decode()).replace('\\"', "'")

    def get_error_message(self, key, value, current_value, validation_parameter):
        """
        This function is responsible for building the error json
        response dynamically
        """
        if value == "min_length":
            message = ngettext_lazy(
                "Ensure this value has at least %(validation_parameter)d "
                "character (it has %(current_length)d).",
                "Ensure this value has at least %(validation_parameter)d "
                "characters (it has %(current_length)d).",
                validation_parameter[key],
            ) % {
                "current_length": len(current_value[key]),
                "validation_parameter": validation_parameter[key],
            }
        elif value == "required":
            message = "This field is required."
        elif value == "invalid_choice":
            message = "Select a valid choice. That choice is not one of the available choices."
        elif value == "invalid_order":
            message = (
                f"The current order of the task is invalid."
                f"The valid input for order ranges from "
                f"{validation_parameter[key][0]}-{validation_parameter[key][-1] + 1}."
            )  # pylint: disable=C0301
        elif value == "zero_order_error":
            message = "Order value must be greater than zero."
        elif value == "timeline_has_no_tasks":
            message = "The Selected Team's Active Timeline doesn't have any tasks."
        elif value == "invalid_score":
            message = "Score must be between 0 to 100"
        return message

    # It is used to disable the "too-mnay-arguments", according to PEP8
    # guidlines if the function has more than 5 arguments in the function
    # it will make code harder to maintain
    # pylint: disable-next=too-many-arguments
    def get_ajax_response(
        self,
        current_value={},
        field_errors={},
        non_field_errors={},
        validation_parameter={},
        custom_validation_error_message={},
    ):
        """
        This function helps to build the desired JSON response dynamically
        """
        field_error_response = {} if field_errors else []
        for key, values in field_errors.items():
            temp = []
            for value in values:
                message = custom_validation_error_message.get(value) or self.get_error_message(
                    key, value, current_value, validation_parameter
                )
                error_details = {
                    "message": message,
                    "code": value,
                }
                temp.append(error_details)
            field_error_response[key] = temp

        non_field_error_response = []
        if non_field_errors != {}:
            non_field_error_response.append(non_field_errors)

        return json.dumps(
            {
                "status": "error",
                "field_errors": str(field_error_response),
                "non_field_errors": str(non_field_error_response),
            }
        )

    # It is used to disable the "too-mnay-arguments", according to PEP8
    # guidlines if the function has more than 5 arguments in the function
    # it will make code harder to maintain
    # pylint: disable-next=dangerous-default-value, too-many-arguments
    def validate_form_errors(
        self,
        form,
        field_errors,
        current_value={},
        validation_parameter={},
        custom_validation_error_message={},
    ):
        """
        Validates form errors by retrieving error messages and asserting
        them for each field
        """
        for key, values in field_errors.items():
            for value in values:
                error_message = custom_validation_error_message.get(
                    value
                ) or self.get_error_message(key, value, current_value, validation_parameter)
                self.assertFormError(form, key, error_message)
