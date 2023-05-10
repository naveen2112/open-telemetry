from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, QueryDict
import os
import datetime 

from django.conf import settings
from django.http import FileResponse
from django.views.generic import TemplateView
from django.http import FileResponse
from ajax_datatable import AjaxDatatableView
from hubble.models import Timeline, Team, TimelineTask, User
from core import template_utils
from django.urls import reverse
from training.forms import TimelineForm, TimelineTaskForm
from core.custom_tags import show_label
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms.models import model_to_dict
from django.views.decorators.http import require_http_methods
from core.utils import CustomDatatable
from django.core.exceptions import ValidationError


class InductionKit(TemplateView):
    """
    Induction Kit
    """
    template_name = "induction_kit.html"
    # Getting the list of pdf files in the static folder.
    static_path = list(settings.STATICFILES_DIRS)
    extra_context = {
        "pdf_files": [
            file
            for file in os.listdir(f"{static_path[0]}/training/pdf")
            if os.path.splitext(file)[1] == ".pdf"
        ],
    }


def induction_kit_detail(request, text):
    """
    Induction Kit Detail
    """
    static_path = list(settings.STATICFILES_DIRS)
    file_path = f"{static_path[0]}/training/pdf/{text}"
    return FileResponse(open(file_path, "rb"), content_type="application/pdf")


def timeline_template(request):
    """
    Timeline Template
    """
    form = TimelineForm()
    return render(request, "timeline_template.html",{'form': form,})


class TimelineTemplateDataTable(CustomDatatable):
    print("bh")
    """
    Timeline Template Datatable
    """
    model = Timeline
    show_column_filters = False
    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": True},
        {"name": "is_active", "visible": True, "searchable": True},
        {'name': 'team', 'visible': True, "searchable": True, "foreign_field": "team__name"},
        {"name": "action", "title": "Action", "visible": True,"searchable": False,"orderable": False,"className": "text-center",},
    ]

    def customize_row(self, row, obj):
        buttons = template_utils.show_btn(reverse("timeline-template.detail", args=[obj.id]))\
                  + template_utils.edit_btn(obj.id)\
                  + template_utils.delete_btn(obj.id)\
                  + template_utils.duplicate_btn(obj.id)
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return
    
    def render_column(self, row, column):

        if column == 'is_active':
            if row.is_active:
                return '<span class="bg-mild-green-10 text-mild-green py-0.5 px-1.5 rounded-xl text-sm">Active</span>'
            else:
                return '<span class="bg-dark-red-10 text-dark-red py-0.5 px-1.5 rounded-xl text-sm">In Active</span>'
        return super().render_column(row, column)
    

    def get_initial_queryset(self, request=None):
        print(Timeline.objects.all())
        return Timeline.objects.all()

def create_timeline_template(request):
    """
    Create Timeline Template
    """
    if request.method == 'POST':
        user = User.objects.get(id = 58)
        form = TimelineForm(request.POST)
        if form.is_valid(): # Check if form is valid or not
            timeline = form.save(commit=False)
            timeline.is_active = True if request.POST.get('is_active') == 'true' else False # Set is_active to true if the input is checked else it will be false
            timeline.created_by = user
            timeline.save()
            return JsonResponse({"status": 'success'})
        else:
            field_errors = form.errors.as_json()  
            non_field_errors = form.non_field_errors().as_json()
            return JsonResponse({'status': 'error', 'field_errors': field_errors, 'non_field_errors': non_field_errors})
    

def timeline_update_form(request):
    """
    Timeline Template Update Form Data
    """
    id = request.GET.get('id')
    timeline = Timeline.objects.get(id = id)
    data = {'timeline': model_to_dict(timeline)} # Covert django queryset object to dict,which can be easily serialized and sent as a JSON response
    return JsonResponse(data, safe= False)


def update_timeline_template(request):
    """
    Update Timeline Template
    """
    id = request.POST.get('id')
    timeline = Timeline.objects.get(id = id)
    form = TimelineForm(request.POST, instance=timeline)
    if form.is_valid(): #check if form is valid or not
        timeline = form.save(commit=False)
        timeline.is_active = True if request.POST.get('is_active') == 'true' else False # Set is_active to true if the input is checked else it will be false
        timeline.save()
        return JsonResponse({"status": 'success'})
    else:
        field_errors = form.errors.as_json() 
        non_field_errors = form.non_field_errors().as_json()
        return JsonResponse({'status': 'error', 'field_errors': field_errors, 'non_field_errors': non_field_errors})

@require_http_methods(["DELETE"]) # This decorator ensures that the view function is only accessible through the DELETE HTTP method
def delete_timeline_template(request):
    """
    Delete Timeline Template 
    Soft delete the template and record the deletion time in deleted_at field
    """
    try: 
        delete = QueryDict(request.body) # Creates a QueryDict object from the request body
        id = delete.get('id') # Get id from dictionary
        timeline = get_object_or_404(Timeline, id=id)
        timeline.delete()
        return JsonResponse({"message": 'Timeline Template deleted succcessfully'})
    except Exception as e:
        return JsonResponse({'message': 'Error while deleting Timeline Template!'}, status=500)


def timeline_duplicate_form(request):
    """
    Timeline Template Form Data 
    """
    id = request.GET.get('id')
    timeline = Timeline.objects.get(id = id)
    data = {'timeline': model_to_dict(timeline)} # Covert django queryset object to dict,which can be easily serialized and sent as a JSON response
    return JsonResponse(data, safe= False)


def duplicate_timeline_template(request):
    """
    Duplicate Timeline Template
    """
    id = request.POST.get('id')
    user = User.objects.get(id = 58)
    timeline = Timeline.objects.get(id = id)
    form = TimelineForm(request.POST)
    if form.is_valid(): # Check the form is valid or not
        timeline = form.save(commit=False)
        timeline.is_active = True if request.POST.get('is_active') == 'true' else False # Set is_active to true if the input is checked else it will be false
        timeline.created_by = user
        timeline.save()
        timeline_task = TimelineTask.objects.filter(timeline_id = id) 
        for task in timeline_task:
            timetask = TimelineTask.objects.create(
                name = task.name, 
                days = task.days, 
                timeline_id = timeline, 
                present_type = task.present_type, 
                type = task.type, 
                created_by = task.created_by
            )
        return JsonResponse({"status": 'success'})
    else:
        field_errors = form.errors.as_json()
        non_field_errors = form.non_field_errors().as_json()
        return JsonResponse({'status': 'error', 'field_errors': field_errors, 'non_field_errors': non_field_errors})
    
    
def timeline_template_details(request, pk):
    """
    Timeline Template Detail
    Display the timeline template tasks for the current template
    """
    timeline = Timeline.objects.get(id = pk)
    form = TimelineTaskForm()
    context = {
        'timeline': timeline,
        'form': form,
        'timeline_id': pk
    }
    return render(request, 'timeline_template_detail.html', context)


class TimelineTemplateTaskDataTable(CustomDatatable):
    """
    Timeline Template Task Datatable
    """
    model = TimelineTask
    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": False},
        {"name": "days", "visible": True, "searchable": False},
        {"name": "present_type", "visible": True, "searchable": False},
        {"name": "task_type", "visible": True, "searchable": False},
        {"name": "action", "title": "Action", "visible": True,"searchable": False,"orderable": False,"className": "text-center",},
    ]


    def customize_row(self, row, obj):
        buttons = template_utils.edit_btn(obj.id)\
        + template_utils.delete_btn(obj.id)
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return
    

    def get_initial_queryset(self, request=None):
        return TimelineTask.objects.filter(timeline_id = request.POST.get('timeline_id'))


def create_timelinetask_template(request):
    """
    Create Timeline Template Task
    """
    if request.method == 'POST':
        form = TimelineTaskForm(request.POST)
        timeline = Timeline.objects.get(id = request.POST.get('timeline_id'))
        user = User.objects.get(id = 58)
        if form.is_valid(): # Check if the valid or not
            timeline_task = form.save(commit=False)
            timeline_task.timeline = timeline
            timeline_task.created_by = user
            timeline_task.save()
            return JsonResponse({"status": 'success'})
        else:
            field_errors = form.errors.as_json()
            non_field_errors = form.non_field_errors().as_json()
            return JsonResponse({'status': 'error', 'field_errors': field_errors, 'non_field_errors': non_field_errors})


def timelinetask_update_form(request):
    """
    Timeline Template Task Update Form Data
    """
    id = request.GET.get('id')
    timeline_task = TimelineTask.objects.get(id = id)
    data = {'timeline_task': model_to_dict(timeline_task)} # Covert django queryset object to dict,which can be easily serialized and sent as a JSON response
    return JsonResponse(data, safe= False)


def update_timelinetask_template(request):
    """
    Update Timeline Template Task
    """
    id = request.POST.get('id')
    timeline_task = TimelineTask.objects.get(id=id)
    form = TimelineTaskForm(request.POST, instance=timeline_task)
    if form.is_valid(): #Check if the valid or not
        form.save()
        return JsonResponse({"status": 'success'})
    else:
        field_errors = form.errors.as_json()
        non_field_errors = form.non_field_errors().as_json()
        return JsonResponse({'status': 'error', 'field_errors': field_errors, 'non_field_errors': non_field_errors})


@require_http_methods(["DELETE"]) # This decorator ensures that the view function is only accessible through the DELETE HTTP method
def delete_timelinetask_template(request):
    """
    Delete Timeline Template Task
    Soft delete the template and record the deletion time in deleted_at field
    """
    try: 
        delete = QueryDict(request.body) # Creates a QueryDict object from the request body
        id = delete.get('id') # Get id from dictionary
        timeline_task = get_object_or_404(TimelineTask, id=id)
        timeline_task.delete()
        return JsonResponse({"message": 'Timeline Template Task deleted succcessfully'})
    except Exception as e:
        return JsonResponse({'message': 'Error while deleting Timeline Template Task!'}, status=500)
    
