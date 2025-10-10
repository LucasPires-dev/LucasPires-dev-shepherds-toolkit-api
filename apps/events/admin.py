from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'event_type', 'start_datetime',
                   'end_datetime', 'location']
    list_filter = ['event_type', 'start_datetime', 'created_at']
    search_fields = ['title', 'description', 'location', 'user__username']
    date_hierarchy = 'start_datetime'