"""
Hubble application url configuration
"""
from django.urls import include, path

from core.constants import ENVIRONMENT_DEVELOPMENT
from hubble_report.settings import ENV_NAME
from hubble import views

urlpatterns = [
    path("login", views.login, name="login"),
    path("signin", views.signin, name="signin"),
    path("signout", views.signout, name="signout"),
]

handler404 = views.error_404

if ENV_NAME == ENVIRONMENT_DEVELOPMENT:
    urlpatterns += [
        path("silk/", include("silk.urls", namespace="silk"))
    ]
