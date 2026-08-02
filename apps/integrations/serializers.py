from rest_framework import serializers
from .models import GoogleCalendarConnection


class GoogleCalendarStatusSerializer(serializers.ModelSerializer):
    connected = serializers.SerializerMethodField()

    class Meta:
        model = GoogleCalendarConnection
        fields = ['connected', 'google_email', 'connected_at']

    def get_connected(self, obj):
        return True


class GoogleCalendarCallbackSerializer(serializers.Serializer):
    code = serializers.CharField()
    redirect_uri = serializers.URLField()


class KoinoniaTokenExchangeSerializer(serializers.Serializer):
    code = serializers.CharField()
    client_secret = serializers.CharField()
