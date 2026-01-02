from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import Application
from jobs.models import Job
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
@role_required(['admin'])
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

@csrf_exempt
@login_required
@role_required(['jobseeker'])
def apply_job(request, job_id):
    try:
        app, created = Application.objects.get_or_create(
            job_id=job_id,
            job_seeker=request.user
        )

        if request.headers.get('Accept') == 'application/json':
            return JsonResponse(
                {'success': True, 'created': created},
                status=201 if created else 200
            )

        return redirect('/dashboard/')

    except Exception as e:
        print('APPLY JOB ERROR:', e)
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
@login_required
@role_required(['jobseeker'])
def application_status(request):
    apps = Application.objects.filter(job_seeker=request.user)
    is_api = request.headers.get('Accept') == 'application/json'

    if is_api:
        return JsonResponse({'applications': list(apps.values())})

    return render(request, 'applications/status.html', {'applications': apps})


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
@login_required
@role_required(['employer'])
def job_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    applications = Application.objects.filter(job=job)

    is_api = request.headers.get('Accept') == 'application/json'

    if is_api:
        data = []
        for app in applications:
            data.append({
                'application_id': app.id,
                'job_seeker': app.job_seeker.email,
                'status': app.status
            })
        return JsonResponse({'applications': data})

    return render(request, 'applications/applicants.html', {
        'job': job,
        'applications': applications
    })

#+==============Approve / Reject applicant (Employer)+===================
@csrf_exempt
@login_required
@role_required(['employer'])
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

    return redirect(request.META.get('HTTP_REFERER', '/dashboard/'))
