from django.contrib import admin
from .models import PrayerRequest

@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'priority', 'status',
                   'is_confidential', 'created_at']
    list_filter = ['category', 'priority', 'status', 'is_confidential', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'member__full_name']
    date_hierarchy = 'created_at'