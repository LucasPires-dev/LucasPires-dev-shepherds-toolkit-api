from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'notification_type',
                 'is_read', 'related_entity_type', 'related_entity_id',
                 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagens"""
    class Meta:
        model = Notification
        fields = ['id', 'title', 'notification_type', 'is_read', 'created_at']