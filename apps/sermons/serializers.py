from rest_framework import serializers
from .models import Sermon, SermonVerse, SermonTag, SermonTagRelation


class SermonTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SermonTag
        fields = ['id', 'name']


class SermonVerseSerializer(serializers.ModelSerializer):
    verse_reference = serializers.CharField(source='verse.reference', read_only=True)
    verse_text = serializers.CharField(source='verse.text', read_only=True)

    class Meta:
        model = SermonVerse
        fields = ['id', 'sermon', 'verse', 'verse_reference',
                  'verse_text', 'order_index', 'created_at']


class SermonSerializer(serializers.ModelSerializer):
    verses = SermonVerseSerializer(many=True, read_only=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    tag_list = serializers.SerializerMethodField(read_only=True)
    author_name = serializers.CharField(source='user.get_full_name', read_only=True)

    # Aceitar tanto sermon_date quanto preached_date
    sermon_date = serializers.DateField(source='preached_date', required=False, allow_null=True)
    scripture_reference = serializers.CharField(source='base_text', required=False, allow_blank=True)

    class Meta:
        model = Sermon
        fields = [
            'id', 'user', 'author_name', 'title', 'content',
            'base_text', 'scripture_reference', 'theme', 'category', 'status',
            'preached_date', 'sermon_date', 'estimated_duration',
            'created_at', 'updated_at', 'verses', 'tags', 'tag_list'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        extra_kwargs = {
            'title': {'required': True},
            'content': {'required': False, 'allow_blank': True, 'allow_null': True},
            'base_text': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

    def get_tag_list(self, obj):
        """Retorna lista de tags do sermão"""
        return [relation.tag.name for relation in obj.tag_relations.select_related('tag').all()]

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        sermon = Sermon.objects.create(**validated_data)

        # Criar tags
        self._handle_tags(sermon, tags_data)

        return sermon

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)

        # Atualizar campos do sermão
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Atualizar tags se fornecidas
        if tags_data is not None:
            self._handle_tags(instance, tags_data)

        return instance

    def _handle_tags(self, sermon, tags_data):
        """Cria ou atualiza tags do sermão"""
        # Remover tags antigas
        SermonTagRelation.objects.filter(sermon=sermon).delete()

        # Adicionar novas tags
        for tag_name in tags_data:
            if tag_name and tag_name.strip():
                tag, created = SermonTag.objects.get_or_create(
                    name=tag_name.strip()
                )
                SermonTagRelation.objects.create(
                    sermon=sermon,
                    tag=tag
                )


class SermonListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagens"""
    author_name = serializers.CharField(source='user.get_full_name', read_only=True)
    verse_count = serializers.SerializerMethodField()
    tag_list = serializers.SerializerMethodField()
    sermon_date = serializers.DateField(source='preached_date', read_only=True)
    scripture_reference = serializers.CharField(source='base_text', read_only=True)

    class Meta:
        model = Sermon
        fields = [
            'id', 'title', 'author_name', 'base_text', 'scripture_reference',
            'theme', 'status', 'preached_date', 'sermon_date', 'created_at',
            'updated_at', 'verse_count', 'tag_list'
        ]

    def get_verse_count(self, obj):
        return obj.verses.count()

    def get_tag_list(self, obj):
        return [relation.tag.name for relation in obj.tag_relations.select_related('tag').all()]