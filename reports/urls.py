from django.urls import path, include, register_converter
from reports import views


urlpatterns = [
    path("auth", include("hubble.urls")),
    path("", views.index, name="index"),
    path("monetization", views.monetization_report, name="monetization"),
    path("detailed-efficiency/<int:pk>", views.detailed_efficiency, name="detailed_efficiency"),
    path("kpi", views.kpi_report, name="kpi"),

    path("overall-efficiency-datatable", views.EfficiencyDatatable.as_view(), name="efficiency_datatable"),
    path("detailed-efficiency-datatable", views.DetaileEfficiencyDatatable.as_view(), name="detailed_efficiency_datatable"),
    path("monetization-datatable", views.MonetizationDatatable.as_view(), name="monetization_datatable"),
    path("kpi-datatable", views.KPIDatatable.as_view(), name="kpi_datatable"),
]
