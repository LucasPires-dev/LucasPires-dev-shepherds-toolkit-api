from django.contrib import admin
from .models import AIInteraction, AIQuota

@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'interaction_type', 'verse', 'total_tokens', 'created_at']
    list_filter = ['interaction_type', 'created_at']
    search_fields = ['user__username', 'query', 'response']
    date_hierarchy = 'created_at'


@admin.register(AIQuota)
class AIQuotaAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'subscription_status', 'updated_at']
    list_filter = ['plan', 'subscription_status']
    search_fields = ['user__username', 'user__email', 'stripe_customer_id']
