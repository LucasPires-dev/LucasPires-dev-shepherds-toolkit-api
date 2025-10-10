from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Member, PastoralVisit
from .serializers import MemberSerializer, PastoralVisitSerializer
from rest_framework import filters


class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'ministry', 'cell_group']
    search_fields = ['full_name', 'email', 'phone']
    ordering = ['full_name']

    def get_queryset(self):
        return Member.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estatísticas de membros"""
        queryset = self.get_queryset()
        data = {
            'total': queryset.count(),
            'active': queryset.filter(status='active').count(),
            'inactive': queryset.filter(status='inactive').count(),
            'visitors': queryset.filter(status='visitor').count(),
        }
        return Response(data)

    @action(detail=False, methods=['get'])
    def birthdays_this_month(self, request):
        """Aniversariantes do mês"""
        current_month = datetime.now().month
        birthdays = self.get_queryset().filter(
            birth_date__month=current_month
        ).order_by('birth_date__day')
        serializer = self.get_serializer(birthdays, many=True)
        return Response(serializer.data)


class PastoralVisitViewSet(viewsets.ModelViewSet):
    serializer_class = PastoralVisitSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['visit_type', 'follow_up_needed', 'member']
    ordering = ['-visit_date']

    def get_queryset(self):
        return PastoralVisit.objects.filter(user=self.request.user).select_related('member')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)