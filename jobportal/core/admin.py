from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'role',
        'is_active',
        'is_email_verified',
        'is_staff',
        'date_joined'
    )

    list_filter = ('role', 'is_active', 'is_email_verified')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
