"""
The Holiday class represents a model for storing holiday details of an organization
"""
from django.db import models

from core import db


class Holiday(db.SoftDeleteWithBaseModel):
    """
    Store the holiday details of the organization
    """

    id = models.BigAutoField(primary_key=True)
    date_of_holiday = models.DateField()
    month_year = models.CharField(max_length=255)
    updated_by = models.ForeignKey("hubble.User", models.CASCADE, db_column="updated_by")
    reason = models.CharField(max_length=255, blank=True, null=True)
    national_holiday = models.BooleanField()
    allow_check_in = models.BooleanField()

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        managed = False
        db_table = "holidays"

    def __str__(self):
        return str(self.date_of_holiday)
