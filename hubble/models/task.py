from django.db import models
from .module import Module
from hubble.models import User


class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    module = models.ForeignKey(Module, models.CASCADE, related_name="module")
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, models.CASCADE, db_column="created_by", related_name="created_by"
    )
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "tasks"
