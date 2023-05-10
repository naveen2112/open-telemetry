from django.db import models
from core import db
from .team import Team
from .user import User
from django.core.exceptions import ValidationError


class Timeline(db.SoftDeleteWithBaseModel):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "timeline"


