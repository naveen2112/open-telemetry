from django.urls import path, include
from reports import views

urlpatterns = [
    path("", views.index, name="index"),
    path("datatable", views.datatable.as_view(), name="datatable"),
    path("monetization", views.monetization_report, name="monetization"),
    path("kpi", views.kpi_report, name="kpi"),
    path("monetization_datatable", views.monetization_datatable.as_view(), name="monetization_datatable"),
    path("kpi_datatable", views.kpi_datatable.as_view(), name="kpi_datatable"),
    path("auth", include("hubble.urls")),
]
