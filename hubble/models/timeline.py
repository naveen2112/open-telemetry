from django.db import models
from core import db
from .teams import Teams
from .users import Users
from django.core.exceptions import ValidationError


class Timeline(db.BaseModel):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False, null=True, blank=True)
    created_by = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "timeline"


    def clean(self):
        """
        This function checks if a team already has an active template and raises a validation error if
        it does.
        """
        super().clean()
        if (
            self.is_active
            and Timeline.objects.filter(team=self.team, is_active=True)
            .exclude(id=self.id)
            .exists()
        ):
            raise ValidationError("Team already has an active template.")

