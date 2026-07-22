from django.contrib import admin
from .models import Writing, WritingVerse, WritingTag


@admin.register(Writing)
class WritingAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'type', 'status', 'category', 'preached_date', 'created_at']
    list_filter = ['status', 'type', 'category']
    search_fields = ['title', 'content', 'theme', 'base_text']


@admin.register(WritingVerse)
class WritingVerseAdmin(admin.ModelAdmin):
    list_display = ['writing', 'verse', 'order_index']


@admin.register(WritingTag)
class WritingTagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
