from django.urls import path
from .views import apply_job, application_status,job_applicants,update_application_status

urlpatterns = [
    path('apply/<int:job_id>/', apply_job, name='apply_job'),   # Job Seeker → apply
    path('status/', application_status, name='application_status'),  
    path('job/<int:job_id>/applicants/', job_applicants, name='job_applicants'),
    path('update/<int:app_id>/', update_application_status, name='update_application_status'),
]
