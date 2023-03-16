from django.urls import path

from hubble.views import sign_in, sign_out, callback, index, dashboard

urlpatterns = [
    path(route="", view=dashboard, name="dashboard"),
    path(route="login/", view=index, name="index",),
    path(route="sign_in/", view=sign_in, name="sign_in",),
    path(route='signout/', view=sign_out, name='signout'),
    path(route='hubble-sso-callback/', view=callback, name='callback'),
]