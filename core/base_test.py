"""
Django application basic testcase configuration and test runner for 
the unmanaged models
"""
import json

from django.apps import apps
from django.conf import settings
from django.db.models import Q
from django.test import Client, TestCase
from django.test.runner import DiscoverRunner
from django.utils.translation import ngettext_lazy
from faker import Faker
from model_bakery import baker

from core.constants import ADMIN_EMAILS
from hubble.models import User
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
        settings.IS_TEST_CASE = True
        super().setup_test_environment(*args, **kwargs)

    def teardown_test_environment(self, *args, **kwargs):
        super().teardown_test_environment(*args, **kwargs)
        settings.IS_TEST_CASE = False


class BaseTestCase(TestCase):
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

    def authenticate(self, user=None):
        """
        This function is responsible for authenticating the created user
        """
        if not user:
            user = self.create_user()
        self.client.force_login(user)

    def make_get_request(self, url_pattern):
        """
        This function is responsible for handling the GET requests
        """
        return self.client.get(url_pattern, SERVER_NAME=self.testcase_server_name)

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
        return {**self.persisted_valid_inputs, **override}

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
            message = f"The current order of the task is invalid. The valid input for order ranges form 1-{validation_parameter[key]}."  # pylint: disable=C0301
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
    # pylint: disable-next=dangerous-default-value
    def validate_form_errors(
        self,
        form,
        field_errors,
        current_value={},
        validation_parameter={},
    ):
        """
        Validates form errors by retrieving error messages and asserting
        them for each field
        """
        for key, values in field_errors.items():
            for value in values:
                error_message = self.get_error_message(
                    key, value, current_value, validation_parameter
                )
                self.assertFormError(form, key, error_message)
