from rest_framework import serializers
from .models import Investment


class InvestmentSerializer(serializers.ModelSerializer):
    counts_as_reserve = serializers.BooleanField(read_only=True)
    current_value_brl = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Investment
        fields = ['id', 'user', 'name', 'investment_type', 'institution', 'currency',
                  'exchange_rate', 'principal_amount', 'current_value', 'rate_type',
                  'rate_value', 'fees_percentage', 'start_date', 'maturity_date',
                  'liquidity', 'status', 'notes', 'counts_as_reserve', 'current_value_brl',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        currency = attrs.get('currency', getattr(self.instance, 'currency', 'BRL'))
        exchange_rate = attrs.get('exchange_rate', getattr(self.instance, 'exchange_rate', None))
        if currency and currency != 'BRL' and not exchange_rate:
            raise serializers.ValidationError({'exchange_rate': 'Obrigatório quando a moeda é diferente de BRL.'})
        maturity_date = attrs.get('maturity_date', getattr(self.instance, 'maturity_date', None))
        liquidity = attrs.get('liquidity', getattr(self.instance, 'liquidity', None))
        if liquidity == 'at_maturity' and not maturity_date:
            raise serializers.ValidationError({'maturity_date': 'Obrigatório quando a liquidez é apenas no vencimento.'})
        return attrs


class InvestmentSummarySerializer(serializers.Serializer):
    """Resumo consolidado dos investimentos, valores convertidos para BRL"""
    total_invested = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_current_value = serializers.DecimalField(max_digits=14, decimal_places=2)
    reserve_total = serializers.DecimalField(max_digits=14, decimal_places=2)
    yield_total = serializers.DecimalField(max_digits=14, decimal_places=2)
