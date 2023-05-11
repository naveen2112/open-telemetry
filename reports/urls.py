from django.urls import path, include
from reports import views

urlpatterns = [
    path("", include('hubble.urls')),
    path("report", views.report, name="report"),
]