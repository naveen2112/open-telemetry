from django.db import models
from .user import User


class Holiday(models.Model):
    id = models.BigAutoField(primary_key=True)
    date_of_holiday = models.DateField()
    month_year = models.CharField(max_length=255)
    updated_by = models.ForeignKey(User, models.CASCADE)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    allow_check_in = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'holidays'

    
    def __str__(self):
        return self.name
