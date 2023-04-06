from django.urls import path, include
from reports import views

urlpatterns = [
    path("", views.index, name="index"),
    path("datatable", views.datatable.as_view(), name="datatable"),
    path("auth", include("hubble.urls")),
]
