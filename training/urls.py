from django.urls import path

from training.views import induction_kit, timeline, timeline_task, batch
 
urlpatterns = [
    # Induction kit
    path("induction-kit", induction_kit.InductionKit.as_view(), name="induction-kit"),
    path("induction-kit/<text>", induction_kit.induction_kit_detail, name="induction-kit.detail"),
    
    # Timeline Template
    path("timeline-template", timeline.TimelineTemplate.as_view(), name="timeline-template"),
    path("timeline-datatable", timeline.TimelineTemplateDataTable.as_view(), name="timeline-template.datatable"),
    path("timeline-template/create", timeline.create_timeline_template, name="timeline-template.create"),
    path("timeline-template/edit-form", timeline.timeline_update_form, name="timeline-template.edit-form"),
    path("timeline-template/edit", timeline.update_timeline_template, name="timeline-template.edit"),
    path("timeline-template/delete", timeline.delete_timeline_template, name="timeline-template.delete"),
    path("timeline-template/duplicate-form", timeline.timeline_duplicate_form, name="timeline-template.duplicate-form"),
    path("timeline-template/duplicate", timeline.duplicate_timeline_template, name="timeline-template.duplicate"),
    path("timeline-template/<int:pk>/details", timeline.timeline_template_details, name="timeline-template.detail"),

    # Timeline Task
    path("timeline-task-datatable", timeline_task.TimelineTemplateTaskDataTable.as_view(), name="timeline-task.datatable"),
    path("timeline-task/create", timeline_task.create_timelinetask_template, name="timeline-task.create"),
    path("timeline-task/edit-form", timeline_task.timelinetask_update_form, name="timeline-task.edit-form"),
    path("timeline-task/edit", timeline_task.update_timelinetask_template, name="timeline-task.edit"),
    path("timeline-task/delete", timeline_task.delete_timelinetask_template, name="timeline-task.delete"),
    path("timeline-task/order", timeline_task.update_order, name="timeline-task.order"),

    # Batch
    path("batch", batch.batch, name="batch"),
    path("batch-datatable", batch.BatchDataTable.as_view(), name="batch.datatable"),
    path("batch/create", batch.create_batch, name="batch.create"),
    path("batch/edit-form", batch.batch_update_form, name="batch.edit-form"),
    path("batch/edit", batch.update_batch, name="batch.edit"),
    path("batch/delete", batch.delete_batch, name="batch.delete"),
    path("batch/<int:pk>/details", batch.batch_details, name="batch.detail"),
]

