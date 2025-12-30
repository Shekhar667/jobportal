from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'employer',
        'job_type',
        'location',
        'created_at'
    )

    list_filter = ('title',)
    search_fields = ('title', 'job_type')
