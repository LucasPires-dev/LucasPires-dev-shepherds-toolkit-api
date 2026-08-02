from django.contrib import admin

from .models import GoogleCalendarConnection


@admin.register(GoogleCalendarConnection)
class GoogleCalendarConnectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'google_email', 'connected_at', 'updated_at']
    readonly_fields = ['access_token', 'refresh_token_encrypted', 'connected_at', 'updated_at']
