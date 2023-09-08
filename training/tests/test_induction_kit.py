"""
Django test classes for testing the files present in Induction Kit
"""
from django.urls import reverse

from core.base_test import BaseTestCase


class HomePageTest(BaseTestCase):
    """
    This class is responsible for testing the home page
    """

    route_name = "induction-kit"

    def test_home_page(self):
        """
        This function is responsible for testing the home page
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse(self.route_name))


class InductionKitTest(BaseTestCase):
    """
    This class is responsible for testing the induction kit
    """

    route_name = "induction-kit"
    induction_kit_template = "induction_kit.html"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_induction_kit_page(self):
        """
        This function is responsible for testing the induction kit page
        """
        response = self.make_get_request(reverse(self.route_name))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.induction_kit_template)


class InductionKitFileTest(BaseTestCase):
    """
    This class is responsible for testing the induction kit file
    """

    route_name = "induction-kit.detail"
    file_name = "Trainee Induction Document-Ver 1.6.pdf"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_induction_kit_file(self):
        """
        This function is responsible for testing the induction kit file
        """
        response = self.make_get_request(reverse(self.route_name, args=[self.file_name]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")


class Error404Test(BaseTestCase):
    """
    This class is responsible for testing the 404 page
    """

    def test_404_page(self):
        """
        This function is responsible for testing the 404 page
        """
        response = self.make_get_request("/404")
        self.assertEqual(response.status_code, 404)
