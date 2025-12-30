from django.urls import path
from .views import *
urlpatterns = [
    path('signup/', signup_view),
    path('login/', login_view),
    path('logout/', logout_view),
    path('profile/', profile_view, name='profile'),
    path('verify-otp-ajax/', verify_otp_view),
    path('resend-otp-ajax/', resend_otp_view),
]
