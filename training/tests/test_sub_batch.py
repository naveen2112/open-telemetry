from django.forms.models import model_to_dict
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import seq
from django.conf import settings
from django.utils import timezone
from training.forms import SubBatchForm

from core.base_test import BaseTestCase
from hubble.models import SubBatch, User


class SubBatchCreateTest(BaseTestCase):
    """
    This class is responsible for testing the CREATE feature in batch module
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

    def update_valid_input(self):
        self.batch_id = baker.make("hubble.Batch").id
        baker.make("hubble.User", is_employed=True, _fill_optional=["email"], employee_id=seq(0), _quantity=5)
        baker.make("hubble.User", is_employed=False, _fill_optional=["email"], employee_id=seq(5), _quantity=5)
        primary_mentor_id = User.objects.get(employee_id=1).id
        secondary_mentor_id = User.objects.get(employee_id=2).id
        team_id = self.create_team().id
        timeline = baker.make(
            "hubble.Timeline", team_id=team_id
        )
        baker.make(
            "hubble.TimelineTask",
            timeline_id=timeline.id,
            _fill_optional=["order"],
            _quantity=5,
            days=2
        )
        self.persisted_valid_inputs = {
            "name": self.faker.name(),
            "team": team_id,
            "start_date": timezone.now().date(),
            "timeline": timeline.id,
            "primary_mentor_id": primary_mentor_id,
            "secondary_mentor_id": secondary_mentor_id
        }

    def get_file_path(self):
        static_path = list(settings.STATICFILES_DIRS)
        return f"{static_path[0]}/training/pdf/Sample_Intern_Upload.xlsx"


    def test_success(self):
        
        with open(self.get_file_path(), 'rb') as sample_file:
            data = self.get_valid_inputs({"users_list_file": sample_file})
            response = self.make_post_request(reverse(self.create_route_name, args=[self.batch_id]), data=data)
            self.assertRedirects(response, reverse(self.route_name, args=[self.batch_id]))
            self.assertEqual(response.status_code, 302)
            self.assertDatabaseHas(
                "SubBatch",
                {
                    "name": data["name"],
                    "team_id": data["team"],
                    "timeline_id": data["timeline"],
                    "start_date": data["start_date"]
                }
            )
            # self.assertFormError(SubBatchForm(data=data), "team", "This field is required.")
            # self.get_form_errors(key="primary_mentor_id", value="invalid_choice", form=SubBatchForm(data=data))
            # self.get_form_errors(key="team", value="required", form=SubBatchForm(data=data))
            # self.get_form_errors(key="name", value="min_length", current_value=data, validation_parameter={"name": 3}, form=SubBatchForm(data=data))

    def test_required_validation(self):
        
        with open(self.get_file_path(), 'rb') as sample_file:
            data = self.get_valid_inputs({"users_list_file": sample_file, "name": "", "team": "", "timeline": "", "primary_mentor_id": "", "secondary_mentor_id": ""})
            self.make_post_request(reverse(self.create_route_name, args=[self.batch_id]), data=data)
            field_errors = {"name" : {"required"}, "team" : {"required"}, "timeline" : {"required"}, "primary_mentor_id" : {"required"}, "secondary_mentor_id" : {"required"}}
            self.get_form_errors(field_errors=field_errors, form=SubBatchForm(data=data))

    def test_invalid_choice_validation(self):
        
        with open(self.get_file_path(), 'rb') as sample_file:
            data = self.get_valid_inputs({"users_list_file": sample_file, "team": self.faker.name(), "timeline": self.faker.name(), "primary_mentor_id": self.faker.name(), "secondary_mentor_id": self.faker.name()})
            self.make_post_request(reverse(self.create_route_name, args=[self.batch_id]), data=data)
            field_errors = {"team" : {"invalid_choice"}, "timeline" : {"invalid_choice"}, "primary_mentor_id" : {"invalid_choice"}, "secondary_mentor_id" : {"invalid_choice"}}
            self.get_form_errors(field_errors=field_errors, form=SubBatchForm(data=data))

    def test_min_length_validation(self):
        
        with open(self.get_file_path(), 'rb') as sample_file:
            data = self.get_valid_inputs({"users_list_file": sample_file, "name": self.faker.pystr(max_chars=2)})
            self.make_post_request(reverse(self.create_route_name, args=[self.batch_id]), data=data)
            field_errors = {"name" : {"min_length"}}
            self.get_form_errors(field_errors=field_errors, current_value=data, validation_parameter={"name": 3}, form=SubBatchForm(data=data))

    def test_file_validation(self):
        # with open(self.get_file_path(), 'rb') as sample_file:
        #     data = self.get_valid_inputs({"users_list_file": sample_file, "name": self.faker.pystr(max_chars=2)})
        data = self.get_valid_inputs()
        response = self.make_post_request(reverse(self.create_route_name, args=[self.batch_id]), data=data)
        print(response.content)
        # form = 
        # print(SubBatchForm(data, auto_id = False))
        # self.assertIn( "Please upload a file", SubBatchForm(data=data).errors)