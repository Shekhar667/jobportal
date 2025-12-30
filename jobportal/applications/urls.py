from django.urls import path
from .views import apply_job, application_status

urlpatterns = [
    path('apply/<int:job_id>/', apply_job, name='apply_job'),   # Job Seeker → apply
    path('status/', application_status, name='application_status'),  # Job Seeker → view applied jobs
]
