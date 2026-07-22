import calendar
import uuid
from decimal import Decimal, ROUND_DOWN, InvalidOperation
import django_filters
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from datetime import datetime, timedelta, date
from .models import Finance
from .serializers import FinanceSerializer, FinanceSummarySerializer
from rest_framework import filters

MAX_SERIES_LENGTH = 60


def add_months(start: date, months: int) -> date:
    """Adiciona N meses a uma data, ajustando o dia para o último dia do mês quando necessário."""
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def parse_date(value):
    return datetime.strptime(value, '%Y-%m-%d').date()


def default_status_for_date(transaction_date: date, today: date):
    """Lançamentos com data prevista antes de hoje já aconteceram de fato; hoje ou no futuro ainda não (podem estar previstos mas não pagos)."""
    if transaction_date < today:
        return 'confirmed', transaction_date
    return 'pending', None


class FinanceFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='transaction_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='transaction_date', lookup_expr='lte')

    class Meta:
        model = Finance
        fields = ['type', 'category', 'payment_method', 'status']


class FinanceViewSet(viewsets.ModelViewSet):
    serializer_class = FinanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = FinanceFilter
    search_fields = ['description']
    ordering = ['-transaction_date']

    def get_queryset(self):
        return Finance.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        extra = {}
        if 'status' not in self.request.data:
            txn_date = serializer.validated_data['transaction_date']
            status_value, confirmed_date = default_status_for_date(txn_date, date.today())
            extra['status'] = status_value
            extra['confirmed_date'] = confirmed_date
        elif serializer.validated_data.get('status') == 'confirmed' and not serializer.validated_data.get('confirmed_date'):
            extra['confirmed_date'] = serializer.validated_data.get('transaction_date') or date.today()
        serializer.save(user=self.request.user, **extra)

    def perform_update(self, serializer):
        extra = {}
        new_status = serializer.validated_data.get('status', serializer.instance.status)
        if new_status == 'confirmed' and not serializer.validated_data.get('confirmed_date') and not serializer.instance.confirmed_date:
            extra['confirmed_date'] = serializer.validated_data.get('transaction_date', serializer.instance.transaction_date)
        elif new_status == 'pending':
            extra['confirmed_date'] = None
        serializer.save(**extra)

    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm(self, request, pk=None):
        """Marca a transação como confirmada (paga/recebida), opcionalmente numa data diferente da prevista."""
        instance = self.get_object()
        confirmed_date_str = request.data.get('confirmed_date')
        if confirmed_date_str:
            try:
                confirmed_date = parse_date(confirmed_date_str)
            except ValueError:
                return Response({'confirmed_date': 'Data inválida.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            confirmed_date = date.today()
        instance.status = 'confirmed'
        instance.confirmed_date = confirmed_date
        instance.save(update_fields=['status', 'confirmed_date', 'updated_at'])
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'], url_path='unconfirm')
    def unconfirm(self, request, pk=None):
        """Volta a transação para pendente (ainda não paga/recebida de fato)."""
        instance = self.get_object()
        instance.status = 'pending'
        instance.confirmed_date = None
        instance.save(update_fields=['status', 'confirmed_date', 'updated_at'])
        return Response(self.get_serializer(instance).data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumo financeiro por período"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_param = request.query_params.get('status')

        queryset = self.get_queryset()
        if start_date and end_date:
            queryset = queryset.filter(
                transaction_date__gte=start_date,
                transaction_date__lte=end_date
            )
        if status_param:
            queryset = queryset.filter(status=status_param)

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
        """Agrupa transações por categoria (opcionalmente filtrado por período e tipo)"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        finance_type = request.query_params.get('type')
        status_param = request.query_params.get('status')

        queryset = self.get_queryset()
        if start_date and end_date:
            queryset = queryset.filter(
                transaction_date__gte=start_date,
                transaction_date__lte=end_date
            )
        if finance_type:
            queryset = queryset.filter(type=finance_type)
        if status_param:
            queryset = queryset.filter(status=status_param)

        categories = queryset.values('category').annotate(
            total=Sum('amount')
        ).order_by('-total')
        return Response(categories)

    @action(detail=False, methods=['post'], url_path='create-installments')
    def create_installments(self, request):
        """Cria uma despesa/receita parcelada: divide o valor total em N lançamentos mensais."""
        data = request.data
        try:
            total_amount = Decimal(str(data.get('total_amount')))
            installments_count = int(data.get('installments_count'))
            start_date = parse_date(data.get('start_date'))
        except (TypeError, ValueError, InvalidOperation):
            return Response({'detail': 'total_amount, installments_count e start_date são obrigatórios e devem ser válidos.'},
                             status=status.HTTP_400_BAD_REQUEST)

        if total_amount <= 0:
            return Response({'total_amount': 'Deve ser maior que zero.'}, status=status.HTTP_400_BAD_REQUEST)
        if installments_count < 2 or installments_count > MAX_SERIES_LENGTH:
            return Response({'installments_count': f'Deve ser entre 2 e {MAX_SERIES_LENGTH}.'}, status=status.HTTP_400_BAD_REQUEST)

        finance_type = data.get('type')
        category = data.get('category')
        if finance_type not in dict(Finance.TYPE_CHOICES):
            return Response({'type': 'Tipo inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        if category not in dict(Finance.CATEGORY_CHOICES):
            return Response({'category': 'Categoria inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        skip_past = bool(data.get('skip_past', False))
        today = date.today()

        base_amount = (total_amount / installments_count).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        remainder = total_amount - (base_amount * installments_count)

        group_id = uuid.uuid4()
        created = []
        for i in range(installments_count):
            due_date = add_months(start_date, i)
            if skip_past and due_date < today:
                continue
            amount = base_amount + (remainder if i == installments_count - 1 else Decimal('0.00'))
            status_value, confirmed_date = default_status_for_date(due_date, today)
            created.append(Finance.objects.create(
                user=request.user,
                type=finance_type,
                category=category,
                description=data.get('description') or '',
                amount=amount,
                transaction_date=due_date,
                status=status_value,
                confirmed_date=confirmed_date,
                payment_method=data.get('payment_method') or None,
                group_id=group_id,
                installment_number=i + 1,
                installment_total=installments_count,
            ))

        if not created:
            return Response({'detail': 'Todas as parcelas calculadas já estão no passado.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(created, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='create-recurring')
    def create_recurring(self, request):
        """Cria uma despesa/receita fixa: gera N ocorrências mensais do mesmo valor."""
        data = request.data
        try:
            amount = Decimal(str(data.get('amount')))
            months = int(data.get('months', 12))
            start_date = parse_date(data.get('start_date'))
        except (TypeError, ValueError, InvalidOperation):
            return Response({'detail': 'amount, months e start_date são obrigatórios e devem ser válidos.'},
                             status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({'amount': 'Deve ser maior que zero.'}, status=status.HTTP_400_BAD_REQUEST)
        if months < 1 or months > MAX_SERIES_LENGTH:
            return Response({'months': f'Deve ser entre 1 e {MAX_SERIES_LENGTH}.'}, status=status.HTTP_400_BAD_REQUEST)

        finance_type = data.get('type')
        category = data.get('category')
        if finance_type not in dict(Finance.TYPE_CHOICES):
            return Response({'type': 'Tipo inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        if category not in dict(Finance.CATEGORY_CHOICES):
            return Response({'category': 'Categoria inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        skip_past = bool(data.get('skip_past', False))
        today = date.today()

        group_id = uuid.uuid4()
        created = []
        for i in range(months):
            due_date = add_months(start_date, i)
            if skip_past and due_date < today:
                continue
            status_value, confirmed_date = default_status_for_date(due_date, today)
            created.append(Finance.objects.create(
                user=request.user,
                type=finance_type,
                category=category,
                description=data.get('description') or '',
                amount=amount,
                transaction_date=due_date,
                status=status_value,
                confirmed_date=confirmed_date,
                payment_method=data.get('payment_method') or None,
                group_id=group_id,
                is_recurring=True,
            ))

        if not created:
            return Response({'detail': 'Todas as ocorrências calculadas já estão no passado.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(created, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='delete-series')
    def delete_series(self, request, pk=None):
        """Exclui as demais transações da mesma série (parcelas ou despesa fixa)."""
        instance = self.get_object()
        if not instance.group_id:
            return Response({'detail': 'Esta transação não faz parte de uma série.'}, status=status.HTTP_400_BAD_REQUEST)

        scope = request.data.get('scope', 'future')
        queryset = self.get_queryset().filter(group_id=instance.group_id)
        if scope == 'future':
            queryset = queryset.filter(transaction_date__gte=instance.transaction_date)

        deleted_count, _ = queryset.delete()
        return Response({'deleted': deleted_count})