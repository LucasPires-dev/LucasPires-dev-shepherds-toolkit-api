from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'church_name', 'ministry', 'role', 'avatar_url',
                  'created_at', 'last_login']
        read_only_fields = ['id', 'created_at', 'last_login']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm',
                  'first_name', 'last_name', 'church_name', 'ministry', 'role']

    def validate_email(self, value):
        """Verifica se o email já existe"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está em uso")
        return value

    def validate_username(self, value):
        """Verifica se o username já existe"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está em uso")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "As senhas não coincidem"})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user