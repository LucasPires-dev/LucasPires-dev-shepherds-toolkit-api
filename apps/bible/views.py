from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    BibleBook, BibleVerse, VerseHighlight, VerseNote,
    ReadingPlan, ReadingPlanProgress
)
from .serializers import (
    BibleBookSerializer, BibleVerseSerializer, VerseHighlightSerializer,
    VerseNoteSerializer, ReadingPlanSerializer, ReadingPlanProgressSerializer
)


class BibleBookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BibleBook.objects.all()
    serializer_class = BibleBookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['testament']
    search_fields = ['name', 'abbrev']


class BibleVerseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BibleVerse.objects.select_related('book')
    serializer_class = BibleVerseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['book', 'chapter', 'version']
    search_fields = ['text']

    @action(detail=False, methods=['get'])
    def by_reference(self, request):
        """Busca versículos por referência (ex: João 3:16)"""
        reference = request.query_params.get('reference')
        # Implementar lógica de parsing de referência
        # Ex: "João 3:16" -> book="João", chapter=3, verse=16
        return Response({'detail': 'Implementar parsing de referência'})


class VerseHighlightViewSet(viewsets.ModelViewSet):
    serializer_class = VerseHighlightSerializer

    def get_queryset(self):
        return VerseHighlight.objects.filter(user=self.request.user).select_related('verse', 'verse__book')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """Lista apenas versículos favoritados"""
        favorites = self.get_queryset().filter(is_favorite=True)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)


class VerseNoteViewSet(viewsets.ModelViewSet):
    serializer_class = VerseNoteSerializer

    def get_queryset(self):
        return VerseNote.objects.filter(user=self.request.user).select_related('verse', 'verse__book')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReadingPlanViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingPlanSerializer

    def get_queryset(self):
        return ReadingPlan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_chapter_complete(self, request, pk=None):
        """Marca um capítulo como completo no plano"""
        plan = self.get_object()
        book_id = request.data.get('book_id')
        chapter = request.data.get('chapter')

        progress, created = ReadingPlanProgress.objects.get_or_create(
            plan=plan,
            book_id=book_id,
            chapter=chapter
        )
        progress.is_completed = True
        progress.save()

        return Response({'status': 'completed'})