from django.db import models
from .user import User
from core import db

class InternDetail(db.SoftDeleteWithBaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="inter_details")
    primary_mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="primary_intern_details")
    secondary_mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="secondary_intern_details")
    college = models.CharField(max_length=250)
    expected_completion = models.DateField(null=True)
    actual_completion = models.DateField(null=True)
    comment = models.TextField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_intern_details")

    class Meta:
        db_table = "intern_details"

    def __str__(self):
        return self.user.name
    
    