from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Q
from .models import ReadingPlanTemplate, UserReadingPlan, ReadingDay
from .reading_plan_serializers import (
    ReadingPlanTemplateSerializer,
    UserReadingPlanSerializer,
    ReadingDaySerializer,
    CreateReadingPlanSerializer,
    UpdateReadingStatusSerializer,
    ReadingStatsSerializer
)


class ReadingPlanTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para templates de planos de leitura"""
    queryset = ReadingPlanTemplate.objects.filter(is_active=True)
    serializer_class = ReadingPlanTemplateSerializer
    permission_classes = [IsAuthenticated]


class UserReadingPlanViewSet(viewsets.ModelViewSet):
    """ViewSet para planos de leitura dos usuários"""
    serializer_class = UserReadingPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserReadingPlan.objects.filter(
            user=self.request.user
        ).prefetch_related('reading_days')

    def get_serializer_context(self):
        """Adiciona o request ao context do serializer"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=False, methods=['get'], url_path='my-plans')
    def my_plans(self, request):
        """Lista planos do usuário"""
        plans = self.get_queryset()
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_plan(self, request):
        """Cria novo plano de leitura"""
        serializer = CreateReadingPlanSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        plan = serializer.save()

        return Response(
            UserReadingPlanSerializer(plan).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def today(self, request, pk=None):
        """Retorna leitura do dia atual"""
        plan = self.get_object()
        today = date.today()

        reading = plan.reading_days.filter(date=today).first()
        if not reading:
            return Response(
                {'detail': 'Não há leitura programada para hoje'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReadingDaySerializer(reading)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        ✅ CORRIGIDO: Retorna TODAS as leituras do plano, opcionalmente filtradas por mês
        Aceita parâmetro 'month' no formato YYYY-MM
        """
        plan = self.get_object()
        month = request.query_params.get('month')

        # ✅ CORREÇÃO: Começar com TODAS as leituras do plano
        readings = plan.reading_days.all()

        # Filtrar por mês se fornecido (para exibição do calendário)
        if month:
            try:
                # Validar formato YYYY-MM
                if len(month) != 7 or month[4] != '-':
                    return Response(
                        {'detail': 'Formato de mês inválido. Use YYYY-MM (ex: 2025-11)'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                year, month_num = map(int, month.split('-'))

                # Validar valores
                if not (1 <= month_num <= 12):
                    return Response(
                        {'detail': 'Mês deve estar entre 01 e 12'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # ✅ IMPORTANTE: Filtrar por ano e mês, mas incluir TODOS os status
                # Isso garante que dias pendentes também apareçam
                readings = readings.filter(date__year=year, date__month=month_num)

            except (ValueError, AttributeError) as e:
                return Response(
                    {'detail': f'Formato de mês inválido. Use YYYY-MM. Erro: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Ordenar por data
        readings = readings.order_by('date')

        # Serializar
        serializer = ReadingDaySerializer(readings, many=True)

        # ✅ DEBUG: Log para verificar quantos dias estão sendo retornados
        print(f"📅 Retornando {len(serializer.data)} dias de leitura para o mês {month}")

        # Retornar array direto (não objeto com results)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Retorna estatísticas do plano"""
        plan = self.get_object()

        # Dias completados
        completed_days = plan.reading_days.filter(status='completed').count()

        # Calcular streak atual
        current_streak = self._calculate_current_streak(plan)

        # Calcular maior streak
        longest_streak = self._calculate_longest_streak(plan)

        # Taxa de conclusão
        completion_rate = round((completed_days / plan.total_days) * 100, 1) if plan.total_days > 0 else 0

        # Média por semana
        days_elapsed = (date.today() - plan.start_date).days + 1
        weeks_elapsed = days_elapsed / 7
        average_per_week = round(completed_days / weeks_elapsed, 1) if weeks_elapsed > 0 else 0

        stats_data = {
            'total_days': plan.total_days,
            'completed_days': completed_days,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'completion_rate': completion_rate,
            'average_per_week': average_per_week
        }

        serializer = ReadingStatsSerializer(stats_data)
        return Response(serializer.data)

    def _calculate_current_streak(self, plan):
        """Calcula sequência atual de dias consecutivos"""
        today = date.today()
        streak = 0
        current_date = today

        while current_date >= plan.start_date:
            reading = plan.reading_days.filter(date=current_date, status='completed').first()
            if not reading:
                break
            streak += 1
            current_date -= timedelta(days=1)

        return streak

    def _calculate_longest_streak(self, plan):
        """Calcula maior sequência de dias consecutivos"""
        completed_readings = plan.reading_days.filter(
            status='completed'
        ).order_by('date').values_list('date', flat=True)

        if not completed_readings:
            return 0

        max_streak = 1
        current_streak = 1

        for i in range(1, len(completed_readings)):
            if (completed_readings[i] - completed_readings[i - 1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1

        return max_streak


class ReadingDayViewSet(viewsets.ModelViewSet):
    """ViewSet para dias de leitura"""
    serializer_class = ReadingDaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReadingDay.objects.filter(
            plan__user=self.request.user
        ).select_related('plan')

    def partial_update(self, request, pk=None):
        """Atualiza status da leitura"""
        reading = self.get_object()
        serializer = UpdateReadingStatusSerializer(
            reading,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(ReadingDaySerializer(reading).data)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Marca leitura como concluída"""
        reading = self.get_object()
        reading.status = 'completed'
        reading.completed_at = timezone.now()
        reading.save()

        serializer = self.get_serializer(reading)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_skipped(self, request, pk=None):
        """Marca leitura como pulada"""
        reading = self.get_object()
        reading.status = 'skipped'
        reading.completed_at = None
        reading.save()

        serializer = self.get_serializer(reading)
        return Response(serializer.data)