from django.urls import path

from reports.views import index

urlpatterns = [
    path(route="index/", view=index, name="index",),
    path(route="work/", view=index, name="work",),
]
