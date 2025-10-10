from django.contrib import admin
from .models import Goal, GoalTask, GoalComment

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'priority', 'status',
                   'progress_percentage', 'start_date', 'end_date']
    list_filter = ['category', 'priority', 'status', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    date_hierarchy = 'created_at'


@admin.register(GoalTask)
class GoalTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'goal', 'status', 'responsible',
                   'due_date', 'order_index']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['title', 'description', 'goal__title']


@admin.register(GoalComment)
class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ['goal', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comment', 'goal__title', 'user__username']
