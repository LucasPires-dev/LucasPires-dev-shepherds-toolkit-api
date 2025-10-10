from django.contrib import admin
from .models import Sermon, SermonVerse, SermonTag, SermonTagRelation

@admin.register(Sermon)
class SermonAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'base_text', 'preached_date', 'created_at']
    list_filter = ['status', 'preached_date', 'created_at']
    search_fields = ['title', 'content', 'user__username', 'theme']
    date_hierarchy = 'created_at'


@admin.register(SermonVerse)
class SermonVerseAdmin(admin.ModelAdmin):
    list_display = ['sermon', 'verse', 'order_index']
    list_filter = ['created_at']
    search_fields = ['sermon__title', 'verse__text']


@admin.register(SermonTag)
class SermonTagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
