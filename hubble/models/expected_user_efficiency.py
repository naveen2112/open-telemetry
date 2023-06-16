from django.db import models

from core import db
from hubble.models import User


class ExpectedUserEfficiency(db.SoftDeleteWithBaseModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        models.CASCADE,
        related_name="expected_user_efficiencies",
        db_column="user_id",
    )
    expected_efficiency = models.FloatField()
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)
    updated_by = models.ForeignKey(
        User,
        models.CASCADE,
        db_column="updated_by",
        related_name="expecteduserefficiencies_updated_by",
    )

    class Meta:
        managed = False
        db_table = "expected_user_efficiencies"
