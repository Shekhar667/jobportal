from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Job
from accounts.decorators import role_required

@login_required
@role_required(['admin'])
def admin_job_list(request):
    jobs = Job.objects.all()
    return render(request, 'jobs/admin_job_list.html', {'jobs': jobs})

# ============================
# EMPLOYER: POST A JOB
# ============================

@login_required
@role_required(['employer'])
def post_job(request):
    if request.method == 'POST':
        Job.objects.create(
            employer=request.user,
            title=request.POST['title'],
            location=request.POST['location'],
            salary=request.POST['salary'],
            description=request.POST['description']
        )
        return redirect('/dashboard/')
    return render(request, 'jobs/post_job.html')


# ============================
# EMPLOYER: VIEW MY JOBS
# ============================

@login_required
@role_required(['employer'])
def my_jobs(request):
    jobs = Job.objects.filter(employer=request.user)
    return render(request, 'jobs/my_jobs.html', {'jobs': jobs})


# ============================
# JOB SEEKER: JOB LIST + SEARCH
# ============================
@login_required
@role_required(['jobseeker'])
def job_list(request):
    jobs = Job.objects.all()
    q = request.GET.get('q')
    if q:
        jobs = jobs.filter(title__icontains=q)
    return render(request, 'jobs/job_list.html', {'jobs': jobs})
