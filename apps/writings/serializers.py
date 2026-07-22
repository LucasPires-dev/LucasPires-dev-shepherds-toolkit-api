from rest_framework import serializers
from .models import Writing, WritingVerse, WritingTag, WritingTagRelation


class WritingTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingTag
        fields = ['id', 'name']


class WritingVerseSerializer(serializers.ModelSerializer):
    verse_reference = serializers.CharField(source='verse.reference', read_only=True)
    verse_text = serializers.CharField(source='verse.text', read_only=True)

    class Meta:
        model = WritingVerse
        fields = ['id', 'writing', 'verse', 'verse_reference',
                  'verse_text', 'order_index', 'created_at']


class WritingSerializer(serializers.ModelSerializer):
    verses = WritingVerseSerializer(many=True, read_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    tag_list = serializers.SerializerMethodField(read_only=True)
    author_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Writing
        fields = [
            'id', 'user', 'author_name', 'title', 'content',
            'base_text', 'theme', 'category', 'status', 'type',
            'preached_date', 'estimated_duration',
            'created_at', 'updated_at', 'verses', 'tags', 'tag_list'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        extra_kwargs = {
            'title': {'required': True},
            'content': {'required': False, 'allow_blank': True, 'allow_null': True},
            'base_text': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    def get_tag_list(self, obj):
        """Retorna lista de tags do escrito"""
        return [relation.tag.name for relation in obj.tag_relations.select_related('tag').all()]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        writing = Writing.objects.create(**validated_data)

        # Criar tags
        self._handle_tags(writing, tags_data)

        return writing

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)

        # Atualizar campos do escrito
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Atualizar tags se fornecidas
        if tags_data is not None:
            self._handle_tags(instance, tags_data)

        return instance

    def _handle_tags(self, writing, tags_data):
        """Cria ou atualiza tags do escrito"""
        # Remover tags antigas
        WritingTagRelation.objects.filter(writing=writing).delete()

        # Adicionar novas tags
        for tag_name in tags_data:
            if tag_name and tag_name.strip():
                tag, created = WritingTag.objects.get_or_create(
                    name=tag_name.strip()
                )
                WritingTagRelation.objects.create(
                    writing=writing,
                    tag=tag
                )


class WritingListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagens"""
    author_name = serializers.CharField(source='user.get_full_name', read_only=True)
    verse_count = serializers.SerializerMethodField()
    tag_list = serializers.SerializerMethodField()

    class Meta:
        model = Writing
        fields = [
            'id', 'title', 'author_name', 'base_text',
            'theme', 'status', 'type', 'preached_date', 'created_at',
            'updated_at', 'verse_count', 'tag_list'
        ]

    def get_verse_count(self, obj):
        return obj.verses.count()

    def get_tag_list(self, obj):
        return [relation.tag.name for relation in obj.tag_relations.select_related('tag').all()]
