from django.urls import path, include, register_converter
from reports import views
from reports.view import project_efficiency, team_efficiency
from .converters import DateConverter

register_converter(DateConverter, 'date')

urlpatterns = [
    path("auth", include("hubble.urls")),
    path("", views.index, name="index"),
    path("monetization", views.monetization_report, name="monetization"),
    path("detailed-efficiency/<int:pk>", views.detailed_efficiency, name="detailed_efficiency"),
    path("kpi", views.kpi_report, name="kpi"),
    path("team-report", views.team_report, name="team_report"),
    path("project-report", views.project_report, name="project_report"),
    path("team-summary/<int:pk>/<date:start>/<date:end>", views.team_summary, name="team_summary"),
    path("project-summary/<int:pk>/<date:start>/<date:end>", views.project_summary, name="project_summary"),

    path("datatable", views.Datatable.as_view(), name="datatable"),
    path("detailed-efficiency-datatable", views.DetaileEfficiencyDatatable.as_view(), name="detailed_efficiency_datatable"),
    path("monetization-datatable", views.MonetizationDatatable.as_view(), name="monetization_datatable"),
    path("kpi-datatable", views.KPIDatatable.as_view(), name="kpi_datatable"),
    path("team-datatable", team_efficiency.TeamsDatatable.as_view(), name="team_datatable"),
    path("team-summary-datatable", team_efficiency.TeamSummaryDatatable.as_view(), name="team_summary_datatable"),
    path("project-datatable", project_efficiency.ProjectsDatatable.as_view(), name="project_datatable"),
    path("project-summary-datatable", project_efficiency.ProjectSummaryDatatable.as_view(), name="project_summary_datatable"),

]
