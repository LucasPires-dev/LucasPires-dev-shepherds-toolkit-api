from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read',
                    'related_entity_type', 'created_at']
    list_filter = ['notification_type', 'is_read', 'related_entity_type', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    date_hierarchy = 'created_at'

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    mark_as_read.short_description = "Marcar como lida"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    mark_as_unread.short_description = "Marcar como não lida"
