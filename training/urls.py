from django.urls import path

from training.views import index

urlpatterns = [
    path(route="index/", view=index, name="index",),
]
