from django.test import TestCase, Client
from model_bakery import baker
from hubble.models import User, Timeline
from training.tests.base import BaseTestCase
from training.forms import TimelineForm
from django.urls import reverse



    
    
    # def create_timeline(self, is_active_choice = False):
    #     new_timeline = baker.prepare(Timeline, _save_related = True)
    #     return {
    #         "name": new_timeline.name,
    #         "team": new_timeline.team,
    #         "is_active": is_active_choice,
    #     }
        
    # def create_second_timeline(self, data):
    #     return {
    #         "name": 'test',
    #         "team": data.team,
    #         "is_active": data.is_active
    #     }
    
    # def update_timeline(self):
    #     timeline = baker.make(Timeline, is_active = True)
    #     return baker.prepare(Timeline, team = timeline.team, is_active = False)
    
    # def delete_timeline(self):
    #     data = self.create_timeline()
    #     return Timeline.objects.latest('id')
    
    # def get_datatable(self):
    #     response = self.login_user()
    #     create = self.create_timeline()
    #     payload = {
    #         "draw": 1,
    #         "columns[0][data]": "pk",
    #         "columns[0][name]": "pk",
    #         "columns[0][searchable]": False,
    #         "columns[0][orderable]": False,
    #         "columns[0][search][value]": '',
    #         "columns[0][search][regex]": False,
    #         "columns[1][data]": "name",
    #         "columns[1][name]": "name",
    #         "columns[1][searchable]": True,
    #         "columns[1][orderable]": True,
    #         "columns[1][search][value]": '',
    #         "columns[1][search][regex]": False,
    #         "columns[2][data]": "Days",
    #         "columns[2][name]": "Days",
    #         "columns[2][searchable]": True,
    #         "columns[2][orderable]": True,
    #         "columns[2][search][value]": '',
    #         "columns[2][search][regex]": False,
    #         "columns[3][data]": "is_active",
    #         "columns[3][name]": "is_active",
    #         "columns[3][searchable]": True,
    #         "columns[3][orderable]": True,
    #         "columns[3][search][value]": "",
    #         "columns[3][search][regex]": False,
    #         "columns[4][data]": "team",
    #         "columns[4][name]": "team",
    #         "columns[4][searchable]": True,
    #         "columns[4][orderable]": True,
    #         "columns[4][search][value]": "",
    #         "columns[4][search][regex]": False,
    #         "columns[5][data]": "action",
    #         "columns[5][name]": "action",
    #         "columns[5][searchable]": False,
    #         "columns[5][orderable]": False,
    #         "columns[5][search][value]": '' ,
    #         "columns[5][search][regex]": False,
    #         "start": 0,
    #         "length": 10,
    #         "search[value]": '', 
    #         "search[regex]": False
    #     }
    #     return self.client.post("/timeline-datatable", data = payload)
    
    # def get_timeline_task(self):
    #     response = self.login_user()
    #     timeline_id = Timeline.objects.latest(id)
    #     return self.client.post(f"/timeline-template/{timeline_id.id}")

        

    

class TimelineCreate(BaseTestCase):

    route_name = "timeline-template"
    create_route_name = "timeline-template.create"

    def test_templates(self):
        """
            To make sure that the correct template is used
        """
        response = self.make_create_get_request(self.route_name)
        self.assertTemplateUsed(response, "timeline_template.html")
        self.assertTemplateNotUsed(response, "timeline_template_detail.html")

    def test_success(self):
        """
            Check what happens when valid data is given as input
        """
        self.make_create_get_request(self.route_name)
        response = self.make_create_post_request(self.create_route_name, data={"name": self.faker.name(), "team": self.create_user().team, "is_active": False})
        self.assertJSONEqual(response.content, {"status": "success"})
        response = self.make_create_post_request(self.create_route_name, data={"name": self.faker.name(), "team": self.create_user().team, "is_active": True})
        self.assertJSONEqual(response.content, {"status": "success"})

    def test_failure_is_active(self):
        """
            Check what happens when invalid data for is_active field is given as input
        """
        self.make_create_get_request(self.route_name)
        team = self.create_user().team
        form_data = {"name": self.faker.name(), "team": team, "is_active": True}
        response = self.make_create_post_request(self.create_route_name, data=form_data)
        check_response = self.make_create_post_request(self.create_route_name, data=form_data)
        # self.assertJSONEqual(check_response.content, {"status": "error"})
        self.assertFormError(check_response, 'form', 'is_active', "Team already has an active template.")

    def test_failure_team(self):
        """
            Check what happens when invalid data for team field is given as input
        """
        self.make_create_get_request(self.route_name)
        response = self.make_create_post_request(self.create_route_name, data={"name": self.faker.name(), "team": "", "is_active": True})
        # self.assertJSONEqual(response.content, {"status": "error"})
        self.assertFormError(response, "form", "team", "This field is required.")
        response = self.make_create_post_request(self.create_route_name, data={"name": self.faker.name(), "team": self.faker.name(), "is_active": True})
        # self.assertJSONEqual(response.content, {"status": "error"})
        self.assertFormError(response, "form", "team", "Select a valid choice.")


    def test_failure_name(self):
        """
            Check what happens when invalid data for name field is given as input
        """
        self.make_create_get_request(self.route_name)
        response = self.make_create_post_request(self.create_route_name, data={"name": "", "team": self.create_user().team, "is_active": True})
        # self.assertJSONEqual(response.content, {"status": "error"})
        self.assertFormError(response, "form", "name", "This field is required.")
        response = self.make_create_post_request(self.create_route_name, 1, data={"name": self.faker.pystr(min_chars=2, max_chars=2), "team": self.create_user().team, "is_active": False})
        self.assertFormError(response, "form", "name", "Ensure this value has at least 3 characters (it has 2).")


class TimelineUpdate(BaseTestCase):
    update_show_route_name = "timeline-template.show"
    update_edit_route_name = "timeline-template.edit"

    def test_success_show(self):
        self.make_update_get_request(self.update_show_route_name, 1)
        self.assertEqual() #TODO::Need to be updated

    def test_failure_show(self):
        self.make_update_get_request(self.update_show_route_name, -1) #negative will not be in ids
        self.assertEqual() #TODO::Need to be updated

    def test_success_edit(self):
        """
            Check what happens when valid data is given as input
        """
        response = self.make_update_post_request(self.update_edit_route_name, 1, data={"name": self.faker.name(), "team": self.create_user().team, "is_active": False})
        self.assertJSONEqual(response.content, {"status": "success"})
        response = self.make_update_post_request(self.update_edit_route_name, 1, data={"name": self.faker.name(), "team": self.create_user().team, "is_active": True})
        self.assertJSONEqual(response.content, {"status": "success"})

    def test_failure_is_active_edit(self):
        """
            Check what happens when invalid data for is_active field is given as input
        """        
        team = self.create_user().team
        form_data = {"name": self.faker.name(), "team": team, "is_active": True}
        response = self.make_update_post_request(self.update_edit_route_name, 1, data=form_data)
        check_response = self.make_update_post_request(self.update_edit_route_name, 1, data=form_data)
        self.assertFormError(check_response, 'form', 'is_active', "Team already has an active template.")

    def test_failure_team(self):
        """
            Check what happens when invalid data for team field is given as input
        """
        response = self.make_update_post_request(self.update_edit_route_name, 1, data={"name": self.faker.name(), "team": "", "is_active": False})
        self.assertFormError(response, "form", "team", "This field is required.")
        response = self.make_update_post_request(self.update_edit_route_name, 1, data={"name": self.faker.name(), "team": self.faker.name(), "is_active": False})
        self.assertFormError(response, "form", "team", "Select a valid choice.")

    def test_failure_name(self):
        """
            Check what happens when invalid data for name field is given as input
        """
        response = self.make_update_post_request(self.update_edit_route_name, 1, data={"name": "", "team": self.create_user().team, "is_active": False})
        self.assertFormError(response, "form", "name", "This field is required.")
        response = self.make_update_post_request(self.update_edit_route_name, 1, data={"name": self.faker.pystr(min_chars=2, max_chars=2), "team": self.create_user().team, "is_active": False})
        self.assertFormError(response, "form", "name", "Ensure this value has at least 3 characters (it has 2).")


class TimelineDelete(BaseTestCase):
    delete_route_name = "timeline-template.delete"

    def test_success(self):
        """
            To check what happens when valid id is given for delete
        """
        response = self.make_delete_request(self.delete_route_name, 1)
        self.assertJSONEqual(response.content, {"message": "Timeline Template deleted succcessfully"})

    def test_failure(self):
        """
            To check what happens when invalid id is given for delete
        """
        response = self.make_delete_request(self.delete_route_name, -1)
        self.assertJSONEqual(response.content, {"message": "Error while deleting Timeline Template!"})        


class TimelineDuplicate(BaseTestCase):
    duplicate_route_name = "timeline-template.create"

    def test_success(self):
        """
            Check what happens when valid data is given as input
        """
        response = self.make_create_post_request(self.duplicate_route_name, data={"name": self.faker.name(), "team": self.create_user().team, "is_active": False, "id":1})
        self.assertJSONEqual(response.content, {"status": "success"})
        response = self.make_create_post_request(self.duplicate_route_name, data={"name": self.faker.name(), "team": self.create_user().team, "is_active": True, "id":1})
        self.assertJSONEqual(response.content, {"status": "success"})

    def test_failure_is_active(self):
        """
            Check what happens when invalid data for is_active field is given as input
        """
        self.make_create_get_request(self.duplicate_route_name)
        team = self.create_user().team
        form_data = {"name": self.faker.name(), "team": team, "is_active": True, "id":1}
        response = self.make_create_post_request(self.create_route_name, data=form_data)
        check_response = self.make_create_post_request(self.create_route_name, data=form_data)
        self.assertFormError(check_response, 'form', 'is_active', "Team already has an active template.")

    def test_failure_team(self):
        """
            Check what happens when invalid data for team field is given as input
        """
        self.make_create_get_request(self.duplicate_route_name)
        response = self.make_create_post_request(self.duplicate_route_name, data={"name": self.faker.name(), "team": "", "is_active": True, "id":1})
        self.assertFormError(response, "form", "team", "This field is required.")
        response = self.make_create_post_request(self.duplicate_route_name, data={"name": self.faker.name(), "team": self.faker.name(), "is_active": True, "id":1})
        self.assertFormError(response, "form", "team", "Select a valid choice.")


    def test_failure_name(self):
        """
            Check what happens when invalid data for name field is given as input
        """
        self.make_create_get_request(self.duplicate_route_name)
        response = self.make_create_post_request(self.duplicate_route_name, data={"name": "", "team": self.create_user().team, "is_active": True, "id":1})
        self.assertFormError(response, "form", "name", "This field is required.")
        response = self.make_create_post_request(self.duplicate_route_name, 1, data={"name": self.faker.pystr(min_chars=2, max_chars=2), "team": self.create_user().team, "is_active": False, "id":1})
        self.assertFormError(response, "form", "name", "Ensure this value has at least 3 characters (it has 2).")

    




        













    # def test_timeline_creation(self):
    #     response = self.login_user()
    #     check_error = self.client.post("/create")
    #     expected_response = {"status": "success"}
    #     self.assertTrue(check_error.status_code, 200)
    #     self.assertEqual(check_error['Content-Type'], "application/json")
    #     self.assertJSONNotEqual(check_error.content, expected_response)
    #     create_timeline = self.client.post("/create", data= self.create_timeline(is_active_choice=True))
    #     self.assertTrue(create_timeline.status_code, 200)
    #     self.assertEqual(create_timeline['Content-Type'], "application/json")
    #     self.assertJSONEqual(create_timeline.content, expected_response)

    # def test_timetime_create_is_active(self):
    #     response = self.login_user()
    #     timeline1 = self.client.post("/create", data=self.create_timeline(is_active_choice=True))
    #     data = Timeline.objects.latest('id')
    #     timeline2 = self.client.post("/create", data=self.create_second_timeline(data))
    #     expected_success_content = {"status": "success"}
    #     expected_error_content = {"status": "error", "field_errors": "{\"is_active\": [{\"message\": \"Team already has an active template.\", \"code\": \"\"}]}", "non_field_errors": "[]"}
    #     self.assertJSONEqual(str(timeline2.content, encoding='utf-8'), expected_error_content)
    #     self.assertJSONNotEqual(str(timeline2.content, encoding='utf-8'), expected_success_content)
    #     data.is_active = False
    #     timeline = self.client.post("/create", data=self.create_second_timeline(data))
    #     self.assertJSONEqual(str(timeline.content, encoding='utf-8'), expected_success_content)

    # def test_timeline_create_invalid_data(self):
    #     response = self.login_user()
    #     expected_success_content = {"status": "success"}
    #     expected_error_content = {"status": "error"}
    #     data = self.create_timeline()
    #     data.team = ''
    #     timeline1 = self.client.post("/create", data=self.create_timeline())
    #     self.assertJSONEqual(timeline1.content.get('status'), expected_error_content['status'])
    #     data = self.create_timeline()
    #     data.name = ''
    #     timeline1 = self.client.post("/create", data=self.create_timeline())
    #     self.assertJSONEqual(timeline1.content.get('status'), expected_error_content['status'])
    #     data = self.create_timeline()
    #     timeline1 = self.client.post("/create", data=self.create_timeline())
    #     self.assertJSONEqual(timeline1.content, expected_success_content)





    # def test_timeline_update(self):
    #     response = self.login_user()
    #     update = self.update_timeline()
    #     check_error = self.client.post(f"/{update.id}/edit", data={})
    #     expected_response = {"status": "success"}
    #     self.assertTrue(check_error.status_code, 200)
    #     self.assertEqual(check_error['Content-Type'], "application/json")
    #     self.assertJSONNotEqual(check_error.content, expected_response)
    #     update_timeline = self.client.post(f"/{update.id}/edit", data = {
    #         "name" : update.name,
    #         "team" : update.team,
    #         "is_active" : update.is_active
    #     })
    #     self.assertTrue(update_timeline.status_code, 200)
    #     self.assertEqual(update_timeline['Content-Type'], "application/json")
    #     self.assertJSONEqual(update_timeline.content, expected_response)

    
    # def test_timetime_update_with_invalid_data(self):
    #     response = self.login_user()
    #     update = self.update_timeline()
    #     expected_success_content = {"status": "success"}
    #     expected_error_content = {"status": "error"}
    #     check_error_name = self.client.post(f"/{update.id}/edit", data={
    #         "name" : '',
    #         "team" : update.team,
    #         "is_active" : update.is_active
    #     })
    #     self.assertJSONEqual(check_error_name.content.get('status'), expected_error_content)
    #     check_error_team = self.client.post(f"/{update.id}/edit", data={
    #         "name" : update.name,
    #         "team" : '',
    #         "is_active" : update.is_active
    #     })
    #     self.assertJSONEqual(check_error_team.content.get('status'), expected_error_content)
    #     check_error_is_active = self.client.post(f"/{update.id}/edit", data={
    #         "name" : update.name,
    #         "team" : update.team,
    #         "is_active" : True
    #     })
    #     self.assertJSONEqual(check_error_team.content.get('status'), expected_error_content)
    #     check_both_empty = self.client.post(f"/{update.id}/edit", data={
    #         "name" : '',
    #         "team" : '',
    #         "is_active" : False
    #     })
    #     self.assertJSONEqual(check_error_team.content.get('status'), expected_error_content)
    #     check_all_invalid = self.client.post(f"/{update.id}/edit", data={
    #         "name" : '',
    #         "team" : '',
    #         "is_active" : True
    #     })
    #     self.assertJSONEqual(check_all_invalid.content.get('status'), expected_error_content)


    # def test_timeline_delete(self):
    #     response = self.login_user()
    #     no_of_data_before_delete = Timeline.objects.count()
    #     delete = self.delete_timeline()
    #     expected_response = {"message": "Timeline Template deleted succcessfully"}
    #     delete_timeline = self.client.delete(f"/{delete.id}/edit")
    #     self.assertEqual(delete_timeline.request.method, "DELETE")
    #     self.assertTrue(delete_timeline.status_code, 200)
    #     self.assertEqual(delete_timeline['Content-Type'], "application/json")
    #     self.assertJSONEqual(delete_timeline.content, expected_response)
    #     no_of_data_after_delete = Timeline.objects.count()
    #     self.assertEqual(no_of_data_after_delete, no_of_data_before_delete - 1)























    # def test_timeline_datatable(self):
    #     response = self.get_datatable()
    #     self.assertTrue(response.status_code, 200)
    #     self.assertEqual(response["Content-Type"], "application/json")
    #     self.assertTrue("draw" in response.json())
    #     self.assertTrue("recordsTotal" in response.json())
    #     self.assertTrue("recordsFiltered" in response.json())
    #     self.assertTrue(len(response.json["data"]) >= 1)
    #     self.assertTrue("pk" in response.json["data"][0])
    #     self.assertTrue("name" in response.json["data"][0])
    #     self.assertTrue("Days" in response.json["data"][0])
    #     self.assertTrue("is_active" in response.json["data"][0])    

    # def test_timeline_links(self):
    #     response = self.login_user()
    #     self.assertContains(response, 'Create Timeline')
    #     self.assertContains(response, "<a href='/timeline-template/3'>")    
    #     self.assertContains(response, "'/timeline-template/3/show')")
    #     self.assertContains(response, "'/timeline-template/3/delete'")
    #     self.assertContains(response, "'/timeline-template/3/show')")

    # def test_datatable_presence_of_dom(self):
    #     response = self.login_user()
    #     self.assertContains(response, '<input type="text" value="" name="search_project"')
    #     self.assertContains(response, 'id="timeline-table_info"')
    #     self.assertContains(response, 'id="timeline-table_paginate">')

    # def test_detailed_timeline(self):
    #     response = self.get_timeline_task()
    #     self.assertTrue(response.status_code, 200)
    #     self.assertContains(response, '<table id="timeline-table"')
    #     self.assertNotContains(response, "<tbody>")

    # def test_detailed_timeline_create(self):
    #     pass


        


