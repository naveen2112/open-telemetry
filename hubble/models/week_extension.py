from django.db import models
from core import db
from .sub_batch import SubBatch
from .user import User

class WeekExtension(db.SoftDeleteWithBaseModel):
    sub_batch = models.ForeignKey(SubBatch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="week_extension_created_by")

    class Meta:
        db_table = "week_extensions"