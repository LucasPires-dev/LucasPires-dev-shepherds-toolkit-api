from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Writing, WritingTag
from .serializers import WritingSerializer, WritingListSerializer, WritingTagSerializer


class WritingViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'type']
    search_fields = ['title', 'content', 'theme', 'base_text']
    ordering_fields = ['created_at', 'preached_date', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Writing.objects.filter(user=self.request.user).select_related('user')

    def get_serializer_class(self):
        if self.action == 'list':
            return WritingListSerializer
        return WritingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Lista escritos recentes"""
        recent = self.get_queryset()[:5]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Agrupa escritos por status"""
        queryset = self.get_queryset()
        data = {
            'draft': queryset.filter(status='draft').count(),
            'completed': queryset.filter(status='completed').count(),
            'archived': queryset.filter(status='archived').count(),
        }
        return Response(data)


class WritingTagViewSet(viewsets.ModelViewSet):
    queryset = WritingTag.objects.all()
    serializer_class = WritingTagSerializer
