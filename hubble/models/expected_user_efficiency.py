"""
The ExpectedUserEfficiency class is a Django model that represents the 
expected efficiency of a user with the required fields
"""
from django.db import models

from core import db


class ExpectedUserEfficiency(db.SoftDeleteWithBaseModel):
    """
    Store the expected user efficiency details.
    """

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        "hubble.User",
        models.CASCADE,
        related_name="expected_user_efficiencies",
        db_column="user_id",
    )
    expected_efficiency = models.FloatField()
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)
    updated_by = models.ForeignKey(
        "hubble.User",
        models.CASCADE,
        db_column="updated_by",
        related_name="expecteduserefficiencies_updated_by",
    )

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        managed = False
        db_table = "expected_user_efficiencies"
