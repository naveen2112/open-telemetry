"""
Django test classes for testing the create,
show, update, delete, and Datatables features in the Batch module
"""
import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Count, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import seq

from core.base_test import BaseTestCase
from core.constants import BATCH_DURATION_IN_MONTHS
from hubble.models import Batch, Holiday, TraineeHoliday


class BatchCreateTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in batch module
    """

    create_route_name = "batch.create"
    route_name = "batch"

    def setUp(self):
        """
        This function will run before every test and makes sure required
        data are ready
        """
        super().setUp()
        self.authenticate()
        self.create_holidays()
        self.update_valid_input()

    def update_valid_input(self):
        """
        This function is responsible for updating the valid inputs and
        creating data in databases as reqiured
        """
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "start_date": datetime.datetime.now().date() + datetime.timedelta(days=1),
        }

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name))
        self.assertTemplateUsed(response, "batch/batch_list.html")
        self.assertContains(response, "Batch List")

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        data = self.get_valid_inputs()
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_has("Batch", {"name": data["name"], "start_date": data["start_date"]})

        # Check whether the Holidays are created in the database
        end_date = data["start_date"] + relativedelta(months=BATCH_DURATION_IN_MONTHS)
        holidays = Holiday.objects.filter(
            date_of_holiday__range=(data["start_date"], end_date)
        ).values_list("date_of_holiday", flat=True)
        trainee_holidays = TraineeHoliday.objects.all().values_list("date_of_holiday", flat=True)
        self.assertEqual(set(holidays), set(trainee_holidays))

    def test_required_validation(self):
        """
        This function checks the required validation for the name field
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"name": "", "start_date": ""}),
        )
        field_errors = {"name": {"required"}, "start_date": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )

    def test_minimum_length_validation(self):
        """
        Check what happens when name field fails MinlengthValidation
        """
        data = self.get_valid_inputs(
            {
                "name": self.faker.pystr(max_chars=2),
                "start_date": datetime.datetime.now().date() + datetime.timedelta(days=1),
            }
        )
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"name": {"min_length"}}
        validation_paramters = {"name": 3}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                current_value=data,
                validation_parameter=validation_paramters,
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_date_validation(self):
        """
        Check what happens when start_date field fails DateValidation
        """
        data = self.get_valid_inputs(
            {
                "name": self.faker.name(),
                "start_date": "Invalid Date",
            }
        )
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"start_date": {"invalid"}}
        custom_validation_error_message = {"invalid": "Enter a valid date."}
        self.assertJSONEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=custom_validation_error_message,
            ),
        )
        # Check what happens if the start date is an holiday
        holday = baker.make("hubble.Holiday", date_of_holiday=timezone.now().date())
        data = self.get_valid_inputs(
            {
                "name": self.faker.name(),
                "start_date": holday.date_of_holiday,
            }
        )
        error_message = "The Selected date falls on a holiday, please reconsider the start date"
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"start_date": {"invalid_date"}}
        custom_validation_error_message = {"invalid_date": error_message}
        self.assertJSONEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=custom_validation_error_message,
            ),
        )


class BatchShowTest(BaseTestCase):
    """
    This class is responsible for testing the SHOW process in timeline module
    """

    update_show_route_name = "batch.show"

    def setUp(self):
        """
        This function will run before every test and makes sure required
        data are ready
        """
        super().setUp()
        self.authenticate()

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        batch = baker.make("hubble.Batch", start_date=datetime.datetime.now().date())
        response = self.make_get_request(reverse(self.update_show_route_name, args=[batch.id]))
        data = {"batch": model_to_dict(Batch.objects.get(id=batch.id))}
        data["batch"]["start_date"] = data["batch"]["start_date"].strftime("%Y-%m-%d")
        self.assertJSONEqual(
            self.decoded_json(response),
            data,
        )

    def test_failure(self):
        """
        To check what happens when invalid id is given as argument
        for batch update
        """
        response = self.make_get_request(reverse(self.update_show_route_name, args=[0]))
        self.assertEqual(response.status_code, 500)


class BatchUpdateTest(BaseTestCase):
    """
    This class is responsible for testing the UPDATE feature in timeline module
    """

    update_edit_route_name = "batch.edit"

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
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "start_date": datetime.datetime.now().date() + datetime.timedelta(days=1),
        }
        self.batch_id = baker.make("hubble.Batch").id

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        data = self.get_valid_inputs()
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.batch_id]),
            data=data,
        )
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_has("Batch", {"name": data["name"], "start_date": data["start_date"]})

    def test_required_validation(self):
        """
        This function checks the required validation for the name field
        """
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.batch_id]),
            data=self.get_valid_inputs(
                {
                    "name": "",
                    "start_date": "",
                }
            ),
        )
        field_errors = {"name": {"required"}, "start_date": {"required"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )

    def test_minimum_length_validation(self):
        """
        To check what happens when name field fails MinlengthValidation
        """
        data = self.get_valid_inputs(
            {
                "name": self.faker.pystr(max_chars=2),
                "start_date": datetime.datetime.now().date() + datetime.timedelta(days=1),
            }
        )
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.batch_id]),
            data=data,
        )
        field_errors = {"name": {"min_length"}}
        validation_paramters = {"name": 3}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                current_value=data,
                validation_parameter=validation_paramters,
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_date_validation(self):
        """
        To check what happens when start_date field fails DateValidation
        """
        data = self.get_valid_inputs(
            {
                "name": self.faker.name(),
                "start_date": "Invalid Date",
            }
        )
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.batch_id]),
            data=data,
        )
        field_errors = {"start_date": {"invalid"}}
        custom_validation_error_message = {"invalid": "Enter a valid date."}
        self.assertJSONEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=custom_validation_error_message,
            ),
        )
        # Check what happens if the start date is an holiday
        holday = baker.make("hubble.Holiday", date_of_holiday=timezone.now().date())
        data = self.get_valid_inputs(
            {
                "name": self.faker.name(),
                "start_date": holday.date_of_holiday,
            }
        )
        response = self.make_post_request(
            reverse(self.update_edit_route_name, args=[self.batch_id]), data=data
        )
        error_message = "The Selected date falls on a holiday, please reconsider the start date"
        field_errors = {"start_date": {"invalid_date"}}
        custom_validation_error_message = {
            "invalid_date": error_message,
        }
        self.assertJSONEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                custom_validation_error_message=custom_validation_error_message,
            ),
        )


class BatchDeleteTest(BaseTestCase):
    """
    This class is responsible for testing the DELETE feature in timeline module
    """

    delete_route_name = "batch.delete"

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
        batch = baker.make("hubble.Batch")
        response = self.make_delete_request(reverse(self.delete_route_name, args=[batch.id]))
        self.assertJSONEqual(response.content, {"message": "Batch deleted succcessfully"})
        self.assertEqual(response.status_code, 200)
        self.assert_database_not_has("Batch", {"id": batch.id})

    def test_failure(self):
        """
        To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(reverse(self.delete_route_name, args=[0]))
        self.assertEqual(response.status_code, 500)


class BatchDatatableTest(BaseTestCase):
    """
    This class is responsible for testing the Datatables present
    in the Batch module
    """

    datatable_route_name = "batch.datatable"
    route_name = "batch"

    def setUp(self):
        """
        This function will run before every test and makes sure required
        data are ready
        """
        super().setUp()
        self.authenticate()
        self.update_valid_input()

    def update_valid_input(self):
        """
        This function is responsible for updating the valid inputs and
        creating data in databases as reqiured
        """
        self.name = self.faker.name()
        self.batch = baker.make(
            "hubble.Batch",
            name=seq(self.name),
            start_date=datetime.datetime.now().date() + datetime.timedelta(days=1),
            _quantity=2,
        )
        self.persisted_valid_inputs = {
            "draw": 1,
            "start": 0,
            "length": 10,
            "search[value]": "",
        }

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(reverse(self.route_name))
        self.assertTemplateUsed(response, "batch/batch_list.html")
        self.assertContains(response, "Batch List")

    def test_datatable(self):
        """
        To check whether all columns are present in datatable
        and length of rows without any filter
        """
        batches = Batch.objects.annotate(
            total_trainee=Count(
                "sub_batches__intern_details",
                filter=Q(sub_batches__intern_details__deleted_at__isnull=True),
            ),
            number_of_sub_batches=Coalesce(
                Subquery(
                    Batch.objects.filter(sub_batches__batch_id=OuterRef("id"))
                    .annotate(
                        number_of_sub_batches=Count(
                            "sub_batches__id",
                            filter=Q(sub_batches__deleted_at__isnull=True),
                        )
                    )
                    .values("number_of_sub_batches")
                ),
                0,
            ),
        )
        response = self.make_post_request(
            reverse(self.datatable_route_name),
            data=self.get_valid_inputs(),
        )
        self.assertEqual(response.status_code, 200)

        # Check whether row details are correct
        for index, batch in enumerate(batches):
            expected_value = batch
            received_value = response.json()["data"][index]
            self.assertEqual(expected_value.pk, int(received_value["pk"]))
            self.assertEqual(expected_value.name, received_value["name"])
            self.assertEqual(
                expected_value.number_of_sub_batches,
                int(received_value["number_of_sub_batches"]),
            )
            self.assertEqual(
                expected_value.start_date.strftime("%d %b %Y"),
                received_value["start_date"],
            )

        # Check whether all headers are present
        for row in response.json()["data"]:
            self.assertTrue("pk" in row)
            self.assertTrue("name" in row)
            self.assertTrue("number_of_sub_batches" in row)
            self.assertTrue("total_trainee" in row)
            self.assertTrue("start_date" in row)
            self.assertTrue("action" in row)

        # Check the numbers of rows received is equal to the number of expected rows
        self.assertTrue(response.json()["recordsTotal"], len(self.batch))

    def test_database_search(self):
        """
        To check what happens when search value is given
        """
        search_value = self.name + "1"
        response = self.make_post_request(
            reverse(self.datatable_route_name),
            data=self.get_valid_inputs({"search[value]": search_value}),
        )
        self.assertTrue(
            response.json()["recordsTotal"],
            Batch.objects.filter(name__icontains=search_value).count(),
        )
