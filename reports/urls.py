from django.urls import path, include
from reports import views

urlpatterns = [
    path("auth", include("hubble.urls")),
    path("", views.index, name="index"),
    path("monetization", views.monetization_report, name="monetization"),
    path("detailed-efficiency/<int:pk>", views.detailed_efficiency, name="detailed_efficiency"),
    path("kpi", views.kpi_report, name="kpi"),
    path("team-report", views.team_report, name="team_report"),
    path("project-report", views.project_report, name="project_report"),
    path("team-summary/<int:pk>", views.team_summary, name="team_summary"),
    path("project-summary/<int:pk>", views.project_summary, name="project_summary"),

    path("datatable", views.Datatable.as_view(), name="datatable"),
    path("monetization-datatable", views.MonetizationDatatable.as_view(), name="monetization_datatable"),
    path("kpi-datatable", views.KPIDatatable.as_view(), name="kpi_datatable"),
    path("team-datatable", views.TeamsDatatable.as_view(), name="team_datatable"),
    path("organization-datatable", views.Organization.as_view(), name="organization_datatable"),
    path("project-datatable", views.ProjectsDatatable.as_view(), name="project_datatable"),

    path("detailed-efficiency-datatable", views.DetaileEfficiencyDatatable.as_view(), name="detailed_efficiency_datatable"),
    path("project-summary-datatable", views.ProjectSummaryDatatable.as_view(), name="project_summary_datatable"),

]
