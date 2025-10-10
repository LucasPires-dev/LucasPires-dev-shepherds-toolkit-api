from django.contrib import admin
from .models import (
    BibleBook, BibleVerse, VerseHighlight, VerseNote,
    ReadingPlan, ReadingPlanProgress
)

@admin.register(BibleBook)
class BibleBookAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbrev', 'testament', 'book_order', 'total_chapters']
    list_filter = ['testament']
    search_fields = ['name', 'abbrev']
    ordering = ['book_order']


@admin.register(BibleVerse)
class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ['book', 'chapter', 'verse', 'version']
    list_filter = ['book', 'version']
    search_fields = ['text', 'book__name']
    ordering = ['book__book_order', 'chapter', 'verse']


@admin.register(VerseHighlight)
class VerseHighlightAdmin(admin.ModelAdmin):
    list_display = ['user', 'verse', 'color', 'is_favorite', 'created_at']
    list_filter = ['color', 'is_favorite', 'created_at']
    search_fields = ['user__username', 'verse__text']


@admin.register(VerseNote)
class VerseNoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'verse', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'note', 'verse__text']


@admin.register(ReadingPlan)
class ReadingPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'plan_type', 'status', 'start_date', 'end_date']
    list_filter = ['plan_type', 'status', 'start_date']
    search_fields = ['name', 'user__username']


@admin.register(ReadingPlanProgress)
class ReadingPlanProgressAdmin(admin.ModelAdmin):
    list_display = ['plan', 'book', 'chapter', 'is_completed', 'completed_at']
    list_filter = ['is_completed', 'completed_at']
    search_fields = ['plan__name', 'book__name']