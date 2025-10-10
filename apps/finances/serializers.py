from rest_framework import serializers
from .models import Finance

class FinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finance
        fields = ['id', 'user', 'type', 'category', 'description',
                 'amount', 'transaction_date', 'payment_method',
                 'reference_number', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class FinanceSummarySerializer(serializers.Serializer):
    """Serializer para resumo financeiro"""
    total_income = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=10, decimal_places=2)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    period_start = serializers.DateField()
    period_end = serializers.DateField()