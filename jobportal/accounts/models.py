from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('jobseeker', 'Job Seeker'),
        ('employer', 'Employer'),
    )

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.TextField()

class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
