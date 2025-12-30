from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
from jobs.models import Job
from applications.models import Application

@login_required
def home(request):
    total_jobs = Job.objects.count()
    total_applications = Application.objects.count()

    categories = Job.objects.values_list('title', flat=True)

    context = {
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'categories': categories,
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'admin':
        return render(request, 'dashboard/admin_dashboard.html')
    if user.role == 'employer':
        return render(request, 'dashboard/employer_dashboard.html')
    return render(request, 'dashboard/jobseeker_dashboard.html')