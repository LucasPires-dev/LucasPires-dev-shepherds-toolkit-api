from django.contrib import admin
from .models import AIInteraction

@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'interaction_type', 'verse', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['user__username', 'query', 'response']
    date_hierarchy = 'created_at'
