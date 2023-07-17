from django.db import models

from core import db

from .sub_batch import SubBatch
from .user import User


class Extension(db.SoftDeleteWithBaseModel):
    sub_batch = models.ForeignKey(
        "SubBatch", on_delete=models.CASCADE, related_name="extensions"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="extensions"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_extensions",
    )

    class Meta:
        db_table = "extensions"
