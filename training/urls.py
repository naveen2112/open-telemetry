"""
Training app url configuration
"""
from django.urls import include, path

from hubble import views as sso_view
from training import view
from training.views import (
    batch,
    induction_kit,
    sub_batch,
    sub_batch_timeline,
    timeline,
    timeline_task,
    user_journey,
)

handler404 = view.error_404
handler500 = view.error_500


handler404 = view.error_404
handler500 = view.error_500

urlpatterns = [
    path("", include("hubble.urls")),
    path("", view.home, name="training.home"),
    path("hubble-sso-callback", sso_view.callback, name="callback"),
    # Induction kit
    path(
        "induction-kit",
        induction_kit.InductionKit.as_view(),
        name="induction-kit",
    ),
    path(
        "induction-kit/<text>",
        induction_kit.induction_kit_detail,
        name="induction-kit.detail",
    ),
    # Timeline Template
    path(
        "timeline-template",
        timeline.TimelineTemplate.as_view(),
        name="timeline-template",
    ),
    path(
        "timeline-datatable",
        timeline.TimelineTemplateDataTable.as_view(),
        name="timeline-template.datatable",
    ),
    path(
        "timeline-template/create",
        timeline.create_timeline_template,
        name="timeline-template.create",
    ),
    path(
        "timeline-template/<int:pk>/show",
        timeline.timeline_template_data,
        name="timeline-template.show",
    ),
    path(
        "timeline-template/<int:pk>/edit",
        timeline.update_timeline_template,
        name="timeline-template.edit",
    ),
    path(
        "timeline-template/<int:pk>/delete",
        timeline.delete_timeline_template,
        name="timeline-template.delete",
    ),
    path(
        "timeline-template/<int:pk>",
        timeline.TimelineTemplateDetails.as_view(),
        name="timeline-template.detail",
    ),
    # Timeline Task
    path(
        "timeline-task-datatable",
        timeline_task.TimelineTemplateTaskDataTable.as_view(),
        name="timeline-task.datatable",
    ),
    path(
        "timeline-task/create",
        timeline_task.create_timeline_task,
        name="timeline-task.create",
    ),
    path(
        "timeline-task/<int:pk>/show",
        timeline_task.timeline_task_data,
        name="timeline-task.show",
    ),
    path(
        "timeline-task/<int:pk>/edit",
        timeline_task.update_timeline_task,
        name="timeline-task.edit",
    ),
    path(
        "timeline-task/<int:pk>/delete",
        timeline_task.delete_timeline_task,
        name="timeline-task.delete",
    ),
    path(
        "timeline-task/reorder",
        timeline_task.update_order,
        name="timeline-task.reorder",
    ),
    # Batch
    path("batch", batch.BatchList.as_view(), name="batch"),
    path(
        "batch-datatable",
        batch.BatchDataTable.as_view(),
        name="batch.datatable",
    ),
    path("batch/create", batch.create_batch, name="batch.create"),
    path(
        "batch/<int:pk>/show",
        batch.batch_data,
        name="batch.show",
    ),
    path(
        "batch/<int:pk>/edit",
        batch.update_batch,
        name="batch.edit",
    ),
    path(
        "batch/<int:pk>/delete",
        batch.delete_batch,
        name="batch.delete",
    ),
    path(
        "batch/<int:pk>",
        batch.BatchDetails.as_view(),
        name="batch.detail",
    ),
    # Sub Batch
    path(
        "sub-batch-datatable",
        sub_batch.SubBatchDataTable.as_view(),
        name="sub-batch-datatable",
    ),
    path(
        "batch/<int:pk>/sub-batch/create",
        sub_batch.create_sub_batch,
        name="sub-batch.create",
    ),
    path(
        "sub-batch/get-timeline",
        sub_batch.get_timelines,
        name="sub-batch.get_timelines",
    ),
    path(
        "sub-batch/<int:pk>/edit",
        sub_batch.update_sub_batch,
        name="sub-batch.edit",
    ),
    path(
        "sub-batch/<int:pk>",
        sub_batch.SubBatchDetail.as_view(),
        name="sub-batch.detail",
    ),
    path(
        "sub-batch/<int:pk>/delete",
        sub_batch.delete_sub_batch,
        name="sub-batch.delete",
    ),
    path(
        "sub-batch/trainees-datatable",
        sub_batch.SubBatchTraineesDataTable.as_view(),
        name="sub-batch.trainees-datatable",
    ),
    path(
        "sub-batch/trainees/add",
        sub_batch.add_trainee,
        name="trainees.add",
    ),
    path(
        "sub-batch/trainee/<int:pk>/remove",
        sub_batch.remove_trainee,
        name="trainee.remove",
    ),
    # sub_batch_timeline
    path(
        "sub-batch/<int:pk>/timeline",
        sub_batch_timeline.SubBatchTimeline.as_view(),
        name="sub-batch.timeline",
    ),
    path(
        "sub-batch/timeline-datatable",
        sub_batch_timeline.SubBatchTimelineDataTable.as_view(),
        name="sub-batch.datatable",
    ),
    path(
        "batch/<int:pk>/sub-batch-timeline/create",
        sub_batch_timeline.create_sub_batch_timeline,
        name="sub_batch.timeline.create",
    ),
    path(
        "sub-batch-timeline/<int:pk>/show",
        sub_batch_timeline.sub_batch_timeline_data,
        name="sub_batch.timeline.show",
    ),
    path(
        "sub-batch-timeline/<int:pk>/edit",
        sub_batch_timeline.update_sub_batch_timeline,
        name="sub_batch.timeline.edit",
    ),
    path(
        "sub-batch-timeline/reorder",
        sub_batch_timeline.update_task_sequence,
        name="sub_batch.timeline.reorder",
    ),
    path(
        "sub-batch-timeline/<int:pk>/delete",
        sub_batch_timeline.delete_sub_batch_timeline,
        name="sub_batch.timeline.delete",
    ),
    # user_reports_crud
    path(
        "user/<int:pk>",
        user_journey.TraineeJourneyView.as_view(),
        name="user_reports",
    ),
    path(
        "user/<int:pk>/update-score",
        user_journey.update_task_score,
        name="user.update-score",
    ),
    path(
        "add-extension/<int:pk>",
        user_journey.add_extension,
        name="extension.create",
    ),
    path(
        "extension/<int:pk>/delete",
        user_journey.delete_extension,
        name="extension.delete",
    ),
]
