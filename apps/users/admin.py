from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'church_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'church_name', 'first_name', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações da Igreja', {
            'fields': ('church_name', 'ministry', 'role', 'avatar_url')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações da Igreja', {
            'fields': ('church_name', 'ministry', 'role')
        }),
    )