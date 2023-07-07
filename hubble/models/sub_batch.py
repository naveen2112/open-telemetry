from django.db import models

from core import db
from hubble.models import Batch, Team, Timeline, User


class SubBatch(db.SoftDeleteWithBaseModel):
    name = models.CharField(max_length=250)
    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="sub_batches"
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    primary_mentor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="primary_sub_batches",
    )
    secondary_mentor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="secondary_sub_batches",
    )
    start_date = models.DateField()
    timeline = models.ForeignKey(Timeline, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "sub_batches"

    def __str__(self):
        return self.name

    @property
    def reporting_persons(self):
        return " / ".join(
            [self.primary_mentor.name, self.secondary_mentor.name]
        )
