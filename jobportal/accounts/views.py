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
from accounts.utils import generate_jwt
from .forms import ProfileImageForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.http import HttpResponse

@csrf_exempt
def signup_view(request):
    is_api = request.headers.get('Accept') == 'application/json'
 
    try:
        if request.method == 'POST':
            data = request.POST
 
            required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone', 'role']
            for field in required_fields:
                if not data.get(field):
                    if is_api:
                        return JsonResponse(
                            {'error': 'Validation error', 'message': f'{field} is required'},
                            status=422
                        )
                    return render(request, 'auth/signup.html', {'error': f'{field} is required'})
            if User.objects.filter(username=data['username']).exists():
                message = 'Username already exists'
                if is_api:
                    return JsonResponse({'error': message}, status=422)
                return render(request, 'auth/signup.html', {'error': message})
 
            if User.objects.filter(email=data['email']).exists():
                if is_api:
                    return JsonResponse(
                        {'error': 'Validation error', 'message': 'Email already exists'},
                        status=422
                    )
                return render(request, 'auth/signup.html', {'error': 'Email already exists'})
 
            otp = str(random.randint(100000, 999999))
 
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
            # send_mail(
            #     'Your OTP Code',
            #     f'Your OTP is: {otp}',
            #     settings.EMAIL_HOST_USER,
            #     [user.email],
            # )
            print("OTP:", otp)
            request.session['otp_email'] = user.email
            request.session['otp_attempts'] = 0
            request.session['otp_time'] = time.time()
 
            if is_api:
                return JsonResponse({'success': True, 'message': 'OTP sent', 'otp': otp}, status=201)
 
            return render(request, 'auth/signup.html', {'show_otp_popup': True,
                'debug_otp': otp})
 
        return render(request, 'auth/signup.html')
 
    except Exception as e:
        print('SIGNUP ERROR:', e)
        if is_api:
            return JsonResponse(
                {'error': 'Internal server error'},
                status=500
            )
        return render(request, 'auth/signup.html', {'error': 'Something went wrong'})
 
@csrf_exempt
def verify_otp_view(request):
    try:
        email = request.session.get('otp_email')
        otp = request.POST.get('otp')
 
 
        if not email or not otp:
            return JsonResponse(
                {'error': 'Validation error', 'message': 'OTP or session missing'},
                status=422
            )
 
        attempts = request.session.get('otp_attempts', 0)
        otp_time = request.session.get('otp_time')
 
        if attempts >= 3:
            return JsonResponse({'error': 'OTP attempts exceeded'}, status=403)
 
        if time.time() - otp_time > 180:
            return JsonResponse({'error': 'OTP expired'}, status=403)
 
        user = User.objects.get(email=email)
 
        if user.otp != otp:
            request.session['otp_attempts'] += 1
            return JsonResponse({'error': 'Invalid OTP'}, status=401)
 
        user.is_active = True
        user.is_email_verified = True
        user.otp = None
        user.save()
        request.session.flush()
 
        return JsonResponse({'success': True}, status=200)
 
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
 
    except Exception as e:
        print('OTP VERIFY ERROR:', e)
        return JsonResponse({'error': 'Internal server error'}, status=500)
 
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
 
    # send_mail(
    #     'Your OTP Code (Resent)',
    #     f'Your OTP is: {otp}',
    #     settings.EMAIL_HOST_USER,
    #     [user.email],
    # )
    print("OTP:", otp)
    return JsonResponse({'success': True})
 
 
 
 
 
# @csrf_exempt
# def login_view(request):
#     is_api = request.headers.get('Accept') == 'application/json'
#     # =====================
#     # GET → HTML FORM
#     # =====================
#     if request.method == 'GET':
#         return render(request, 'auth/login.html')
#     # =====================
#     # POST → LOGIN
#     # =====================
#     try:
#         user = authenticate(
#             request,
#             email=request.POST.get('email'),
#             password=request.POST.get('password')
#         )
 
#         if not user:
#             if is_api:
#                 return JsonResponse({'error': 'Invalid credentials'}, status=401)
#             return render(request, 'auth/login.html', {'error': 'Invalid credentials'})
 
#         if not user.is_email_verified and not user.is_superuser:
#             if is_api:
#                 return JsonResponse({'error': 'Email not verified'}, status=403)
#             return render(request, 'auth/login.html', {'error': 'Verify email first'})
 
#         # ✅ Session login (browser)
#         login(request, user)
 
#         # ✅ JWT for API
#         token = generate_jwt(user)
 
#         if is_api:
#             return JsonResponse({
#                 'success': True,
#                 'access_token': token,
#                 'user': {
#                     # 'id': user.id,
#                     # 'email': user.email,
#                     'role': user.role
#                 }
#             }, status=200)
#         # Browser redirect
#         return redirect('/')
 
#     except Exception as e:
#         print('LOGIN ERROR:', e)
#         if is_api:
#             return JsonResponse({'error': 'Internal server error'}, status=500)
#         return render(request, 'auth/login.html', {'error': 'Something went wrong'})
 
 
@csrf_exempt
def login_view(request):
    is_api = request.headers.get('Accept') == 'application/json'
 
    if request.method == 'GET':
        return render(request, 'auth/login.html')
 
    try:
        user = authenticate(
            request,
            email=request.POST.get('email'),
            password=request.POST.get('password')
        )
 
        if not user:
            if is_api:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
            return render(request, 'auth/login.html', {'error': 'Invalid credentials'})
 
        if not user.is_email_verified and not user.is_superuser:
            if is_api:
                return JsonResponse({'error': 'Email not verified'}, status=403)
            return render(request, 'auth/login.html', {'error': 'Verify email first'})
 
        login(request, user)
 
        token = generate_jwt(user)
 
        if is_api:
            return JsonResponse({
                'success': True,
                'access_token': token,
                'user': {
                    'role': user.role
                }
            }, status=200)
 
        # ✅ ONLY CHANGE HERE
        if user.is_superuser:
            return redirect('/')
        return redirect('/')
 
    except Exception as e:
        print('LOGIN ERROR:', e)
        if is_api:
            return JsonResponse({'error': 'Internal server error'}, status=500)
        return render(request, 'auth/login.html', {'error': 'Something went wrong'})
 
 
 
 
def logout_view(request):
    logout(request)
    return redirect('/')
 
 
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
 
 
@login_required
def edit_profile(request):
    user = request.user
 
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
 
        user.save()
        return redirect('profile')
 
    return render(request, 'accounts/edit_profile.html', {
        'user': user
    })
 
 
@login_required
def upload_profile_image(request):
    if request.method == 'POST' and request.FILES.get('profile_image'):
        request.user.profile_image = request.FILES['profile_image']
        request.user.save()
    return redirect('profile')  
 

 
def create_admin_once(request):
    User = get_user_model()
 
    if User.objects.filter(email="admin@jobportal.com").exists():
        return HttpResponse("Superuser already exists")
 
    User.objects.create_superuser(
        username="admin",
        email="admin@jobportal.com",
        password="admin12"
    )
    return HttpResponse("Superuser created successfully")