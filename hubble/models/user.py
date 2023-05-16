from django.db import models
from .team import Team
from .designation import Designation


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee_id = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(unique=True, max_length=255)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    is_employed = models.BooleanField(blank=True, null=True)
    remember_token = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=255)
    team = models.ForeignKey(Team, models.CASCADE, blank=True, null=True)
    branch_id = models.BigIntegerField(blank=True, null=True)
    designation = models.ForeignKey(Designation, models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    team_owner = models.BooleanField(blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    is_saturday_working = models.BooleanField()

    class Meta:
        managed = False
        db_table = "users"


    def __str__(self):
        return self.name
