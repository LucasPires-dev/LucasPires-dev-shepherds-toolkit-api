from django.contrib import admin
from .models import Member, PastoralVisit

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'status', 'ministry',
                   'member_since', 'email', 'phone']
    list_filter = ['status', 'ministry', 'member_since', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'user__username']
    date_hierarchy = 'member_since'


@admin.register(PastoralVisit)
class PastoralVisitAdmin(admin.ModelAdmin):
    list_display = ['member', 'user', 'visit_date', 'visit_type',
                   'follow_up_needed']
    list_filter = ['visit_type', 'follow_up_needed', 'visit_date', 'created_at']
    search_fields = ['member__full_name', 'user__username', 'notes']
    date_hierarchy = 'visit_date'

