"""
The TrainingConfig class is a Django app configuration class for the "training" app
"""
from django.apps import AppConfig


class TrainingConfig(AppConfig):
    """
    TrainingConfig class is a Django app configuration class with a default
    auto field and the name "training"
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "training"
