from django.db import models
from core import db
from .teams import Teams
from .users import Users


class Timeline(db.BaseModel):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False, null=True, blank=True)
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'timeline'