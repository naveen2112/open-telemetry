from django.urls import path, include, register_converter
from reports import views
from hubble import views as sso_view


urlpatterns = [
    path("auth", include("hubble.urls")),
    path("hubble-sso-callback", sso_view.callback, name="callback"),
    path("", views.Index.as_view(), name="index"),
    path("monetization", views.MonetizationReport.as_view(), name="monetization"),
    path(
        "detailed-efficiency/<int:pk>",
        views.DetailedEfficiency.as_view(),
        name="detailed_efficiency",
    ),
    path("kpi", views.KpiReport.as_view(), name="kpi"),
    path(
        "overall-efficiency-datatable",
        views.EfficiencyDatatable.as_view(),
        name="efficiency_datatable",
    ),
    path(
        "detailed-efficiency-datatable",
        views.DetaileEfficiencyDatatable.as_view(),
        name="detailed_efficiency_datatable",
    ),
    path(
        "monetization-datatable",
        views.MonetizationDatatable.as_view(),
        name="monetization_datatable",
    ),
    path("kpi-datatable", views.KPIDatatable.as_view(), name="kpi_datatable"),
]
