from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime, timedelta
from .models import Finance
from .serializers import FinanceSerializer, FinanceSummarySerializer
from rest_framework import filters


class FinanceViewSet(viewsets.ModelViewSet):
    serializer_class = FinanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'category', 'payment_method']
    ordering = ['-transaction_date']

    def get_queryset(self):
        return Finance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumo financeiro por período"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = self.get_queryset()
        if start_date and end_date:
            queryset = queryset.filter(
                transaction_date__gte=start_date,
                transaction_date__lte=end_date
            )

        income = queryset.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense = queryset.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

        data = {
            'total_income': income,
            'total_expense': expense,
            'balance': income - expense,
            'period_start': start_date,
            'period_end': end_date,
        }

        serializer = FinanceSummarySerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Agrupa transações por categoria"""
        queryset = self.get_queryset()
        categories = queryset.values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')
        return Response(categories)