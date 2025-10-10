from django.contrib import admin
from .models import Finance

@admin.register(Finance)
class FinanceAdmin(admin.ModelAdmin):
    list_display = ['type', 'category', 'amount', 'transaction_date',
                   'payment_method', 'user']
    list_filter = ['type', 'category', 'payment_method', 'transaction_date', 'created_at']
    search_fields = ['description', 'reference_number', 'user__username']
    date_hierarchy = 'transaction_date'
