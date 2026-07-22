from rest_framework import serializers
from .models import AIInteraction


class AIInteractionSerializer(serializers.ModelSerializer):
    verse_reference = serializers.CharField(source='verse.reference',
                                            read_only=True, allow_null=True)

    class Meta:
        model = AIInteraction
        fields = ['id', 'user', 'verse', 'verse_reference',
                  'interaction_type', 'query', 'response', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class AIRequestSerializer(serializers.Serializer):
    """Serializer para requisições à IA"""
    verse_id = serializers.IntegerField(required=False, allow_null=True)
    interaction_type = serializers.ChoiceField(
        choices=['context', 'etymology', 'related_texts', 'application']
    )
    query = serializers.CharField(max_length=1000)


class AIResponseSerializer(serializers.Serializer):
    """Serializer para respostas da IA"""
    response = serializers.CharField()
    interaction_id = serializers.UUIDField()
    created_at = serializers.DateTimeField()
    tokens_used = serializers.IntegerField()
    tokens_remaining = serializers.IntegerField(allow_null=True)


class AIUsageSerializer(serializers.Serializer):
    """Serializer para o resumo de cota/uso de IA do usuário"""
    plan = serializers.CharField()
    monthly_token_limit = serializers.IntegerField(allow_null=True)
    tokens_used = serializers.IntegerField()
    tokens_remaining = serializers.IntegerField(allow_null=True)
    period_reset_at = serializers.DateTimeField()