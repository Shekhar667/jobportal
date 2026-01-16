from django.urls import path
from .views import apply_job, application_status,job_applicants,update_application_status,contactus,aboutus,quickeasy, notifications, notifications_json, delete_notification
 
urlpatterns = [
    path('apply/<int:job_id>/', apply_job, name='apply_job'),   # Job Seeker → apply
    path('status/', application_status, name='application_status'),  
    path('job/<int:job_id>/applicants/', job_applicants, name='job_applicants'),
    path('update/<int:app_id>/', update_application_status, name='update_application_status'),
    path('contactus/', contactus, name='contactus'),
    path('aboutus/', aboutus, name='aboutus'),
    path('quickeasy/', quickeasy, name='quickeasy'),
    path('notifications/', notifications, name='notifications'),
    path('notifications/json/', notifications_json, name='notifications_json'),
    path('notifications/delete/<int:notification_id>/', delete_notification,name='delete_notification'),
]