from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer, NotificationListSerializer


class NotificationViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Lista notificações não lidas"""
        unread = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marca notificação como lida"""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Marca todas como lidas"""
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all marked as read'})