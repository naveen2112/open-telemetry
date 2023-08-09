from django.db import models

from core import db
from hubble.models import User, Batch


class TraineeHoliday(db.SoftDeleteWithBaseModel):
    id = models.BigAutoField(primary_key=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="holidays")
    date_of_holiday = models.DateField()
    month_year = models.CharField(max_length=255)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255, blank=True, null=True)
    allow_check_in = models.BooleanField()

    class Meta:
        managed = True
        db_table = "trainee_holidays"

    def __str__(self):
        return str(self.date_of_holiday)
