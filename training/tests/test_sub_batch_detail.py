from django.db.models import Avg, Count, OuterRef, Q, Subquery, Sum, F, Case, When, Value
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import seq

from core.base_test import BaseTestCase
from hubble.models import InternDetail, SubBatchTaskTimeline


class AddInternTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in SubBatchDetail module
    """

    route_name = "sub-batch.detail"
    create_route_name = "trainees.add"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.update_valid_input()

    def update_valid_input(self):
        """
        This function is responsible for updating the valid inputs and creating data in databases as reqiured
        """
        intern = baker.make("hubble.User", is_employed=False, _fill_optional=["email"])
        self.sub_batch = baker.make("hubble.SubBatch", start_date=timezone.now().date())
        baker.make(
            "hubble.SubBatchTaskTimeline",
            days=10,
            sub_batch=self.sub_batch,
            end_date=(timezone.now() + timezone.timedelta(10)).date(),
            order=1,
        )
        self.persisted_valid_inputs = {
            "user_id": intern.id,
            "college": self.faker.name(),
            "sub_batch_id": self.sub_batch.id,
        }

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(
            reverse(self.route_name, args=[self.sub_batch.id])
        )
        self.assertTemplateUsed(response, "sub_batch/sub_batch_detail.html")
        self.assertContains(response, self.sub_batch.name)

    def test_success(self):
        """
        Check what happens when valid data is given as input
        """
        data = self.get_valid_inputs()
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        self.assertJSONEqual(self.decoded_json(response), {"status": "success"})
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseHas(
            "InternDetail",
            {
                "user_id": data["user_id"],
                "college": data["college"],
                "sub_batch_id": data["sub_batch_id"],
            },
        )

    def test_required_validation(self):
        """
        This function checks the required validation for the team and name fields
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data={},
        )
        field_errors = {
            "user_id": {"required"},
            "college": {"required"},
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )

        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"sub_batch_id": ""}),
        )
        self.assertJSONEqual(
            self.decoded_json(response),
            {"message": "Invalid SubBatch id", "status": "error"},
        )

    def test_minimum_length_validation(self):
        """
        To check what happens when college field fails MinlengthValidation
        """
        data = self.get_valid_inputs({"college": self.faker.pystr(max_chars=2)})
        response = self.make_post_request(reverse(self.create_route_name), data=data)
        field_errors = {"college": {"min_length"}}
        validation_paramters = {"college": 3}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                current_value=data,
                validation_parameter=validation_paramters,
            ),
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_choice_validation(self):
        """
        Check what happens when invalid data for user_id field is given as input
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"user_id": 0}),
        )
        field_errors = {"user_id": {"invalid_choice"}}
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(field_errors=field_errors),
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_sub_batch_id(self):
        """
        Check what happens when invalid sub_batch id is given as input
        """
        response = self.make_post_request(
            reverse(self.create_route_name),
            data=self.get_valid_inputs({"sub_batch_id": 0}),
        )
        field_errors = {"__all__": {""}}
        error_message = {"": "You are trying to add trainees to an invalid SubBatch"}
        non_field_errors = {
            "message": "You are trying to add trainees to an invalid SubBatch",
            "code": "",
        }
        self.assertEqual(
            self.bytes_cleaner(response.content),
            self.get_ajax_response(
                field_errors=field_errors,
                non_field_errors=non_field_errors,
                custom_validation_error_message=error_message,
            ),
        )


class DeleteInternTest(BaseTestCase):
    """
    This class is responsible for testing the DELETE feature in timeline module
    """

    delete_route_name = "trainee.remove"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()

    def test_success(self):
        """
        To check what happens when valid id is given for delete
        """
        trainee = baker.make("hubble.InternDetail")
        self.assertDatabaseHas("InternDetail", {"id": trainee.id})
        response = self.make_delete_request(
            reverse(self.delete_route_name, args=[trainee.id])
        )
        self.assertJSONEqual(
            response.content,
            {"message": "Intern has been deleted succssfully"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertDatabaseNotHas("InternDetail", {"id": trainee.id})

    def test_failure(self):
        """
        To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(reverse(self.delete_route_name, args=[0]))
        self.assertJSONEqual(
            response.content,
            {"message": "Error while deleting Trainee!"},
        )
        self.assertEqual(response.status_code, 500)


class TraineeDatatableTest(BaseTestCase):
    """
    This class is responsible for testing the Datatables present in the Batch module
    """

    datatable_route_name = "sub-batch.trainees-datatable"
    route_name = "sub-batch.detail"

    def setUp(self):
        """
        This function will run before every test and makes sure required data are ready
        """
        super().setUp()
        self.authenticate()
        self.update_valid_input()

    def update_valid_input(self):
        """
        This function is responsible for updating the valid inputs and creating data in databases as reqiured
        """
        self.name = self.faker.name()
        self.sub_batch = baker.make("hubble.SubBatch", start_date=timezone.now().date())
        baker.make(
            "hubble.InternDetail",
            user__name=seq(self.name),
            sub_batch_id=self.sub_batch.id,
            _fill_optional=["expected_completion"],
            _quantity=5,
        )
        baker.make(
            "hubble.SubBatchTaskTimeline",
            days=seq(0),
            order=seq(0),
            sub_batch_id=self.sub_batch.id
        )
        self.persisted_valid_inputs = {
            "draw": 1,
            "start": 0,
            "length": 10,
            "sub_batch": self.sub_batch.id,
        }

    def test_template(self):
        """
        To makes sure that the correct template is used
        """
        response = self.make_get_request(
            reverse(self.route_name, args=[self.sub_batch.id])
        )
        self.assertTemplateUsed(response, "sub_batch/sub_batch_detail.html")
        self.assertContains(response, self.sub_batch.name)
        self.assertContains(response, "Performance")
        self.assertContains(response, "Good")
        self.assertContains(response, "Meet Expectation")
        self.assertContains(response, "Above Average")
        self.assertContains(response, "Average")
        self.assertContains(response, "Poor")

    def test_datatable(self):
        """
        To check whether all columns are present in datatable and length of rows without any filter
        """
        task_count = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch_id=self.sub_batch.id
            )
            .values("id")
            .count()
        )
        retries = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch_id=self.sub_batch.id,
                assessments__user_id=OuterRef("user_id"),
                id=OuterRef("user__assessments__task_id"),
            )
            .annotate(
                count=Count("assessments__is_retry", filter=Q(assessments__is_retry=True)),
            )
            .values("assessments__user_id", "id", "count", "assessments__score")   
        )
        last_attempt = (
            SubBatchTaskTimeline.objects.filter(
                id=OuterRef("user__assessments__task_id"),
                assessments__user_id=OuterRef("user_id"),
            )
            .order_by("-assessments__id")[:1]
        )
        desired_output = (
            InternDetail.objects.filter(sub_batch__id=self.sub_batch.id)
            .select_related("user")
            .annotate(
                average_marks=Case(
                    When(
                        user_id=F("user__assessments__user_id"),
                        then=Coalesce(
                            Avg(
                                Subquery(last_attempt.values("assessments__score")),
                                distinct=True,
                            ),
                            0.0,
                        ),
                    ),
                    default=None,
                ),
                no_of_retries=Coalesce(
                    Sum(Subquery(retries.values("count")), distinct=True), 0
                ),
                completion=Coalesce(
                    (
                        Count("user__assessments__task_id", filter=Q(user__assessments__user_id=F("user_id")), distinct=True)
                        / float(task_count)
                    )
                    * 100,
                    0.0,
                ),
            )
        )
        response = self.make_post_request(
            reverse(self.datatable_route_name), data=self.get_valid_inputs()
        )
        self.assertEqual(response.status_code, 200)
        for row in range(len(desired_output)):
            expected_value = desired_output[row]
            received_value = response.json()["data"][row]
            self.assertEqual(expected_value.pk, int(received_value["pk"]))
            self.assertEqual(expected_value.user.name, received_value["user"])
            self.assertEqual(expected_value.college, received_value["college"])
            self.assertEqual(expected_value.completion, float(received_value["completion"]))
            if expected_value.average_marks == None:
                self.assertEqual(
                    "-", received_value["average_marks"]
                )
            else:
                self.assertEqual(
                    expected_value.average_marks, float(received_value["average_marks"])
                )
            self.assertEqual(
                expected_value.no_of_retries, int(received_value["no_of_retries"])
            )
            self.assertEqual(
                expected_value.expected_completion.strftime("%d %b %Y"),
                received_value["expected_completion"],
            )
        for row in response.json()["data"]:
            self.assertTrue("pk" in row)
            self.assertTrue("user" in row)
            self.assertTrue("college" in row)
            self.assertTrue("expected_completion" in row)
        self.assertTrue(response.json()["recordsTotal"], len(desired_output))

    def test_database_search(self):
        """
        To check what happens when search value is given
        """
        search_value = self.name + "1"
        response = self.make_post_request(
            reverse(self.datatable_route_name),
            data=self.get_valid_inputs({"search[value]": search_value}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.json()["recordsTotal"],
            InternDetail.objects.filter(user__name__icontains=search_value).count(),
        )

    def test_performance_report(self):
        """
        To ensure that the received performance reports are valid
        """
        performance_report = {
            "Good": 0,
            "Meet Expectation": 0,
            "Above Average": 0,
            "Average": 0,
            "Poor": 0,
        }
        response = self.make_post_request(
            reverse(self.datatable_route_name), data=self.get_valid_inputs()
        )
        for performance in response.json()["data"]:
            if performance["average_marks"] != "-":
                if float(performance["average_marks"]) >= 90:
                    performance_report["Good"] += 1
                elif 90 > float(performance["average_marks"]) >= 75:
                    performance_report["Meet Expectation"] += 1
                elif 75 > float(performance["average_marks"]) >= 65:
                    performance_report["Above Average"] += 1
                elif 65 > float(performance["average_marks"]) >= 50:
                    performance_report["Average"] += 1
                elif float(performance["average_marks"]) < 50:
                    performance_report["Poor"] += 1

        self.assertTrue("extra_data" in response.json())
        self.assertTrue("Good" in response.json()["extra_data"])
        self.assertTrue("Meet Expectation" in response.json()["extra_data"])
        self.assertTrue("Above Average" in response.json()["extra_data"])
        self.assertTrue("Average" in response.json()["extra_data"])
        self.assertTrue("Poor" in response.json()["extra_data"])

        self.assertTrue(
            performance_report["Good"] == response.json()["extra_data"]["Good"]
        )
        self.assertTrue(
            performance_report["Meet Expectation"]
            == response.json()["extra_data"]["Meet Expectation"]
        )
        self.assertTrue(
            performance_report["Above Average"]
            == response.json()["extra_data"]["Above Average"]
        )
        self.assertTrue(
            performance_report["Average"] == response.json()["extra_data"]["Average"]
        )
        self.assertTrue(
            performance_report["Poor"] == response.json()["extra_data"]["Poor"]
        )
