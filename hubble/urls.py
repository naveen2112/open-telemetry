from django.urls import path
from hubble import views

urlpatterns = [
    path("login", views.index, name="index"),
    path("signin", views.signin, name="signin"),
    path("signout", views.signout, name="signout"),
    path("hubble-sso-callback", views.callback, name="callback"),
]
