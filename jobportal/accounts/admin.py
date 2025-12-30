
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
        'phone',
        'is_email_verified'
    )

    list_filter = ('role',  'username')
    search_fields = ('username', 'email')
    # ordering = ('-date_joined',)
