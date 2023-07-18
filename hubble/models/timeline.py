from django.db import models

from core import db
from hubble.models import Team, User


class Timeline(db.SoftDeleteWithBaseModel):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_active = models.BooleanField(
        default=False, blank=True, verbose_name="is_active"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "timelines"

    def __str__(self):
        return self.name
