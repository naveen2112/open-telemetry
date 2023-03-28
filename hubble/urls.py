from django.urls import path
from hubble import views

urlpatterns = [
    path(route="login/", view=views.index, name="index"),
    path(route="signin/", view=views.signin, name="signin"),
    path(route="signout/", view=views.signout, name="signout"),
    path(route="hubble-sso-callback/", view=views.callback, name="callback"),
]