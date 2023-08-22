"""
The Extension class is used to store extension week data for trainees
"""
from django.db import models

from core import db

from .user import User


class Extension(db.SoftDeleteWithBaseModel):
    """
    Store the extension week data of trainee
    """

    name = models.CharField(max_length=255, blank=True)
    sub_batch = models.ForeignKey("SubBatch", on_delete=models.CASCADE, related_name="extensions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="extensions")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_extensions",
    )

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        db_table = "extensions"
