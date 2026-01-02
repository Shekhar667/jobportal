from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Job
from accounts.decorators import role_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
@role_required(['admin'])
def admin_job_list(request):
    jobs = Job.objects.all()
    is_api = request.headers.get('Accept') == 'application/json'

    if is_api:
        data = list(jobs.values())
        return JsonResponse({'jobs': data})

    return render(request, 'jobs/admin_job_list.html', {'jobs': jobs})

# ============================
# EMPLOYER: POST A JOB
# ============================

@csrf_exempt
@login_required
@role_required(['employer'])
def post_job(request):
    is_api = request.headers.get('Accept') == 'application/json'

    try:
        if request.method == 'POST':
            job = Job.objects.create(
                employer=request.user,
                title=request.POST.get('title'),
                location=request.POST.get('location'),
                salary=request.POST.get('salary'),
                description=request.POST.get('description'),
                job_type=request.POST.get('job_type')
            )

            if is_api:
                return JsonResponse({'success': True, 'job_id': job.id}, status=201)

            return redirect('/my_jobs/')

        return render(request, 'jobs/post_job.html')

    except Exception as e:
        print('POST JOB ERROR:', e)
        if is_api:
            return JsonResponse({'error': 'Internal server error'}, status=500)
        return render(request, 'jobs/post_job.html', {'error': 'Something went wrong'})


# ============================
# EMPLOYER: VIEW MY JOBS
# ============================
@csrf_exempt
@login_required
@role_required(['employer'])
def my_jobs(request):
    jobs = Job.objects.filter(employer=request.user)
    is_api = request.headers.get('Accept') == 'application/json'

    if is_api:
        return JsonResponse({
            'jobs': list(jobs.values())
        })

    return render(request, 'jobs/my_jobs.html', {'jobs': jobs})


# =============================
# JOB SEEKER: JOB LIST + SEARCH
# =============================
@login_required
@role_required(['jobseeker'])
def job_list(request):
    jobs = Job.objects.all()
    q = request.GET.get('q')
    if q:
        jobs = jobs.filter(title__icontains=q)

    is_api = request.headers.get('Accept') == 'application/json'

    if is_api:
        return JsonResponse({'jobs': list(jobs.values())})

    return render(request, 'jobs/job_list.html', {'jobs': jobs})


@csrf_exempt
@login_required
@role_required(['employer'])
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    is_api = request.headers.get('Accept') == 'application/json'

    if request.method == 'POST':
        job.title = request.POST.get('title', job.title)
        job.location = request.POST.get('location', job.location)
        job.salary = request.POST.get('salary', job.salary)
        job.description = request.POST.get('description', job.description)
        job.job_type = request.POST.get('job_type', job.job_type)
        job.save()

        if is_api:
            return JsonResponse({'success': True, 'message': 'Job updated'})

        return redirect('my_jobs')

    if is_api:
        return JsonResponse({'job': {
            'id': job.id,
            'title': job.title,
            'location': job.location,
            'salary': job.salary,
            'description': job.description,
            'job_type': job.job_type,
        }})

    return render(request, 'jobs/edit_job.html', {'job': job})

@csrf_exempt
@login_required
@role_required(['employer'])
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    is_api = request.headers.get('Accept') == 'application/json'

    if request.method == 'POST':
        job.delete()

        if is_api:
            return JsonResponse({'success': True, 'message': 'Job deleted'})

        return redirect('my_jobs')

    return HttpResponseForbidden("Invalid request")

#++++++++++++++++++Job ACTIVE / INACTIVE toggle (Employer)+++++++++++++++#
@csrf_exempt
@login_required
@role_required(['employer'])
def toggle_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    is_api = request.headers.get('Accept') == 'application/json'

    job.is_active = not job.is_active
    job.save()

    if is_api:
        return JsonResponse({
            'success': True,
            'job_id': job.id,
            'is_active': job.is_active
        })

    return redirect('my_jobs')
