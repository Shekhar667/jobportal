from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Application
from accounts.decorators import role_required
from .models import Application
from jobs.models import Job

@login_required
@role_required(['admin'])
def admin_applications(request):
    applications = Application.objects.select_related('job', 'job_seeker')

    if request.method == 'POST':
        app_id = request.POST.get('app_id')
        status = request.POST.get('status')
        app = get_object_or_404(Application, id=app_id)
        app.status = status
        app.save()
        return redirect(request.path)

    return render(request, 'applications/admin_applications.html', {
        'applications': applications
    })


@login_required
@role_required(['jobseeker'])
def apply_job(request, job_id):
    Application.objects.get_or_create(
        job_id=job_id,
        job_seeker=request.user
    )
    return redirect('/dashboard/')

@login_required
@role_required(['jobseeker'])
def application_status(request):
    apps = Application.objects.filter(job_seeker=request.user)
    return render(request, 'applications/status.html', {'applications': apps})


@login_required
@role_required(['employer'])
def job_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    applications = Application.objects.filter(job=job)

    return render(request, 'applications/applicants.html', {
        'job': job,
        'applications': applications
    })