from django.contrib import admin
from .models import LibraryResource, LibraryHighlight

@admin.register(LibraryResource)
class LibraryResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'resource_type', 'user',
                   'publication_year', 'is_favorite']
    list_filter = ['resource_type', 'is_favorite', 'publication_year', 'created_at']
    search_fields = ['title', 'author', 'isbn', 'user__username']


@admin.register(LibraryHighlight)
class LibraryHighlightAdmin(admin.ModelAdmin):
    list_display = ['resource', 'user', 'page_number', 'color', 'created_at']
    list_filter = ['color', 'created_at']
    search_fields = ['resource__title', 'user__username', 'highlighted_text']