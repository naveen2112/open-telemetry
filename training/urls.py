from django.urls import path

from training.views import induction_kit, timeline, timeline_task, batch, sub_batch
 
urlpatterns = [
    # Induction kit
    path("induction-kit", induction_kit.InductionKit.as_view(), name="induction-kit"),
    path("induction-kit/<text>", induction_kit.induction_kit_detail, name="induction-kit.detail"),
    
    # Timeline Template
    path("timeline-template", timeline.TimelineTemplate.as_view(), name="timeline-template"),
    path("timeline-datatable", timeline.TimelineTemplateDataTable.as_view(), name="timeline-template.datatable"),
    path("timeline-template/create", timeline.create_timeline_template, name="timeline-template.create"),
    path("timeline-template/<int:pk>/show", timeline.timeline_template_data, name="timeline-template.show"),
    path("timeline-template/<int:pk>/edit", timeline.update_timeline_template, name="timeline-template.edit"),
    path("timeline-template/<int:pk>/delete", timeline.delete_timeline_template, name="timeline-template.delete"),
    path("timeline-template/<int:pk>", timeline.TimelineTemplateDetails.as_view(), name="timeline-template.detail"),

    # Timeline Task
    path("timeline-task-datatable", timeline_task.TimelineTemplateTaskDataTable.as_view(), name="timeline-task.datatable"),
    path("timeline-task/create", timeline_task.create_timeline_task, name="timeline-task.create"),
    path("timeline-task/<int:pk>/show", timeline_task.timeline_task_data, name="timeline-task.show"),
    path("timeline-task/<int:pk>/edit", timeline_task.update_timeline_task, name="timeline-task.edit"),
    path("timeline-task/<int:pk>/delete", timeline_task.delete_timeline_task, name="timeline-task.delete"),
    path("timeline-task/reorder", timeline_task.update_order, name="timeline-task.reorder"),

    # Batch
    path("batch", batch.BatchList.as_view(), name="batch"),
    path("batch-datatable", batch.BatchDataTable.as_view(), name="batch.datatable"),
    path("batch/create", batch.create_batch, name="batch.create"),
    path("batch/<int:pk>/show", batch.batch_data, name="batch.show"),
    path("batch/<int:pk>/edit", batch.update_batch, name="batch.edit"),
    path("batch/<int:pk>/delete", batch.delete_batch, name="batch.delete"),
    path("batch/<int:pk>", batch.BatchDetails.as_view(), name="batch.detail"),

    # Sub Batch
    path("sub-batch-datatable", sub_batch.SubBatchDataTable.as_view(), name="sub-batch-datatable"),
    path("batch/<int:pk>/sub-batch/create", sub_batch.create_sub_batch, name="sub-batch.create"),
    path("sub-batch/get-team", sub_batch.get_team, name="sub-batch.team"),
    path("batch/<int:batch>/sub-batch/<int:pk>", sub_batch.update_sub_batch, name="sub-batch.edit"),
    path("sub-batch/<int:pk>", sub_batch.SubBatchDetail.as_view(), name="sub-batch.detail"),
    path("sub-batch/<int:pk>/delete", sub_batch.delete_sub_batch, name="sub-batch.delete"),
    path("sub-batch/trainies-datatable", sub_batch.SubBatchTrainiesDataTable.as_view(), name="sub-batch.trainies-datatable"),
    path("sub-batch/trainies/create", sub_batch.add_trainies, name="trainies.create"),
]
