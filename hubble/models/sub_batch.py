from django.db import models
from core import db
from .user import User
from .intern_detail import InternDetail
from .team import Team
from .timeline import Timeline
from .batch import Batch

class SubBatch(db.SoftDeleteWithBaseModel):
    name = models.CharField(max_length=250)
    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="sub_batches"
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    start_date = models.DateField()
    timeline = models.ForeignKey(Timeline, on_delete=models.CASCADE)
    intern = models.ManyToManyField(InternDetail, related_name="trainie")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "sub_batches"

    def __str__(self):
        return self.name
