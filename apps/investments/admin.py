from django.contrib import admin
from .models import Investment


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'investment_type', 'institution', 'currency', 'current_value',
                     'liquidity', 'status', 'start_date', 'maturity_date', 'user']
    list_filter = ['investment_type', 'liquidity', 'status', 'currency']
    search_fields = ['name', 'institution', 'user__username']
    date_hierarchy = 'start_date'
