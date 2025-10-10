from rest_framework import serializers
from .models import Sermon, SermonVerse, SermonTag


class SermonVerseSerializer(serializers.ModelSerializer):
    verse_reference = serializers.CharField(source='verse.reference', read_only=True)
    verse_text = serializers.CharField(source='verse.text', read_only=True)

    class Meta:
        model = SermonVerse
        fields = ['id', 'sermon', 'verse', 'verse_reference',
                  'verse_text', 'order_index', 'created_at']


class SermonTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SermonTag
        fields = ['id', 'name']


class SermonSerializer(serializers.ModelSerializer):
    verses = SermonVerseSerializer(many=True, read_only=True)
    tags = SermonTagSerializer(many=True, read_only=True, source='tag_relations.tag')
    author_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Sermon
        fields = ['id', 'user', 'author_name', 'title', 'content',
                  'base_text', 'theme', 'category', 'status',
                  'preached_date', 'estimated_duration',
                  'created_at', 'updated_at', 'verses', 'tags']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class SermonListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagens"""
    author_name = serializers.CharField(source='user.get_full_name', read_only=True)
    verse_count = serializers.SerializerMethodField()

    class Meta:
        model = Sermon
        fields = ['id', 'title', 'author_name', 'base_text', 'theme',
                  'status', 'preached_date', 'created_at', 'verse_count']

    def get_verse_count(self, obj):
        return obj.verses.count()