from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

from bold_voice.identity.models import User

admin.site.register(Permission)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'email_verified', 'date_joined']
    list_display_links = ['id', 'username']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    search_help_text = 'Search by username, email, first name, last name'
    fieldsets = [
        (None, {'fields': ['username', 'password']}),
        (_('Personal info'), {
            'fields': ['first_name', 'last_name', 'avatar', ('email', 'email_verified')]
        }),
        (_('Permissions'), {
            'fields': ['is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions']
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    ]
    add_fieldsets = [
        (None, {
            'classes': ['wide'],
            'fields': ['email', 'username', 'password1', 'password2'],
        })
    ]
    ordering = ['-id']
