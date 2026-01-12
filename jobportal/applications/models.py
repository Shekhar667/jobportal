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

    # =====================
    # RELATIONS
    # =====================
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    job_seeker = models.ForeignKey(User, on_delete=models.CASCADE)

    # =====================
    # JOB SEEKER DETAILS (PER APPLICATION)
    # =====================
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    qualification = models.CharField(max_length=255, blank=True)
    experience = models.PositiveIntegerField(default=0)
    skills = models.TextField(blank=True)
    address = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='APPLIED'
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'job_seeker')

        
    def __str__(self):
        return f"{self.job_seeker.email} → {self.job.title}"
