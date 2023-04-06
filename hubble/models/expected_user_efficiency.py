from django.db import models
from hubble.models import User


class ExpectedUserEfficiency(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.IntegerField(unique=True, db_column="user_id")
    expected_efficiency = models.FloatField()
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)
    updated_by = models.ForeignKey(
        User,
        models.CASCADE,
        db_column="updated_by",
        related_name="ExpectedUserEfficiencies_updated_by",
    )
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "expected_user_efficiencies"
