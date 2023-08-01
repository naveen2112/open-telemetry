from django.db.models import (Avg, Case, Count, F, OuterRef, Q, Subquery,
                              Value, When)
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import seq

from core.base_test import BaseTestCase
from core.constants import (ABOVE_AVERAGE, AVERAGE, GOOD, MEET_EXPECTATION,
                            NOT_YET_STARTED, POOR, TASK_TYPE_ASSESSMENT)
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
        self.another_sub_batch = baker.make("hubble.SubBatch", start_date=timezone.now().date())
        baker.make(
            "hubble.InternDetail",
            user__name=seq(self.name),
            sub_batch_id=self.sub_batch.id,
            _fill_optional=["expected_completion"],
            _quantity=7,
        )
        baker.make(
            "hubble.InternDetail",
            user__name=seq(self.name),
            sub_batch_id=self.another_sub_batch.id,
            _fill_optional=["expected_completion"],
            _quantity=7,
        )
        task = baker.make(
            "hubble.SubBatchTaskTimeline",
            task_type=TASK_TYPE_ASSESSMENT,
            days=seq(0),
            order=seq(0),
            sub_batch_id=self.sub_batch.id,
        )
        intern_details_iterator = InternDetail.objects.values_list("user__id", flat=True).iterator()
        baker.make(
            "hubble.assessment",
            task=task,
            user_id=intern_details_iterator,
            score=seq(start=40, increment_by=10, value=0),
            sub_batch_id=self.sub_batch.id,
            _quantity=6
        )
        task_count = (
            SubBatchTaskTimeline.objects.filter(
                sub_batch_id=self.sub_batch.id, task_type=TASK_TYPE_ASSESSMENT
            )
            .values("id")
            .count()
        )
        last_attempt_score = SubBatchTaskTimeline.objects.filter(
            id=OuterRef("user__assessments__task_id"),
            assessments__user_id=OuterRef("user_id"),
        ).order_by("-assessments__id")[:1]
        self.desired_output = (
            InternDetail.objects.filter(sub_batch__id=self.sub_batch.id)
            .select_related("user")
            .annotate(
                average_marks=Case(
                    When(
                        user_id=F("user__assessments__user_id"),
                        then=Coalesce(
                            Avg(
                                Subquery(last_attempt_score.values("assessments__score")),
                                distinct=True,
                            ),
                            0.0,
                        ),
                    ),
                    default=None,
                ),
                no_of_retries=Coalesce(
                    Count(
                        "user__assessments__is_retry",
                        filter=Q(Q(user__assessments__is_retry=True) & Q(user__assessments__extension__isnull=True)),
                    ),
                    0,
                ),
                completion=Coalesce(
                    (
                        Count(
                            "user__assessments__task_id",
                            filter=Q(user__assessments__user_id=F("user_id")),
                            distinct=True,
                        )
                        / float(task_count)
                    )
                    * 100,
                    0.0,
                ),
                performance=Case(
                    When(average_marks__gte=90, then=Value(GOOD)),
                    When(
                        Q(average_marks__lt=90) & Q(average_marks__gte=75),
                        then=Value(MEET_EXPECTATION),
                    ),
                    When(
                        Q(average_marks__lt=75) & Q(average_marks__gte=65),
                        then=Value(ABOVE_AVERAGE),
                    ),
                    When(
                        Q(average_marks__lt=65) & Q(average_marks__gte=50),
                        then=Value(AVERAGE),
                    ),
                    When(average_marks__lt=65, then=Value(POOR)),
                    default=Value(NOT_YET_STARTED),
                ),
            )
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
        self.assertContains(response, GOOD)
        self.assertContains(response, MEET_EXPECTATION)
        self.assertContains(response, ABOVE_AVERAGE)
        self.assertContains(response, AVERAGE)
        self.assertContains(response, POOR)

    def test_datatable(self):
        """
        To check whether all columns are present in datatable and length of rows without any filter
        """
        response = self.make_post_request(
            reverse(self.datatable_route_name), data=self.get_valid_inputs()
        )
        self.assertEqual(response.status_code, 200)
        for row in range(len(self.desired_output)):
            expected_value = self.desired_output[row]
            received_value = response.json()["data"][row]
            self.assertEqual(expected_value.pk, int(received_value["pk"]))
            self.assertEqual(expected_value.user.name, received_value["user"])
            self.assertEqual(expected_value.college, received_value["college"])
            self.assertEqual(
                round(expected_value.completion, 2), float(received_value["completion"])
            )
            if expected_value.average_marks == None:
                self.assertEqual("-", received_value["average_marks"])
            else:
                self.assertEqual(
                    round(expected_value.average_marks, 2), float(received_value["average_marks"])
                )
            self.assertEqual(expected_value.performance, received_value["performance"].split(">")[1].split("<")[0])
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
            self.assertTrue("performance" in row)
            self.assertTrue("average_marks" in row)
            self.assertTrue("completion" in row)
            self.assertTrue("no_of_retries" in row)
        self.assertEqual(response.json()["recordsTotal"], len(self.desired_output))

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
            GOOD: 0,
            MEET_EXPECTATION: 0,
            ABOVE_AVERAGE: 0,
            AVERAGE: 0,
            POOR: 0,
            NOT_YET_STARTED: 0,
        }
        response = self.make_post_request(
            reverse(self.datatable_route_name), data=self.get_valid_inputs()
        )
        for performance in self.desired_output:
            if performance.average_marks != None:
                if float(performance.average_marks) >= 90:
                    performance_report[GOOD] += 1
                elif 90 > float(performance.average_marks) >= 75:
                    performance_report[MEET_EXPECTATION] += 1
                elif 75 > float(performance.average_marks) >= 65:
                    performance_report[ABOVE_AVERAGE] += 1
                elif 65 > float(performance.average_marks) >= 50:
                    performance_report[AVERAGE] += 1
                elif float(performance.average_marks) < 50:
                    performance_report[POOR] += 1
            else:
                performance_report[NOT_YET_STARTED] += 1

        self.assertTrue("extra_data" in response.json())
        self.assertTrue(GOOD in response.json()["extra_data"]["performance_report"])
        self.assertTrue(
            MEET_EXPECTATION in response.json()["extra_data"]["performance_report"]
        )
        self.assertTrue(
            ABOVE_AVERAGE in response.json()["extra_data"]["performance_report"]
        )
        self.assertTrue(
            AVERAGE in response.json()["extra_data"]["performance_report"]
        )
        self.assertTrue(POOR in response.json()["extra_data"]["performance_report"])
        self.assertTrue(
            NOT_YET_STARTED in response.json()["extra_data"]["performance_report"]
        )

        self.assertTrue(
            performance_report[GOOD]
            == response.json()["extra_data"]["performance_report"][GOOD]
        )
        self.assertTrue(
            performance_report[MEET_EXPECTATION]
            == response.json()["extra_data"]["performance_report"][MEET_EXPECTATION]
        )
        self.assertTrue(
            performance_report[ABOVE_AVERAGE]
            == response.json()["extra_data"]["performance_report"][ABOVE_AVERAGE]
        )
        self.assertTrue(
            performance_report[AVERAGE]
            == response.json()["extra_data"]["performance_report"][AVERAGE]
        )
        self.assertTrue(
            performance_report[POOR]
            == response.json()["extra_data"]["performance_report"][POOR]
        )
        self.assertTrue(
            performance_report[NOT_YET_STARTED]
            == response.json()["extra_data"]["performance_report"][NOT_YET_STARTED]
        )

    def test_no_assignment(self):
        """
        To check what happens when no assignment is given
        """
        response = self.make_post_request(
            reverse(self.datatable_route_name), data=self.get_valid_inputs({"sub_batch": self.another_sub_batch.id})
        )
        self.assertEqual(response.status_code, 200)
