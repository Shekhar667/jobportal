from django.urls import path
from .views import post_job, my_jobs, job_list,my_jobs

urlpatterns = [
    path('post/', post_job, name='post_job'),        # Employer → post job
    path('list/', job_list, name='job_list'),  
    # path('applicants/', job_applicants, name='job_applicants'),
    path('my_jobs/', my_jobs, name='my_jobs')
]