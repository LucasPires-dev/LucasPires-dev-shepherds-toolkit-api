from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PrayerRequest
from .serializers import PrayerRequestSerializer
from rest_framework import filters


class PrayerRequestViewSet(viewsets.ModelViewSet):
    serializer_class = PrayerRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'priority', 'status', 'is_confidential']
    search_fields = ['title', 'description']
    ordering = ['-created_at']

    def get_queryset(self):
        return PrayerRequest.objects.filter(user=self.request.user).select_related('member')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Lista apenas pedidos ativos"""
        active = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_answered(self, request, pk=None):
        """Marca pedido como respondido"""
        prayer = self.get_object()
        prayer.status = 'answered'
        prayer.answered_date = request.data.get('answered_date')
        prayer.answer_description = request.data.get('answer_description')
        prayer.save()
        return Response({'status': 'answered'})