from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('signup/', signup_view),
    path('login/', login_view),
    path('logout/', logout_view),
    path('profile/', profile_view, name='profile'),
    path('verify-otp-ajax/', verify_otp_view),
    path('resend-otp-ajax/', resend_otp_view),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path(
        'password/change/',
        auth_views.PasswordChangeView.as_view(
            template_name='accounts/change_password.html',
            success_url='/accounts/password/change/done/'
        ),
        name='password_change'
    ),
 
    path(
        'password/change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='accounts/change_password_done.html'
        ),
        name='password_change_done'
    ),
]
 