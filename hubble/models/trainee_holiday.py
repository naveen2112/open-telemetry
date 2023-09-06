"""
Django test cases for the create, delete and Datatables features in the
TraineeHoliday module
"""
from django.db import models

from core import db
from hubble.models import Batch


class TraineeHoliday(db.SoftDeleteWithBaseModel):
    """
    Store the trainee holiday details for a batch
    """

    id = models.BigAutoField(primary_key=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="holidays")
    date_of_holiday = models.DateField()
    month_year = models.CharField(max_length=255)
    updated_by = models.ForeignKey("hubble.User", on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    national_holiday = models.BooleanField()
    allow_check_in = models.BooleanField()

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        db_table = "trainee_holidays"

    def __str__(self):
        return str(self.date_of_holiday)
