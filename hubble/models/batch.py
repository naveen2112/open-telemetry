from django.db import models
from core import db
from .user import User


class Batch(db.SoftDeleteWithBaseModel):
    name = models.CharField(max_length=250)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "batches"

    def __str__(self):
        return self.name