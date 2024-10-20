from django.db import models
from django.utils import timezone

from django.contrib.auth.models import AbstractUser

class Custom_User(AbstractUser):
    USER=[
        ('recruiter','Recruiter'),('jobseeker','JobSeeker')
    ]
    user_type=models.CharField(choices=USER,max_length=120,null=True)
    auth_token = models.CharField(max_length=100,null=True)
    is_verified = models.BooleanField(default=False,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    
    def __str__(self):
        return self.username