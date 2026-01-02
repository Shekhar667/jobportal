from django.urls import path
from .views import post_job, my_jobs, job_list,my_jobs,edit_job,delete_job,toggle_job_status

urlpatterns = [
    path('post/', post_job, name='post_job'),        # Employer → post job
    path('list/', job_list, name='job_list'),  
    path('edit/<int:job_id>/', edit_job, name='edit_job'),
    path('delete/<int:job_id>/', delete_job, name='delete_job'),
    path('my_jobs/', my_jobs, name='my_jobs'),
    path('toggle/<int:job_id>/', toggle_job_status, name='toggle_job_status'),

]