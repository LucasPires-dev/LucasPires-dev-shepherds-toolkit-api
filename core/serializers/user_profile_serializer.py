from rest_framework import serializers
from django.contrib.auth.models import User
from models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    # Campos do usuário relacionados (opcional, só leitura)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'email',
            'display_name',
            'profile_image',
            'bio',
            'role',
            'church_name',
            'church_location',
            'ordination_date',
            'ministerial_focus',
            'theme',
            'language',
            'verse_version_default',
            'created_at',
            'last_active_at',
        ]
        read_only_fields = ['id', 'created_at', 'last_active_at']
