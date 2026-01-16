 
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
# from accounts.decorators import role_required
from .models import Application, Notification  
from jobs.models import Job
from django.http import HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.decorators import hybrid_auth_required
from django.http import JsonResponse
from .models import Notification  
from django.contrib.auth.decorators import user_passes_test
# @login_required
 
# @role_required(['admin'])
@hybrid_auth_required(['admin'])
def admin_applications(request):
    is_api = request.headers.get('Accept') == 'application/json'
    applications = Application.objects.select_related('job', 'job_seeker')
    if is_api:
        data = []
        for app in applications:
            data.append({
                'id': app.id,
                'job': app.job.title,
                'job_seeker': app.job_seeker.email,
                'status': app.status
            })
        return JsonResponse({'applications': data})
    return render(request, 'applications/admin_applications.html', {
        'applications': applications
    })
 
 
# @csrf_exempt
# @login_required
# @role_required(['jobseeker'])
# @hybrid_auth_required(['jobseeker'])
 
# def apply_job(request, job_id):
#     try:
#         app, created = Application.objects.get_or_create(
#             job_id=job_id,
#             job_seeker=request.user
#         )
 
#         if request.headers.get('Accept') == 'application/json':
#             return JsonResponse(
#                 {'success': True, 'created': created},
#                 status=201 if created else 200
#             )
#         return redirect('/dashboard/')
#     except Exception as e:
#         print('APPLY JOB ERROR:', e)
#         return JsonResponse({'error': 'Internal server error'}, status=500)
# ===================== JOBSEEKER: APPLY JOB =====================
@csrf_exempt
@hybrid_auth_required(['jobseeker'])
def apply_job(request, job_id):
    # Job ko fetch karo
    job = get_object_or_404(Job, id=job_id)
 
    # -------- GET → SHOW FORM --------
    if request.method == 'GET':
        return render(request, 'applications/apply_job.html', {
            'job': job
        })
 
    # -------- POST → SUBMIT FORM --------
    elif request.method == 'POST':
        try:
            # Check if user already applied
            app, created = Application.objects.get_or_create(
                job=job,
                job_seeker=request.user
            )
 
            if not created:
                # Already applied
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse(
                        {'error': 'You have already applied for this job'},
                        status=409
                    )
                return redirect('/applications/status/')
 
            # Fill remaining fields
            app.qualification = request.POST.get('qualification')
            app.experience = request.POST.get('experience', 0)
            app.skills = request.POST.get('skills')
            app.address = request.POST.get('address')
 
            if request.FILES.get('resume'):
                app.resume = request.FILES['resume']
 
            app.save()
            applicant_name = f"{request.user.first_name} {request.user.last_name}".strip()
            Notification.objects.create(
                user=job.employer,
                message=f"{applicant_name} has applied for your job '{job.title}'"
            )
 
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'application_id': app.id
                }, status=201)
            else:
                return redirect('/applications/status/')
 
        except Exception as e:
            print('APPLY JOB ERROR:', e)
            return JsonResponse({'error': 'Internal server error'}, status=500)
 
    # Invalid method
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
# ===================== JOBSEEKER: VIEW MY APPLICATION STATUS =====================
@hybrid_auth_required(['jobseeker'])
def application_status(request):
    apps = Application.objects.filter(job_seeker=request.user)
    is_api = request.headers.get('Accept') == 'application/json'
 
    if is_api:
        data = []
        for app in apps:
            data.append({
                'job': app.job.title,
                'status': app.status,
                'applied_at': app.applied_at
            })
        return JsonResponse({'applications': data})
 
    return render(request, 'applications/status.html', {
        'applications': apps
    })
# @login_required
 
# @role_required(['employer'])
 
# def job_applicants(request, job_id):
 
#     job = get_object_or_404(Job, id=job_id, employer=request.user)
 
#     applications = Application.objects.filter(job=job)
 
 
 
#     if request.headers.get('Accept') == 'application/json':
 
#         return JsonResponse({
 
#             'job': job.title,
 
#             'applications': list(applications.values())
 
#         })
 
 
 
#     return render(request, 'applications/applicants.html', {
 
#         'job': job,
 
#         'applications': applications
 
#     })
 
 
 
# ==============Employer → View applicants of a job++++++++++++++++
@csrf_exempt
@hybrid_auth_required(['employer'])
def job_applicants(request, job_id):
    # ✅ METHOD GUARD
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    applications = (
        Application.objects
        .filter(job=job)
        .select_related('job_seeker')
    )
    is_api = request.headers.get('Accept') == 'application/json'
    if is_api:
        data = []
        for app in applications:
            data.append({
                'application_id': app.id,
                'status': app.status,
                'applied_at': app.applied_at,
                'job_seeker': {
                    'id': app.job_seeker.id,
                    'email': app.job_seeker.email,
                    'full_name': f"{app.job_seeker.first_name} {app.job_seeker.last_name}",
                    'phone': app.job_seeker.phone,
                },
                'qualification': app.qualification,
                'experience': app.experience,
                'skills': app.skills,
                'address': app.address,
                # ✅ Resume URL (MEDIA)
                'resume_url': request.build_absolute_uri(app.resume.url)
                if app.resume else None,
            })
        return JsonResponse({
            'job': {
                'id': job.id,
                'title': job.title,
            },
            'total_applications': len(data),
            'applications': data,
        }, status=200)
    # ✅ TEMPLATE RESPONSE
    return render(
        request,
        'applications/applicants.html',
        {
            'job': job,
            'applications': applications,
        }
    )
#+==============Approve / Reject applicant (Employer)+===================
@csrf_exempt
# @login_required
# @role_required(['employer'])
@hybrid_auth_required(['employer'])
def update_application_status(request, app_id):
    application = get_object_or_404(
        Application,
        id=app_id,
        job__employer=request.user
    )
    is_api = request.headers.get('Accept') == 'application/json'
    status = request.POST.get('status')  # approved / rejected
    if status not in ['approved', 'rejected']:
        return JsonResponse({'error': 'Invalid status'}, status=400)
    application.status = status
    application.save()
    if is_api:
        return JsonResponse({
            'success': True,
            'application_id': application.id,
            'status': application.status
        })
    return redirect(request.META.get('HTTP_REFERER', '/'))
 
def aboutus(request):
    return render(request, 'applications/aboutus.html')
 
def contactus(request):
    return render(request, 'applications/contactus.html')
 
 
def quickeasy(request):
    return render(request, 'applications/quickeasy.html')
 
# =====================notifications============================================
 
@hybrid_auth_required(['employer'])
def notifications(request):
 
    employer_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
 
    unread_notifications = employer_notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
 
    return render(request, 'applications/notifications.html', {
        'employer_notifications': employer_notifications
    })
 
 
def notifications_json(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    data = [
        {
            'message': n.message,
            'created_at': n.created_at.strftime('%b %d, %Y %H:%M'),
            'is_read': n.is_read
        } for n in notifications
    ]
    return JsonResponse({'notifications': data})
 
from django.shortcuts import redirect
 
@hybrid_auth_required(['employer'])
def notifications(request):
    # sirf current logged-in user ke notifications fetch kare
    employer_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
 
    # sab unread notifications ko read mark karo
    unread_notifications = employer_notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
 
    return render(request, 'applications/notifications.html', {
        'employer_notifications': employer_notifications
    })
 
 
@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.delete()
    return redirect('notifications')
 
 
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html')
 