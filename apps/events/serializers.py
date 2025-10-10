from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'user', 'title', 'description', 'event_type',
                 'location', 'start_datetime', 'end_datetime', 'all_day',
                 'color', 'reminder_minutes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
