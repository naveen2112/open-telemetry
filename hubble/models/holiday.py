from django.db import models
from hubble.models import User
from core import db

class Holiday(db.SoftDeleteWithBaseModel):
    id = models.BigAutoField(primary_key=True)
    date_of_holiday = models.DateField()
    month_year = models.CharField(max_length=255)
    updated_by = models.ForeignKey(User, models.CASCADE)
    reason = models.CharField(max_length=255, blank=True, null=True)
    allow_check_in = models.BooleanField()

    class Meta:
        managed = False
        db_table = "holidays"

    def __str__(self):
        return self.name