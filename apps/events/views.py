from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import Event
from .serializers import EventSerializer
from rest_framework import filters


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event_type', 'all_day']
    ordering = ['start_datetime']

    def get_queryset(self):
        return Event.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Lista eventos próximos (próximos 30 dias)"""
        today = datetime.now()
        next_month = today + timedelta(days=30)
        upcoming = self.get_queryset().filter(
            start_datetime__gte=today,
            start_datetime__lte=next_month
        )
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Lista eventos de hoje"""
        today = datetime.now().date()
        today_events = self.get_queryset().filter(
            start_datetime__date=today
        )
        serializer = self.get_serializer(today_events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_month(self, request):
        """Lista eventos por mês"""
        year = request.query_params.get('year', datetime.now().year)
        month = request.query_params.get('month', datetime.now().month)

        events = self.get_queryset().filter(
            start_datetime__year=year,
            start_datetime__month=month
        )
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)