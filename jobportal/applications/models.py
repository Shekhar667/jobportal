
# Create your models here.
from django.db import models
from jobs.models import Job
from accounts.models import User

class Application(models.Model):
    STATUS_CHOICES = (
        ('APPLIED', 'Applied'),
        ('REVIEWED', 'Reviewed'),
        ('REJECTED', 'Rejected'),
        ('ACCEPTED', 'Accepted'),
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    job_seeker = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    applied_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('job', 'job_seeker')


# class Application(models.Model):
#     job = models.ForeignKey(Job, on_delete=models.CASCADE)
#     job_seeker = models.ForeignKey(User, on_delete=models.CASCADE)
#     status = models.CharField(max_length=20, default='Applied')
#     applied_at = models.DateTimeField(auto_now_add=True)
