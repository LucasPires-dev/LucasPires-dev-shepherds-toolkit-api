from rest_framework import serializers
from .models import (
    BibleBook, BibleVerse, VerseHighlight, VerseNote,
    ReadingPlan, ReadingPlanProgress
)


class BibleBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = BibleBook
        fields = '__all__'


class BibleVerseSerializer(serializers.ModelSerializer):
    book_name = serializers.CharField(source='book.name', read_only=True)
    reference = serializers.CharField(read_only=True)
    user_highlight = serializers.SerializerMethodField()  # ← NOVO

    class Meta:
        model = BibleVerse
        fields = ['id', 'book', 'book_name', 'chapter', 'verse',
                  'text', 'version', 'reference', 'user_highlight']  # ← ADICIONADO

    def get_user_highlight(self, obj):
        """Retorna os dados de marcação do usuário logado para este versículo"""
        request = self.context.get('request')

        # Se não há usuário logado, retorna None
        if not request or not request.user.is_authenticated:
            return None

        # Busca a marcação do usuário para este versículo
        highlight = VerseHighlight.objects.filter(
            user=request.user,
            verse=obj
        ).first()

        if highlight:
            return {
                'id': str(highlight.id),
                'color': highlight.color,
                'is_favorite': highlight.is_favorite,
                'created_at': highlight.created_at,
            }

        return None


class VerseHighlightSerializer(serializers.ModelSerializer):
    verse_reference = serializers.CharField(source='verse.reference', read_only=True)
    verse_text = serializers.CharField(source='verse.text', read_only=True)

    class Meta:
        model = VerseHighlight
        fields = ['id', 'user', 'verse', 'verse_reference', 'verse_text',
                  'color', 'is_favorite', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class VerseNoteSerializer(serializers.ModelSerializer):
    verse_reference = serializers.CharField(source='verse.reference', read_only=True)

    class Meta:
        model = VerseNote
        fields = ['id', 'user', 'verse', 'verse_reference', 'note',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ReadingPlanProgressSerializer(serializers.ModelSerializer):
    book_name = serializers.CharField(source='book.name', read_only=True)

    class Meta:
        model = ReadingPlanProgress
        fields = ['id', 'plan', 'book', 'book_name', 'chapter',
                  'is_completed', 'completed_at', 'notes']


class ReadingPlanSerializer(serializers.ModelSerializer):
    progress = ReadingPlanProgressSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = ReadingPlan
        fields = ['id', 'user', 'name', 'description', 'plan_type',
                  'start_date', 'end_date', 'status', 'created_at',
                  'progress', 'progress_percentage']
        read_only_fields = ['id', 'user', 'created_at']

    def get_progress_percentage(self, obj):
        total = obj.progress.count()
        completed = obj.progress.filter(is_completed=True).count()
        return (completed / total * 100) if total > 0 else 0
