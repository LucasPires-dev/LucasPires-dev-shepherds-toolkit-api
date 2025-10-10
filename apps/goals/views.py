from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Goal, GoalTask, GoalComment
from .serializers import (
    GoalSerializer, GoalListSerializer, GoalTaskSerializer, GoalCommentSerializer
)


class GoalViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'priority', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'end_date', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return GoalListSerializer
        return GoalSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Retorna dados do dashboard de metas"""
        queryset = self.get_queryset()
        data = {
            'total': queryset.count(),
            'not_started': queryset.filter(status='not_started').count(),
            'in_progress': queryset.filter(status='in_progress').count(),
            'completed': queryset.filter(status='completed').count(),
            'paused': queryset.filter(status='paused').count(),
            'high_priority': queryset.filter(priority='high').count(),
        }
        return Response(data)

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Atualiza o progresso da meta"""
        goal = self.get_object()
        progress = request.data.get('progress_percentage')
        if progress is not None:
            goal.progress_percentage = progress
            goal.save()
        return Response({'progress_percentage': goal.progress_percentage})


class GoalTaskViewSet(viewsets.ModelViewSet):
    serializer_class = GoalTaskSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'goal']

    def get_queryset(self):
        return GoalTask.objects.filter(goal__user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marca tarefa como concluída"""
        task = self.get_object()
        task.status = 'completed'
        task.save()
        return Response({'status': 'completed'})


class GoalCommentViewSet(viewsets.ModelViewSet):
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        return GoalComment.objects.filter(goal__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)