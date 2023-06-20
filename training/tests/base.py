from django.test import TestCase, Client
from model_bakery import baker
from hubble.models import User, Team
from django.urls import reverse
from faker import Faker
import logging
from django.utils.translation import activate
from django.conf import settings


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.faker = Faker()

    def create_user(self):
        return baker.make(User, _fill_optional=['email', 'team'])
    
    def authenticate(self):
        user = self.create_user()
        self.client.login(email = user.email, password = user.password)

    def make_create_get_request(self, route_name):
        # print()
        # print(reverse(f"training:{route_name}"))
        # print(route_name)
        # print()
        return self.client.get(reverse(route_name))
    
    def make_create_post_request(self, route_name, data):
        return self.client.post(reverse(route_name), data)
    
    def make_update_get_request(self, route_name, timeline_id):
        # print(route_name, timeline_id, end="\n\n\n\n")
        # print(reverse(f"{route_name}, args={[timeline_id]}"), end="\n\n\n\n")
        # print(f"{route_name}, args={[timeline_id]}", end="\n\n\n\n")
        return self.client.get(reverse(route_name, args=[timeline_id]))
    
    def make_update_post_request(self, route_name, timeline_id, data):
        return self.client.post(reverse(route_name, args=[timeline_id]), data)
    
    def make_delete_request(self, route_name, timeline_id):
        return self.client.delete(reverse(route_name, args=[timeline_id]))
