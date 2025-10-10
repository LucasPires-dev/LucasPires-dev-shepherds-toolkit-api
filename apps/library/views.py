from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LibraryResource, LibraryHighlight
from .serializers import (
    LibraryResourceSerializer, LibraryResourceListSerializer, LibraryHighlightSerializer
)
from rest_framework import filters


class LibraryResourceViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type', 'category', 'is_favorite']
    search_fields = ['title', 'author', 'notes']
    ordering = ['title']

    def get_queryset(self):
        return LibraryResource.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return LibraryResourceListSerializer
        return LibraryResourceSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """Lista recursos favoritos"""
        favorites = self.get_queryset().filter(is_favorite=True)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)


class LibraryHighlightViewSet(viewsets.ModelViewSet):
    serializer_class = LibraryHighlightSerializer

    def get_queryset(self):
        return LibraryHighlight.objects.filter(user=self.request.user).select_related('resource')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)