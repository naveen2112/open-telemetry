from django.db import models
from .user import User
from core import db

class InternDetail(db.BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="intern_user")
    primary_mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="intern_primary_mentor")
    secondary_mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="intern_secondary_mentor")
    college = models.CharField(max_length=250)
    expected_completion = models.DateField(null=True)
    actual_completion = models.DateField(null=True)
    comment = models.TextField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by")

    class Meta:
        db_table = 'intern_details'


    def __str__(self):
        return self.user.name
    
    