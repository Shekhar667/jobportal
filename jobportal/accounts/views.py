from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from django.http import JsonResponse
import random
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
import time
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def signup_view(request):
    context = {}

    if request.method == 'POST':
        data = request.POST

        required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'role']
        for field in required_fields:
            if not data.get(field):
                context['error'] = 'All fields are required'
                return render(request, 'auth/signup.html', context)

        if len(data['password']) < 6:
            context['error'] = 'Password must be at least 6 characters'
            return render(request, 'auth/signup.html', context)

        if User.objects.filter(email=data['email']).exists():
            context['error'] = 'Email already registered'
            return render(request, 'auth/signup.html', context)

        otp = str(random.randint(100000, 999999))

        try:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data['phone'],
                role=data['role'],
                is_active=False,
                otp=otp
            )
        except IntegrityError:
            context['error'] = 'Something went wrong'
            return render(request, 'auth/signup.html', context)

        send_mail(
            'Your OTP Code',
            f'Your OTP is: {otp}',
            settings.EMAIL_HOST_USER,
            [user.email],
        )

        request.session['otp_email'] = user.email
        request.session['otp_attempts'] = 0
        request.session['otp_time'] = time.time()

        context['show_otp_popup'] = True

    return render(request, 'auth/signup.html', context)

@csrf_exempt
def verify_otp_view(request):
    if request.method == 'POST':
        email = request.session.get('otp_email')
        otp = request.POST.get('otp')

        if not email:
            return JsonResponse({'success': False, 'msg': 'Session expired'})

        attempts = request.session.get('otp_attempts', 0)
        otp_time = request.session.get('otp_time')

        if attempts >= 3:
            return JsonResponse({'success': False, 'msg': 'OTP attempts exceeded'})

        if time.time() - otp_time > 180:
            return JsonResponse({'success': False, 'msg': 'OTP expired'})

        user = User.objects.get(email=email)

        if user.otp == otp:
            user.is_active = True
            user.is_email_verified = True
            user.otp = None
            user.save()

            request.session.flush()
            return JsonResponse({'success': True})

        request.session['otp_attempts'] += 1
        return JsonResponse({'success': False, 'msg': 'Invalid OTP'})

@csrf_exempt
def resend_otp_view(request):
    email = request.session.get('otp_email')
    if not email:
        return JsonResponse({'success': False})

    otp = str(random.randint(100000, 999999))
    user = User.objects.get(email=email)
    user.otp = otp
    user.save()

    request.session['otp_attempts'] = 0
    request.session['otp_time'] = time.time()

    send_mail(
        'Your OTP Code (Resent)',
        f'Your OTP is: {otp}',
        settings.EMAIL_HOST_USER,
        [user.email],
    )

    return JsonResponse({'success': True})


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            email=request.POST['email'],
            password=request.POST['password']
        )

        if user is None:
            return render(request, 'auth/login.html', {'error': 'Invalid credentials'})

        if not user.is_email_verified:
            return render(request, 'auth/login.html', {'error': 'Verify email first'})
        login(request, user)
        return redirect('/dashboard/')
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
