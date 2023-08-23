"""
The HubbleConfig class is a Django app configuration class for the "hubble" app
"""
from django.apps import AppConfig


class HubbleConfig(AppConfig):
    """
    The HubbleConfig class is a Django app configuration class with a default
    auto field and the name hubble
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "hubble"
