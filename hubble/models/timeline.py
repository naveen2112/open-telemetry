from django.db import models
from core import db
from .team import Team
from .user import User
from django.core.exceptions import ValidationError


class Timeline(db.SoftDeleteWithBaseModel):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "timelines"

    def __str__(self):
        return self.name

    def clean(self):
        """
        This function checks if a team already has an active template and raises a validation error if
        it does.
        """
        if (
            self.is_active
            and Timeline.objects.filter(team=self.team, is_active=True)
            .exclude(id=self.id)
            .exists()
        ):
            raise ValidationError("Team already has an active template.")