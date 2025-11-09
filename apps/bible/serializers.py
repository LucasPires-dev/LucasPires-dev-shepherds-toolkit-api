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
    user_highlight = serializers.SerializerMethodField()

    # ✅ NOVOS CAMPOS DE NAVEGAÇÃO
    navigation = serializers.SerializerMethodField()

    class Meta:
        model = BibleVerse
        fields = ['id', 'book', 'book_name', 'chapter', 'verse',
                  'text', 'version', 'reference', 'user_highlight', 'navigation']

    def get_user_highlight(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        from .models import VerseHighlight
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
                'updated_at': highlight.updated_at,
            }
        return None

    def get_navigation(self, obj):
        """
        Retorna links de navegação para capítulos anterior/próximo
        Incluído apenas no PRIMEIRO versículo de cada capítulo
        """
        # Só adicionar navegação no primeiro versículo
        if obj.verse != 1:
            return None

        book = obj.book
        chapter = obj.chapter
        version = obj.version

        # Buscar informações do livro anterior e próximo
        previous_book = BibleBook.objects.filter(
            book_order=book.book_order - 1
        ).first()

        next_book = BibleBook.objects.filter(
            book_order=book.book_order + 1
        ).first()

        navigation = {
            'current': {
                'book': book.abbrev,
                'book_name': book.name,
                'chapter': chapter,
                'total_chapters': book.total_chapters
            },
            'previous': None,
            'next': None
        }

        # Capítulo anterior
        if chapter > 1:
            # Capítulo anterior no mesmo livro
            navigation['previous'] = {
                'book': book.abbrev,
                'book_name': book.name,
                'chapter': chapter - 1,
                'is_same_book': True
            }
        elif previous_book:
            # Último capítulo do livro anterior
            navigation['previous'] = {
                'book': previous_book.abbrev,
                'book_name': previous_book.name,
                'chapter': previous_book.total_chapters,
                'is_same_book': False
            }

        # Próximo capítulo
        if chapter < book.total_chapters:
            # Próximo capítulo no mesmo livro
            navigation['next'] = {
                'book': book.abbrev,
                'book_name': book.name,
                'chapter': chapter + 1,
                'is_same_book': True
            }
        elif next_book:
            # Primeiro capítulo do próximo livro
            navigation['next'] = {
                'book': next_book.abbrev,
                'book_name': next_book.name,
                'chapter': 1,
                'is_same_book': False
            }

        return navigation


# ✅ NOVO SERIALIZER ESPECÍFICO PARA RESPOSTA DE CAPÍTULO
class ChapterResponseSerializer(serializers.Serializer):
    """Serializer para resposta completa de um capítulo"""
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = BibleVerseSerializer(many=True)

    # Navegação de capítulo
    chapter_navigation = serializers.DictField()

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
