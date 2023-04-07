from django.urls import path
from training import views
 
urlpatterns = [
    # Induction kit
    path("induction-kit", views.InductionKit.as_view(), name="induction-kit"),
    path("induction-kit/<text>", views.induction_kit_detail, name="induction-kit.detail"),
    
    # Timeline Template
    path("timeline-template", views.timeline_template, name="timeline-template"),
    path("timeline-datatable", views.TimelineTemplateDataTable.as_view(), name="timeline-template.datatable"),
    path("timeline-template/create-timeline-template", views.create_timeline_template, name="timeline-template.create"),
    path("timeline-template/timeline-update-form", views.timeline_update_form, name="timeline-template.timeline-update-form"),
    path("timeline-template/update-timeline-template", views.update_timeline_template, name="timeline-template.update"),
    path("timeline-template/delete-timeline-template", views.delete_timeline_template, name="timeline-template.delete"),
    path("timeline-template/timeline-duplicate-form", views.timeline_duplicate_form, name="timeline-template.timeline-duplicate-form"),
    path("timeline-template/duplicate-timeline-template", views.duplicate_timeline_template, name="timeline-template.duplicate"),
    path("timeline-template/<int:pk>/details", views.timeline_template_details, name="timeline-template.detail"),

    # Timeline Task
    path("timeline-task-datatable", views.TimelineTemplateTaskDataTable.as_view(), name="timeline-template-task.datatable"),
    path("timeline-template/create-timelinetask-template", views.create_timelinetask_template, name="timeline-template.task-create"),
    path("timeline-template/timelinetask-update-form", views.timelinetask_update_form, name="timeline-template.timelinetask-update-form"),
    path("timeline-template/update-timelinetask-template", views.update_timelinetask_template, name="timeline-template.task-update"),
    path("timeline-template/delete-timelinetask-template", views.delete_timelinetask_template, name="timeline-template.task-delete"),
]

