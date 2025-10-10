from rest_framework import serializers
from .models import PrayerRequest


class PrayerRequestSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name',
                                        read_only=True, allow_null=True)

    class Meta:
        model = PrayerRequest
        fields = ['id', 'user', 'member', 'member_name', 'title',
                  'description', 'category', 'priority', 'status',
                  'is_confidential', 'answered_date', 'answer_description',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
