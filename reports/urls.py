from django.urls import path

from reports.views import index

urlpatterns = [
    path(
        route="index/",
        view=index,
        name="index",
    ),
]
