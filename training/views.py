from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import os
import datetime 
from django.conf import settings
from django.views.generic import TemplateView
from django.http import FileResponse
from ajax_datatable import AjaxDatatableView
from hubble.models import Timeline, Teams, TimelineTask, Users
from core import template_utils
from django.urls import reverse
from training.forms import TimelineForm, TimelineTaskForm
from core.custom_tags import show_label
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms.models import model_to_dict
from django.views.decorators.http import require_http_methods
from core.utils import CustomDatatable


class InductionKit(TemplateView):
    template_name = "induction_kit.html"
    # Getting the list of pdf files in the static folder.
    static_path = list(settings.STATICFILES_DIRS)
    extra_context = {
        "pdf_files": [file for file in os.listdir(f"{static_path[0]}/training/pdf") if os.path.splitext(file)[1] == ".pdf"
        ],
    }


def induction_kit_detail(request, text):
    static_path = list(settings.STATICFILES_DIRS)
    file_path = f"{static_path[0]}/training/pdf/{text}"
    return FileResponse(open(file_path, "rb"), content_type="application/pdf")


def timeline_template(request):
    form = TimelineForm()
    return render(request, "timeline_template.html",{'form': form,})


class TimelineTemplate(TemplateView):
    template_name = 'timeline_template.html'
    form_class = TimelineForm


class TimelineTemplateDataTable(CustomDatatable):
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
                  + template_utils.delete_btn(obj.id)
        row["action"] = f'<div class="form-inline justify-content-center">{buttons}</div>'
        return


def create_timeline_template(request):
    if request.method == 'POST':
        user = Users.objects.get(id = 58)
        form = TimelineForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": 'success'})
        else:
            field_errors = form.errors.as_json()
            non_field_errors = form.non_field_errors().as_json()
            return JsonResponse({'status': 'error', 'field_errors': field_errors, 'non_field_errors': non_field_errors})
    

def timeline_update_form(request):
    id = request.GET.get('id')
    timeline = Timeline.objects.get(id = id)
    data = {'timeline': model_to_dict(timeline)}
    return JsonResponse(data, safe= False)


def update_timeline_template(request):
    id = request.POST.get('id')
    timeline = Timeline.objects.get(id = id)
    form = TimelineForm(request.POST, instance=timeline)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": 'success'})
    else:
        field_errors = form.errors.as_json()
        non_field_errors = form.non_field_errors().as_json()
        return JsonResponse({'status': 'error', 'field_errors': field_errors, 'non_field_errors': non_field_errors})


def delete_timeline_template(request):
    try: 
        id = request.POST.get('id')
        timeline = get_object_or_404(Timeline, id=id)
        timeline.delete()
        return JsonResponse({"message": 'Timeline Template deleted succcessfully'})
    except Exception as e:
        return JsonResponse({'message': 'Error while deleting Timeline Template!'}, status=500)

    
def timeline_template_details(request, pk):
    timeline = Timeline.objects.get(id = pk)
    form = TimelineTaskForm()
    context = {
        'timeline': timeline,
        'form': form,
        'timeline_id': pk
    }
    return render(request, 'timeline_template_detail.html', context)



class TimelineTemplateTaskDataTable(CustomDatatable):
    model = TimelineTask
    column_defs = [
        {"name": "id", "visible": False, "searchable": False},
        {"name": "name", "visible": True, "searchable": False},
        {"name": "days", "visible": True, "searchable": False},
        {"name": "present_type", "visible": True, "searchable": False},
        {"name": "type", "visible": True, "searchable": False},
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
    if request.method == 'POST':
        form = TimelineTaskForm(request.POST)
        timeline = Timeline.objects.get(id = request.POST.get('timeline_id'))
        user = Users.objects.get(id = 58)
        if form.is_valid():
            form.save(commit=False)
            form.timeline_id = timeline
            form.created_by = user
            form.save()
            return JsonResponse({"status": 'success'})
        else:
            field_errors = form.errors.as_json()
            non_field_errors = form.non_field_errors().as_json()
            return JsonResponse({'status': 'error', 'field_errors': field_errors, 'non_field_errors': non_field_errors})


def timelinetask_update_form(request):
    id = request.GET.get('id')
    timeline_task = TimelineTask.objects.get(id = id)
    data = {'timeline_task': model_to_dict(timeline_task)}
    return JsonResponse(data, safe= False)


def update_timelinetask_template(request):
    id = request.POST.get('id')
    timeline_task = TimelineTask.objects.get(id=id)
    form = TimelineTaskForm(request.POST, instance=timeline_task)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": 'success'})
    else:
        field_errors = form.errors.as_json()
        non_field_errors = form.non_field_errors().as_json()
        return JsonResponse({'status': 'error', 'field_errors': field_errors, 'non_field_errors': non_field_errors})


def delete_timelinetask_template(request):
    try: 
        id = request.POST.get('id')
        timeline_task = get_object_or_404(TimelineTask, id=id)
        timeline_task.delete()
        return JsonResponse({"message": 'Timeline Template Task deleted succcessfully'})
    except Exception as e:
        return JsonResponse({'message': 'Error while deleting Timeline Template Task!'}, status=500)

