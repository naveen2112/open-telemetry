"""
The ReportsConfig class is a Django app configuration class for the "reports" app.
"""
from django.apps import AppConfig


class ReportsConfig(AppConfig):
    """
    The ReportsConfig class is a Django app configuration class with a default auto field
    and the name reports
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "reports"
