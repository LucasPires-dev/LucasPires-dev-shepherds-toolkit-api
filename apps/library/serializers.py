from rest_framework import serializers
from .models import LibraryResource, LibraryHighlight


class LibraryHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryHighlight
        fields = ['id', 'user', 'resource', 'page_number',
                  'highlighted_text', 'note', 'color', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class LibraryResourceSerializer(serializers.ModelSerializer):
    highlights = LibraryHighlightSerializer(many=True, read_only=True)
    highlight_count = serializers.SerializerMethodField()

    class Meta:
        model = LibraryResource
        fields = ['id', 'user', 'title', 'author', 'resource_type',
                  'category', 'isbn', 'publisher', 'publication_year',
                  'file_url', 'cover_image_url', 'notes', 'is_favorite',
                  'created_at', 'updated_at', 'highlights', 'highlight_count']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_highlight_count(self, obj):
        return obj.highlights.count()


class LibraryResourceListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagens"""

    class Meta:
        model = LibraryResource
        fields = ['id', 'title', 'author', 'resource_type',
                  'publication_year', 'is_favorite', 'cover_image_url']
