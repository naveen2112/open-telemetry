from django.urls import reverse
from model_bakery import baker

from core.base_test import BaseTestCase
from hubble.models import TraineeHoliday
import datetime
from dateutil.relativedelta import relativedelta


class TraineeHolidayCreateTest(BaseTestCase):
    """
    This class is responsible for testing the Trainee Holiday CREATE feature in Batch Holiday module
    """

    create_route_name = "holiday.create"
    route_name = "batch.holiday"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.create_holidays()
        self.update_valid_input()

    def update_valid_input(self):
        """
        This function is responsible for updating the valid input
        """
        self.batch_id = baker.make("hubble.Batch").id
        self.persisted_valid_inputs = {
            "date_of_holiday": datetime.date.today() + relativedelta(days=1),
            "reason": self.faker.sentence(),
            "national_holiday": False,
            "allow_check_in": False,
            "batch_id": self.batch_id,
        }

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name, args=[self.batch_id]))
        self.assertTemplateUsed(response, "trainee_holiday/trainee_holiday.html")
        self.assertContains(response, "Holidays")

    def test_success(self):
        """
        To makes sure that the Trainee Holiday is created successfully
        """
        data = self.persisted_valid_inputs
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]), data
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "TraineeHoliday",
            {
                "date_of_holiday": data["date_of_holiday"],
                "reason": data["reason"],
                "national_holiday": data["national_holiday"],
                "allow_check_in": data["allow_check_in"],
                "batch_id": data["batch_id"],
            },
        )

    def test_required_validation(self):
        """
        To makes sure that the required fields are validated
        """
        data = {}
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]), data
        )
        field_errors = {
            "date_of_holiday": {"required"},
            "reason": {"required"},
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )

    def test_unique_validation(self):
        """
        To makes sure that the unique fields are validated
        """
        data = self.get_valid_inputs()
        self.make_post_request(reverse(self.create_route_name, args=[self.batch_id]), data)
        response = self.make_post_request(
            reverse(self.create_route_name, args=[self.batch_id]), data
        )
        field_errors = {
            "date_of_holiday": {"invalid_date"},
        }
        custom_validation_error_message = {
            "invalid_date": "The date of holiday has already been taken."
        }
        self.assertJSONEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=custom_validation_error_message,
            ),
        )


class TraineeHolidayUpdateTest(BaseTestCase):
    """
    This class is responsible for testing the Trainee Holiday UPDATE feature in Batch Holiday module
    """

    update_route_name = "holiday.edit"
    route_name = "batch.holiday"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.create_holidays()
        self.update_valid_input()

    def update_valid_input(self):
        """
        This function is responsible for updating the valid input
        """
        self.batch_id = baker.make("hubble.Batch").id
        self.holiday = self.create_trinee_holidays(self.batch_id)
        self.persisted_valid_inputs = {
            "date_of_holiday": datetime.date.today() + relativedelta(days=1),
            "reason": self.faker.sentence(),
            "national_holiday": False,
            "allow_check_in": False,
            "batch_id": self.batch_id,
            "id": self.holiday.id,
        }

    def test_success(self):
        """
        To makes sure that the Trainee Holiday is updated successfully
        """
        data = self.get_valid_inputs(
            {
                "date_of_holiday": self.holiday.date_of_holiday.strftime("%Y-%m-%d"),
            }
        )
        response = self.make_post_request(
            reverse(self.update_route_name, args=[self.holiday.id]), data
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "TraineeHoliday",
            {
                "date_of_holiday": data["date_of_holiday"],
                "reason": data["reason"],
                "national_holiday": data["national_holiday"],
                "allow_check_in": data["allow_check_in"],
                "batch_id": data["batch_id"],
            },
        )

    def test_required_validation(self):
        """
        To makes sure that the required fields are validated
        """
        data = {}
        response = self.make_post_request(
            reverse(self.update_route_name, args=[self.holiday.id]), data
        )
        field_errors = {
            "date_of_holiday": {"required"},
            "reason": {"required"},
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )

    def test_unique_validation(self):
        """
        To makes sure that the unique fields are validated
        """
        another_date = (
            TraineeHoliday.objects.filter(batch_id=self.batch_id)
            .first()
            .date_of_holiday.strftime("%Y-%m-%d")
        )
        data = self.get_valid_inputs(
            {
                "date_of_holiday": another_date,
            }
        )
        response = self.make_post_request(
            reverse(self.update_route_name, args=[self.holiday.id]), data
        )
        field_errors = {
            "date_of_holiday": {"invalid_date"},
        }
        custom_validation_error_message = {
            "invalid_date": "The date of holiday has already been taken."
        }
        self.assertJSONEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=custom_validation_error_message,
            ),
        )


class TraineeHolidayDeleteTest(BaseTestCase):
    """
    This class is responsible for testing the Trainee Holiday DELETE feature in Batch Holiday module
    """

    delete_route_name = "holiday.delete"
    route_name = "batch.holiday"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.create_holidays()
        self.batch_id = baker.make("hubble.Batch").id
        self.holiday = self.create_trinee_holidays(self.batch_id)

    def test_success(self):
        """
        To makes sure that the Trainee Holiday is deleted successfully
        """
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[self.holiday.id])
        )
        self.assertJSONEqual(
            self.decoded_json(response), {"message": "Holiday deleted succcessfully"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseNotHas(
            "TraineeHoliday",
            {
                "date_of_holiday": self.holiday.date_of_holiday,
                "reason": self.holiday.reason,
                "national_holiday": self.holiday.national_holiday,
                "allow_check_in": self.holiday.allow_check_in,
                "batch_id": self.holiday.batch_id,
            },
        )

    def test_failure(self):
        """
        To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(reverse(self.delete_route_name, args=[0]))
        self.assertEqual(response.status_code, 500)


class TraineeHolidayDatatableTest(BaseTestCase):
    """
    This class is responsible for testing the Trainee Holiday DATATABLE feature in Batch Holiday module
    """

    datatable_route_name = "holiday-datatable"
    route_name = "batch.holiday"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.batch_id = baker.make("hubble.Batch").id
        self.create_trinee_holidays(self.batch_id)

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name, args=[self.batch_id]))
        self.assertTemplateUsed(response, "trainee_holiday/trainee_holiday.html")
        self.assertContains(response, "Holidays")

    def test_datatable(self):
        """
        To check whether all columns are present in datatable and length of rows without any filter
        """
        holidays = TraineeHoliday.objects.filter(batch_id=self.batch_id)

        payload = {
            "draw": 1,
            "start": 0,
            "length": 100,
            "batch": self.batch_id,
        }
        response = self.make_post_request(reverse(self.datatable_route_name), data=payload)
        self.assertEqual(response.status_code, 200)

        # Check whether row details are correct
        for row in range(len(holidays)):
            expected_value = holidays[row]
            received_value = response.json()["data"][row]
            self.assertEqual(expected_value.pk, int(received_value["pk"]))
            self.assertEqual(
                expected_value.date_of_holiday.strftime("%d %b %Y"),
                received_value["date_of_holiday"],
            )
            self.assertEqual(expected_value.reason, received_value["reason"])
            if expected_value.national_holiday:
                self.assertEqual("Yes", received_value["national_holiday"])
            else:
                self.assertEqual("No", received_value["national_holiday"])
            if expected_value.allow_check_in:
                self.assertEqual("Yes", received_value["allow_check_in"])
            else:
                self.assertEqual("No", received_value["allow_check_in"])

        # Check whether all headers are present
        for row in response.json()["data"]:
            self.assertTrue("pk" in row)
            self.assertTrue("date_of_holiday" in row)
            self.assertTrue("reason" in row)
            self.assertTrue("national_holiday" in row)
            self.assertTrue("allow_check_in" in row)
            self.assertTrue("action" in row)

        # Check the numbers of rows received is equal to the number of expected rows
        self.assertTrue(response.json()["recordsTotal"], len(holidays))
