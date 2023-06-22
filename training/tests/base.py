import json

from django.apps import apps
from django.conf import settings
from django.db.models import Q
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.translation import activate, ngettext_lazy
from faker import Faker
from model_bakery import baker

from core.constants import ADMIN_EMAILS
from hubble.models import Team, Timeline, User


class BaseTestCase(TestCase):
    persisted_valid_inputs = {}

    def setUp(self):
        """
        This function will be called before the start of every test
        """
        settings.ROOT_URLCONF = "training.urls"
        self.client = Client()
        self.faker = Faker()

    def create_user(self):
        """
        This function is responsible for creating an user and giving them admi access
        """
        user = baker.make(User, is_employed=True, _fill_optional=["email"])
        user.set_password("12345")
        user.save()
        ADMIN_EMAILS.append(user.email) # TODO :: Need to remove this logic after roles and permission
        return user

    def authenticate(self, user=None):
        """
        This function is responsible for authenticating the created user
        """
        if not user:
            user = self.create_user()
        self.client.force_login(user)

    def make_get_request(self, route_name):
        """
        This function is responsible for handling the GET requests without any arguments
        """
        return self.client.get(reverse(route_name)) # Need to change pass reversed url here

    def make_post_request(self, route_name, data):
        """
        This function is responsible for handling the POST requests without any arguments
        """
        return self.client.post(reverse(route_name), data) # Need to change pass reversed url here

    def make_get_request_with_argument(self, route_name, timeline_id):
        """
        This function is responsible for handling GET requests with arguments
        """
        return self.client.get(reverse(route_name, args=[timeline_id])) # Need to change pass reversed url here

    def make_post_request_with_argument(self, route_name, timeline_id, data):
        """
        This function is responsible for handling POST requests with arguments
        """
        return self.client.post(reverse(route_name, args=[timeline_id]), data) # Need to change pass reversed url here

    def make_delete_request(self, route_name, timeline_id):
        """
        This function is responsible for handling DELETE requests with arguments
        """
        return self.client.delete(reverse(route_name, args=[timeline_id])) # Need to change pass reversed url here

    def get_valid_inputs(self, override={}):
        """
        This function is responsible for getting the valid inputs for testcases and updating it as per need
        """
        return {**self.persisted_valid_inputs, **override}

    def decoded_json(self, response):
        """
        This function is responsible getting the response and converting into bytes
        """
        return response.content

    def get_model_instance(self, model_name):
        """
        This function is responsible for getting the correct model for DB testcases
        """
        return apps.get_model(app_label="hubble", model_name=model_name)

    def get_queryset_instance(self, model_name, filters):
        """
        This function is responsible for filtering the model as per the need
        """
        model = self.get_model_instance(model_name)
        query_filters = Q(**filters)
        return model.objects.filter(query_filters)

    def assertDatabaseHas(self, model_name, filters):
        """
        This function checks whether the DB has the data which we have created or manipulated
        """
        queryset = self.get_queryset_instance(model_name, filters)
        self.assertTrue(queryset.exists())

    def assertDatabaseCount(self, model_name, filters, count):
        """
        Gives the number of rows present in a table
        """
        queryset = self.get_queryset_instance(model_name, filters)
        self.assertEqual(queryset.count(), count)

    def assertDatabaseNotHas(self, model_name, filters):
        """
        This function checks whether the data we desired to delete, has been deleted ot not
        """
        queryset = self.get_queryset_instance(model_name, filters)
        self.assertFalse(queryset.exists())

    def bytes_cleaner(self, response):
        """
        This function cleans the unwanted slashes and mismatches in the quotes
        """
        return str(response.decode()).replace('\\"', "'")

    def get_ajax_response(self, current_value, field_errors={}, non_field_errors={}, validation_parameter=None):
        """
        This function helps to build the desired JSON response dynamically
        """
        field_error_response = {} # TODO :: if empty return list
        for key, values in field_errors.items():
            temp = []
            for value in values:
                # TODO
                if value == "min_length":
                    limit = 3
                    message = ngettext_lazy(
                        "Ensure this value has at least %(limit)d character (it has %(current_length)d).",
                        "Ensure this value has at least %(limit)d characters (it has %(current_length)d).",
                        limit
                        ) % {'current_length' : len(current_value[key]), 'limit' : limit}
                    # message = f"Ensure this value has at least 3 characters (it has {len(current_value[key])})."
                elif value == "required":
                    message = "This field is required."
                elif value == "":
                    message = "Team already has an active template."
                elif value == "invalid_choice":
                    message = "Select a valid choice. That choice is not one of the available choices."

                abc = {
                    "message": message,
                    "code": value,
                }
                temp.append(abc)
            field_error_response[key] = temp

        non_field_error_response = []
        for non_field_error in non_field_errors:
            pass

        return json.dumps(
            {
                "status": "error",
                "field_errors": str(field_error_response),
                "non_field_errors": str(non_field_error_response),
            }
        )
