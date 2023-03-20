from django.db import models
from .teams import Teams
from .designations import Designations
from django.contrib.auth.models import AbstractBaseUser
from datetime import datetime

class Users(AbstractBaseUser):
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
    team = models.ForeignKey(Teams, models.CASCADE, blank=True, null=True)
    branch_id = models.BigIntegerField(blank=True, null=True)
    designation = models.ForeignKey(Designations, models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    team_owner = models.BooleanField(blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    is_saturday_working = models.BooleanField()
    is_active = True
    is_staff=True
    last_login = datetime.now()
    is_superuser=False
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    @property
    def is_authenticated(self):
        return self.email != None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['id', 'name', 'status', 'is_saturday_working']

    class Meta:
        managed = False
        db_table = 'users'
