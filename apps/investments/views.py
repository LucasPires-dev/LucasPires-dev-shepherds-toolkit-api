import django_filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from .models import Investment
from .serializers import InvestmentSerializer, InvestmentSummarySerializer


class InvestmentFilter(django_filters.FilterSet):
    class Meta:
        model = Investment
        fields = ['investment_type', 'liquidity', 'status', 'currency']


class InvestmentViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = InvestmentFilter
    search_fields = ['name', 'institution']
    ordering = ['-start_date']

    def get_queryset(self):
        return Investment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        extra = {}
        if 'current_value' not in self.request.data:
            extra['current_value'] = serializer.validated_data.get('principal_amount')
        serializer.save(user=self.request.user, **extra)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Totais consolidados (em BRL): total investido, valor atual, reserva financeira e rendimento."""
        queryset = self.get_queryset().filter(status='active')

        total_invested = sum((inv.principal_amount_brl for inv in queryset), start=0)
        total_current_value = sum((inv.current_value_brl for inv in queryset), start=0)
        reserve_total = sum((inv.current_value_brl for inv in queryset if inv.counts_as_reserve), start=0)

        data = {
            'total_invested': total_invested,
            'total_current_value': total_current_value,
            'reserve_total': reserve_total,
            'yield_total': total_current_value - total_invested,
        }
        serializer = InvestmentSummarySerializer(data)
        return Response(serializer.data)
