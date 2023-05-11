from django.urls import path

from training import views

urlpatterns = [
    path("induction-kit", views.InductionKit.as_view(), name="induction-kit"),
    path(
        "induction-kit/<text>", views.induction_kit_detail, name="induction-kit.detail"
    ),
]
